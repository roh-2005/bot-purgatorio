import telebot
import random
import os
import threading
from flask import Flask

# ================= CONFIGURAÇÕES =================
# O Render exige que você use variáveis de ambiente ou uma porta específica
TOKEN = "8600770877:AAEu929aQvg9UITe4km52OQYYSehjKlFO1U"
bot = telebot.TeleBot(TOKEN, parse_mode="HTML")

# Servidor Web para o Render não dar erro
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot está vivo!", 200

# Variáveis do Jogo
turno_vd = {} # {chat_id: {message_id: user_id_da_vez}}
usuarios_ativos_grupo = {} # {chat_id: {user_id: nome}}

# ================= LISTAS =================
VERDADES = [
    "Qual a sua maior insegurança na cama?",
    "Já teve sonhos eróticos com alguém deste grupo?",
    "Qual a mentira mais descarada que já contou?",
    "Qual o fetiche que você acha bizarro, mas tem vontade de testar?"
]

DESAFIOS = [
    "Mande um áudio de 10 segundos fingindo cansaço.",
    "Mude a sua bio para 'Gosto de ser dominado(a)' por 10 min.",
    "Mande a 15ª foto da sua galeria agora.",
    "Ligue para o primeiro do histórico e desligue na cara."
]

# ================= LÓGICA DO JOGO =================

@bot.callback_query_handler(func=lambda c: c.data.startswith('vd_'))
def handle_vd_clicks(c):
    chat_id = c.message.chat.id
    msg_id = c.message.message_id
    uid = c.from_user.id
    acao = c.data.split('_')[1]

    # 1. VERIFICAÇÃO DO JOGADOR DA VEZ
    jogador_da_vez = turno_vd.get(chat_id, {}).get(msg_id)

    # 2. POP-UP PARA INTRUSOS
    if jogador_da_vez and uid != jogador_da_vez:
        return bot.answer_callback_query(
            c.id, 
            "⚠️ NÃO É SUA VEZ!\nAguarde sua vez para interagir.", 
            show_alert=True
        )

    # 3. AÇÕES DO JOGADOR CORRETO
    if acao == 'verdade':
        res = random.choice(VERDADES)
        bot.edit_message_text(f"🟢 <b>VERDADE PARA:</b> {c.from_user.first_name}\n\n<i>{res}</i>", chat_id, msg_id)
        # Opcional: manter o botão de girar para a próxima rodada
    
    elif acao == 'desafio':
        res = random.choice(DESAFIOS)
        bot.edit_message_text(f"🔴 <b>DESAFIO PARA:</b> {c.from_user.first_name}\n\n<i>{res}</i>", chat_id, msg_id)

    elif acao == 'girar':
        participantes = list(usuarios_ativos_grupo.get(chat_id, {}).keys())
        
        if len(participantes) < 2:
            return bot.answer_callback_query(c.id, "❌ Preciso de pelo menos 2 pessoas ativas!", show_alert=True)
        
        outros = [p for p in participantes if p != uid]
        escolhido_id = random.choice(outros if outros else participantes)
        escolhido_nome = usuarios_ativos_grupo[chat_id][escolhido_id]
        
        # Define o novo dono da vez para esta mensagem
        if chat_id not in turno_vd: turno_vd[chat_id] = {}
        turno_vd[chat_id][msg_id] = escolhido_id

        markup = telebot.types.InlineKeyboardMarkup()
        markup.row(
            telebot.types.InlineKeyboardButton("🟢 Verdade", callback_data="vd_verdade"),
            telebot.types.InlineKeyboardButton("🔴 Desafio", callback_data="vd_desafio")
        )
        markup.add(telebot.types.InlineKeyboardButton("🍾 Girar Novamente", callback_data="vd_girar"))
        
        bot.edit_message_text(
            f"🍾 A garrafa parou em: <b>{escolhido_nome}</b>!\n\nEscolha sua punição:", 
            chat_id, 
            msg_id, 
            reply_markup=markup
        )

@bot.message_handler(commands=['vd'])
def cmd_vd(m):
    chat_id = m.chat.id
    uid = m.from_user.id
    nome = m.from_user.first_name
    
    if chat_id not in usuarios_ativos_grupo: usuarios_ativos_grupo[chat_id] = {}
    usuarios_ativos_grupo[chat_id][uid] = nome

    markup = telebot.types.InlineKeyboardMarkup()
    markup.row(
        telebot.types.InlineKeyboardButton("🟢 Verdade", callback_data="vd_verdade"),
        telebot.types.InlineKeyboardButton("🔴 Desafio", callback_data="vd_desafio")
    )
    markup.add(telebot.types.InlineKeyboardButton("🍾 Girar Garrafa", callback_data="vd_girar"))
    
    msg = bot.send_message(chat_id, f"🎯 <b>JOGO INICIADO!</b>\n\nVez de: <b>{nome}</b>", reply_markup=markup)
    
    if chat_id not in turno_vd: turno_vd[chat_id] = {}
    turno_vd[chat_id][msg.message_id] = uid

@bot.message_handler(func=lambda m: True)
def monitorar(m):
    chat_id = m.chat.id
    if chat_id not in usuarios_ativos_grupo: usuarios_ativos_grupo[chat_id] = {}
    usuarios_ativos_grupo[chat_id][m.from_user.id] = m.from_user.first_name

# ================= EXECUÇÃO =================

def run_bot():
    bot.infinity_polling(skip_pending=True)

if __name__ == "__main__":
    # Inicia o Bot em uma thread separada
    threading.Thread(target=run_bot).start()
    # Inicia o servidor Web na porta correta para o Render
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
    
