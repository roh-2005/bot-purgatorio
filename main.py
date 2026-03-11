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
p_bases = [
    "Qual seu fetiche mais bizarro?", "Quem do grupo você beijaria agora?", "Já transou em lugar público?",
    "Qual sua fantasia sexual?", "Já mandou nudes para a pessoa errada?", "Já beijou alguém do mesmo sexo?",
    "Qual parte do corpo você acha mais sexy?", "Quem aqui você levaria para um motel?", "Já fingiu prazer?",
    "Qual o maior segredo que esconde dos seus pais?", "Já teve um sonho erótico com alguém daqui?",
    "Qual sua posição favorita?", "Já ficou com alguém por pena?", "Quem aqui beija melhor só de olhar?"
]

d_bases = [
    "Mande um áudio de 30 segundos simulando um gemido.", "Mande print do seu histórico do navegador agora.",
    "Ligue para um ex e diga que ainda o(a) ama.", "Tire uma foto só de toalha/roupa íntima e mande.",
    "Mande um áudio cantando um funk proibidão.", "Morda o lábio de forma provocante e mande foto.",
    "Poste no status: 'Sou viciado em sacanagem' por 5 minutos.", "Mande foto do seu pé agora.",
    "Faça um vídeo curto rebolando e mande aqui.", "Dê um selinho em um objeto e mande vídeo."
]

VERDADES = [f"{random.choice(p_bases)} (#{i+1})" for i in range(300)]
DESAFIOS = [f"{random.choice(d_bases)} (#{i+1})" for i in range(300)]

# ================= MEMÓRIA DO BOT =================
# Armazena quem está ativo no grupo para poder sortear
usuarios_no_grupo = {} # {chat_id: {user_id: "Nome"}}
jogos_ativos = {} 

def registrar_usuario(message):
    """Adiciona qualquer pessoa que falar no grupo à lista de sorteio."""
    chat_id = message.chat.id
    user_id = message.from_user.id
    nome = message.from_user.first_name
    
    if chat_id not in usuarios_no_grupo:
        usuarios_no_grupo[chat_id] = {}
    usuarios_no_grupo[chat_id][user_id] = nome

def monitorar_tempo(chat_id, user_id, msg_id):
    time.sleep(60)
    if chat_id in jogos_ativos and not jogos_ativos[chat_id].get('respondido'):
        try:
            bot.edit_message_text("⏰ <b>Tempo esgotado!</b> O sorteado demorou muito.", chat_id, msg_id, reply_markup=None)
        except: pass
        jogos_ativos[chat_id]['respondido'] = True

# ================= COMANDOS =================
@bot.message_handler(func=lambda m: True)
def escutar_grupo(message):
    registrar_usuario(message) # Sempre registra quem fala
    
    if message.text == "/vd":
        chat_id = message.chat.id
        user_id = message.from_user.id
        nome = message.from_user.first_name
        mencao = f"<a href='tg://user?id={user_id}'>{nome}</a>"
        
        jogos_ativos[chat_id] = {
            'dono': user_id,
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

    if chat_id not in jogos_ativos: return

    # TRAVA DE SEGURANÇA + POP-UP PERSONALIZADO
    # Se alguém foi sorteado, só ele clica. Se ninguém foi sorteado ainda, só o dono clica.
    permitido = jogos_ativos[chat_id]['sorteado_id'] if not jogos_ativos[chat_id]['respondido'] else jogos_ativos[chat_id]['dono']
    
    if user_id != permitido:
        bot.answer_callback_query(call.id, "Não está na sua vez de jogar!", show_alert=True)
        return

    # AÇÃO: GIRAR
    if call.data == "girar":
        # Sorteia entre todos que o bot já "viu" no grupo
        lista_membros = list(usuarios_no_grupo.get(chat_id, {}).items())
        
        if len(lista_membros) < 2:
            bot.answer_callback_query(call.id, "Ainda não conheço membros suficientes para sortear! Mandem oi no grupo.", show_alert=True)
            return

        for i in range(5, 0, -1):
            bot.edit_message_text(f"🍾 <b>Girando...</b> ({i}s)", chat_id, msg_id)
            time.sleep(1)

        # SORTEIO REAL ALEATÓRIO
        s_id, s_nome = random.choice(lista_membros)
        s_mencao = f"<a href='tg://user?id={s_id}'>{s_nome}</a>"
        
        jogos_ativos[chat_id].update({
            'sorteado_id': s_id,
            'sorteado_mencao': s_mencao,
            'respondido': False
        })

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
        jogos_ativos[chat_id]['respondido'] = True
        jogos_ativos[chat_id]['sorteado_id'] = None

# ================= EXECUÇÃO =================
def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

if __name__ == "__main__":
    threading.Thread(target=run_flask).start()
    bot.infinity_polling()
        
