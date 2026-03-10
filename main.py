import telebot
import time
import threading
import os
import logging
import random

# ================= CONFIGURAÇÕES =================
TOKEN = "8600770877:AAEu929aQvg9UITe4km52OQYYSehjKlFO1U"
bot = telebot.TeleBot(TOKEN, parse_mode="HTML", threaded=True)

# Variáveis do Jogo
# Estrutura: {chat_id: {message_id: user_id_da_vez}}
turno_vd = {} 
# Estrutura: {chat_id: {user_id: nome}}
usuarios_ativos_grupo = {} 

# ================= LISTAS (Resumidas para o exemplo) =================
VERDADES = [
    "Qual a sua maior insegurança na cama?",
    "Já teve sonhos eróticos com alguém deste grupo?",
    "Qual a mentira mais descarada que já contou?",
    "Qual o fetiche que você acha bizarro, mas tem vontade de testar?"
]

DESAFIOS = [
    "Mande um áudio de 10 segundos fingindo cansaço.",
    "Mude a sua bio para 'Gosto de ser dominado(a)' por 10 min.",
    "Mande a 15ª foto da sua galeria agora.",
    "Ligue para o primeiro do histórico e desligue na cara."
]

# ================= LÓGICA DO JOGO =================

@bot.callback_query_handler(func=lambda c: c.data.startswith('vd_'))
def handle_vd_clicks(c):
    chat_id = c.message.chat.id
    msg_id = c.message.message_id
    uid = c.from_user.id
    acao = c.data.split('_')[1]

    # 1. BUSCA QUEM É O DONO DA VEZ NESTA MENSAGEM ESPECÍFICA
    # Se não houver registro, o bot ignora ou define como livre (segurança)
    jogador_da_vez = turno_vd.get(chat_id, {}).get(msg_id)

    # 2. VERIFICAÇÃO DE INTRUSO
    if jogador_da_vez and uid != jogador_da_vez:
        return bot.answer_callback_query(
            c.id, 
            "⚠️ SAI DAÍ, INTRUSO!\nNão é a sua vez de girar ou escolher.", 
            show_alert=True
        )

    # 3. SE FOR O JOGADOR CORRETO, SEGUE O JOGO
    if acao == 'verdade':
        res = random.choice(VERDADES)
        bot.edit_message_text(f"🟢 <b>VERDADE PARA:</b> {c.from_user.first_name}\n\n<i>{res}</i>", chat_id, msg_id)
        # Limpa o turno após responder para permitir novo /vd sem lixo na memória
        if msg_id in turno_vd[chat_id]: del turno_vd[chat_id][msg_id]
    
    elif acao == 'desafio':
        res = random.choice(DESAFIOS)
        bot.edit_message_text(f"🔴 <b>DESAFIO PARA:</b> {c.from_user.first_name}\n\n<i>{res}</i>", chat_id, msg_id)
        if msg_id in turno_vd[chat_id]: del turno_vd[chat_id][msg_id]

    elif acao == 'girar':
        participantes = list(usuarios_ativos_grupo.get(chat_id, {}).keys())
        
        if len(participantes) < 2:
            return bot.answer_callback_query(c.id, "❌ Preciso de pelo menos 2 pessoas ativas no chat!", show_alert=True)
        
        # Sorteia alguém que não seja quem clicou (opcional, para dar dinâmica)
        outros = [p for p in participantes if p != uid]
        escolhido_id = random.choice(outros if outros else participantes)
        escolhido_nome = usuarios_ativos_grupo[chat_id][escolhido_id]
        
        # ATUALIZAÇÃO CRUCIAL: Agora o dono da vez passa a ser o sorteado
        turno_vd[chat_id][msg_id] = escolhido_id

        markup = telebot.types.InlineKeyboardMarkup()
        markup.row(
            telebot.types.InlineKeyboardButton("🟢 Verdade", callback_data="vd_verdade"),
            telebot.types.InlineKeyboardButton("🔴 Desafio", callback_data="vd_desafio")
        )
        markup.add(telebot.types.InlineKeyboardButton("🍾 Girar Novamente", callback_data="vd_girar"))
        
        bot.edit_message_text(
            f"🍾 A garrafa girou e parou em: <b>{escolhido_nome}</b>!\n\nO que você escolhe?", 
            chat_id, 
            msg_id, 
            reply_markup=markup
        )

@bot.message_handler(commands=['vd'])
def cmd_vd(m):
    chat_id = m.chat.id
    uid = m.from_user.id
    nome = m.from_user.first_name
    
    # Registra o usuário como ativo
    if chat_id not in usuarios_ativos_grupo: usuarios_ativos_grupo[chat_id] = {}
    usuarios_ativos_grupo[chat_id][uid] = nome

    markup = telebot.types.InlineKeyboardMarkup()
    markup.row(
        telebot.types.InlineKeyboardButton("🟢 Verdade", callback_data="vd_verdade"),
        telebot.types.InlineKeyboardButton("🔴 Desafio", callback_data="vd_desafio")
    )
    markup.add(telebot.types.InlineKeyboardButton("🍾 Girar Garrafa", callback_data="vd_girar"))
    
    msg = bot.send_message(chat_id, f"🎯 <b>JOGO INICIADO!</b>\n\nVez de: <b>{nome}</b>\n<i>Gire a garrafa para sortear alguém!</i>", reply_markup=markup)
    
    # Define que, nesta mensagem, apenas quem deu /vd pode clicar inicialmente
    if chat_id not in turno_vd: turno_vd[chat_id] = {}
    turno_vd[chat_id][msg.message_id] = uid

@bot.message_handler(func=lambda m: True)
def monitorar_atividades(m):
    # Atualiza a lista de quem está falando para o sorteio funcionar
    chat_id = m.chat.id
    if chat_id not in usuarios_ativos_grupo: usuarios_ativos_grupo[chat_id] = {}
    usuarios_ativos_grupo[chat_id][m.from_user.id] = m.from_user.first_name

if __name__ == "__main__":
    print("Bot rodando e vigiando intrusos...")
    bot.infinity_polling(skip_pending=True)
    
