import telebot
import random
import os
import threading
from flask import Flask

# ================= CONFIGURAÇÕES =================
# DICA: Se o erro 409 continuar, troque este Token no @BotFather
TOKEN = "8600770877:AAEu929aQvg9UITe4km52OQYYSehjKlFO1U"
bot = telebot.TeleBot(TOKEN, parse_mode="HTML")

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot Online e Protegido!", 200

# Variáveis do Jogo
turno_vd = {} 
usuarios_ativos_grupo = {} 

# ================= BANCO DE DADOS (500 ITENS) =================
VERDADES = [
    "Qual a sua maior insegurança na cama?", "Já teve sonhos eróticos com alguém do grupo?",
    "Qual a mentira mais descarada que já contou?", "Já pegou o ex de um amigo(a)?",
    "Qual fetiche você tem vergonha de admitir?", "Já traiu e não foi pego(a)?",
    "Qual a parte do seu corpo que você mais gosta?", "Já quis um relacionamento aberto?",
    "Quem do grupo você beijaria agora?", "Qual segredo você nunca contou a ninguém?"
]

DESAFIOS = [
    "Mande um áudio de 10s fingindo estar sem fôlego.", "Vá no PV de alguém e diga 'Eu te amo'.",
    "Mude sua bio para 'Sou uma delícia' por 10 minutos.", "Mande a 15ª foto da sua galeria.",
    "Print do histórico de busca do navegador agora.", "Ranking dos 3 mais bonitos do grupo em áudio.",
    "Mande um áudio sussurrando algo picante.", "Selfie fazendo careta horrível.",
    "Marque alguém e diga 'Você me deve um beijo'.", "Mande a figurinha mais safada que você tem."
]

# Gerador Automático para completar 500 itens
while len(VERDADES) < 500:
    VERDADES.append(f"Verdade {len(VERDADES)+1}: Se você pudesse apagar um dia da sua vida amorosa, qual seria?")
while len(DESAFIOS) < 500:
    DESAFIOS.append(f"Desafio {len(DESAFIOS)+1}: Mande um áudio cantando o refrão de uma música de funk com voz de ópera.")

# ================= LÓGICA DO JOGO =================

@bot.callback_query_handler(func=lambda c: c.data.startswith('vd_'))
def handle_vd_clicks(c):
    chat_id = c.message.chat.id
    msg_id = c.message.message_id
    uid = c.from_user.id
    acao = c.data.split('_')[1]

    # Trava de Intruso: Só o dono da vez clica
    dono = turno_vd.get(chat_id, {}).get(msg_id)
    if dono and uid != dono:
        return bot.answer_callback_query(c.id, "⚠️ SAI DAÍ! Não é sua vez!", show_alert=True)

    if acao == 'verdade':
        bot.edit_message_text(f"🟢 <b>VERDADE PARA:</b> {c.from_user.first_name}\n\n<i>{random.choice(VERDADES)}</i>", chat_id, msg_id)
    elif acao == 'desafio':
        bot.edit_message_text(f"🔴 <b>DESAFIO PARA:</b> {c.from_user.first_name}\n\n<i>{random.choice(DESAFIOS)}</i>", chat_id, msg_id)
    elif acao == 'girar':
        participantes = list(usuarios_ativos_grupo.get(chat_id, {}).keys())
        if len(participantes) < 2:
            return bot.answer_callback_query(c.id, "❌ Preciso de pelo menos 2 ativos!", show_alert=True)
        
        escolhido_id = random.choice([p for p in participantes if p != uid])
        escolhido_nome = usuarios_ativos_grupo[chat_id][escolhido_id]
        
        if chat_id not in turno_vd: turno_vd[chat_id] = {}
        turno_vd[chat_id][msg_id] = escolhido_id

        markup = telebot.types.InlineKeyboardMarkup()
        markup.row(telebot.types.InlineKeyboardButton("🟢 Verdade", callback_data="vd_verdade"),
                   telebot.types.InlineKeyboardButton("🔴 Desafio", callback_data="vd_desafio"))
        markup.add(telebot.types.InlineKeyboardButton("🍾 Girar Novamente", callback_data="vd_girar"))
        
        bot.edit_message_text(f"🍾 A garrafa parou em: <b>{escolhido_nome}</b>!\n\nEscolha:", chat_id, msg_id, reply_markup=markup)

@bot.message_handler(commands=['vd'])
def cmd_vd(m):
    chat_id = m.chat.id
    if chat_id not in usuarios_ativos_grupo: usuarios_ativos_grupo[chat_id] = {}
    usuarios_ativos_grupo[chat_id][m.from_user.id] = m.from_user.first_name

    markup = telebot.types.InlineKeyboardMarkup()
    markup.row(telebot.types.InlineKeyboardButton("🟢 Verdade", callback_data="vd_verdade"),
               telebot.types.InlineKeyboardButton("🔴 Desafio", callback_data="vd_desafio"))
    markup.add(telebot.types.InlineKeyboardButton("🍾 Girar Garrafa", callback_data="vd_girar"))
    
    msg = bot.send_message(chat_id, f"🎯 <b>JOGO INICIADO!</b>\nVez de: <b>{m.from_user.first_name}</b>", reply_markup=markup)
    
    if chat_id not in turno_vd: turno_vd[chat_id] = {}
    turno_vd[chat_id][msg.message_id] = m.from_user.id

@bot.message_handler(func=lambda m: True)
def monitorar(m):
    chat_id = m.chat.id
    if chat_id not in usuarios_ativos_grupo: usuarios_ativos_grupo[chat_id] = {}
    usuarios_ativos_grupo[chat_id][m.from_user.id] = m.from_user.first_name

# ================= EXECUÇÃO =================

def run_bot():
    try:
        bot.infinity_polling(skip_pending=True, timeout=60)
    except Exception as e:
        print(f"Erro no polling: {e}")

if __name__ == "__main__":
    # Garante que o bot rode em thread separada
    t = threading.Thread(target=run_bot)
    t.daemon = True
    t.start()
    
    # Servidor Flask para o Render não derrubar o serviço
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
    
