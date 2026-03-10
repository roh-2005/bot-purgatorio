import telebot
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
    return "Bot de Verdade ou Desafio Online!", 200

# Variáveis de Controle
turno_vd = {} # {chat_id: {message_id: user_id}}
usuarios_ativos = {} # {chat_id: {user_id: nome}}
expira_em = {} # {message_id: True/False}

# ================= BANCO DE DADOS (700 ITENS CADA) =================

VERDADES_BASE = [
    "Qual a sua maior insegurança na cama?", "Já teve sonhos eróticos com alguém do grupo?",
    "Marque @ e diga o que você mudaria no estilo dessa pessoa.",
    "Qual a mentira mais descarada que já contou?", "Já pegou o ex de um amigo(a)?",
    "Qual fetiche você tem vergonha de admitir?", "Já traiu e não foi pego(a)?",
    "Marque @ e confesse uma coisa que você nunca teve coragem de dizer.",
    "Quem do grupo você beijaria agora? Marque @.",
    "Se você pudesse mandar @ calar a boca agora, você mandaria?",
    "Já beijou alguém por pena? Se sim, marque @ se a pessoa estiver aqui.",
    "Qual a sua maior fantasia sexual não realizada?",
    "Marque @ e diga se você acha que essa pessoa beija bem ou mal."
]

DESAFIOS_BASE = [
    "Mande um áudio de 10s fingindo estar sem fôlego.", "Vá no PV de @ e diga 'Você não sai da minha cabeça'.",
    "Mude sua bio para 'Sou uma delícia' por 10 minutos.", "Mande a 15ª foto da sua galeria.",
    "Marque @ e peça para ele(a) te dar uma nota de 0 a 10.",
    "Mande um áudio sussurrando algo picante no PV de @ e mande o print.",
    "Marque @ e diga: 'Se você me desse mole, eu não perdoava'.",
    "Poste uma foto preta no status: 'Decepcionado...' e mande print.",
    "Grave um áudio de 5s fazendo um gemido curto e mande aqui.",
    "Marque @ e desafie essa pessoa a te mandar um nude no PV.",
    "Ligue para @ e desligue assim que ele(a) atender."
]

# Completando a lista para 700 itens
while len(VERDADES_BASE) < 700:
    VERDADES_BASE.append(f"Verdade {len(VERDADES_BASE)+1}: Marque @ e diga se você confia nela(e).")
while len(DESAFIOS_BASE) < 700:
    DESAFIOS_BASE.append(f"Desafio {len(DESAFIOS_BASE)+1}: Marque @ e mande uma figurinha pesada para ela(e).")

# ================= FUNÇÕES DE APOIO =================

def processar_texto(texto, chat_id):
    if "@" in texto:
        participantes = list(usuarios_ativos.get(chat_id, {}).keys())
        if participantes:
            sorteado_id = random.choice(participantes)
            nome_sorteado = usuarios_ativos[chat_id][sorteado_id]
            return texto.replace("@", f"<b>{nome_sorteado}</b>")
    return texto

def cronometro_expiracao(chat_id, msg_id, nome_jogador):
    time.sleep(60)
    if msg_id in expira_em:
        del expira_em[msg_id]
        if chat_id in turno_vd and msg_id in turno_vd[chat_id]:
            del turno_vd[chat_id][msg_id]
        try:
            bot.edit_message_text(f"⏰ <b>TEMPO ESGOTADO!</b>\n\nO tempo de <b>{nome_jogador}</b> acabou. Use /vd para girar novamente.", chat_id, msg_id)
        except: pass

# ================= LÓGICA DO JOGO =================

