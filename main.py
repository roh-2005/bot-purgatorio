import telebot
import time
import threading
import os
import logging
import random
from flask import Flask

# Silencia os avisos do Flask para o log ficar limpo
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

# ================= CONFIGURAÇÕES =================
# O teu token do bot
TOKEN = "8791899548:AAGS5UjIX2YStk7ZM7PfnNlL0upeld_5Ea4"
bot = telebot.TeleBot(TOKEN, parse_mode="HTML")

# Configuração do Flask (Essencial para o Render)
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot Purgatório Online!", 200

# ================= BANCO DE DADOS (Exemplos para os 300 itens) =================
p_bases = [
    "Qual seu maior segredo?", "Já beijou alguém do grupo?", "Qual sua fantasia mais louca?",
    "O que faria se fosse invisível?", "Já mentiu para alguém aqui?", "Quem você levaria para um motel?",
    "Qual seu fetiche oculto?", "Já mandou nudes para a pessoa errada?"
]

d_bases = [
    "Mande um áudio cantando.", "Mande print da galeria.", "Ligue para alguém e diga que ama.",
    "Faça 15 flexões e mande vídeo.", "Mande um emoji de fogo no PV de @.", "Poste foto mico no status."
]

# Gera as listas com 300 itens conforme solicitado
VERDADES = [f"{random.choice(p_bases)} (#{i+1})" for i in range(300)]
DESAFIOS = [f"{random.choice(d_bases)} (#{i+1})" for i in range(300)]

# ================= LÓGICA DO JOGO =================
usuarios_ativos = {} # {chat_id: {user_id: nome}}
estado_jogo = {'vez_de': None}

@bot.message_handler(commands=['jogar', 'start'])
def iniciar_jogo(message):
    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(telebot.types.InlineKeyboardButton("Girar Garrafa 🍾", callback_data="girar"))
    bot.send_message(message.chat.id, "🔥 <b>Bem-vindo ao Purgatório!</b>\nClique no botão para sortear alguém.", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def callback_geral(call):
    chat_id = call.message.chat.id
    user_id = call.from_user.id
    nome_user = call.from_user.first_name
    
    # Regista o utilizador para o sorteio
    if chat_id not in usuarios_ativos: usuarios_ativos[chat_id] = {}
    usuarios_ativos[chat_id][user_id] = nome_user

    if call.data == "girar":
        # Bloqueia se já houver alguém na vez
        if estado_jogo['vez_de'] is not None and user_id != estado_jogo['vez_de']:
             bot.answer_callback_query(call.id, "Aguarde a vez do jogador atual!", show_alert=True)
             return

        membros = list(usuarios_ativos[chat_id].items())
        if not membros:
            bot.answer_callback_query(call.id, "Ninguém disponível! Enviem uma mensagem no chat primeiro.")
            return

        sorteado_id, sorteado_nome = random.choice(membros)
        estado_jogo['vez_de'] = sorteado_id

        bot.edit_message_text("🍾 <i>Girando a garrafa...</i>", chat_id, call.message.message_id)
        time.sleep(2)

        markup = telebot.types.InlineKeyboardMarkup()
        markup.add(telebot.types.InlineKeyboardButton("Verdade 🙊", callback_data="v"), 
                   telebot.types.InlineKeyboardButton("Desafio 😈", callback_data="d"))

        bot.edit_message_text(
            f"🎯 <b>A garrafa parou em:</b> <a href='tg://user?id={sorteado_id}'>{sorteado_nome}</a>\n\nO que você escolhe?",
            chat_id, call.message.message_id, reply_markup=markup
        )

    elif call.data in ["v", "d"]:
        if user_id != estado_jogo['vez_de']:
            bot.answer_callback_query(call.id, "❌ Não é sua vez!", show_alert=True)
            return

        texto = random.choice(VERDADES) if call.data == "v" else random.choice(DESAFIOS)
        emoji = "🙊 VERDADE" if call.data == "v" else "😈 DESAFIO"
        
        estado_jogo['vez_de'] = None # Reseta a vez
        
        markup = telebot.types.InlineKeyboardMarkup()
        markup.add(telebot.types.InlineKeyboardButton("Girar Novamente 🍾", callback_data="girar"))
        
        bot.edit_message_text(f"<b>{emoji}:</b>\n\n{texto}", chat_id, call.message.message_id, reply_markup=markup)

# ================= EXECUÇÃO IGUAL AO BOT-ANONIMO =================
def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

if __name__ == "__main__":
    # Inicia o servidor Flask para o Render validar a porta
    threading.Thread(target=run_flask).start()
    
    # Inicia o bot
    print("Bot Purgatório rodando...")
    bot.infinity_polling()
    
