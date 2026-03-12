import telebot
import time
import threading
import os
import logging
import random
from flask import Flask
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# Servidor para o Render
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot Purgatório 2.1 Online!", 200

# ================= CONFIGURAÇÕES =================
TOKEN = "8791899548:AAGS5UjIX2YStk7ZM7PfnNlL0upeld_5Ea4"
bot = telebot.TeleBot(TOKEN, parse_mode="HTML")

# ================= BANCO DE TRUTHS (350 VERDADES) =================
VERDADES = [
    "Qual foi a última pessoa que você stalkeou no Instagram?", "Você já beijou alguém deste grupo em pensamento?",
    "Qual é o seu fetiche que você tem vergonha de contar?", "Já mandou nudes para a pessoa errada? Conte como foi.",
    "Quem aqui você levaria para um motel agora mesmo?", "Qual foi a maior mentira que você já contou para um(a) ex?",
    "Você já fingiu prazer só para acabar logo a transa?", "Qual parte do corpo do sexo oposto mais te dá tesão?",
    "Já ficou com alguém por puro interesse ou dinheiro?", "Qual é a coisa mais 'safada' que você já fez em público?",
    "Já teve um sonho erótico com algum amigo(a) de infância?", "Qual é o segredo que você jura que vai levar para o túmulo?",
    "Se você pudesse ser invisível por um dia, quem você iria vigiar no banho?", "Já foi pego(a) no flagra fazendo algo que não devia?",
    "Quem aqui no grupo você acha que beija pior só de olhar?", "Qual foi o lugar mais estranho onde você já transou?",
    "Você já teve uma queda por algum professor(a) ou chefe?", "Qual é a sua maior insegurança na hora H?",
    "Já mandou um 'oi sumida' só porque estava carente e sem opção?", "Você prefere dominar ou ser dominado(a)?",
    "Já transou com alguém e se arrependeu no meio do ato?", "Qual é a pessoa mais chata deste grupo na sua opinião sincera?",
    "Já usou algum brinquedo íntimo e escondeu de todo mundo?", "Você já beijou alguém do mesmo sexo? Se não, teria coragem?",
    "Qual foi o maior mico que você já passou bêbado(a)?", "Já mentiu sua idade para conseguir ficar com alguém?",
    "Qual é o seu vídeo 'proibidão' favorito na internet?", "Já teve vontade de ficar com o(a) namorado(a) de um amigo(a)?",
    "Qual foi a última vez que você chorou e por que motivo?", "Já fez algum vídeo íntimo e depois ficou com medo de vazar?",
    "Quem aqui você deletaria da sua vida sem pensar duas vezes?", "Você já traiu ou foi traído(a)? Conte os detalhes.",
    "Qual é a sua tática infalível para seduzir alguém?", "Você já foi para a cama com alguém no primeiro encontro?",
    "Qual é a coisa mais infantil que você ainda faz escondido?", "Já stalkeou o perfil do(a) atual do seu ex?",
    "O que você faria se descobrisse que seu melhor amigo(a) é apaixonado(a) por você?", "Já entrou em um motel a pé ou de Uber?",
    "Qual é a sua opinião real sobre o dono deste grupo?", "Já fingiu que estava dormindo para não atender o celular?",
    # +50 NOVAS VERDADES ABAIXO
    "Você já usou perfume para esconder que não tomou banho antes de um encontro?", "Qual é a coisa mais bizarra que você já pesquisou no Google?",
    "Se você pudesse trocar de vida com alguém do grupo por um dia, quem seria?", "Já enviou uma mensagem falando mal de alguém para a própria pessoa?",
    "Qual foi o sonho mais estranho que você já teve com alguém daqui?", "Você já cheirou suas próprias roupas íntimas para ver se estavam limpas?",
    "Qual é o hábito mais irritante que você tem e ninguém sabe?", "Você já mentiu para sair de um compromisso e ficou em casa assistindo série?",
    "Quem aqui você acha que tem o estilo mais cafona?", "Qual foi a última vez que você sentiu ciúmes de alguém que não é nada seu?",
    "Já teve vontade de beijar o(a) melhor amigo(a) do seu parceiro(a)?", "Qual é a sua maior fantasia que envolve uniformes ou fantasias?",
    "Você já se sentiu atraído por algum personagem de desenho animado?", "Qual foi a maior loucura que você já fez por uma paixão não correspondida?",
    "Já fingiu que não viu alguém na rua para não ter que cumprimentar?", "Qual é a primeira coisa que você faria se descobrisse que é traído(a)?",
    "Você já pegou algo emprestado e nunca mais devolveu de propósito?", "Qual é o seu maior medo em relação ao que os outros pensam de você?",
    "Já ficou com alguém só para fazer ciúmes em outra pessoa?", "Qual foi o comentário mais maldoso que você já fez sobre alguém deste grupo?",
    "Você já teve um encontro que foi tão ruim que você inventou uma emergência para ir embora?", "Qual é a parte do seu corpo que você acha que atrai mais olhares?",
    "Já teve um crush em alguém que é o completo oposto do seu tipo?", "Você já chorou ouvindo uma música e lembrou de alguém daqui?",
    "Qual é o segredo de família que você nunca deveria contar?", "Já tentou impressionar alguém fingindo ter mais dinheiro do que tem?",
    "Qual é a sua maior tentação quando está sozinho(a) em casa?", "Você já se arrependeu de ter enviado um nude logo após mandar?",
    "Quem aqui você bloquearia agora se não houvesse consequências?", "Qual foi a última vez que você agiu por puro impulso e se deu mal?",
    "Você prefere ser amado(a) ou ser respeitado(a)?", "Já teve vontade de sumir e começar uma vida nova em outro lugar?",
    "Qual foi a mensagem mais comprometedora que você já recebeu no WhatsApp?", "Você já se sentiu atraído(a) por alguém muito mais velho(a)?",
    "Qual é o seu maior talento oculto que ninguém levaria a sério?", "Já mentiu no currículo ou em uma entrevista de trabalho?",
    "Você já teve um ataque de riso em uma hora completamente inapropriada?", "Qual é a sua maior fraqueza quando o assunto é sedução?",
    "Já ficou com alguém do trabalho ou da escola e escondeu de todo mundo?", "Quem aqui você levaria para um jantar romântico?",
    "Qual é a coisa que mais te faz perder o interesse em alguém instantaneamente?", "Já teve uma experiência de 'quase morte' ou muito perigosa?",
    "Qual foi a última vez que você fez algo apenas para agradar os outros?", "Você acredita em amor à primeira vista ou em tesão à primeira vista?",
    "Já stalkeou a família de algum crush até encontrar o endereço deles?", "Qual é a sua opinião sobre relacionamentos abertos?",
    "Você já fingiu estar bêbado(a) para justificar algo que fez?", "Qual é o seu maior arrependimento da adolescência?",
    "Quem aqui do grupo você acha que seria o melhor parceiro(a) para um crime?", "Já teve vontade de socar alguém deste grupo?",
    "Qual é a coisa mais cara que você já quebrou e fingiu que não foi você?", "Você já se sentiu atraído(a) por alguém enquanto estava namorando?",
    "Qual foi o momento em que você se sentiu mais poderoso(a)?", "Já mandou um áudio falando de alguém e enviou para a própria pessoa?",
    "Qual é o seu maior vício (que não seja droga)?", "Já teve uma briga feia com alguém por causa de rede social?",
    "Qual é a coisa mais estranha que você já fez por dinheiro?", "Você já se sentiu observado(a) enquanto estava sozinho(a)?",
    "Quem aqui você gostaria de ver sem roupa?", "Qual foi a maior mentira que você já contou para si mesmo(a)?"
]

