import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import random
import os
import threading
import time
from flask import Flask

# ================= CONFIGURAÇÕES =================
TOKEN = "8791899548:AAGS5UjIX2YStk7ZM7PfnNlL0upeld_5Ea4"
bot = telebot.TeleBot(TOKEN, parse_mode="HTML")

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot Online!", 200

# ================= BANCO DE DADOS (300 + 300) =================
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

# Gera 300 itens únicos misturando as bases
VERDADES = [f"{random.choice(p_bases)} (#{i+1})" for i in range(300)]
DESAFIOS = [f"{random.choice(d_bases)} (#{i+1})" for i in range(300)]

# ================= LÓGICA DO JOGO =================
usuarios_ativos = {}
estado_jogo = {'vez': None, 'msg_id': None, 'chat_id': None, 'timer': None}

def reset_timer(chat_id, msg_id, user_id):
    time.sleep(60) # 1 minuto
    if estado_jogo['vez'] == user_id:
        try:
            bot.edit_message_text("⏰ <b>O tempo acabou!</b> O jogador não escolheu nada. Girando novamente...", chat_id, msg_id, reply_markup=None)
            estado_jogo['vez'] = None
        except: pass

@bot.message_handler(commands=['jogar', 'start'])
def comando_jogar(message):
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("Girar Garrafa 🍾", callback_data="girar_inicio"))
    bot.send_message(message.chat.id, "🔥 <b>Purgatório: Verdade ou Desafio</b>\nAperte o botão para começar!", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def processar_clique(call):
    chat_id = call.message.chat.id
    user_id = call.from_user.id
    msg_id = call.message.message_id
    
    # Rastreia quem interage
    if chat_id not in usuarios_ativos: usuarios_ativos[chat_id] = {}
    usuarios_ativos[chat_id][user_id] = call.from_user.first_name

    # Só quem está na vez pode apertar
    if estado_jogo['vez'] and user_id != estado_jogo['vez'] and call.data != "girar_inicio":
        bot.answer_callback_query(call.id, "❌ Não é sua vez! Espere o sorteado.", show_alert=True)
        return

    if call.data in ["girar_inicio", "girar_denovo"]:
        # Anti-flood: Remove botões
        bot.edit_message_reply_markup(chat_id, msg_id, reply_markup=None)
        
        membros = list(usuarios_ativos.get(chat_id, {}).items())
        if not membros:
            bot.send_message(chat_id, "Preciso que alguém mande mensagem no grupo antes!")
            return

        # Contagem de 5s
        for i in range(5, 0, -1):
            try:
                bot.edit_message_text(f"🍾 <b>Girando... {i}s</b>", chat_id, msg_id)
                time.sleep(1)
            except: pass

        sorteado_id, nome = random.choice(membros)
        estado_jogo['vez'] = sorteado_id
        
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("Verdade 🙊", callback_data="v"), InlineKeyboardButton("Desafio 😈", callback_data="d"))
        bot.edit_message_text(f"🎯 <b>Vez de:</b> <a href='tg://user?id={sorteado_id}'>{nome}</a>\n\nEscolha em 1 minuto!", chat_id, msg_id, reply_markup=markup)
        
        # Inicia timer em thread separada
        threading.Thread(target=reset_timer, args=(chat_id, msg_id, sorteado_id)).start()

    elif call.data == "v":
        bot.edit_message_text(f"🙊 <b>VERDADE:</b>\n{random.choice(VERDADES)}", chat_id, msg_id, reply_markup=None)
        estado_jogo['vez'] = None
    
    elif call.data == "d":
        bot.edit_message_text(f"😈 <b>DESAFIO:</b>\n{random.choice(DESAFIOS)}", chat_id, msg_id, reply_markup=None)
        estado_jogo['vez'] = None

# ================= RODAR TUDO =================
if __name__ == "__main__":
    # Inicia o bot em uma thread
    threading.Thread(target=lambda: bot.infinity_polling(timeout=20)).start()
    
    # Inicia o Flask (O Render exige isso para confirmar que o bot está vivo)
    port = int(os.environ.get("PORT", 10000))
    print(f"Servidor rodando na porta {port}")
    app.run(host="0.0.0.0", port=port)
    
