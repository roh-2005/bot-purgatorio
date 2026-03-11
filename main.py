import telebot
import time
import threading
import os
import logging
import random
from flask import Flask
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# Configuração do Flask para o Render
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot Purgatório Online!", 200

# ================= CONFIGURAÇÕES =================
TOKEN = "8791899548:AAGS5UjIX2YStk7ZM7PfnNlL0upeld_5Ea4"
bot = telebot.TeleBot(TOKEN, parse_mode="HTML")

# ================= BANCO DE DADOS =================
p_bases = ["Qual seu fetiche?", "Beijaria quem aqui?", "Já transou em público?", "Maior segredo?", "Já fingiu prazer?"]
d_bases = ["Áudio gemendo.", "Print do histórico.", "Ligue pro ex.", "Foto de agora.", "Vídeo rebolando."]

VERDADES = [f"{random.choice(p_bases)} (#{i+1})" for i in range(300)]
DESAFIOS = [f"{random.choice(d_bases)} (#{i+1})" for i in range(300)]

# ================= MEMÓRIA DO BOT =================
# Banco de dados temporário de membros por grupo
usuarios_conhecidos = {} 
jogos_ativos = {} 

def registrar_membro(chat_id, user_id, nome):
    """Registra qualquer pessoa que o bot encontrar."""
    if chat_id not in usuarios_conhecidos:
        usuarios_conhecidos[chat_id] = {}
    
    # Não registra o próprio bot
    if user_id not in [536215124, 777000]: 
        usuarios_conhecidos[chat_id][user_id] = nome

def monitorar_tempo(chat_id, user_id, msg_id):
    time.sleep(60)
    if chat_id in jogos_ativos and not jogos_ativos[chat_id].get('respondido'):
        try:
            bot.edit_message_text("⏰ <b>Tempo esgotado!</b> O sorteado não escolheu.", chat_id, msg_id, reply_markup=None)
        except: pass
        jogos_ativos[chat_id]['respondido'] = True

# ================= CAPTURA DE MEMBROS =================
@bot.message_handler(content_types=['new_chat_members', 'text'])
def capturar_interacao(message):
    chat_id = message.chat.id
    # Se alguém entrar
    if message.content_type == 'new_chat_members':
        for m in message.new_chat_members:
            registrar_membro(chat_id, m.id, m.first_name)
    # Se alguém falar
    else:
        registrar_membro(chat_id, message.from_user.id, message.from_user.first_name)
        if message.text == "/vd":
            iniciar_partida(message)

# ================= COMANDO PRINCIPAL =================
def iniciar_partida(message):
    chat_id = message.chat.id
    u_id = message.from_user.id
    nome = message.from_user.first_name
    mencao = f"<a href='tg://user?id={u_id}'>{nome}</a>"
    
    jogos_ativos[chat_id] = {
        'dono': u_id,
        'dono_mencao': mencao,
        'respondido': True,
        'sorteado_id': None,
        'sorteado_mencao': ""
    }
    
    markup = InlineKeyboardMarkup()
    markup.row(InlineKeyboardButton("Girar Garrafa 🍾", callback_data="girar"))
    markup.row(InlineKeyboardButton("Verdade 🙊", callback_data="v"), InlineKeyboardButton("Desafio 😈", callback_data="d"))
    
    bot.send_message(chat_id, f"🔥 <b>Purgatório: Verdade ou Desafio</b>\nRodada iniciada por: {mencao}", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def tratar_cliques(call):
    chat_id = call.message.chat.id
    user_id = call.from_user.id
    msg_id = call.message.message_id
    
    # Registra quem clica também (ajuda a popular a lista)
    registrar_membro(chat_id, user_id, call.from_user.first_name)

    if chat_id not in jogos_ativos: return

    # TRAVA: Só quem iniciou ou quem foi sorteado joga
    permitido = jogos_ativos[chat_id]['sorteado_id'] if not jogos_ativos[chat_id]['respondido'] else jogos_ativos[chat_id]['dono']
    
    if user_id != permitido:
        bot.answer_callback_query(call.id, "Não está na sua vez de jogar!", show_alert=True)
        return

    # AÇÃO: GIRAR
    if call.data == "girar":
        # Puxa Admins na hora para aumentar a lista de sorteáveis
        try:
            admins = bot.get_chat_administrators(chat_id)
            for adm in admins:
                if not adm.user.is_bot:
                    registrar_membro(chat_id, adm.user.id, adm.user.first_name)
        except: pass

        lista_membros = list(usuarios_conhecidos.get(chat_id, {}).items())

        for i in range(5, 0, -1):
            bot.edit_message_text(f"🍾 <b>Girando...</b> ({i}s)", chat_id, msg_id)
            time.sleep(1)

        # Sorteia qualquer um da lista acumulada
        s_id, s_nome = random.choice(lista_membros)
        s_mencao = f"<a href='tg://user?id={s_id}'>{s_nome}</a>"
        
        jogos_ativos[chat_id].update({'sorteado_id': s_id, 'sorteado_mencao': s_mencao, 'respondido': False})

        markup = InlineKeyboardMarkup()
        markup.row(InlineKeyboardButton("Verdade 🙊", callback_data="v"), InlineKeyboardButton("Desafio 😈", callback_data="d"))
        
        bot.edit_message_text(f"🎯 <b>Parou em:</b> {s_mencao}\nEscolha agora!", chat_id, msg_id, reply_markup=markup)
        threading.Thread(target=monitorar_tempo, args=(chat_id, s_id, msg_id), daemon=True).start()

    # AÇÃO: VERDADE OU DESAFIO
    elif call.data in ["v", "d"]:
        texto = random.choice(VERDADES) if call.data == "v" else random.choice(DESAFIOS)
        titulo = "🙊 VERDADE" if call.data == "v" else "😈 DESAFIO"
        alvo = jogos_ativos[chat_id]['sorteado_mencao'] if jogos_ativos[chat_id]['sorteado_id'] else jogos_ativos[chat_id]['dono_mencao']
        
        bot.edit_message_text(f"<b>{titulo} PARA {alvo}:</b>\n\n{texto}", chat_id, msg_id, reply_markup=None)
        jogos_ativos[chat_id].update({'respondido': True, 'sorteado_id': None})

# ================= EXECUÇÃO =================
def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

if __name__ == "__main__":
    threading.Thread(target=run_flask).start()
    bot.infinity_polling()
    
