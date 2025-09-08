import discord
from discord.ext import commands, tasks
import os
import asyncio

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

online_players = set()
channel_id = None  # Will store the channel ID for automatic messages

class OnlinePlayersView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
    
    @discord.ui.button(label='Entrei! 🎮', style=discord.ButtonStyle.green, custom_id='join_game')
    async def join_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        username = interaction.user.display_name
        online_players.add(username)
        await interaction.response.send_message(f'{username} está online! 🎮', ephemeral=True)
        
        # Update the original message
        if online_players:
            lista = "\n".join(online_players)
            embed = discord.Embed(
                title="👥 Jogadores Online", 
                description=f"{lista}",
                color=0x00ff00
            )
        else:
            embed = discord.Embed(
                title="👥 Jogadores Online", 
                description="Ninguém está online no momento.",
                color=0xff0000
            )
        
        view = OnlinePlayersView()
        await interaction.edit_original_response(embed=embed, view=view)
    
    @discord.ui.button(label='Sai ❌', style=discord.ButtonStyle.red, custom_id='leave_game')
    async def leave_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        username = interaction.user.display_name
        if username in online_players:
            online_players.remove(username)
            await interaction.response.send_message(f'{username} saiu do jogo. ❌', ephemeral=True)
        else:
            await interaction.response.send_message(f'{username} não estava na lista.', ephemeral=True)
            
        # Update the original message
        if online_players:
            lista = "\n".join(online_players)
            embed = discord.Embed(
                title="👥 Jogadores Online", 
                description=f"{lista}",
                color=0x00ff00
            )
        else:
            embed = discord.Embed(
                title="👥 Jogadores Online", 
                description="Ninguém está online no momento.",
                color=0xff0000
            )
        
        view = OnlinePlayersView()
        await interaction.edit_original_response(embed=embed, view=view)

@tasks.loop(minutes=15)
async def send_online_status():
    if channel_id:
        channel = bot.get_channel(channel_id)
        if channel and isinstance(channel, (discord.TextChannel, discord.DMChannel, discord.GroupChannel)):
            if online_players:
                lista = "\n".join(online_players)
                embed = discord.Embed(
                    title="👥 Jogadores Online", 
                    description=f"{lista}",
                    color=0x00ff00
                )
            else:
                embed = discord.Embed(
                    title="👥 Jogadores Online", 
                    description="Ninguém está online no momento.",
                    color=0xff0000
                )
            
            view = OnlinePlayersView()
            await channel.send(embed=embed, view=view)

@bot.event
async def on_ready():
    print(f'✅ Bot conectado como {bot.user}')
    send_online_status.start()
    print('🔄 Sistema automático ativado (mensagem a cada 15 minutos)')

@bot.command()
async def entrei(ctx):
    username = ctx.author.display_name
    online_players.add(username)
    await ctx.send(f'{username} está online! 🎮')

@bot.command()
async def sai(ctx):
    username = ctx.author.display_name
    if username in online_players:
        online_players.remove(username)
        await ctx.send(f'{username} saiu do jogo. ❌')
    else:
        await ctx.send(f'{username} não estava na lista.')

@bot.command()
async def online(ctx):
    global channel_id
    channel_id = ctx.channel.id  # Set channel for automatic messages
    
    if online_players:
        lista = "\n".join(online_players)
        embed = discord.Embed(
            title="👥 Jogadores Online", 
            description=f"{lista}",
            color=0x00ff00
        )
    else:
        embed = discord.Embed(
            title="👥 Jogadores Online", 
            description="Ninguém está online no momento.",
            color=0xff0000
        )
    
    view = OnlinePlayersView()
    await ctx.send(embed=embed, view=view)
    
@bot.command()
async def config_canal(ctx):
    """Define este canal para receber mensagens automáticas"""
    global channel_id
    channel_id = ctx.channel.id
    await ctx.send(f'✅ Canal configurado! Mensagens automáticas serão enviadas aqui a cada 15 minutos.')

@bot.command()
async def enquete(ctx, *, texto=None):
    """Cria uma enquete com pergunta e opções separadas por |"""
    # Emojis numerados para as reações
    numero_emojis = ['1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣']
    
    # Verifica se foi fornecido texto
    if not texto:
        await ctx.send('❌ Formato incorreto! Use: `!enquete pergunta | opção1 | opção2 | ...`\n\n**Exemplo:**\n`!enquete Qual atividade vamos fazer? | Fazer rally | Participar do evento | Outra ideia`')
        return
    
    try:
        # Separa o texto por |
        partes = [parte.strip() for parte in texto.split('|')]
        
        if len(partes) < 2:
            await ctx.send('❌ Formato incorreto! Use: `!enquete pergunta | opção1 | opção2 | ...`\n\n**Exemplo:**\n`!enquete Qual atividade vamos fazer? | Fazer rally | Participar do evento | Outra ideia`')
            return
        
        pergunta = partes[0]
        opcoes = partes[1:]
        
        # Limita a 5 opções máximo
        if len(opcoes) > 5:
            await ctx.send('❌ Máximo de 5 opções permitidas!')
            return
        
        # Verifica se há opções vazias
        opcoes = [opcao for opcao in opcoes if opcao.strip()]
        if len(opcoes) < 1:
            await ctx.send('❌ É necessário pelo menos 1 opção válida!')
            return
        
        # Cria a mensagem formatada
        descricao = ""
        for i, opcao in enumerate(opcoes):
            descricao += f"{numero_emojis[i]} {opcao}\n"
        
        embed = discord.Embed(
            title=f"📊 {pergunta}",
            description=descricao,
            color=0x3498db
        )
        
        # Envia a mensagem
        mensagem = await ctx.send(embed=embed)
        
        # Adiciona as reações correspondentes
        for i in range(len(opcoes)):
            await mensagem.add_reaction(numero_emojis[i])
            
    except Exception as e:
        await ctx.send('❌ Erro ao criar enquete. Verifique o formato: `!enquete pergunta | opção1 | opção2 | ...`\n\n**Exemplo:**\n`!enquete Qual atividade vamos fazer? | Fazer rally | Participar do evento | Outra ideia`')

token = os.getenv('TOKEN')
if token:
    print(f'🔑 Token encontrado, tentando conectar...')
    try:
        bot.run(token)
    except discord.LoginFailure:
        print('❌ Erro de login: Token inválido. Verifique se o token está correto.')
    except discord.ConnectionClosed as e:
        print(f'❌ Conexão fechada: {e}. Possível problema de rede ou token.')
    except KeyboardInterrupt:
        print('\n🛑 Bot interrompido pelo usuário')
    except Exception as e:
        print(f'❌ Erro inesperado: {e}')
else:
    print("❌ TOKEN não encontrado. Configure a variável de ambiente TOKEN com o token do seu bot Discord.")