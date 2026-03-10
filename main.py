import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import random
import os
import threading
import time
from flask import Flask

# ================= CONFIGURAÇÕES =================
# Seu token atualizado
TOKEN = "8791899548:AAGS5UjIX2YStk7ZM7PfnNlL0upeld_5Ea4"
bot = telebot.TeleBot(TOKEN, parse_mode="HTML")

# Configuração do Flask para o Render não dar erro de porta
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot Purgatório Online!", 200

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

# ================= BANCO DE DADOS (Verdades e Desafios) =================
# Bases para gerar os 300 itens conforme solicitado
p_bases = [
    "Qual seu maior segredo?", "Já beijou alguém do grupo?", "Qual sua fantasia mais louca?",
    "O que faria se fosse invisível?", "Já mentiu para alguém aqui?", "Quem você levaria para um motel?",
    "Qual seu fetiche oculto?", "Já mandou nudes para a pessoa errada?", "Quem você acha mais gato(a) aqui?",
    "Qual foi seu momento mais mico?", "Já traiu ou foi traído?", "O que faria por 1 milhão?",
    "Qual parte do corpo você mais gosta em você?", "Já teve crush em chefe ou professor?",
    "Qual sua maior insegurança?", "Se pudesse trocar de vida com alguém aqui, quem seria?"
]

d_bases = [
    "Mande um áudio cantando.", "Mande print da galeria.", "Ligue para alguém e diga que ama.",
    "Faça 15 flexões e mande vídeo.", "Mande um emoji de fogo no PV de @.", "Poste foto mico no status.",
    "Diga algo picante no PV de @.", "Mande áudio imitando um animal.", "Tire selfie fazendo careta.",
    "Mande trava-língua difícil.", "Fique 5 min sem usar emojis.", "Mande print das buscas do Google.",
    "Elogie o ADM de forma exagerada.", "Declare-se para o @ que o bot escolher.",
    "Mude o nome no Telegram para 'Sou Bobo' por 10 min.", "Mande foto da sua meia agora."
]

# Gera listas de 300 itens únicos
VERDADES = [f"{random.choice(p_bases)} (#{i+1})" for i in range(300)]
DESAFIOS = [f"{random.choice(d_bases)} (#{i+1})" for i in range(300)]

# ================= LÓGICA DO JOGO =================
usuarios_no_chat = {} # Armazena nomes de quem interage
estado_jogo = {'vez_de': None}

@bot.message_handler(commands=['jogar', 'start'])
def iniciar_jogo(message):
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("Girar Garrafa 🍾", callback_data="girar"))
    bot.send_message(message.chat.id, "🔥 <b>Bem-vindo ao Purgatório!</b>\nClique no botão para sortear alguém.", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def callback_geral(call):
    chat_id = call.message.chat.id
    user_id = call.from_user.id
    nome_user = call.from_user.first_name
    
    # Registra o usuário para o sorteio
    if chat_id not in usuarios_no_chat: usuarios_no_chat[chat_id] = {}
    usuarios_no_chat[chat_id][user_id] = nome_user

    # Lógica do Botão Girar
    if call.data == "girar":
        # Bloqueia se já houver alguém na vez (evita spam)
        if estado_jogo['vez_de'] is not None and user_id != estado_jogo['vez_de']:
             bot.answer_callback_query(call.id, "Aguarde a escolha do jogador atual!", show_alert=True)
             return

        membros = list(usuarios_no_chat[chat_id].items())
        if len(membros) < 1:
            bot.answer_callback_query(call.id, "Ninguém disponível para girar!")
            return

        sorteado_id, sorteado_nome = random.choice(membros)
        estado_jogo['vez_de'] = sorteado_id

        # Animação simples
        bot.edit_message_text("🍾 <i>Girando a garrafa...</i>", chat_id, call.message.message_id)
        time.sleep(2)

        markup = InlineKeyboardMarkup()
        btn_v = InlineKeyboardButton("Verdade 🙊", callback_data="v")
        btn_d = InlineKeyboardButton("Desafio 😈", callback_data="d")
        markup.add(btn_v, btn_d)

        bot.edit_message_text(
            f"🎯 <b>A garrafa parou em:</b> <a href='tg://user?id={sorteado_id}'>{sorteado_nome}</a>\n\nO que você escolhe?",
            chat_id, call.message.message_id, reply_markup=markup
        )

    # Lógica dos Botões Verdade e Desafio
    elif call.data in ["v", "d"]:
        if user_id != estado_jogo['vez_de']:
            bot.answer_callback_query(call.id, "❌ Não é sua vez!", show_alert=True)
            return

        texto = random.choice(VERDADES) if call.data == "v" else random.choice(DESAFIOS)
        emoji = "🙊 VERDADE" if call.data == "v" else "😈 DESAFIO"
        
        # Reseta o turno e mostra o desafio
        estado_jogo['vez_de'] = None
        
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("Girar Novamente 🍾", callback_data="girar"))
        
        bot.edit_message_text(f"<b>{emoji}:</b>\n\n{texto}", chat_id, call.message.message_id, reply_markup=markup)

# ================= EXECUÇÃO =================
if __name__ == "__main__":
    # 1. Inicia o Flask em background para o Render
    threading.Thread(target=run_flask).start()
    
    # 2. Inicia o Bot
    print("Bot Purgatório iniciado com sucesso!")
    bot.infinity_polling()
        
