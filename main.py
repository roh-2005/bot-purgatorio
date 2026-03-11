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

# ================= CONFIGURAÇÕES =================
TOKEN = "8791899548:AAGS5UjIX2YStk7ZM7PfnNlL0upeld_5Ea4"
bot = telebot.TeleBot(TOKEN, parse_mode="HTML")

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot Purgatório Online!", 200

# ================= BANCO DE DADOS (300 + 300) =================
p_bases = [
    "Qual seu fetiche mais bizarro?", "Quem do grupo você beijaria agora?", "Já transou em lugar público?",
    "Qual sua maior fantasia sexual?", "Já mandou nudes para a pessoa errada?", "Já beijou alguém do mesmo sexo?",
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

# Gerando 300 itens únicos para cada
VERDADES = [f"{random.choice(p_bases)} (#{i+1})" for i in range(300)]
DESAFIOS = [f"{random.choice(d_bases)} (#{i+1})" for i in range(300)]

# ================= ESTADO DO JOGO =================
usuarios_ativos = {} 
estado_global = {
    'vez_de': None,
    'nome_vez': "",
    'respondido': True,
    'botoes_clicados': set() # Anti-flood: rastreia IDs de mensagens já processadas
}

def reset_estado():
    estado_global['vez_de'] = None
    estado_global['nome_vez'] = ""
    estado_global['respondido'] = True

def timer_limite(chat_id, user_id, msg_id):
    """Aguarda 1 minuto. Se não responder, remove os botões e avisa."""
    time.sleep(60)
    if not estado_global['respondido'] and estado_global['vez_de'] == user_id:
        try:
            bot.edit_message_text(
                f"⏰ <b>O tempo acabou!</b>\n<a href='tg://user?id={user_id}'>{estado_global['nome_vez']}</a> não respondeu a tempo.",
                chat_id, msg_id, reply_markup=None
            )
        except: pass
        reset_estado()

# ================= COMANDOS =================
@bot.message_handler(commands=['vd'])
def iniciar_vd(message):
    markup = InlineKeyboardMarkup()
    # Apenas o botão de Girar inicialmente
    markup.add(InlineKeyboardButton("Girar Garrafa 🍾", callback_data="girar"))
    
    bot.send_message(
        message.chat.id, 
        "🔥 <b>Bem-vindo ao Purgatório!</b>\nClique no botão abaixo para começar a partida.", 
        reply_markup=markup
    )

@bot.callback_query_handler(func=lambda call: True)
def tratar_cliques(call):
    chat_id = call.message.chat.id
    user_id = call.from_user.id
    msg_id = call.message.message_id
    nome = call.from_user.first_name

    # Registra o usuário
    if chat_id not in usuarios_ativos: usuarios_ativos[chat_id] = {}
    usuarios_ativos[chat_id][user_id] = nome

    # 1. Trava de Intruso: Só quem está na vez pode clicar (se houver alguém na vez)
    if estado_global['vez_de'] and user_id != estado_global['vez_de']:
        bot.answer_callback_query(call.id, "⚠️ Não é sua vez! Espere o sorteado jogar.", show_alert=True)
        return

    # 2. Anti-Flood: Evita que o mesmo botão seja apertado duas vezes
    if f"{msg_id}_{call.data}" in estado_global['botoes_clicados']:
        bot.answer_callback_query(call.id, "Botão já processado!")
        return

    # AÇÃO: GIRAR
    if call.data == "girar":
        estado_global['botoes_clicados'].add(f"{msg_id}_{call.data}")
        
        # Contagem regressiva
        for i in range(5, 0, -1):
            bot.edit_message_text(f"🍾 <b>Girando a garrafa...</b>\nSorteando em {i} segundos!", chat_id, msg_id)
            time.sleep(1)

        membros = list(usuarios_ativos[chat_id].items())
        sorteado_id, sorteado_nome = random.choice(membros)
        
        estado_global.update({
            'vez_de': sorteado_id,
            'nome_vez': sorteado_nome,
            'respondido': False
        })

        # Cria botões Verdade e Desafio (lado a lado)
        markup = InlineKeyboardMarkup()
        markup.row(
            InlineKeyboardButton("Verdade 🙊", callback_data="v"),
            InlineKeyboardButton("Desafio 😈", callback_data="d")
        )

        bot.edit_message_text(
            f"🎯 <b>A garrafa parou em:</b> <a href='tg://user?id={sorteado_id}'>{sorteado_nome}</a>\n\nEscolha o que deseja!",
            chat_id, msg_id, reply_markup=markup
        )
        
        # Inicia o timer de 1 minuto
        threading.Thread(target=timer_limite, args=(chat_id, sorteado_id, msg_id), daemon=True).start()

    # AÇÃO: VERDADE OU DESAFIO
    elif call.data in ["v", "d"]:
        estado_global['botoes_clicados'].add(f"{msg_id}_{call.data}")
        
        texto = random.choice(VERDADES) if call.data == "v" else random.choice(DESAFIOS)
        emoji = "🙊 VERDADE" if call.data == "v" else "😈 DESAFIO"
        
        # Remove os botões completamente e envia a pergunta
        bot.edit_message_text(
            f"<b>{emoji} PARA {estado_global['nome_vez']}:</b>\n\n{texto}", 
            chat_id, msg_id, 
            reply_markup=None # OS BOTÕES SOMEM AQUI
        )
        
        reset_estado()

# ================= SERVIDOR =================
def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

if __name__ == "__main__":
    threading.Thread(target=run_flask).start()
    print("Bot Purgatório Rodando - Regras Atualizadas!")
    bot.infinity_polling()
    
