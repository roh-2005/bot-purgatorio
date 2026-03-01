import asyncio
import random
import os
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# --- CONFIGURAÇÕES ---
API_ID = 28373470 
API_HASH = "55d56fcb5e62b12998b5f77b1151136c" 
BOT_TOKEN = "8791899548:AAGOLZ2qXBuo0QNIBQsUAY-l3QOW3PHZlzc"

app = Client("purgatorio_v7", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# Dicionários de controle
sorteados = {} 
jogos_ativos = {} 

# --- BANCO DE DADOS INTEGRADO ---
VERDADES = [
    "Já se apaixonou por alguém aqui do grupo em segredo?", "Já chegou a gozar vendo a foto de perfil de alguém daqui ou imaginando a pessoa?",
    "Quem do grupo você teria uma amizade colorida agora mesmo?", "Já teve um sonho erótico com algum membro daqui? Se sim, quem?",
    "Qual pessoa do grupo tem o corpo que mais te dá gatilho?", "Já salvou alguma foto de alguém daqui na sua galeria privada?",
    "Se você fosse obrigado a transar com alguém do grupo hoje, quem seria?", "Já sentiu ciúmes de algum membro aqui conversando com outra pessoa?",
    "Quem aqui você acha que transa melhor só pelo jeito de falar?", "Já teve pensamento +18 com alguém daqui?", 
    "Qual foi a coisa mais safada que você já fez escondido(a)?", "Já mandou nude alguma vez na vida?", 
    "Já recebeu nude inesperado e gostou?", "Você já se tocou pensando em alguém que não devia?", 
    "Já ficou com duas pessoas na mesma semana?", "Já fingiu sentimento só pra não ficar sozinho(a)?", 
    "Qual sua maior fantasia que quase ninguém sabe?", "Já fez algo +18 em lugar “inapropriado”?", 
    "Já se arrependeu de um beijo minutos depois?", "Já teve webnamoro intenso?", 
    "Já fez algo só por puro tesão do momento?", "Já se envolveu com alguém comprometido?", 
    "Já ficou excitado(a) só por mensagem?", "Já mentiu sobre sua experiência?", 
    "Já fez joguinho emocional com alguém?", "Já ficou com alguém por carência?", 
    "Já teve amizade colorida?", "Já sentiu atração por alguém proibido(a)?", 
    "Já fez chamada de vídeo suspeita?", "Já quis sumir depois de mandar algo vergonhoso?", 
    "Já sentiu ciúmes sem ter direito nenhum?", "Já mandou foto “arriscada” e apagou depois?", 
    "Já fingiu não sentir nada, mas estava pegando fogo por dentro?", "Já fez algo impulsivo que deu ruim depois?", 
    "Já ficou com alguém e pensou em outra pessoa?", "Já teve recaída que prometeu nunca ter?", 
    "Já foi tóxico(a) por ciúmes?", "Já competiu por alguém?", 
    "Já teve crush secreto dentro do grupo?", "Já mandou nude pra alguém do grupo?", 
    "Já teve conversa muito safada no PV?", "Já imaginou alguém daqui sem roupa?", 
    "Já ficou nervoso(a) com foto de alguém do grupo?", "Já quis beijar alguém daqui e nunca falou nada?", 
    "Já mentiu que estava ocupado(a) só pra provocar?", "Já se declarou e se arrependeu?", 
    "Já iludiu alguém sem perceber?", "Já foi iludido feio?", 
    "Já pensou “se essa pessoa chamar, eu vou”?", "Qual a parte do corpo que você mais gosta em você?", 
    "Qual o lugar mais estranho que já sentiu tesão?", "Já transou em lugar público?", 
    "Qual sua posição favorita?", "O que te dá tesão instantâneo?", 
    "Já usou brinquedos eróticos?", "Já fez menagem ou tem vontade?", 
    "Prefere dominar ou ser dominado?", "Qual sua maior 'red flag' em um relacionamento?", 
    "Já stalkeou alguém daqui hoje?", "Qual a última pessoa que você pesquisou no Instagram?", 
    "Qual foi a última vez que você se tocou?", "Você prefere beijo no pescoço ou mordida na orelha?", 
    "Já mandou mensagem bêbado(a) se declarando?", "Qual o perfil do grupo que você mais visita?", 
    "Já quis pegar o(a) ex de algum amigo?", "Qual sua maior insegurança na hora H?", 
    "Já gravou vídeo fazendo?", "Já teve um 'pente e rala' que se arrependeu?", 
    "Quem do grupo você bloquearia por 24h?", "Já mentiu a idade pra ficar com alguém?", 
    "Qual sua maior tara secreta?", "Já fez fio terra ou tem curiosidade?", 
    "Quem do grupo tem a voz mais sexy?", "Já mandou áudio gemendo pra alguém?", 
    "Você é do tipo que se apega fácil ou só quer diversão?", "Já chorou depois do sexo?", 
    "Qual foi o maior tempo que já ficou sem fazer nada?", "Já usou alguma fantasia (roupa) especial?", 
    "Já teve um 'repoly' com ex?", "Você prefere luz acesa ou apagada?", 
    "Já fez algo por dinheiro ou interesse?", "Qual a mensagem mais pesada que tem no seu celular?", 
    "Quem aqui você levaria para um motel agora?", "Já beijou alguém do mesmo sexo?", 
    "Qual sua primeira impressão do dono do grupo?", "Já tomou um fora histórico?", 
    "Já deu um fora e se arrependeu?", "Qual o print mais comprometedor que você tem?", 
    "Já fingiu orgasmo?", "O que você nunca faria na cama?", 
    "Quem do grupo você acha que é 'biscoiteiro'?", "Já teve um crush em algum professor(a)?", 
    "Qual a coisa mais estranha que você já usou como lubrificante?", "Já foi pego no flagra?", 
    "Qual sua maior loucura por amor?", "Já traiu ou foi traído?", 
    "Quem do grupo você acha que não toma banho?", "Já dormiu durante o ato?", 
    "Qual o cheiro que mais te excita?", "Já mandou foto do corpo para um estranho?", 
    "Você se considera uma pessoa safada ou santa?", "Quem aqui você daria um beijo de 1 minuto?", 
    "Qual sua opinião sobre relacionamento aberto?", "Já teve um sonho com alguém que você odeia?", 
    "Qual a coisa mais boba que te faz rir?", "Quem do grupo é o seu número?", 
    "Já quis beijar dois ao mesmo tempo?", "Qual sua maior vergonha em um encontro?", 
    "Você prefere ser elogiado pela inteligência ou pelo corpo?", "Já beijou alguém daqui fora do Telegram?", 
    "Qual a pessoa mais rodada que você conhece?", "Quem você acha que é virgem no grupo?", 
    "Já fez strip-tease?", "Qual sua música favorita para o 'vrau'?", 
    "Já mandou mensagem errada pro grupo?", "Qual o maior tabu que você já quebrou?", 
    "Já namorou alguém que conheceu em grupo de chat?", "Quem do grupo você não suporta?", 
    "Já desejou o namorado(a) de um amigo(a)?", "Qual sua maior habilidade na cama?", 
    "Já deu em cima de alguém hoje?", "Quem daqui você acha que é o mais fogoso?", 
    "Já teve amizade que acabou por causa de sexo?", "Qual a sua maior cantada infalível?", 
    "Já fez algo ilegal por adrenalina?", "Quem do grupo você acha que tem o maior 'instrumento'?", 
    "Já pagou para ter prazer?", "Qual sua reação se alguém do grupo te mandasse um nude agora?", 
    "Já ficou com alguém por pena?", "Qual o maior tempo que você já durou?", 
    "Já teve experiência com BDSM?", "Qual sua maior curiosidade sobre o sexo oposto?", 
    "Quem aqui você gostaria de ver sem roupa?", "Já fez sexting com alguém do trabalho?", 
    "Qual a coisa mais nojenta que você já aceitou fazer?", "Já teve um 'crush' em um desenho animado?", 
    "Você prefere carinho ou tapas?", "Já foi expulso de algum lugar por estar fazendo safadeza?", 
    "Qual a maior mentira que você já contou pra transar?", "Quem do grupo você acha que é o mais santinho(a)?", 
    "Já teve vontade de lamber alguma parte estranha de alguém?", "Qual sua comida favorita pós-sexo?", 
    "Já mandou foto da raba pra alguém hoje?", "Quem daqui te deixa com as pernas bambas?", 
    "Qual o primeiro detalhe que você olha em alguém?", "Já teve um 'remember' que durou meses?", 
    "Quem aqui você acha que tem o melhor bumbum?", "Já sentiu atração por alguém 20 anos mais velho(a)?", 
    "Qual o seu maior fetiche com pés?", "Quem aqui você daria uma chance se estivesse solteiro(a)?", 
    "Qual o segredo que você vai levar para o túmulo?"
]

DESAFIOS = [
    "Escolha alguém do grupo e diga se você já teve algum pensamento impuro com a foto dela.",
    "Marque a pessoa do grupo que você acha mais sexy e mande um emoji de fogo.",
    "Mande um áudio de 10 segundos dizendo o que você faria se estivesse trancado num quarto com alguém daqui.",
    "Mande um emoji provocante e diga “eu sei o que você fez” sem explicar.", 
    "Escolha alguém do grupo e elogie de forma ousada.",
    "Mande no grupo sua última figurinha suspeita.", "Diga qual tipo de pessoa mais te atrai.",
    "Mande um áudio de 5 segundos falando algo sedutor.", "Poste um print da sua galeria (sem mostrar nada íntimo).",
    "Fale a coisa mais safada que já pensou hoje.", "Diga quem você ficaria aqui, mas sem marcar.",
    "Mande “eu nunca te esqueci” para alguém no PV e printa a resposta.", "Escolha alguém e diga uma qualidade + um defeito.",
    "Mande uma selfie agora.", "Revele sua última pesquisa estranha.",
    "Mande um “tô com saudade” pra alguém daqui e mostra o print.", "Descreva como seria seu beijo perfeito.",
    "Marque alguém e diga: “a gente precisa conversar…”", "Escolha alguém e diga o que faria num encontro.",
    "Poste um áudio sussurrando algo provocante.", "Fale quem você acha que já teve fantasia com você.",
    "Mande um “se tu chamar eu vou” no grupo.", "Escolha alguém e diga se beijaria ou não, e por quê.",
    "Diga a parte do corpo que você mais gosta em alguém.", "Mande um coração pra quem mexe com você (sem explicar).",
    "Escolha alguém e diga se teria algo casual ou sério.", "Conte sua maior vergonha +18.",
    "Poste um emoji que represente seu nível de safadeza hoje.", "Mande um áudio de 10s fazendo voz provocante.",
    "Grave um vídeo fazendo “cara de safado(a)” por 5s.", "Mande um emoji 😈 e diga quem te deixaria sem juízo.",
    "Envie no PV de alguém: “se a gente tivesse sozinho agora…” e mostre o print.", "Poste uma selfie: “perigo ambulante”.",
    "Mande um áudio sussurrando algo quente.", "Escolha alguém e diga qual parte do corpo você mais repara.",
    "Mande no grupo: “eu não presto” e não explique nada.", "Envie um “me provoca mais” para alguém no PV e printa.",
    "Grave um áudio dando uma risada maliciosa.", "Escolha alguém: noite sem compromisso ou algo sério?",
    "Poste um emoji que represente o que você está pensando agora 😏🔥", 
    "Mande mensagem para alguém do grupo: “você não faz ideia do que eu penso…” e mostre o print.",
    "Vídeo mordendo o lábio por 5 segundos.", "Escolha alguém e diga se já imaginou um clima entre vocês.",
    "Mande no grupo: “eu toparia uma loucura hoje”", "Diga qual tipo de toque mais te arrepia.",
    "Envie um “me conta seu segredo mais sujo” no PV e printa.", "Grave um áudio dizendo “fala que você quer” provocando.",
    "Escolha duas pessoas e diga qual é mais perigosa.", "Poste foto fazendo olhar intenso.",
    "Mande no grupo: “alguém aqui me deixa sem controle…”", "Diga se já teve curiosidade de testar química com alguém daqui.",
    "Mande um emoji 🔥 para quem te dá mais vontade de provocar (sem marcar).",
    "Mande um áudio gemendo baixo o nome de alguém do grupo.", "Marque 3 pessoas e diga quem você: Beija, Mata ou Casa.",
    "Poste uma foto do seu pescoço agora.", "Diga qual o maior fetiche da pessoa que postou antes de você.",
    "Mande um print da sua lista de bloqueados.", "Mande para o seu ex: 'vi isso e lembrei de você' e apague em seguida.",
    "Faça uma declaração de amor para um objeto aleatório em áudio.", "Poste um vídeo rebolando por 5 segundos.",
    "Mande um áudio de 15 segundos fingindo um orgasmo.", "Diga quem do grupo você passaria a noite em um motel.",
    "Mande uma mensagem para sua mãe dizendo 'estou grávida/alguém vai ser pai' e mostre o print.",
    "Coloque na sua bio do Telegram: 'Eu sou um(a) safado(a)' por 10 minutos.", "Mande um nude... de um ombro.",
    "Mostre sua última conversa no WhatsApp.", "Ligue para alguém do grupo por 10 segundos e desligue.",
    "Diga qual a cor da sua peça íntima agora.", "Mande um 'quero você' no PV do ADM e mostre o print.",
    "Tire uma foto da sua mão e mande no grupo.", "Descreva como você está vestido(a) de forma sexy.",
    "Mande um áudio dizendo: 'Eu sou todinho(a) seu(sua)' para o @ dono do bot.", "Tire print do seu histórico do YouTube e mande.",
    "Mande um 'oi sumido(a)' para a 5ª pessoa da sua lista de contatos.", "Diga qual a maior mentira que você já contou aqui.",
    "Escolha alguém e mande: 'Sua foto de perfil me deu calor'.", "Grave um vídeo mandando um beijo de língua para a câmera.",
    "Diga quem aqui tem a melhor raba na sua opinião.", "Mande um emoji de 🍌 ou 🍑 para alguém no PV.",
    "Poste um vídeo mostrando a língua.", "Diga qual o nome da pessoa que você está afim agora.",
    "Mande uma figurinha de 'safadeza' para o seu último contato do WhatsApp.", "Conte um segredo que ninguém aqui sabe.",
    "Mande um áudio de 20 segundos cantando uma música erótica.", "Diga quem do grupo você daria um 'tapa na gostosa'.",
    "Poste uma foto dos seus pés.", "Tire uma foto fazendo biquinho.",
    "Mande um áudio sussurrando: 'Vem cá me pegar'.", "Diga quem você acha que é o mais 'pau mandado' do grupo.",
    "Mande uma mensagem no grupo: 'Cansei de ser santo(a)'", "Diga se você prefere por cima ou por baixo.", 
    "Poste o print do seu tempo de uso do celular.", "Mande um 'você me excita' para alguém aleatório no PV.",
    "Diga quem do grupo você bloquearia para sempre.", "Faça um desenho de um pinto no papel e mande a foto.", 
    "Mande um áudio falando em espanhol de forma sedutora.", "Poste uma foto do seu umbigo.", 
    "Mande um emoji de 👅 para quem você quer beijar agora.", "Grave um vídeo curto fazendo um 'quadradinho'.", 
    "Mande um 'te amo' para o seu melhor amigo(a) e mostre a reação.", "Diga quem aqui você acha que tem chulé.",
    "Mande um áudio dizendo: 'Eu quero ser seu(sua) brinquedinho(a)'.", "Mande um emoji de 💍 para quem você casaria aqui.", 
    "Diga qual a maior vergonha que você passou bêbado(a).", "Diga quem aqui você acha que é 'ruim de cama'.",
    "Mande um áudio imitando um animal tendo um orgasmo.", "Mande um 'me usa' no PV de alguém e printa.", 
    "Mande um áudio de 10s apenas respirando ofegante.", "Diga quem aqui você levaria para um quarto escuro.", 
    "Grave um áudio dizendo: 'Você não imagina o que eu faria com você'.", "Diga quem é a pessoa mais chata do grupo.",
    "Diga se você usa calcinha/cueca em casa agora.", "Mande um 'bora fechar?' no PV de alguém.",
    "Poste uma foto da sua sombra de forma artística.", "Mande um áudio rindo igual um vilão de novela.",
    "Diga quem aqui você daria um banho de língua.", "Mande um emoji de 🤫 para o seu crush do grupo.",
    "Grave um vídeo mandando um beijo para o ADM.", "Diga se você prefere ser a caça ou o caçador.",
    "Mande um 'você é meu/minha' no PV de alguém.", "Diga quem aqui você faria um ménage.",
    "Mande um emoji de 😈 para as 3 últimas pessoas que falaram.", "Diga quem do grupo você acha que tem o olhar mais penetrante.",
    "Grave um vídeo piscando para a câmera de forma sensual.", "Mande um emoji de 🌊 para quem te deixa molhado(a).",
    "Mande um áudio de 5 segundos dizendo: 'Vem me calar'.", "Diga quem aqui você gostaria de ver acordando do seu lado.",
    "Mande um emoji de ⚡ para quem te dá um choque de realidade.", "Mande um print dos seus stickers favoritos."
]

# --- LÓGICA DE FILTRO ---
@app.on_message(filters.group & (filters.regex(r"@Vddoudsf_purgatorio_bot") | filters.command("vd")))
async def handle_start(client, message):
    uid = message.from_user.id
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("🍾 GIRAR GARRAFA", callback_data="girar_garrafa")],
        [InlineKeyboardButton("❓ VERDADE", callback_data=f"v_{uid}"),
         InlineKeyboardButton("🔥 DESAFIO", callback_data=f"d_{uid}")]
    ])
    await message.reply_text(
        f"⛓️ **PURGATÓRIO V7**\n\n👤 Jogador: {message.from_user.mention}\nEscolha seu destino ou gire a garrafa:",
        reply_markup=kb
    )

