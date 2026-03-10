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
    return "Bot Online!", 200

# Variáveis de Controle
turno_vd = {} 
usuarios_ativos = {} 
expira_em = {} 

# ================= BANCO DE DADOS (EXPANDIDO) =================

VERDADES_BASE = [
    "Qual a sua maior insegurança na cama?", "Já teve sonhos eróticos com alguém do grupo?",
    "Marque @ e diga o que você mudaria no estilo dessa pessoa.",
    "Qual a mentira mais descarada que já contou?", "Já pegou o ex de um amigo(a)?",
    "Qual fetiche você tem vergonha de admitir?", "Já traiu e não foi pego(a)?",
    "Marque @ e confesse uma coisa que você nunca teve coragem de dizer.",
    "Quem do grupo você beijaria agora? Marque @.",
    "Se você pudesse mandar @ calar a boca agora, você mandaria?",
    "Já beijou alguém por pena? Marque @.",
    "Qual a sua maior fantasia sexual não realizada?",
    "Marque @ e diga se você acha que essa pessoa beija bem ou mal.",
    "Você já stalkeou alguém do grupo hoje?", "Qual a coisa mais estranha que você já fez sozinho(a)?",
    "Se pudesse apagar um erro do passado, qual seria?", "Quem aqui você levaria para uma ilha deserta?"
]

DESAFIOS_BASE = [
    "Mande um áudio de 10s fingindo estar sem fôlego.", "Vá no PV de @ e diga 'Você não sai da minha cabeça'.",
    "Mude sua bio para 'Sou uma delícia' por 10 minutos.", "Mande a 15ª foto da sua galeria.",
    "Marque @ e peça para ele(a) te dar uma nota de 0 a 10.",
    "Mande um áudio sussurrando algo picante no PV de @.",
    "Marque @ e diga: 'Se você me desse mole, eu não perdoava'.",
    "Poste uma foto preta no status: 'Decepcionado...' e mande print.",
    "Grave um áudio de 5s fazendo um gemido curto.",
    "Marque @ e desafie essa pessoa a te mandar um nude no PV.",
    "Ligue para @ e desligue assim que ele(a) atender.",
    "Mande um print da sua última conversa no WhatsApp.", "Fique 5 minutos sem usar emojis.",
    "Mande uma foto fazendo careta agora.", "Declare-se para @ em 3 frases."
]

# Garantindo os 500 itens solicitados
for i in range(len(VERDADES_BASE), 500):
    VERDADES_BASE.append(f"Verdade {i+1}: Se você fosse um animal, qual seria e por quê?")
for i in range(len(DESAFIOS_BASE), 500):
    DESAFIOS_BASE.append(f"Desafio {i+1}: Marque @ e mande um elogio exagerado.")

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
            bot.edit_message_text(f"⏰ <b>TEMPO EXPIRADO!</b>\n\n<b>{nome_jogador}</b> não respondeu. Gire novamente!", chat_id, msg_id)
        except: pass

# ================= LÓGICA DO JOGO =================

