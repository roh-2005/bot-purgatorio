import telebot
import time
import threading
import os
import logging
import random
from flask import Flask
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# Silencia avisos do Flask para o log do Render ficar limpo
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
    "Qual seu fetiche mais estranho?", "Já beijou alguém deste grupo em segredo?", 
    "Qual a coisa mais 'errada' que você já fez?", "Quem aqui você levaria para um quarto agora?",
    "Já fingiu prazer?", "Qual parte do seu corpo você mais gosta?", "Já mandou nudes para a pessoa errada?",
    "Qual sua fantasia sexual nunca realizada?", "Já teve um sonho erótico com alguém aqui?", 
    "Qual o lugar mais inusitado onde você já 'fez'?", "Quem aqui você acha que beija melhor só de olhar?",
    "Já ficou com alguém por pena?", "Qual sua opinião real sobre a pessoa que girou a garrafa?",
    "Qual foi sua maior mentira para conseguir sexo?", "Já usou brinquedos íntimos?", "Qual sua posição favorita?"
]

d_bases = [
    "Mande um áudio de 30 segundos simulando um gemido.", "Mande print do seu histórico de busca agora.",
    "Mande um print da sua galeria (sem apagar nada).", "Ligue para um ex e diga que sente saudade.",
    "Tire uma foto só de roupa íntima (ou sem camisa) e mande.", "Diga algo picante no PV de alguém do grupo.",
    "Mande um áudio cantando um funk proibidão.", "Poste no status: 'Sou viciado em sacanagem' por 5 min.",
    "Morda o lábio de forma provocante e mande foto.", "Mande uma foto do seu pé agora.",
    "Faça um vídeo curto rebolando e mande aqui.", "Mande mensagem para sua mãe dizendo 'estou grávida/engravidei alguém'."
]

# Gerando as listas de 300 itens
VERDADES = [f"{random.choice(p_bases)} (#{i+1})" for i in range(300)]
DESAFIOS = [f"{random.choice(d_bases)} (#{i+1})" for i in range(300)]

# ================= ESTADO DO JOGO =================
usuarios_ativos = {} 
jogo_estado = {
    'vez_de': None,
    'nome_vez': "",
    'timestamp': 0,
    'respondido': True
}

def monitorar_tempo(chat_id, user_id):
    """Verifica se o usuário sorteado responde em 1 minuto."""
    time.sleep(60)
    if not jogo_estado['respondido'] and jogo_estado['vez_de'] == user_id:
        bot.send_message(chat_id, f"⏰ <b>Tempo esgotado!</b>\n<a href='tg://user?id={user_id}'>{jogo_estado['nome_vez']}</a> demorou muito e não escolheu nada.")
        jogo_estado['vez_de'] = None
        jogo_estado['respondido'] = True

# ================= INTERFACE DE BOTÕES =================
def gerar_teclado():
    markup = InlineKeyboardMarkup()
    btn_girar = InlineKeyboardButton("Girar Garrafa 🍾", callback_data="girar")
    btn_v = InlineKeyboardButton("Verdade 🙊", callback_data="v")
    btn_d = InlineKeyboardButton("Desafio 😈", callback_data="d")
    
    # Layout: Girar em cima, Verdade e Desafio lado a lado embaixo
    markup.row(btn_girar)
    markup.row(btn_v, btn_d)
    return markup

# ================= COMANDOS =================
@bot.message_handler(commands=['vd'])
def iniciar_vd(message):
    bot.send_message(
        message.chat.id, 
        "🔥 <b>Bem-vindo ao Purgatório!</b>\nClique no botão para sortear alguém.", 
        reply_markup=gerar_teclado()
    )

@bot.callback_query_handler(func=lambda call: True)
def processar_callback(call):
    chat_id = call.message.chat.id
    user_id = call.from_user.id
    nome = call.from_user.first_name
    
    # Registra usuários para o sorteio
    if chat_id not in usuarios_ativos: usuarios_ativos[chat_id] = {}
    usuarios_ativos[chat_id][user_id] = nome

    # Segurança: Se houver alguém na vez, apenas essa pessoa pode clicar
    if jogo_estado['vez_de'] is not None and user_id != jogo_estado['vez_de']:
        bot.answer_callback_query(call.id, "⚠️ Não é sua vez! Aguarde o sorteado responder.", show_alert=True)
        return

    if call.data == "girar":
        membros = list(usuarios_ativos[chat_id].items())
        if not membros:
            bot.answer_callback_query(call.id, "Nenhum usuário detectado. Mandem mensagens no grupo!")
            return

        # Contagem regressiva de 5 segundos
        for i in range(5, 0, -1):
            bot.edit_message_text(f"🍾 <b>Girando a garrafa...</b>\nParando em {i} segundos!", chat_id, call.message.message_id, reply_markup=gerar_teclado())
            time.sleep(1)

        sorteado_id, sorteado_nome = random.choice(membros)
        jogo_estado.update({
            'vez_de': sorteado_id,
            'nome_vez': sorteado_nome,
            'timestamp': time.time(),
            'respondido': False
        })

        bot.edit_message_text(
            f"🎯 <b>A garrafa parou em:</b> <a href='tg://user?id={sorteado_id}'>{sorteado_nome}</a>\n\nEscolha rápido! Você tem 1 minuto.",
            chat_id, call.message.message_id, reply_markup=gerar_teclado()
        )
        
        # Inicia timer de 1 minuto em thread separada
        threading.Thread(target=monitorar_tempo, args=(chat_id, sorteado_id), daemon=True).start()

    elif call.data in ["v", "d"]:
        # Se clicar sem ter girado, o bot apenas envia a pergunta (como solicitado)
        texto = random.choice(VERDADES) if call.data == "v" else random.choice(DESAFIOS)
        titulo = "🙊 VERDADE" if call.data == "v" else "😈 DESAFIO"
        
        jogo_estado['respondido'] = True
        jogo_estado['vez_de'] = None # Libera para o próximo
        
        bot.edit_message_text(
            f"<b>{titulo}:</b>\n\n{texto}", 
            chat_id, call.message.message_id, 
            reply_markup=gerar_teclado()
        )

# ================= EXECUÇÃO (WEB SERVER) =================
def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

if __name__ == "__main__":
    # Inicia Flask para o Render não dar erro de porta
    threading.Thread(target=run_flask).start()
    print("Bot Purgatório ONLINE com comando /vd!")
    bot.infinity_polling()
    
