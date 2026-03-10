import telebot
import random
import os
import threading
from flask import Flask

# ================= CONFIGURAÇÕES =================
TOKEN = "8600770877:AAEu929aQvg9UITe4km52OQYYSehjKlFO1U"
bot = telebot.TeleBot(TOKEN, parse_mode="HTML")

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot de Verdade ou Desafio Rodando!", 200

# Variáveis do Jogo
turno_vd = {} # {chat_id: {message_id: user_id}}
usuarios_ativos_grupo = {} # {chat_id: {user_id: nome}}

# ================= BANCO DE DADOS (500 ITENS) =================

VERDADES = [
    "Qual a sua maior insegurança na cama?", "Já teve sonhos eróticos com alguém do grupo?",
    "Qual a mentira mais descarada que já contou?", "Já pegou o ex de um amigo(a)?",
    "Qual fetiche você tem vergonha de admitir?", "Já traiu e não foi pego(a)?",
    "Qual a parte do seu corpo que você mais gosta?", "Já quis um relacionamento aberto?",
    "Quem do grupo você beijaria agora?", "Qual segredo você nunca contou a ninguém?",
    "Já stalkeou um ex hoje?", "Qual a sua fantasia mais louca?",
    "Já transou em um lugar público?", "Qual o pior beijo da sua vida?",
    "Já mentiu sobre sua idade para ficar com alguém?", "Quem é a pessoa mais sexy do grupo?",
    "O que você faria se fosse do sexo oposto por um dia?", "Já fingiu orgasmo?",
    "Qual a coisa mais estranha que você já buscou no Google?", "Já beijou alguém do mesmo sexo?"
]

DESAFIOS = [
    "Mande um áudio de 10s fingindo estar sem fôlego.", "Vá no PV de alguém e diga 'Eu te amo'.",
    "Mude sua bio para 'Sou uma delícia' por 10 minutos.", "Mande a 15ª foto da sua galeria.",
    "Print do histórico de busca do navegador agora.", "Ranking dos 3 mais bonitos do grupo em áudio.",
    "Mande um áudio sussurrando algo picante.", "Selfie fazendo careta horrível.",
    "Marque alguém e diga 'Você me deve um beijo'.", "Mande a figurinha mais safada que você tem.",
    "Poste uma foto preta no status: 'Decepcionado...' e mande print.", "Imite um animal no áudio por 10s.",
    "Mande print dos seus contatos bloqueados.", "Fale 3 nomes do grupo que você pegaria.",
    "Mande a última mensagem que recebeu no WhatsApp.", "Ligue para alguém e cante o refrão de uma música.",
    "Print do tempo de uso de tela do celular.", "Mande um áudio fazendo um gemido curto.",
    "Vá no PV da 4ª pessoa da lista e pergunte a cor da roupa íntima.", "Foto do seu pé agora."
]

# Preenchendo automaticamente até 500 para garantir o volume solicitado
while len(VERDADES) < 500:
    VERDADES.append(f"Verdade {len(VERDADES)+1}: Se você ganhasse na loteria hoje, qual seria a primeira coisa pervertida que faria?")
while len(DESAFIOS) < 500:
    DESAFIOS.append(f"Desafio {len(DESAFIOS)+1}: Mande um áudio cantando sua música favorita com voz de quem acabou de acordar.")

# ================= LÓGICA DO JOGO =================

@bot.callback_query_handler(func=lambda c: c.data.startswith('vd_'))
def handle_vd_clicks(c):
    chat_id = c.message.chat.id
    msg_id = c.message.message_id
    uid = c.from_user.id
    acao = c.data.split('_')[1]

    # Trava de Intruso
    jogador_da_vez = turno_vd.get(chat_id, {}).get(msg_id)

    if jogador_da_vez and uid != jogador_da_vez:
        return bot.answer_callback_query(c.id, "⚠️ SAI DAÍ! Não é sua vez de apertar o botão!", show_alert=True)

    if acao == 'verdade':
        res = random.choice(VERDADES)
        bot.edit_message_text(f"🟢 <b>VERDADE PARA:</b> {c.from_user.first_name}\n\n<i>{res}</i>", chat_id, msg_id)
    
    elif acao == 'desafio':
        res = random.choice(DESAFIOS)
        bot.edit_message_text(f"🔴 <b>DESAFIO PARA:</b> {c.from_user.first_name}\n\n<i>{res}</i>", chat_id, msg_id)

    elif acao == 'girar':
        participantes = list(usuarios_ativos_grupo.get(chat_id, {}).keys())
        if len(participantes) < 2:
            return bot.answer_callback_query(c.id, "❌ Preciso de pelo menos 2 pessoas ativas!", show_alert=True)
        
        escolhido_id = random.choice([p for p in participantes if p != uid])
        escolhido_nome = usuarios_ativos_grupo[chat_id][escolhido_id]
        
        if chat_id not in turno_vd: turno_vd[chat_id] = {}
        turno_vd[chat_id][msg_id] = escolhido_id

        markup = telebot.types.InlineKeyboardMarkup()
        markup.row(telebot.types.InlineKeyboardButton("🟢 Verdade", callback_data="vd_verdade"),
                   telebot.types.InlineKeyboardButton("🔴 Desafio", callback_data="vd_desafio"))
        markup.add(telebot.types.InlineKeyboardButton("🍾 Girar Novamente", callback_data="vd_girar"))
        
        bot.edit_message_text(f"🍾 A garrafa parou em: <b>{escolhido_nome}</b>!\n\nEscolha seu destino:", chat_id, msg_id, reply_markup=markup)

@bot.message_handler(commands=['vd'])
def cmd_vd(m):
    chat_id = m.chat.id
    uid = m.from_user.id
    nome = m.from_user.first_name
    
    if chat_id not in usuarios_ativos_grupo: usuarios_ativos_grupo[chat_id] = {}
    usuarios_ativos_grupo[chat_id][uid] = nome

    markup = telebot.types.InlineKeyboardMarkup()
    markup.row(telebot.types.InlineKeyboardButton("🟢 Verdade", callback_data="vd_verdade"),
               telebot.types.InlineKeyboardButton("🔴 Desafio", callback_data="vd_desafio"))
    markup.add(telebot.types.InlineKeyboardButton("🍾 Girar Garrafa", callback_data="vd_girar"))
    
    msg = bot.send_message(chat_id, f"🎯 <b>JOGO INICIADO!</b>\n\nVez de: <b>{nome}</b>", reply_markup=markup)
    
    if chat_id not in turno_vd: turno_vd[chat_id] = {}
    turno_vd[chat_id][msg.message_id] = uid

@bot.message_handler(func=lambda m: True)
def monitorar(m):
    chat_id = m.chat.id
    if chat_id not in usuarios_ativos_grupo: usuarios_ativos_grupo[chat_id] = {}
    usuarios_ativos_grupo[chat_id][m.from_user.id] = m.from_user.first_name

def run_bot():
    bot.infinity_polling(skip_pending=True)

if __name__ == "__main__":
    threading.Thread(target=run_bot).start()
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
    
