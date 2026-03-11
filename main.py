import telebot
import time
import threading
import os
import logging
import random
from flask import Flask
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# Silencia avisos do Flask
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
    "Qual sua posição favorita?", "Já ficou com alguém por pena?", "Quem aqui beija melhor só de olhar?",
    "O que você faria se fosse invisível em um vestiário?", "Já foi pego no flagra?", "Qual sua maior loucura na cama?"
]

d_bases = [
    "Mande um áudio de 30 segundos simulando um gemido.", "Mande print do seu histórico do navegador agora.",
    "Ligue para um ex e diga que ainda o(a) ama.", "Tire uma foto só de toalha/roupa íntima e mande.",
    "Mande um áudio cantando um funk proibidão.", "Morda o lábio de forma provocante e mande foto.",
    "Poste no status: 'Sou viciado em sacanagem' por 5 minutos.", "Mande foto do seu pé agora.",
    "Faça um vídeo curto rebolando e mande aqui.", "Dê um selinho em um objeto e mande vídeo.",
    "Mande mensagem para sua mãe dizendo 'estou grávida/engravidei alguém' e mostre o print.",
    "Descreva detalhadamente o que faria com o @ que girou a garrafa."
]

VERDADES = [f"{random.choice(p_bases)} (#{i+1})" for i in range(300)]
DESAFIOS = [f"{random.choice(d_bases)} (#{i+1})" for i in range(300)]

# ================= ESTADO DO JOGO =================
jogos = {} 

def monitorar_tempo(chat_id, user_id, msg_id):
    time.sleep(60)
    if chat_id in jogos and not jogos[chat_id].get('respondido'):
        try:
            bot.edit_message_text("⏰ <b>Tempo esgotado!</b> O jogador perdeu a vez.", chat_id, msg_id, reply_markup=None)
        except: pass
        jogos[chat_id]['respondido'] = True

def criar_menu():
    markup = InlineKeyboardMarkup()
    btn_girar = InlineKeyboardButton("Girar Garrafa 🍾", callback_data="girar")
    btn_v = InlineKeyboardButton("Verdade 🙊", callback_data="v")
    btn_d = InlineKeyboardButton("Desafio 😈", callback_data="d")
    markup.row(btn_girar)
    markup.row(btn_v, btn_d)
    return markup

# ================= COMANDOS =================
@bot.message_handler(commands=['vd'])
def cmd_vd(message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    nome = message.from_user.first_name
    
    # Cria a menção clicável
    mencao = f"<a href='tg://user?id={user_id}'>{nome}</a>"
    
    jogos[chat_id] = {
        'dono': user_id,
        'dono_nome': nome,
        'dono_mencao': mencao,
        'respondido': True
    }
    
    bot.send_message(
        chat_id, 
        f"🔥 <b>Purgatório: Verdade ou Desafio</b>\nRodada iniciada por: {mencao}", 
        reply_markup=criar_menu()
    )

@bot.callback_query_handler(func=lambda call: True)
def tratar_cliques(call):
    chat_id = call.message.chat.id
    user_id = call.from_user.id
    msg_id = call.message.message_id

    if chat_id not in jogos:
        bot.answer_callback_query(call.id, "Use /vd para começar!", show_alert=True)
        return

    # TRAVA: Só o dono do /vd (mencionado) pode clicar
    if user_id != jogos[chat_id]['dono']:
        bot.answer_callback_query(call.id, f"⚠️ Apenas {jogos[chat_id]['dono_nome']} pode interagir nesta rodada!", show_alert=True)
        return

    # AÇÃO: GIRAR
    if call.data == "girar":
        for i in range(5, 0, -1):
            bot.edit_message_text(f"🍾 <b>Girando...</b> ({i}s)", chat_id, msg_id)
            time.sleep(1)
        
        jogos[chat_id]['respondido'] = False
        mencao = jogos[chat_id]['dono_mencao']

        bot.edit_message_text(
            f"🎯 <b>Parou em você, {mencao}!</b>\nEscolha Verdade ou Desafio rápido!",
            chat_id, msg_id, reply_markup=criar_menu()
        )
        threading.Thread(target=monitorar_tempo, args=(chat_id, user_id, msg_id), daemon=True).start()

    # AÇÃO: VERDADE OU DESAFIO
    elif call.data in ["v", "d"]:
        texto = random.choice(VERDADES) if call.data == "v" else random.choice(DESAFIOS)
        emoji = "🙊 VERDADE" if call.data == "v" else "😈 DESAFIO"
        
        bot.edit_message_text(
            f"<b>{emoji} PARA {jogos[chat_id]['dono_mencao']}:</b>\n\n{texto}", 
            chat_id, msg_id, 
            reply_markup=None 
        )
        jogos[chat_id]['respondido'] = True

# ================= EXECUÇÃO =================
def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

if __name__ == "__main__":
    threading.Thread(target=run_flask).start()
    bot.infinity_polling()
    
