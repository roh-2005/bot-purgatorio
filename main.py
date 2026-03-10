import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import random
import os
import threading
import time
from flask import Flask

# ================= CONFIGURAÇÕES =================
# Lembre-se de manter sua API Key segura!
TOKEN = "8791899548:AAGS5UjIX2YStk7ZM7PfnNlL0upeld_5Ea4"
bot = telebot.TeleBot(TOKEN, parse_mode="HTML")

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot Online e Operante!", 200

# ================= VARIÁVEIS DE CONTROLE =================
usuarios_ativos = {} # chat_id: {user_id: nome}
estado_jogo = {}     # chat_id: {'vez': user_id, 'timer': ThreadTimer, 'verdades': [], 'desafios': []}

# ================= BANCO DE DADOS (GERAÇÃO DE 300+ ÚNICOS) =================

# Listas base super variadas
verdades_iniciais = [
    "Qual a sua maior insegurança na cama?", "Já teve sonhos eróticos com alguém do grupo?",
    "Marque @ e diga o que você mudaria no estilo dessa pessoa.",
    "Qual a mentira mais descarada que já contou?", "Já pegou o ex de um amigo(a)?",
    "Qual fetiche você tem vergonha de admitir?", "Já traiu e não foi pego(a)?",
    "Marque @ e confesse uma coisa que você nunca teve coragem de dizer.",
    "Quem do grupo você beijaria agora? Marque @.",
    "Se você pudesse mandar @ calar a boca agora, você mandaria?",
    "Já beijou alguém por pena? Marque @.", "Qual a sua maior fantasia sexual não realizada?",
    "Você já stalkeou alguém do grupo hoje?", "Qual a coisa mais estranha que você já fez sozinho(a)?"
]

desafios_iniciais = [
    "Mande um áudio de 10s fingindo estar sem fôlego.", "Vá no PV de @ e diga 'Você não sai da minha cabeça'.",
    "Mude sua bio para 'Sou uma delícia' por 10 minutos.", "Mande a 15ª foto da sua galeria.",
    "Marque @ e peça para ele(a) te dar uma nota de 0 a 10.",
    "Mande um áudio sussurrando algo picante no PV de @.",
    "Marque @ e diga: 'Se você me desse mole, eu não perdoava'.",
    "Poste uma foto preta no status: 'Decepcionado...' e mande print.",
    "Grave um áudio de 5s fazendo um gemido curto.",
    "Marque @ e desafie essa pessoa a te mandar um nude no PV.",
    "Ligue para @ e desligue assim que ele(a) atender.",
    "Mande um print da sua última conversa no WhatsApp.", "Fique 5 minutos sem usar emojis."
]

# Gerador para completar as 300 únicas sem repetir a mesma frase
v_sujeitos = ["alguém do grupo", "seu ex", "seu melhor amigo(a)", "a última pessoa que você beijou", "quem você mais odeia aqui"]
v_acoes = ["você levaria para uma ilha deserta", "você stalkeia toda semana", "você acha que tem um segredo sujo", "você acha que beija mal"]
d_acoes = ["Mande um áudio cantando", "Escreva um texto dramático para", "Mande um emoji de fogo no PV de", "Elogie exageradamente a foto de"]
d_alvos = ["a pessoa mais calada do grupo.", "o administrador do grupo.", "a última pessoa que mandou mensagem.", "o @ que o bot escolher agora."]

TODAS_VERDADES = verdades_iniciais.copy()
TODOS_DESAFIOS = desafios_iniciais.copy()

# Preenchendo até 300 combinando partes diferentes
while len(TODAS_VERDADES) < 300:
    nova_v = f"Verdade sincera: Se fosse obrigatório, qual {random.choice(v_sujeitos)} {random.choice(v_acoes)}?"
    if nova_v not in TODAS_VERDADES: TODAS_VERDADES.append(nova_v)

while len(TODOS_DESAFIOS) < 300:
    novo_d = f"Desafio cruel: {random.choice(d_acoes)} {random.choice(d_alvos)}"
    if novo_d not in TODOS_DESAFIOS: TODOS_DESAFIOS.append(novo_d)

# ================= FUNÇÕES DO JOGO =================

def iniciar_jogo_chat(chat_id):
    if chat_id not in estado_jogo:
        estado_jogo[chat_id] = {
            'vez': None,
            'timer': None,
            'verdades': TODAS_VERDADES.copy(),
            'desafios': TODOS_DESAFIOS.copy()
        }
        random.shuffle(estado_jogo[chat_id]['verdades'])
        random.shuffle(estado_jogo[chat_id]['desafios'])

def pegar_pergunta(chat_id, tipo):
    lista = estado_jogo[chat_id][tipo]
    if not lista: # Se a lista esvaziar, recarrega e embaralha de novo (Evita repetição)
        estado_jogo[chat_id][tipo] = TODAS_VERDADES.copy() if tipo == 'verdades' else TODOS_DESAFIOS.copy()
        random.shuffle(estado_jogo[chat_id][tipo])
        lista = estado_jogo[chat_id][tipo]
    return lista.pop()

