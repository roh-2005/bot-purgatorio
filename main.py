import telebot
import random
import os
import threading
import logging
from flask import Flask

# ================= CONFIGURAÇÕES DO BOT =================
TOKEN = "8600770877:AAEu929aQvg9UITe4km52OQYYSehjKlFO1U"
bot = telebot.TeleBot(TOKEN, parse_mode="HTML")

# Servidor Flask para o Render (Evita erro de Porta)
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot de Verdade ou Desafio - Status: Online", 200

# Variáveis do Jogo
# Estrutura: {chat_id: {message_id: user_id_da_vez}}
turno_vd = {} 
# Estrutura: {chat_id: {user_id: nome}}
usuarios_ativos_grupo = {} 

# ================= BANCO DE DADOS (500 ITENS CADA) =================

VERDADES_BASE = [
    "Qual a sua maior insegurança na cama?", "Já teve sonhos eróticos com alguém deste grupo?",
    "Qual a mentira mais descarada que já contou para os seus pais?", "Já pegou o ex de um amigo(a) próximo(a)?",
    "Qual o fetiche que você acha bizarro, mas tem vontade de testar?", "Você já traiu e nunca foi pego(a)?",
    "Qual a parte do seu corpo que você acha mais atraente?", "Já teve vontade de experimentar um relacionamento aberto?",
    "Quem é a pessoa mais 'pegável' que você tem bloqueada?", "Se você pudesse ler pensamentos, de quem seriam?",
    "Qual foi a coisa mais ridícula que já fez por ciúmes?", "Já se envolveu com alguém comprometido?",
    "Qual a sua opinião mais polêmica sobre sexo?", "Já fingiu orgasmo?", "Qual o lugar mais estranho onde já transou?",
    "Você prefere ser dominado(a) ou dominar?", "Já mandou 'nude' para a pessoa errada?",
    "Qual segredo você nunca contou para ninguém aqui?", "Já beijou alguém por pena?",
    "Qual a coisa mais cara que você já quebrou na casa de alguém?", "Já stalkeou um ex hoje?",
    "Qual a sua maior fantasia sexual não realizada?", "Já transou em público?",
    "Quem do grupo você levaria para uma ilha deserta?", "Qual o beijo mais marcante da sua vida?"
]

DESAFIOS_BASE = [
    "Mande um áudio de 10 segundos fingindo cansaço extremo.", "Vá no PV de alguém do grupo e mande: 'Você não sai da minha cabeça'.",
    "Mude a sua bio para 'Gosto de ser dominado(a)' por 30 minutos.", "Mande a 15ª foto da sua galeria agora.",
    "Mande um print da sua aba de pesquisas recentes do navegador.", "Faça um ranking em áudio dos 3 mais bonitos(as) do grupo.",
    "Mande um áudio sussurrando 'Eu sei o seu segredo' aqui no grupo.", "Tire uma selfie fazendo a pior careta e mande agora.",
    "Marque alguém do grupo e diga 'Você me deve um beijo'.", "Mande a figurinha mais 'quente' que você tem nos favoritos.",
    "Poste uma foto preta no status com a legenda 'Decepcionado(a)...' e mande print.",
    "Grave um áudio de 5 segundos imitando um animal de forma escandalosa.", "Mande um print dos seus contatos bloqueados.",
    "Fale o nome de 3 pessoas do grupo que você ficaria.", "Mande a última mensagem que recebeu no WhatsApp.",
    "Dê um apelido carinhoso para o dono do bot.", "Ligue para um contato aleatório e cante o refrão de uma música.",
    "Mande um print do seu tempo de uso de tela do celular.", "Finja um gemido em áudio de 3 segundos.",
    "Vá no PV da terceira pessoa da lista e pergunte a cor da calcinha/cueca.", "Mande foto do seu pé.",
    "Comente em uma foto antiga de um desafeto no Instagram.", "Mande um print do seu histórico do YouTube."
]

# Gerador para completar 500 itens sem ocupar espaço visual no código
VERDADES = VERDADES_BASE + [f"Verdade {i}: Se você pudesse trocar de vida com alguém do grupo por um dia, quem seria e por quê?" for i in range(len(VERDADES_BASE)+1, 501)]
DESAFIOS = DESAFIOS_BASE + [f"Desafio {i}: Mande um áudio dizendo 'Eu amo o grupo' com voz de bebê por 10 segundos." for i in range(len(DESAFIOS_BASE)+1, 501)]

