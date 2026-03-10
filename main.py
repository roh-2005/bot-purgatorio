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
    return "Bot de Verdade ou Desafio com Cronômetro Online!", 200

# Variáveis de Controle
turno_vd = {} # {chat_id: {message_id: user_id}}
usuarios_ativos = {} # {chat_id: {user_id: nome}}
expira_em = {} # {message_id: timestamp_limite}

# ================= BANCO DE DADOS (700 ITENS CADA) =================

VERDADES_BASE = [
    "Qual a sua maior insegurança na cama?", "Já teve sonhos eróticos com alguém do grupo?",
    "Qual a mentira mais descarada que já contou?", "Já pegou o ex de um amigo(a)?",
    "Qual fetiche você tem vergonha de admitir?", "Já traiu e não foi pego(a)?",
    "Qual a parte do seu corpo que você mais gosta?", "Quem do grupo você beijaria agora?",
    "Marque o @ de quem você acha que tem o beijo mais gostoso aqui.",
    "Marque o @ da pessoa que você acha mais 'biscoiteira' do grupo.",
    "Se você tivesse que transar com alguém do grupo agora, marque o @ dessa pessoa.",
    "Qual o segredo que você esconde de @?",
    "Já mandou nude para alguém deste grupo e ninguém sabe?",
    "Qual a coisa mais estranha que você já fez por @?"
]

DESAFIOS_BASE = [
    "Mande um áudio de 10s fingindo estar sem fôlego.", "Vá no PV de @ e diga 'Eu te amo'.",
    "Mude sua bio para 'Sou uma delícia' por 10 minutos.", "Mande a 15ª foto da sua galeria.",
    "Mande um print do histórico de busca do navegador agora.",
    "Marque @ e diga qual a primeira impressão que você teve dele(a).",
    "Mande um áudio sussurrando 'Eu sei o seu segredo' no PV de @.",
    "Poste uma foto preta no status: 'Decepcionado...' e mande print.",
    "Marque @ e peça uma foto do pé dele(a) no PV.",
    "Grave um áudio de 5s fazendo um gemido curto e mande aqui.",
    "Marque @ e diga: 'Se você me pedisse um beijo, eu daria?'",
    "Mande um print das suas últimas 3 conversas do WhatsApp."
]

# Gerador para completar exatamente 700 itens de cada
while len(VERDADES_BASE) < 700:
    VERDADES_BASE.append(f"Verdade {len(VERDADES_BASE)+1}: Se você pudesse passar uma noite com @, o que fariam?")
while len(DESAFIOS_BASE) < 700:
    DESAFIOS_BASE.append(f"Desafio {len(DESAFIOS_BASE)+1}: Marque @ e mande uma figurinha que descreva o que você sente por ele(a).")

# ================= FUNÇÕES DE APOIO =================

def formatar_texto(texto, chat_id):
    """Substitui o placeholder @ pelo nome de um usuário aleatório do grupo"""
    if "@" in texto:
        participantes = list(usuarios_ativos.get(chat_id, {}).keys())
        if participantes:
            sorteado_id = random.choice(participantes)
            nome_sorteado = usuarios_ativos[chat_id][sorteado_id]
            return texto.replace("@", f"<b>{nome_sorteado}</b>")
    return texto

def cronometro_expiracao(chat_id, msg_id, user_name):
    """Aguarda 60 segundos e avisa se o tempo expirou"""
    time.sleep(60)
    if msg_id in expira_em:
        # Se ainda estiver no dicionário, significa que não escolheu
        del expira_em[msg_id]
        if chat_id in turno_vd and msg_id in turno_vd[chat_id]:
            del turno_vd[chat_id][msg_id]
        
        try:
            bot.edit_message_text(f"⏰ <b>TEMPO ESGOTADO!</b>\n\n{user_name} demorou demais para escolher. O jogo expirou. Use /vd para tentar novamente.", chat_id, msg_id)
        except:
            pass

# ================= LÓGICA DO JOGO =================