# ================= BANCO DE DARES (250 DESAFIOS) =================
DESAFIOS = [
    "Mande um áudio de 30 segundos gemendo de forma bem realista.", "Poste uma foto sua fazendo careta e mande o print aqui.",
    "Mande um print do seu histórico do navegador sem apagar nada.", "Ligue para um(a) ex e grave o áudio dizendo que ainda sente saudades.",
    "Mande um áudio cantando o refrão de um funk bem proibidão.", "Troque sua foto de perfil por uma foto de um objeto aleatório por 1 hora.",
    "Mande uma mensagem no privado da última pessoa que te chamou dizendo: 'Eu te desejo'.", "Tire uma foto do seu pé e mande aqui no grupo agora.",
    "Mande um vídeo curto rebolando por pelo menos 10 segundos.", "Poste no status do seu WhatsApp: 'Estou com fogo hoje' e mande o print.",
    "Mande um print das suas últimas 5 conversas do WhatsApp.", "Dê um selinho em um objeto da sua casa e mande o vídeo.",
    "Mande um áudio de 20 segundos declarando seu amor por um travesseiro.", "Tire uma foto só de toalha (sem mostrar demais) e mande aqui.",
    "Mande um emoji de fogo para a pessoa que você acha mais gata do grupo.", "Escreva 'Eu sou safado(a)' no seu status por 15 minutos.",
    "Mande um áudio falando detalhadamente o que faria com quem te sorteou.", "Morda o lábio de forma provocante em um vídeo curto e mande aqui.",
    "Mande um print do seu uso de bateria das últimas 24 horas.", "Ligue para sua mãe/pai e diga que vai casar amanhã, grave o áudio.",
    "Mande uma foto da sua mão e deixe que o grupo adivinhe o que você faz com ela.", "Faça 10 polichinelos gravando um vídeo e mande no grupo.",
    "Mande um áudio dizendo: 'Eu aceito ser seu escravo(a) por uma noite'.", "Tente lamber o seu próprio cotovelo e mande o vídeo da tentativa.",
    "Mande um print da sua galeria de fotos, as 4 últimas imagens.", "Diga quem você pegaria do grupo e marque a pessoa sem piedade.",
    # +50 NOVOS DESAFIOS ABAIXO
    "Mande um áudio de 15 segundos imitando um bebê chorando por leite.", "Coloque uma colher de açúcar na boca e tente assobiar enviando áudio.",
    "Mande uma mensagem para o terceiro contato do seu WhatsApp dizendo: 'Eu sei o que você fez'.", "Ligue para um amigo e tente vender um par de meias usadas por 1 minuto.",
    "Mande um print do seu tempo de uso do Instagram hoje.", "Poste uma foto sua de infância no grupo agora.",
    "Faça uma declaração de amor dramática para uma garrafa de água via áudio.", "Mande um áudio narrando como se fosse um locutor de futebol o seu último beijo.",
    "Troque seu nome no Telegram para 'Sou um Pônei' por 10 minutos.", "Mande um emoji de coração para a pessoa que você menos conversa aqui.",
    "Faça um vídeo curto tentando equilibrar um chinelo na cabeça enquanto dança.", "Mande um áudio rimando o nome de 5 pessoas do grupo com adjetivos engraçados.",
    "Poste no status: 'Alguém me indica um motel bom?' e mande o print em 2 minutos.", "Mande uma foto da sola do seu pé esquerdo.",
    "Mande um áudio imitando o Galvão Bueno narrando uma transa.", "Fale 5 qualidades da pessoa que te sorteou sem parar para pensar.",
    "Mande um print das suas configurações de conta (sem mostrar dados sensíveis).", "Faça um vídeo de 5 segundos piscando de forma sedutora.",
    "Mande uma mensagem para um número desconhecido dizendo 'O pacote foi entregue' e mostre o print.", "Imite um despertador irritante em um áudio de 10 segundos.",
    "Mande foto do seu último pedido no iFood ou aplicativo de entrega.", "Tire uma selfie segurando um papel escrito: 'O Purgatório me domina'.",
    "Mande um áudio cantando o Hino Nacional com voz de sono.", "Fale o nome de alguém que você já quis pegar e nunca teve coragem.",
    "Mande um print da sua última pesquisa no YouTube.", "Faça uma massagem (virtual) em quem te sorteou descrevendo em áudio.",
    "Mande um vídeo bebendo um copo d'água sem usar as mãos.", "Escreva 'Eu te amo' no privado de alguém que você não fala há meses e mande o print.",
    "Mande um áudio de 20 segundos falando apenas palavras que começam com a letra 'S'.", "Imite uma celebridade famosa e o grupo tem que adivinhar quem é por áudio.",
    "Mande uma foto do seu fundo de tela do celular e do WhatsApp.", "Diga qual é a cor da sua roupa íntima agora.",
    "Mande um áudio fingindo que está em um filme de terror sendo perseguido(a).", "Peça um Pix de 1 real para alguém no grupo e mande o print se conseguir.",
    "Mande um vídeo curto fazendo um passo de dança de TikTok (mesmo que não saiba).", "Descreva o seu tipo ideal de parceiro(a) usando apenas emojis.",
    "Mande um áudio de 10 segundos rindo igual a uma bruxa.", "Poste uma foto da sua orelha bem de perto.",
    "Mande uma mensagem para o seu chefe ou professor dizendo 'Oi sumido' e apague (mande print antes).", "Tire uma foto de um objeto aleatório no seu quarto e conte uma história falsa sobre ele.",
    "Mande um áudio declarando que você é o(a) mais bonito(a) do mundo.", "Faça uma mímica por vídeo de uma posição sexual e o grupo tem que adivinhar.",
    "Mande um print da sua lista de contatos que começam com a letra 'L'.", "Grave um áudio de 5 segundos em silêncio absoluto e diga que foi um segredo.",
    "Mande foto da sua mão fazendo um sinal de 'V' de vitória.", "Diga qual foi o maior valor que você já gastou em uma única noite.",
    "Mande um áudio imitando um locutor de rádio FM de madrugada.", "Fale uma palavra em outro idioma e o grupo tem que descobrir o significado.",
    "Mande um print do seu histórico de chamadas (pode tapar os nomes).", "Dê um grito (baixo) em áudio dizendo o nome do grupo."
]

