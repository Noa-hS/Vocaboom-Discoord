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
        self.last_word = None
        self.game_started = False
        self.used_words = set()

    def add_player(self, player):
        self.players.append(player)

    def start_game(self):
        self.current_player = random.choice(self.players)
        self.game_started = True

    def next_player(self):
        current_index = self.players.index(self.current_player)
        if current_index == len(self.players) - 1:
            self.current_player = self.players[0]
        else:
            self.current_player = self.players[current_index + 1]

    def validate_word(self, word):
        if self.last_word is None:
            return True
        if word in self.used_words:
            return False
        return word[0] == self.last_word[-1]

    def eliminate_player(self):
        self.players.remove(self.current_player)
        if self.players:
            self.next_player()

    def reset_game(self):
        self.players = []
        self.current_player = None
        self.last_word = None
        self.game_started = False
        self.used_words.clear()

game = WordBomb()

@bot.event
async def on_ready():
    print('Ready!')

@bot.command()
async def startwordbomb(ctx):
    if game.game_started:
        await ctx.send("A game is already in progress.")
        return

    game.reset_game()
    await ctx.send("A new game is starting. Use !joinwordbomb to join the game.")
    await asyncio.sleep(30)  # Wait for 30 seconds for players to join

    if len(game.players) < 2:
        await ctx.send("Not enough players to start the game.")
        return

    game.start_game()
    await ctx.send(f"The game has started! {game.current_player.mention}, provide a word.")

@bot.command()
async def joinwordbomb(ctx):
    if game.game_started:
        await ctx.send("A game is already in progress. Please wait for the next game.")
        return

    if ctx.author in game.players:
        await ctx.send("You have already joined the game.")
        return

    game.add_player(ctx.author)
    await ctx.send(f"{ctx.author.mention} has joined the game.")

@bot.command()
async def word(ctx, word):
    if not game.game_started:
        await ctx.send("No game is currently in progress.")
        return

    if ctx.author != game.current_player:
        await ctx.send("It's not your turn.")
        return

    try:
        await asyncio.wait_for(process_word(ctx, word), timeout=10)
    except asyncio.TimeoutError:
        await ctx.send(f"{ctx.author.mention} took too long to respond. They have been eliminated.")
        game.eliminate_player()

    if len(game.players) == 1:
        await ctx.send(f"Game over! {game.players[0].mention} is the winner!")
        game.reset_game()
    elif not game.players:
        await ctx.send("Game over! All players have been eliminated.")
        game.reset_game()
    else:
        await ctx.send(f"It's {game.current_player.mention}'s turn.")

async def process_word(ctx, word):
    if not game.validate_word(word):
        await ctx.send("Invalid word.")
        game.eliminate_player()
        return

    game.last_word = word
    game.used_words.add(word)
    game.next_player()

@bot.command()
async def phelp(ctx):
    await ctx.send("Use !startwordbomb to start a new game. Use !joinwordbomb to join a game. Use !word <word> to play a word.")

bot.run('MTIzNjE5MDc0MjcyNTAwNTQwNA.GnfZ1Z.T2cZMY00yMxpMq7yW9X2zPoQqjiutR9CknB4Qw')
