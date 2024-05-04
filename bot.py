import discord
import responses

Token = 'MTIzNjE5MDc0MjcyNTAwNTQwNA.GQPOrF.r-8ZY91F3G2ioPNYlrC1G5iOLe-7kQ8AbX0X18'  
intents = discord.Intents.default() 

async def send_msgs(msgs, user_msgs, is_private):
    try:
        response = responses.handle_responses(user_msgs) 
        await msgs.author.send(response) if is_private else await msgs.channel.send(response)
    except Exception as e:
        print(e)

def run_voca(): 

    client = discord.Client(intents = intents)

    @client.event
    async def on_ready():
        print(f'{client.user} is now running!')

    @client.event
    async def on_message(msgs):
        if msgs.author == client.user:
            return
        
        username = str(msgs.author)
        user_msgs = str(msgs.content)
        channel = str(msgs.channel)

        print(f"{username} said: '{user_msgs}' ({channel})")

        if user_msgs[0] == '?':
            user_msgs = user_msgs[1:]
            await send_msgs(msgs, user_msgs, is_private=True)
        else:
            await send_msgs(msgs, user_msgs, is_private=False)

    client.run(Token)