@app.on_callback_query()
async def game_engine(client, query):
    chat_id = query.message.chat.id
    user_id = query.from_user.id
    data = query.data

    if data == "girar_garrafa":
        try:
            membros = []
            async for m in client.get_chat_members(chat_id, limit=80):
                if not m.user.is_bot and m.user.status != "long_ago":
                    membros.append(m.user)
            
            if not membros: return await query.answer("Não achei ninguém disponível! 🤷‍♂️")

            for i in range(5, 0, -1):
                await query.edit_message_text(f"🍾 **GIRANDO A GARRAFA...**\n\n⏳ Parando em {i} segundos...")
                await asyncio.sleep(1.1)

            sorteado = random.choice(membros)
            sorteados[chat_id] = sorteado.id
            
            kb = InlineKeyboardMarkup([
                [InlineKeyboardButton("❓ VERDADE", callback_data=f"v_{sorteado.id}"),
                 InlineKeyboardButton("🔥 DESAFIO", callback_data=f"d_{sorteado.id}")]
            ])
            
            msg = await query.edit_message_text(
                f"🍾 A garrafa parou para: {sorteado.mention}!\n\n⚠️ **VOCÊ TEM 10 SEGUNDOS PARA ESCOLHER!**",
                reply_markup=kb
            )
            
            jogos_ativos[chat_id] = msg.id
            await asyncio.sleep(10)
            
            if chat_id in sorteados and sorteados[chat_id] == sorteado.id:
                if chat_id in jogos_ativos and jogos_ativos[chat_id] == msg.id:
                    await msg.delete()
                    await client.send_message(chat_id, f"⏰ **TEMPO ESGOTADO!**\n{sorteado.mention} não escolheu a tempo e foi pro inferno. Próximo!")
                    sorteados.pop(chat_id, None)
                    jogos_ativos.pop(chat_id, None)

        except Exception as e:
            await query.answer("Me dê permissão de ADM para ver membros!", show_alert=True)

    elif data.startswith(("v_", "d_")):
        tipo, dono_id = data.split("_")
        if user_id != int(dono_id):
            return await query.answer("❌ Não é sua vez! A garrafa não parou em você.", show_alert=True)

        sorteados.pop(chat_id, None)
        jogos_ativos.pop(chat_id, None)

        res = "❓ **VERDADE**" if tipo == "v" else "🔥 **DESAFIO**"
        lista = VERDADES if tipo == "v" else DESAFIOS
        await query.edit_message_text(f"{res} PARA {query.from_user.mention}:\n\n{random.choice(lista)}")

@app.on_message(filters.private)
async def pv_handler(client, message):
    respostas = [
        "😏 O fogo está no grupo! Vá para lá e use `/vd`.",
        "🚫 Para jogar, você precisa ir em um grupo e enviar o comando `/vd`!",
        "🤫 Segredos só no grupo! Me adicione em um e digite `/vd`.",
        "⚡ O Purgatório só abre nos grupos. Use o comando `/vd` lá!"
    ]
    await message.reply_text(random.choice(respostas))

# Garante que o bot rode mesmo sem porta definida (para Render)
if __name__ == "__main__":
    print("🔥 Purgatório V7 ON!")
    app.run()
                       