def timeout_jogada(chat_id, message_id, user_id):
    # Se o tempo acabar e ainda for a vez do usuário, cancela a vez dele
    if estado_jogo.get(chat_id, {}).get('vez') == user_id:
        try:
            bot.edit_message_text("⏰ <b>O tempo esgotou (1 minuto)!</b>\nO jogador arregou ou sumiu. Quem vai ser o próximo a girar?", chat_id, message_id, parse_mode="HTML")
            estado_jogo[chat_id]['vez'] = None
        except:
            pass

@bot.message_handler(func=lambda m: True)
def rastrear_usuarios(message):
    # Salva quem manda mensagem para poder sortear depois
    chat_id = message.chat.id
    if chat_id not in usuarios_ativos:
        usuarios_ativos[chat_id] = {}
    usuarios_ativos[chat_id][message.from_user.id] = message.from_user.first_name
    
    # Se mandarem /jogar, inicia o painel
    if message.text.lower() in ['/jogar', '/vd']:
        iniciar_jogo_chat(chat_id)
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("Girar Garrafa 🍾", callback_data="iniciar_giro"))
        bot.send_message(chat_id, "🔥 <b>O Jogo Começou!</b> 🔥\nAperte para girar a garrafa e ver quem vai sofrer agora.", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def botoes_jogo(call):
    chat_id = call.message.chat.id
    user_id = call.from_user.id
    msg_id = call.message.message_id

    iniciar_jogo_chat(chat_id)
    vez_atual = estado_jogo[chat_id].get('vez')

    # Verifica se é a vez do cara ou se é o giro inicial livre
    if call.data != "iniciar_giro" and vez_atual is not None and user_id != vez_atual:
        bot.answer_callback_query(call.id, "Não é a sua vez! Deixa o jogador escolher.", show_alert=True)
        return

    # Cancela o timer se existir, pois o jogador tomou uma ação
    if estado_jogo[chat_id].get('timer'):
        estado_jogo[chat_id]['timer'].cancel()

    if call.data in ["iniciar_giro", "girar"]:
        # Tira os botões para evitar flood
        bot.edit_message_reply_markup(chat_id, msg_id, reply_markup=None)
        
        membros = list(usuarios_ativos.get(chat_id, {}).items())
        if not membros or len(membros) < 2:
            bot.answer_callback_query(call.id, "Preciso de mais pessoas falando no grupo para poder sortear!")
            return
            
        bot.answer_callback_query(call.id, "Girando a garrafa...")
        
        # Contagem regressiva de 5 segundos
        for i in range(5, 0, -1):
            try:
                bot.edit_message_text(f"🍾 <i>Girando a garrafa... {i}s</i>", chat_id, msg_id)
                time.sleep(1)
            except:
                pass
                
        sorteado_id, sorteado_nome = random.choice(membros)
        estado_jogo[chat_id]['vez'] = sorteado_id

        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("Verdade 🙊", callback_data="verdade"),
                   InlineKeyboardButton("Desafio 😈", callback_data="desafio"))
        markup.add(InlineKeyboardButton("Girar Novamente 🍾", callback_data="girar"))

        texto = f"🎯 A garrafa parou em: <a href='tg://user?id={sorteado_id}'>{sorteado_nome}</a>!\n\nVocê tem <b>1 minuto</b> para escolher sua punição."
        bot.edit_message_text(texto, chat_id, msg_id, reply_markup=markup)

        # Inicia o timer de 1 minuto
        timer = threading.Timer(60.0, timeout_jogada, args=(chat_id, msg_id, sorteado_id))
        timer.start()
        estado_jogo[chat_id]['timer'] = timer

    elif call.data == "verdade":
        bot.answer_callback_query(call.id, "Você escolheu Verdade!")
        pergunta = pegar_pergunta(chat_id, 'verdades')
        bot.edit_message_text(f"🙊 <b>VERDADE:</b>\n\n{pergunta}\n\n<i>Responda no chat!</i>", chat_id, msg_id, reply_markup=None)
        estado_jogo[chat_id]['vez'] = None # Libera a vez

    elif call.data == "desafio":
        bot.answer_callback_query(call.id, "Você escolheu Desafio!")
        desafio = pegar_pergunta(chat_id, 'desafios')
        bot.edit_message_text(f"😈 <b>DESAFIO:</b>\n\n{desafio}\n\n<i>Cumpra e mande a prova!</i>", chat_id, msg_id, reply_markup=None)
        estado_jogo[chat_id]['vez'] = None # Libera a vez

# ================= INICIALIZAÇÃO =================
def run_bot():
    bot.infinity_polling()

if __name__ == "__main__":
    # Roda o bot em uma thread separada para o Flask poder segurar a porta do Render
    t = threading.Thread(target=run_bot)
    t.start()
    
    # O Render exige que a aplicação web use a porta definida nas variáveis de ambiente
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
    