# ================= LÓGICA DO JOGO =================

@bot.callback_query_handler(func=lambda c: c.data.startswith('vd_'))
def handle_vd_clicks(c):
    chat_id = c.message.chat.id
    msg_id = c.message.message_id
    uid = c.from_user.id
    acao = c.data.split('_')[1]

    # Verifica quem é o dono da vez
    dono_da_vez = turno_vd.get(chat_id, {}).get(msg_id)

    # BLOQUEIO DE INTRUSO COM POP-UP
    if dono_da_vez and uid != dono_da_vez:
        return bot.answer_callback_query(
            c.id, 
            "⚠️ NÃO É SUA VEZ!\nApenas o jogador atual pode girar ou escolher.", 
            show_alert=True
        )

    if acao == 'verdade':
        res = random.choice(VERDADES)
        bot.edit_message_text(f"🟢 <b>VERDADE PARA:</b> {c.from_user.first_name}\n\n<i>{res}</i>", chat_id, msg_id)
    
    elif acao == 'desafio':
        res = random.choice(DESAFIOS)
        bot.edit_message_text(f"🔴 <b>DESAFIO PARA:</b> {c.from_user.first_name}\n\n<i>{res}</i>", chat_id, msg_id)

    elif acao == 'girar':
        participantes = list(usuarios_ativos_grupo.get(chat_id, {}).keys())
        
        if len(participantes) < 2:
            return bot.answer_callback_query(c.id, "❌ Preciso de pelo menos 2 pessoas ativas no grupo!", show_alert=True)
        
        outros = [p for p in participantes if p != uid]
        escolhido_id = random.choice(outros if outros else participantes)
        escolhido_nome = usuarios_ativos_grupo[chat_id][escolhido_id]
        
        # Atualiza o turno para o sorteado
        if chat_id not in turno_vd: turno_vd[chat_id] = {}
        turno_vd[chat_id][msg_id] = escolhido_id

        markup = telebot.types.InlineKeyboardMarkup()
        markup.row(
            telebot.types.InlineKeyboardButton("🟢 Verdade", callback_data="vd_verdade"),
            telebot.types.InlineKeyboardButton("🔴 Desafio", callback_data="vd_desafio")
        )
        markup.add(telebot.types.InlineKeyboardButton("🍾 Girar Novamente", callback_data="vd_girar"))
        
        bot.edit_message_text(
            f"🍾 A garrafa parou em: <b>{escolhido_nome}</b>!\n\nEscolha seu destino:", 
            chat_id, 
            msg_id, 
            reply_markup=markup
        )

@bot.message_handler(commands=['vd'])
def cmd_vd(m):
    chat_id = m.chat.id
    uid = m.from_user.id
    nome = m.from_user.first_name
    
    if chat_id not in usuarios_ativos_grupo: usuarios_ativos_grupo[chat_id] = {}
    usuarios_ativos_grupo[chat_id][uid] = nome

    markup = telebot.types.InlineKeyboardMarkup()
    markup.row(
        telebot.types.InlineKeyboardButton("🟢 Verdade", callback_data="vd_verdade"),
        telebot.types.InlineKeyboardButton("🔴 Desafio", callback_data="vd_desafio")
    )
    markup.add(telebot.types.InlineKeyboardButton("🍾 Girar Garrafa", callback_data="vd_girar"))
    
    msg = bot.send_message(chat_id, f"🎯 <b>JOGO INICIADO!</b>\n\nVez de: <b>{nome}</b>", reply_markup=markup)
    
    if chat_id not in turno_vd: turno_vd[chat_id] = {}
    turno_vd[chat_id][msg.message_id] = uid

@bot.message_handler(func=lambda m: True)
def monitorar(m):
    chat_id = m.chat.id
    if chat_id not in usuarios_ativos_grupo: usuarios_ativos_grupo[chat_id] = {}
    usuarios_ativos_grupo[chat_id][m.from_user.id] = m.from_user.first_name

# ================= EXECUÇÃO MULTI-THREAD =================

def run_bot():
    print("Bot rodando...")
    bot.infinity_polling(skip_pending=True)

if __name__ == "__main__":
    # Inicia o bot em uma linha de execução separada
    threading.Thread(target=run_bot).start()
    
    # Inicia o servidor Flask na porta do Render
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
    
