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
# Bases de dados diversificadas (Safadas, Engraçadas, Revelações)
p_bases = [
    "Qual seu fetiche mais estranho?", "Já beijou alguém deste grupo e ninguém sabe?", 
    "Qual a coisa mais 'errada' que você já fez?", "Quem aqui você levaria para um quarto agora?",
    "Já fingiu prazer com alguém?", "Qual parte do seu corpo você mais gosta de exibir?",
    "Qual foi a última pessoa que você stalkeou?", "Já mandou nudes para quem não devia?",
    "Qual sua fantasia sexual nunca realizada?", "O que você faria se fosse do sexo oposto por um dia?",
    "Já teve um sonho erótico com alguém aqui?", "Qual o lugar mais inusitado onde você já 'fez'?",
    "Se tivesse que escolher alguém do grupo para um 'lance', quem seria?",
    "Já traiu em algum relacionamento?", "Qual sua maior mentira contada para transar?",
    "O que você acha mais atraente no(a) administrador(a)?", "Já beijou dois em uma noite?",
    "Qual segredo você nunca contou para seus pais?", "Já usou brinquedos íntimos?",
    "Qual sua posição favorita e por quê?", "Quem aqui você acha que beija melhor só de olhar?",
    "Já ficou com alguém por pena?", "Qual sua opinião real sobre o @ que girou a garrafa?"
]

d_bases = [
    "Mande um áudio de 30 segundos simulando um gemido.", "Mande print do seu histórico de busca agora.",
    "Ligue para um ex e diga que ainda sente saudade (mande prova).", "Tire uma foto só de roupa íntima (ou sem camisa) e mande.",
    "Diga no PV de @ algo que você faria com ele(a) entre quatro paredes.", "Mande um áudio cantando Funk de forma sensual.",
    "Poste no status do WhatsApp: 'Gente, sou viciado em sacanagem' por 10 min.",
    "Mande um emoji de fogo no PV da 3ª pessoa da sua lista de contatos.", "Morda o lábio de forma provocante e mande foto.",
    "Fale um segredo cabeludo seu no áudio do grupo.", "Dê um selinho em um objeto e mande vídeo.",
    "Mande uma mensagem para sua mãe dizendo 'Eu sei o que você fez' e mostre o print.",
    "Descreva detalhadamente como seria uma noite perfeita com alguém daqui.",
    "Mude sua foto de perfil para uma foto feia por 30 minutos.", "Mande um 'oi sumido(a)' para a última pessoa que te deu vácuo.",
    "Tire uma foto do seu pé e mande no grupo.", "Faça uma declaração de amor para o @ que o bot escolher.",
    "Mande um áudio imitando um animal no cio.", "Fique 5 minutos mandando apenas figurinhas safadas."
]

# Gera listas com 300 itens únicos
VERDADES = [f"{random.choice(p_bases)} (#{i+1})" for i in range(300)]
DESAFIOS = [f"{random.choice(d_bases)} (#{i+1})" for i in range(300)]

# ================= ESTADO DO JOGO =================
usuarios_ativos = {} # {chat_id: {user_id: nome}}
estado = {
    'vez_de': None,
    'nome_vez': "",
    'timestamp': 0,
    'respondido': True,
    'mensagem_id': None
}

def monitorar_tempo(chat_id):
    """Verifica se o jogador demorou mais de 1 minuto para responder."""
    while True:
        time.sleep(5)
        if not estado['respondido'] and time.time() - estado['timestamp'] > 60:
            bot.send_message(chat_id, f"⏰ <b>O tempo acabou!</b>\n<a href='tg://user?id={estado['vez_de']}'>{estado['nome_vez']}</a> não respondeu a tempo e perdeu a vez.")
            estado['respondido'] = True
            estado['vez_de'] = None

# ================= COMANDOS =================
@bot.message_handler(commands=['vd'])
def iniciar_vd(message):
    markup = InlineKeyboardMarkup(row_width=1)
    btn_girar = InlineKeyboardButton("Girar Garrafa 🍾", callback_data="girar")
    btn_v = InlineKeyboardButton("Verdade 🙊", callback_data="v")
    btn_d = InlineKeyboardButton("Desafio 😈", callback_data="d")
    markup.add(btn_girar, btn_v, btn_d)
    
    bot.send_message(
        message.chat.id, 
        "🔥 <b>Bem-vindo ao Purgatório!</b>\nClique no botão para sortear alguém.", 
        reply_markup=markup
    )

@bot.callback_query_handler(func=lambda call: True)
def processar_cliques(call):
    chat_id = call.message.chat.id
    user_id = call.from_user.id
    nome = call.from_user.first_name
    
    # Registra o usuário que interage
    if chat_id not in usuarios_ativos: usuarios_ativos[chat_id] = {}
    usuarios_ativos[chat_id][user_id] = nome

    # TRAVA DE SEGURANÇA: Somente quem está na vez pode clicar (ou qualquer um se não houver jogo ativo)
    if estado['vez_de'] and user_id != estado['vez_de']:
        bot.answer_callback_query(call.id, "⚠️ Você não está na vez de jogar! Aguarde o sorteado.", show_alert=True)
        return

    # Ação: GIRAR GARRAFA
    if call.data == "girar":
        membros = list(usuarios_ativos[chat_id].items())
        if len(membros) < 1:
            bot.answer_callback_query(call.id, "Mande uma mensagem no grupo primeiro para o bot te reconhecer!")
            return

        # Contagem Regressiva de 5 segundos
        for i in range(5, 0, -1):
            bot.edit_message_text(f"🍾 <b>A garrafa está girando...</b>\nParando em {i} segundos!", chat_id, call.message.message_id)
            time.sleep(1)

        sorteado_id, sorteado_nome = random.choice(membros)
        estado.update({
            'vez_de': sorteado_id,
            'nome_vez': sorteado_nome,
            'timestamp': time.time(),
            'respondido': False,
            'mensagem_id': call.message.message_id
        })

        markup = InlineKeyboardMarkup(row_width=2)
        markup.add(InlineKeyboardButton("Verdade 🙊", callback_data="v"), InlineKeyboardButton("Desafio 😈", callback_data="d"))
        
        bot.edit_message_text(
            f"🎯 <b>A garrafa parou em:</b> <a href='tg://user?id={sorteado_id}'>{sorteado_nome}</a>\n\nVocê tem <b>1 minuto</b> para escolher!",
            chat_id, call.message.message_id, reply_markup=markup
        )
        
        # Inicia o monitoramento de tempo para este chat
        threading.Thread(target=monitorar_tempo, args=(chat_id,), daemon=True).start()

    # Ação: VERDADE OU DESAFIO
    elif call.data in ["v", "d"]:
        if not estado['vez_de']:
            bot.answer_callback_query(call.id, "Gire a garrafa primeiro!")
            return

        texto = random.choice(VERDADES) if call.data == "v" else random.choice(DESAFIOS)
        titulo = "🙊 VERDADE" if call.data == "v" else "😈 DESAFIO"
        
        estado['respondido'] = True # Para o timer
        estado['vez_de'] = None # Libera o "Girar" para todos novamente
        
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("Girar Novamente 🍾", callback_data="girar"))
        
        bot.edit_message_text(f"<b>{titulo}:</b>\n\n{texto}", chat_id, call.message.message_id, reply_markup=markup)

# ================= EXECUÇÃO (WEB SERVER) =================
def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

if __name__ == "__main__":
    threading.Thread(target=run_flask).start()
    print("Bot Purgatório Iniciado com Comando /vd!")
    bot.infinity_polling()
    
