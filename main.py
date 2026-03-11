import telebot
import time
import threading
import os
import logging
import random
from flask import Flask
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# Configuração de logs e servidor Flask para o Render
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot Purgatório Online!", 200

# ================= CONFIGURAÇÕES =================
TOKEN = "8791899548:AAGS5UjIX2YStk7ZM7PfnNlL0upeld_5Ea4"
bot = telebot.TeleBot(TOKEN, parse_mode="HTML")

# ================= BANCO DE DADOS (300 + 300) =================
p_bases = [
    "Qual seu fetiche mais bizarro?", "Quem do grupo você beijaria agora?", "Já transou em lugar público?",
    "Qual sua fantasia sexual?", "Já mandou nudes para a pessoa errada?", "Já beijou alguém do mesmo sexo?",
    "Qual parte do corpo você acha mais sexy em alguém?", "Quem aqui você levaria para um motel?",
    "Já fingiu prazer?", "Qual o maior segredo que você esconde dos seus pais?", "Já usou brinquedos íntimos?",
    "Qual sua posição favorita?", "Já teve um sonho erótico com alguém daqui?", "Qual foi sua pior experiência na cama?",
    "Você prefere dominar ou ser dominado?", "Qual a coisa mais 'safada' que você já fez?", "Já ficou com alguém por interesse?"
]

d_bases = [
    "Mande um áudio de 30 segundos gemendo.", "Mande print do seu histórico do navegador agora.",
    "Ligue para um ex e diga que ainda o(a) ama.", "Tire uma foto só de toalha/roupa íntima e mande.",
    "Mande um emoji de fogo no PV da última pessoa que te chamou.", "Mande um áudio cantando um funk proibidão.",
    "Poste no status: 'Sou viciado em sacanagem' por 5 minutos.", "Morda o lábio de forma provocante e mande foto.",
    "Tire uma foto do seu pé e mande no grupo.", "Faça um vídeo curto rebolando e mande aqui.",
    "Mande uma mensagem picante para um contato aleatório e mostre o print.", "Descreva detalhadamente o que faria com o @ que girou a garrafa."
]

VERDADES = [f"{random.choice(p_bases)} (#{i+1})" for i in range(300)]
DESAFIOS = [f"{random.choice(d_bases)} (#{i+1})" for i in range(300)]

# ================= LÓGICA DO JOGO =================
usuarios_ativos = {}
estado_partida = {
    'vez_de': None,
    'nome_vez': "",
    'respondido': True,
    'processados': set()
}

def monitorar_tempo(chat_id, user_id, msg_id):
    time.sleep(60)
    if not estado_partida['respondido'] and estado_partida['vez_de'] == user_id:
        try:
            bot.edit_message_text("⏰ <b>Tempo esgotado!</b> O jogador não escolheu a tempo.", chat_id, msg_id, reply_markup=None)
        except: pass
        estado_partida['vez_de'] = None
        estado_partida['respondido'] = True

def menu_principal():
    markup = InlineKeyboardMarkup()
    btn_girar = InlineKeyboardButton("Girar Garrafa 🍾", callback_data="girar")
    btn_v = InlineKeyboardButton("Verdade 🙊", callback_data="v")
    btn_d = InlineKeyboardButton("Desafio 😈", callback_data="d")
    markup.row(btn_girar)
    markup.row(btn_v, btn_d)
    return markup

@bot.message_handler(commands=['vd'])
def cmd_vd(message):
    bot.send_message(
        message.chat.id, 
        "🔥 <b>Purgatório: Verdade ou Desafio</b>\nEscolha sua ação abaixo:", 
        reply_markup=menu_principal()
    )

@bot.callback_query_handler(func=lambda call: True)
def tratar_cliques(call):
    chat_id = call.message.chat.id
    user_id = call.from_user.id
    nome = call.from_user.first_name
    msg_id = call.message.message_id

    if chat_id not in usuarios_ativos: usuarios_ativos[chat_id] = {}
    usuarios_ativos[chat_id][user_id] = nome

    # Se já houver um sorteio da garrafa rolando, trava para outros
    if estado_partida['vez_de'] and user_id != estado_partida['vez_de']:
        bot.answer_callback_query(call.id, "⚠️ Você não está na vez!", show_alert=True)
        return

    # Ação: GIRAR
    if call.data == "girar":
        for i in range(5, 0, -1):
            bot.edit_message_text(f"🍾 <b>Girando...</b> ({i}s)", chat_id, msg_id)
            time.sleep(1)

        sorteado_id, sorteado_nome = random.choice(list(usuarios_ativos[chat_id].items()))
        estado_partida.update({'vez_de': sorteado_id, 'nome_vez': sorteado_nome, 'respondido': False})

        markup = InlineKeyboardMarkup()
        markup.row(InlineKeyboardButton("Verdade 🙊", callback_data="v"), InlineKeyboardButton("Desafio 😈", callback_data="d"))
        
        bot.edit_message_text(
            f"🎯 <b>Parou em:</b> <a href='tg://user?id={sorteado_id}'>{sorteado_nome}</a>\nEscolha em 1 minuto!",
            chat_id, msg_id, reply_markup=markup
        )
        threading.Thread(target=monitorar_tempo, args=(chat_id, sorteado_id, msg_id), daemon=True).start()

    # Ação: VERDADE OU DESAFIO (Direto ou após Girar)
    elif call.data in ["v", "d"]:
        texto = random.choice(VERDADES) if call.data == "v" else random.choice(DESAFIOS)
        titulo = "🙊 VERDADE" if call.data == "v" else "😈 DESAFIO"
        
        # O nome de quem recebe o desafio/pergunta
        alvo = estado_partida['nome_vez'] if estado_partida['nome_vez'] else nome
        
        bot.edit_message_text(f"<b>{titulo} PARA {alvo}:</b>\n\n{texto}", chat_id, msg_id, reply_markup=None)
        
        estado_partida['vez_de'] = None
        estado_partida['nome_vez'] = ""
        estado_partida['respondido'] = True

# ================= EXECUÇÃO =================
def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

if __name__ == "__main__":
    threading.Thread(target=run_flask).start()
    print("Bot Rodando 100% no Render!")
    bot.infinity_polling()
    
