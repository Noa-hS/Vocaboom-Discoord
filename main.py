import discord
from discord.ext import commands
import random
import asyncio
import os

bot = commands.Bot(command_prefix='!', intents=discord.Intents.all())

class WordBomb:
    def __init__(self):
        self.players = []
        self.current_player = None
        self.last_prompt = None
        self.game_started = False
        self.used_words = set()
        self.eliminated_players = []
        self.game_start_time = None
        self.turn_time = 10
        self.round_count = 0
        with open('worddictionary.txt', 'r') as f:
            self.valid_words = set(word.strip().lower() for word in f)
        with open('promptlist.txt', 'r') as f:
            self.prompts = [prompt.strip() for prompt in f]

    def add_player(self, player):
        self.players.append(player)

    def start_game(self):
        self.current_player = random.choice(self.players)
        self.game_started = True
        self.game_start_time = asyncio.get_event_loop().time()

    def next_player(self):
        current_index = self.players.index(self.current_player)
        if current_index == len(self.players) - 1:
            self.current_player = self.players[0]
            self.round_count += 1
            if self.round_count % len(self.players) == 0:
                self.turn_time = max(3, self.turn_time - 1)
        else:
            self.current_player = self.players[current_index + 1]

    def validate_word(self, word):
        word = word.lower()
        if self.last_prompt is None:
            return word in self.valid_words
        if word in self.used_words:
            return False
        return self.last_prompt.lower() in word and word in self.valid_words

    def eliminate_player(self):
        self.eliminated_players.append(self.current_player)
        self.players.remove(self.current_player)
        if len(self.players) == 1:
            last_player = self.players[0]
            self.reset_game()
            return last_player
        else:
            self.next_player()
            return None

    def reset_game(self):
        self.players = []
        self.current_player = None
        self.last_prompt = None
        self.game_started = False
        self.used_words.clear()
        self.eliminated_players = []
        self.game_start_time = None
        self.turn_time = 10

game = WordBomb()

@bot.event
async def on_ready():
    print('Ready!')

@bot.command()
async def startgame(ctx):
    if game.game_started:
        await ctx.send("A game is already in progress.")
        return

    game.reset_game()
    game.add_player(ctx.author)
    await ctx.send(f"{ctx.author.mention} has started a new game and joined. You have 30 seconds to join the game! Use '!joingame' to quickly join the game.")
    await asyncio.sleep(30)

    if len(game.players) < 2 or len(game.players) > 4:
        await ctx.send("Oops! Lobby session ended. Not enough players or too many players to start the game. Write '!startgame' to create a new lobby.")
        return

    game.start_game()
    game.last_prompt = random.choice(game.prompts)
    await ctx.send(f"The game has started! The first prompt is: **{game.last_prompt}**\n{game.current_player.mention}, provide a word containing the prompt. You have {game.turn_time} seconds.")

@bot.command()
async def joingame(ctx):
    if game.game_started:
        await ctx.send("A game is already in progress. Please wait for the next game.")
        return

    if ctx.author in game.players:
        await ctx.send("You have already joined the game.")
        return

    if len(game.players) >= 4:
        await ctx.send("The game is already full. Please wait for the next game.")
        return
    

    game.add_player(ctx.author)
    await ctx.send(f"{ctx.author.mention} has joined the game.")
    await ctx.send(f"Current players: {', '.join(player.mention for player in game.players)}")

@bot.command()
async def w(ctx, *, word):
    if not game.game_started:
        await ctx.send("No game is currently in progress.")
        return

    if ctx.author != game.current_player:
        await ctx.send("It's not your turn.")
        return

    if not game.validate_word(word):
        await ctx.send("Invalid word.")
        last_player = game.eliminate_player()
        if last_player:
            await ctx.send(f"Game over! {last_player.mention} is the winner!")
        elif game.game_started:
            await ctx.send(f"Current players: {', '.join(player.mention for player in game.players)}\nIt's {game.current_player.mention}'s turn.")
        return

    game.used_words.add(word.lower())
    game.next_player()

    if game.current_player == ctx.author:
        await ctx.send(f"{ctx.author.mention} took too long to respond. They have been eliminated.")
        last_player = game.eliminate_player()
        if last_player:
            await ctx.send(f"Game over! {last_player.mention} is the winner!")
        elif game.game_started:
            await ctx.send(f"It's {game.current_player.mention}'s turn.")

@bot.command()
async def gamestatus(ctx):
    if not game.game_started:
        await ctx.send("No game is currently in progress.")
        return

    elapsed_time = int(asyncio.get_event_loop().time() - game.game_start_time)
    minutes, seconds = divmod(elapsed_time, 60)

    status = f"Current players: {', '.join(player.mention for player in game.players)}\n"
    status += f"Eliminated players: {', '.join(player.mention for player in game.eliminated_players)}\n"
    status += f"Time elapsed: {minutes:02d}:{seconds:02d}\n"

    if ctx.author in game.players:
        status += "You are still in the game."
    elif ctx.author in game.eliminated_players:
        status += "You have been eliminated."
    else:
        status += "You are not in the game."

    await ctx.send(status)

@bot.command()
async def phelp(ctx):
    await ctx.send(f"Hi {ctx.author.mention}! Here are some commands to get you started:\n"
                   "- Use !startgame to start a new game.\n"
                   "- Use !joingame to join a game.\n"
                   "- Use !w <your word> to play a word.\n"
                   "- Use !gamestatus to check the current game status.\n"
                   "There are also some hidden commands!")

bot.run('MTIzNjE5MDc0MjcyNTAwNTQwNA.GnfZ1Z.T2cZMY00yMxpMq7yW9X2zPoQqjiutR9CknB4Qw')