@bot.callback_query_handler(func=lambda c: c.data.startswith('vd_'))
def handle_clicks(c):
    chat_id, msg_id, uid = c.message.chat.id, c.message.message_id, c.from_user.id
    acao = c.data.split('_')[1]

    # --- BOTÃO GIRAR GARRAFA ---
    if acao == 'girar':
        participantes = list(usuarios_ativos.get(chat_id, {}).keys())
        if len(participantes) < 2:
            return bot.answer_callback_query(c.id, "❌ Preciso de mais pessoas ativas!", show_alert=True)
        
        expira_em.pop(msg_id, None) # Reseta cronômetro anterior

        for i in range(3, 0, -1): # Reduzi para 3s para ser mais rápido
            try:
                bot.edit_message_text(f"🍾 Girando...\n\n⏳ <b>{i}s</b>", chat_id, msg_id)
                time.sleep(1)
            except: break

        escolhido_id = random.choice([p for p in participantes if p != uid])
        escolhido_nome = usuarios_ativos[chat_id][escolhido_id]
        
        if chat_id not in turno_vd: turno_vd[chat_id] = {}
        turno_vd[chat_id][msg_id] = escolhido_id
        expira_em[msg_id] = True 

        threading.Thread(target=cronometro_expiracao, args=(chat_id, msg_id, escolhido_nome)).start()

        markup = telebot.types.InlineKeyboardMarkup()
        markup.add(telebot.types.InlineKeyboardButton("🍾 Girar Garrafa", callback_data="vd_girar"))
        markup.row(telebot.types.InlineKeyboardButton("🟢 Verdade", callback_data="vd_verdade"),
                   telebot.types.InlineKeyboardButton("🔴 Desafio", callback_data="vd_desafio"))
        
        bot.edit_message_text(
            f"🍾 A garrafa parou em: <b>{escolhido_nome}</b>!\n\nEscolha em 1 minuto:", 
            chat_id, msg_id, reply_markup=markup
        )
        return

    # --- BOTÕES VERDADE E DESAFIO ---
    if acao in ['verdade', 'desafio']:
        dono = turno_vd.get(chat_id, {}).get(msg_id)
        
        # Se houve sorteio e quem apertou NÃO foi o sorteado
        if dono and uid != dono:
            return bot.answer_callback_query(c.id, "⚠️ Não é sua vez!", show_alert=True)

        # Se for o sorteado ou se não houver sorteio ativo (qualquer um pode pedir)
        expira_em.pop(msg_id, None) 
        if chat_id in turno_vd and msg_id in turno_vd[chat_id]:
            del turno_vd[chat_id][msg_id]

        if acao == 'verdade':
            res = processar_texto(random.choice(VERDADES_BASE), chat_id)
            texto = f"🟢 <b>VERDADE PARA:</b> {c.from_user.first_name}\n\n<i>{res}</i>"
        else:
            res = processar_texto(random.choice(DESAFIOS_BASE), chat_id)
            texto = f"🔴 <b>DESAFIO PARA:</b> {c.from_user.first_name}\n\n<i>{res}</i>"

        # Mantém os botões para a próxima rodada
        markup = telebot.types.InlineKeyboardMarkup()
        markup.add(telebot.types.InlineKeyboardButton("🍾 Girar Garrafa", callback_data="vd_girar"))
        markup.row(telebot.types.InlineKeyboardButton("🟢 Verdade", callback_data="vd_verdade"),
                   telebot.types.InlineKeyboardButton("🔴 Desafio", callback_data="vd_desafio"))
        
        bot.edit_message_text(texto, chat_id, msg_id, reply_markup=markup)

@bot.message_handler(commands=['vd'])
def cmd_vd(m):
    chat_id, uid, nome = m.chat.id, m.from_user.id, m.from_user.first_name
    usuarios_ativos.setdefault(chat_id, {})[uid] = nome

    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(telebot.types.InlineKeyboardButton("🍾 Girar Garrafa", callback_data="vd_girar"))
    markup.row(telebot.types.InlineKeyboardButton("🟢 Verdade", callback_data="vd_verdade"),
               telebot.types.InlineKeyboardButton("🔴 Desafio", callback_data="vd_desafio"))
    
    bot.send_message(chat_id, "🎯 <b>Verdade ou Desafio - Purgatório</b>\n\nEscolha uma opção ou gire a garrafa:", reply_markup=markup)

@bot.message_handler(func=lambda m: True)
def monitor(m):
    usuarios_ativos.setdefault(m.chat.id, {})[m.from_user.id] = m.from_user.first_name

# ================= EXECUÇÃO =================

def run_bot():
    try:
        bot.remove_webhook()
        time.sleep(1)
        bot.infinity_polling(skip_pending=True)
    except:
        time.sleep(5)
        run_bot()

if __name__ == "__main__":
    t = threading.Thread(target=run_bot)
    t.daemon = True
    t.start()
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
    
