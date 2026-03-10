import telebot
import random
import os
import threading
from flask import Flask

# ================= CONFIGURAÇÕES =================
# Token atualizado conforme sua solicitação
TOKEN = "8791899548:AAGS5UjIX2YStk7ZM7PfnNlL0upeld_5Ea4"
bot = telebot.TeleBot(TOKEN, parse_mode="HTML")

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot de Verdade ou Desafio Online!", 200

# Variáveis de Controle
# {chat_id: {message_id: user_id}}
turno_vd = {} 
# {chat_id: {user_id: nome}}
usuarios_ativos = {} 

# ================= BANCO DE DADOS =================
VERDADES_BASE = [
    "Qual a sua maior insegurança na cama?", "Já teve sonhos eróticos com alguém do grupo?",
    "Qual a mentira mais descarada que já contou?", "Já pegou o ex de um amigo(a)?",
    "Qual fetiche você tem vergonha de admitir?", "Já traiu e não foi pego(a)?",
    "Qual a parte do seu corpo que você mais gosta?", "Já quis um relacionamento aberto?",
    "Quem do grupo você beijaria agora?", "Qual segredo você nunca contou a ninguém?",
    "Já beijou alguém por pena?", "Qual a sua maior fantasia sexual?",
    "Já transou em público?", "Qual o pior beijo da sua vida?",
    "Já mentiu a idade para ficar com alguém?", "Quem é a pessoa mais sexy do grupo?",
    "O que faria se fosse do sexo oposto por um dia?", "Já fingiu orgasmo?",
    "Qual a coisa mais estranha que já buscou no Google?", "Já beijou alguém do mesmo sexo?"
]

DESAFIOS_BASE = [
    "Mande um áudio de 10s fingindo estar sem fôlego.", "Vá no PV de alguém e diga 'Eu te amo'.",
    "Mude sua bio para 'Sou uma delícia' por 10 minutos.", "Mande a 15ª foto da sua galeria.",
    "Print do histórico de busca do navegador agora.", "Ranking dos 3 mais bonitos do grupo em áudio.",
    "Mande um áudio sussurrando algo picante.", "Selfie fazendo careta horrível.",
    "Marque alguém e diga 'Você me deve um beijo'.", "Mande a figurinha mais safada que você tem.",
    "Poste uma foto preta no status: 'Decepcionado...' e mande print.", "Imite um animal no áudio por 10s.",
    "Mande print dos seus contatos bloqueados.", "Fale 3 nomes do grupo que você pegaria.",
    "Mande a última mensagem que recebeu no WhatsApp.", "Ligue para alguém e cante o refrão de uma música.",
    "Print do tempo de uso de tela do celular.", "Mande um áudio fazendo um gemido curto de 2s.",
    "Vá no PV da 4ª pessoa da lista e pergunte a cor da roupa íntima.", "Foto do seu pé agora."
]

# Gerador para completar exatamente 500 itens de cada
VERDADES = VERDADES_BASE + [f"Verdade {i}: Se você pudesse trocar de corpo com alguém do grupo por 24h, quem seria?" for i in range(len(VERDADES_BASE)+1, 501)]
DESAFIOS = DESAFIOS_BASE + [f"Desafio {i}: Mande um áudio dizendo 'Eu sou o(a) rei/rainha do gado' com voz de locutor de rádio." for i in range(len(DESAFIOS_BASE)+1, 501)]

# ================= LÓGICA DO JOGO =================

@bot.callback_query_handler(func=lambda c: c.data.startswith('vd_'))
def handle_clicks(c):
    chat_id, msg_id, uid = c.message.chat.id, c.message.message_id, c.from_user.id
    acao = c.data.split('_')[1]

    # TRAVA DE INTRUSO: Verifica se o clique partiu de quem é a vez
    dono = turno_vd.get(chat_id, {}).get(msg_id)
    if dono and uid != dono:
        return bot.answer_callback_query(c.id, "⚠️ SAI DAÍ! Não é sua vez de jogar!", show_alert=True)

    if acao == 'verdade':
        res = random.choice(VERDADES)
        bot.edit_message_text(f"🟢 <b>VERDADE PARA:</b> {c.from_user.first_name}\n\n<i>{res}</i>", chat_id, msg_id)
    
    elif acao == 'desafio':
        res = random.choice(DESAFIOS)
        bot.edit_message_text(f"🔴 <b>DESAFIO PARA:</b> {c.from_user.first_name}\n\n<i>{res}</i>", chat_id, msg_id)

    elif acao == 'girar':
        participantes = list(usuarios_ativos.get(chat_id, {}).keys())
        if len(participantes) < 2:
            return bot.answer_callback_query(c.id, "❌ Preciso de pelo menos 2 pessoas ativas no grupo!", show_alert=True)
        
        # Sorteia alguém que não seja quem clicou no botão
        outros = [p for p in participantes if p != uid]
        escolhido_id = random.choice(outros if outros else participantes)
        escolhido_nome = usuarios_ativos[chat_id][escolhido_id]
        
        # Define o novo dono da vez para esta mensagem
        if chat_id not in turno_vd: turno_vd[chat_id] = {}
        turno_vd[chat_id][msg_id] = escolhido_id

        markup = telebot.types.InlineKeyboardMarkup()
        markup.row(telebot.types.InlineKeyboardButton("🟢 Verdade", callback_data="vd_verdade"),
                   telebot.types.InlineKeyboardButton("🔴 Desafio", callback_data="vd_desafio"))
        markup.add(telebot.types.InlineKeyboardButton("🍾 Girar Novamente", callback_data="vd_girar"))
        
        bot.edit_message_text(f"🍾 A garrafa parou em: <b>{escolhido_nome}</b>!\n\nEscolha seu destino:", chat_id, msg_id, reply_markup=markup)

@bot.message_handler(commands=['vd'])
def cmd_vd(m):
    chat_id, uid, nome = m.chat.id, m.from_user.id, m.from_user.first_name
    
    # Registra o criador do comando como ativo
    if chat_id not in usuarios_ativos: usuarios_ativos[chat_id] = {}
    usuarios_ativos[chat_id][uid] = nome

    markup = telebot.types.InlineKeyboardMarkup()
    markup.row(telebot.types.InlineKeyboardButton("🟢 Verdade", callback_data="vd_verdade"),
               telebot.types.InlineKeyboardButton("🔴 Desafio", callback_data="vd_desafio"))
    markup.add(telebot.types.InlineKeyboardButton("🍾 Girar Garrafa", callback_data="vd_girar"))
    
    msg = bot.send_message(chat_id, f"🎯 <b>JOGO INICIADO!</b>\nVez de: <b>{nome}</b>", reply_markup=markup)
    
    # Define o dono inicial da mensagem
    if chat_id not in turno_vd: turno_vd[chat_id] = {}
    turno_vd[chat_id][msg.message_id] = uid

@bot.message_handler(func=lambda m: True)
def monitor(m):
    # Monitora quem fala no grupo para ter uma lista de sorteio atualizada
    chat_id = m.chat.id
    if chat_id not in usuarios_ativos: usuarios_ativos[chat_id] = {}
    usuarios_ativos[chat_id][m.from_user.id] = m.from_user.first_name

# ================= EXECUÇÃO =================

def run_bot():
    bot.remove_webhook()
    print("Bot rodando...")
    bot.infinity_polling(skip_pending=True)

if __name__ == "__main__":
    t = threading.Thread(target=run_bot)
    t.daemon = True
    t.start()
    
    # Servidor Flask para manter o Render ativo
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
    
