import discord
import responses

intents = discord.Intents.default() 

async def send_msgs(msgs, user_msgs, is_private):
    try:
        response = responses.handle_responses(user_msgs) 
        await msgs.author.send(response) if is_private else await msgs.channel.send(response)
    except Exception as e:
        print(e)

def run_voco(): 
    Token = 'MTIzNjE5MDc0MjcyNTAwNTQwNA.Gku8e8.iCpzBP60YJde9pscmBCIFBln0BhTs3KyTfU9ug'  
    client = discord.Client(intents=intents)

    @client.event
    async def on_ready():
        print(f'{client.user} is now running!')

    client.run(Token)