@bot.callback_query_handler(func=lambda c: c.data.startswith('vd_'))
def handle_clicks(c):
    chat_id, msg_id, uid = c.message.chat.id, c.message.message_id, c.from_user.id
    acao = c.data.split('_')[1]

    dono = turno_vd.get(chat_id, {}).get(msg_id)
    if dono and uid != dono:
        return bot.answer_callback_query(c.id, "⚠️ NÃO É SUA VEZ!", show_alert=True)

    if acao in ['verdade', 'desafio'] and msg_id not in expira_em:
        return bot.answer_callback_query(c.id, "⏰ Tempo expirado!", show_alert=True)

    if acao == 'verdade':
        expira_em.pop(msg_id, None)
        res = processar_texto(random.choice(VERDADES_BASE), chat_id)
        bot.edit_message_text(f"🟢 <b>VERDADE PARA:</b> {c.from_user.first_name}\n\n<i>{res}</i>", chat_id, msg_id)
    
    elif acao == 'desafio':
        expira_em.pop(msg_id, None)
        res = processar_texto(random.choice(DESAFIOS_BASE), chat_id)
        bot.edit_message_text(f"🔴 <b>DESAFIO PARA:</b> {c.from_user.first_name}\n\n<i>{res}</i>", chat_id, msg_id)

    elif acao == 'girar':
        participantes = list(usuarios_ativos.get(chat_id, {}).keys())
        if len(participantes) < 2:
            return bot.answer_callback_query(c.id, "❌ Preciso de mais pessoas ativas!", show_alert=True)
        
        for i in range(5, 0, -1):
            try:
                bot.edit_message_text(f"🍾 Girando a garrafa...\n\n⏳ <b>{i}s</b>", chat_id, msg_id)
                time.sleep(1)
            except: break

        escolhido_id = random.choice([p for p in participantes if p != uid])
        escolhido_nome = usuarios_ativos[chat_id][escolhido_id]
        
        if chat_id not in turno_vd: turno_vd[chat_id] = {}
        turno_vd[chat_id][msg_id] = escolhido_id
        expira_em[msg_id] = True

        threading.Thread(target=cronometro_expiracao, args=(chat_id, msg_id, escolhido_nome)).start()

        # --- ORGANIZAÇÃO DOS BOTÕES ---
        markup = telebot.types.InlineKeyboardMarkup()
        # Botão de Girar sozinho no topo
        markup.add(telebot.types.InlineKeyboardButton("🍾 Girar Garrafa", callback_data="vd_girar"))
        # Botões de Verdade e Desafio logo abaixo, na mesma linha
        markup.row(telebot.types.InlineKeyboardButton("🟢 Verdade", callback_data="vd_verdade"),
                   telebot.types.InlineKeyboardButton("🔴 Desafio", callback_data="vd_desafio"))
        
        bot.edit_message_text(
            f"🍾 A garrafa parou em: <b>{escolhido_nome}</b>!\n\nVocê tem <b>1 minuto</b> para escolher:", 
            chat_id, msg_id, reply_markup=markup
        )

@bot.message_handler(commands=['vd'])
def cmd_vd(m):
    chat_id, uid, nome = m.chat.id, m.from_user.id, m.from_user.first_name
    if chat_id not in usuarios_ativos: usuarios_ativos[chat_id] = {}
    usuarios_ativos[chat_id][uid] = nome

    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(telebot.types.InlineKeyboardButton("🍾 Girar Garrafa", callback_data="vd_girar"))
    markup.row(telebot.types.InlineKeyboardButton("🟢 Verdade", callback_data="vd_verdade"),
               telebot.types.InlineKeyboardButton("🔴 Desafio", callback_data="vd_desafio"))
    
    bot.send_message(chat_id, f"🎯 <b>JOGO INICIADO!</b>\n\nClique para girar a garrafa:", reply_markup=markup)

@bot.message_handler(func=lambda m: True)
def monitor(m):
    chat_id = m.chat.id
    if chat_id not in usuarios_ativos: usuarios_ativos[chat_id] = {}
    usuarios_ativos[chat_id][m.from_user.id] = m.from_user.first_name

# ================= EXECUÇÃO =================

def run_bot():
    bot.remove_webhook()
    bot.infinity_polling(skip_pending=True)

if __name__ == "__main__":
    t = threading.Thread(target=run_bot)
    t.daemon = True
    t.start()
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
    