@bot.callback_query_handler(func=lambda c: c.data.startswith('vd_'))
def handle_clicks(c):
    chat_id, msg_id, uid = c.message.chat.id, c.message.message_id, c.from_user.id
    acao = c.data.split('_')[1]

    # TRAVA DE INTRUSO
    dono = turno_vd.get(chat_id, {}).get(msg_id)
    if dono and uid != dono:
        return bot.answer_callback_query(c.id, "⚠️ NÃO É SUA VEZ!", show_alert=True)

    # Verifica se o tempo já expirou
    if msg_id not in expira_em and acao != 'girar':
        return bot.answer_callback_query(c.id, "⏰ Seu tempo expirou! Inicie um novo jogo.", show_alert=True)

    if acao == 'verdade':
        expira_em.pop(msg_id, None) # Cancela o cronômetro
        res = formatar_texto(random.choice(VERDADES_BASE), chat_id)
        bot.edit_message_text(f"🟢 <b>VERDADE PARA:</b> {c.from_user.first_name}\n\n<i>{res}</i>", chat_id, msg_id)
    
    elif acao == 'desafio':
        expira_em.pop(msg_id, None) # Cancela o cronômetro
        res = formatar_texto(random.choice(DESAFIOS_BASE), chat_id)
        bot.edit_message_text(f"🔴 <b>DESAFIO PARA:</b> {c.from_user.first_name}\n\n<i>{res}</i>", chat_id, msg_id)

    elif acao == 'girar':
        participantes = list(usuarios_ativos.get(chat_id, {}).keys())
        if len(participantes) < 2:
            return bot.answer_callback_query(c.id, "❌ Preciso de pelo menos 2 pessoas ativas!", show_alert=True)
        
        # 1. Contagem Regressiva de 5 segundos
        for i in range(5, 0, -1):
            bot.edit_message_text(f"🍾 Girando a garrafa...\n\n⏳ {i}...", chat_id, msg_id)
            time.sleep(1)

        # 2. Sorteio
        escolhido_id = random.choice([p for p in participantes if p != uid])
        escolhido_nome = usuarios_ativos[chat_id][escolhido_id]
        
        # 3. Define novo dono e tempo limite
        if chat_id not in turno_vd: turno_vd[chat_id] = {}
        turno_vd[chat_id][msg_id] = escolhido_id
        expira_em[msg_id] = time.time() + 60

        # Inicia thread de expiração
        threading.Thread(target=cronometro_expiracao, args=(chat_id, msg_id, escolhido_nome)).start()

        markup = telebot.types.InlineKeyboardMarkup()
        markup.add(telebot.types.InlineKeyboardButton("🍾 Girar Novamente", callback_data="vd_girar")) # Botão no topo
        markup.row(telebot.types.InlineKeyboardButton("🟢 Verdade", callback_data="vd_verdade"),
                   telebot.types.InlineKeyboardButton("🔴 Desafio", callback_data="vd_desafio"))
        
        bot.edit_message_text(
            f"🍾 A garrafa parou em: <b>{escolhido_nome}</b>!\n\nVocê tem <b>1 minuto</b> para escolher seu destino:", 
            chat_id, msg_id, reply_markup=markup
        )

@bot.message_handler(commands=['vd'])
def cmd_vd(m):
    chat_id, uid, nome = m.chat.id, m.from_user.id, m.from_user.first_name
    if chat_id not in usuarios_ativos: usuarios_ativos[chat_id] = {}
    usuarios_ativos[chat_id][uid] = nome

    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(telebot.types.InlineKeyboardButton("🍾 Girar Garrafa", callback_data="vd_girar")) # Topo
    markup.row(telebot.types.InlineKeyboardButton("🟢 Verdade", callback_data="vd_verdade"),
               telebot.types.InlineKeyboardButton("🔴 Desafio", callback_data="vd_desafio"))
    
    msg = bot.send_message(chat_id, f"🎯 <b>JOGO INICIADO!</b>\nVez de: <b>{nome}</b>", reply_markup=markup)
    
    if chat_id not in turno_vd: turno_vd[chat_id] = {}
    turno_vd[chat_id][msg.message_id] = uid

@bot.message_handler(func=lambda m: True)
def monitor(m):
    chat_id = m.chat.id
    if chat_id not in usuarios_ativos: usuarios_ativos[chat_id] = {}
    usuarios_ativos[chat_id][m.from_user.id] = m.from_user.first_name

# ================= EXECUÇÃO =================

def run_bot():
    bot.remove_webhook()
    print("Bot rodando com cronômetro e 1400 itens...")
    bot.infinity_polling(skip_pending=True)

if __name__ == "__main__":
    t = threading.Thread(target=run_bot)
    t.daemon = True
    t.start()
    
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
    