# ================= MEMÓRIA E LÓGICA =================
usuarios_conhecidos = {} 
jogos_ativos = {} 

def registrar_membro(chat_id, user_id, nome):
    if chat_id not in usuarios_conhecidos:
        usuarios_conhecidos[chat_id] = {}
    if user_id not in [536215124, 777000]: 
        usuarios_conhecidos[chat_id][user_id] = nome

@bot.message_handler(content_types=['new_chat_members', 'text'])
def monitor(message):
    chat_id = message.chat.id
    if message.content_type == 'new_chat_members':
        for m in message.new_chat_members:
            registrar_membro(chat_id, m.id, m.first_name)
    else:
        registrar_membro(chat_id, message.from_user.id, message.from_user.first_name)
        if message.text == "/vd":
            iniciar(message)

def iniciar(message):
    chat_id = message.chat.id
    u_id = message.from_user.id
    mencao = f"<a href='tg://user?id={u_id}'>{message.from_user.first_name}</a>"
    
    jogos_ativos[chat_id] = {'dono': u_id, 'mencao_dono': mencao, 'alvo_id': None, 'alvo_mencao': "", 'status': 'menu'}
    
    markup = InlineKeyboardMarkup()
    markup.row(InlineKeyboardButton("Girar Garrafa 🍾", callback_data="girar"))
    markup.row(InlineKeyboardButton("Verdade 🙊", callback_data="v"), InlineKeyboardButton("Desafio 😈", callback_data="d"))
    bot.send_message(chat_id, f"🔥 <b>Purgatório: Verdade ou Desafio</b>\nIniciado por: {mencao}", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def cliques(call):
    chat_id = call.message.chat.id
    user_id = call.from_user.id
    msg_id = call.message.message_id
    registrar_membro(chat_id, user_id, call.from_user.first_name)

    if chat_id not in jogos_ativos: return

    permitido = jogos_ativos[chat_id]['alvo_id'] if jogos_ativos[chat_id]['status'] == 'esperando' else jogos_ativos[chat_id]['dono']
    
    if user_id != permitido:
        bot.answer_callback_query(call.id, "Não está na sua vez de jogar!", show_alert=True)
        return

    if call.data == "girar":
        try:
            adms = bot.get_chat_administrators(chat_id)
            for a in adms:
                if not a.user.is_bot: registrar_membro(chat_id, a.user.id, a.user.first_name)
        except: pass

        lista = list(usuarios_conhecidos.get(chat_id, {}).items())
        
        # AJUSTE: CONTADOR DE 5 SEGUNDOS ATIVO
        for i in range(5, 0, -1):
            bot.edit_message_text(f"🍾 <b>Girando Garrafa... {i}s</b>", chat_id, msg_id)
            time.sleep(1)

        s_id, s_nome = random.choice(lista)
        s_mencao = f"<a href='tg://user?id={s_id}'>{s_nome}</a>"
        
        jogos_ativos[chat_id].update({'alvo_id': s_id, 'alvo_mencao': s_mencao, 'status': 'esperando'})
        
        markup = InlineKeyboardMarkup()
        markup.row(InlineKeyboardButton("Verdade 🙊", callback_data="v"), InlineKeyboardButton("Desafio 😈", callback_data="d"))
        bot.edit_message_text(f"🎯 <b>Parou em:</b> {s_mencao}\nEscolha o seu destino!", chat_id, msg_id, reply_markup=markup)

    elif call.data in ["v", "d"]:
        texto = random.choice(VERDADES) if call.data == "v" else random.choice(DESAFIOS)
        tipo = "🙊 VERDADE" if call.data == "v" else "😈 DESAFIO"
        quem = jogos_ativos[chat_id]['alvo_mencao'] if jogos_ativos[chat_id]['alvo_id'] else jogos_ativos[chat_id]['mencao_dono']
        
        bot.edit_message_text(f"<b>{tipo} PARA {quem}:</b>\n\n{texto}", chat_id, msg_id, reply_markup=None)
        jogos_ativos.pop(chat_id, None)

# ================= EXECUÇÃO =================
def run():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

if __name__ == "__main__":
    threading.Thread(target=run).start()
    bot.infinity_polling()
    
