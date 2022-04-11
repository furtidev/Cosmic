import os
import sys
import discord
from discord.ext import commands
import random
from utils import * # utilities.py implementation
#from keep_alive import keep_alive
from decouple import config, UndefinedValueError

intents = discord.Intents.default()
intents.members = True

try:
	tokens = {
		'discord': config('DISCORD_API_TOKEN', cast=str),
		'map_key': config('BING_MAP_API_KEY', cast=str)
	}
except UndefinedValueError:
	exit()

# system variables
prefix = '$'
description = "Get information about various space related stuff. Oh, and there are some non-space related stuff too."
accent = 0x352f2e
error_color = 0xFF5555
footers = ["Seems good to me."]

bot = commands.Bot(command_prefix=prefix, description=description, intents=intents, help_command=None)

# system functions

# credits: hitblast. (note: it works, so why bother making another system yourself? hehe)
def fetch_cog(cog_name):
	all_commands = str()
	cog = bot.get_cog(cog_name)
	for command in cog.get_commands():
		all_commands += f'`{command}`;'
	return all_commands

# Bot events
@bot.event
async def on_ready():
	await bot.change_presence(status=discord.Status.online, activity=discord.Game("$help"))
	print(f'Bot ID: {bot.user.id} \nBot Username: {bot.user}')

@bot.event
async def on_command_error(ctx, error):
	if isinstance(error, commands.CommandNotFound):
		embed = discord.Embed(title='Command Not Found!', color=error_color)

@bot.group(invoke_without_command=True)
async def help(ctx, command_name=None):
	# no arguments passed
	if not command_name:
		embed = discord.Embed(title='Help the lost man, TARS!', description=f"`{prefix}help all` to fetch all commands. Good stuff.", color=accent)
		embed.add_field(name='About Cosmic', value='Cosmic is an informational, space themed & space related Discord bot.')
		embed.set_author(name='Thanks for using Cosmic!', icon_url=ctx.author.avatar_url)
		await ctx.send(embed=embed)
	# 'all' passed as argument
	elif command_name.lower() == 'all':
		embed = discord.Embed(title='This is our menu, sir.', description=f"Use `{prefix}help <command_name>` to get more information about each command.", color=accent)
		embed.add_field(name='Core', value=fetch_cog('coreCommands'))
		embed.add_field(name='Space', value=fetch_cog('spaceCommands'))
		await ctx.send(embed=embed)
	# if something else is passed as argument
	else:
		for command in bot.commands:
			if str(command.name) == str(command_name.lower()):
				embed = (discord.Embed(title=f'Fetched Command: {command.name}', color=accent).add_field(name='Description', value=command.help, inline=False).add_field(name='Usage', value=f"`{prefix}{command.name} {command.signature}`", inline=False).set_author(name='C\'mon TARS!', icon_url=ctx.author.avatar_url))
				await ctx.send(embed=embed)

class coreCommands(commands.Cog):
	def __init__(self, ctx):
		self.bot = bot

	@commands.command(name='ping', help='Returns bot\'s latency and current status.', aliases=['latency', 'status'])
	async def ping(self, ctx):
		ping = round(bot.latency * 1000)
		embed = discord.Embed(title='Status :ringed_planet:', color=accent)
		embed.add_field(name=":sunny: API Latency", value=f"{ping}ms ")
		embed.set_footer(text=random.choice(footers))
		await ctx.send(embed=embed)


class spaceCommands(commands.Cog):
	def __init__(self, ctx):
		self.bot = bot

	@commands.command(name='locate_iss', help='Fetch Internation Space Station\'s current location')
	async def locate_iss(self, ctx):
		msg = await ctx.send("Tracking **ISS**..")
		json = use_rest_api('http://api.open-notify.org/iss-now.json')
		embed = discord.Embed(title="ISS's current location")
		embed.add_field(name='Latitude', value=f"{json['iss_position']['latitude']}", inline=False)
		embed.add_field(name='Longitude', value=f"{json['iss_position']['longitude']}", inline=False)
		embed.set_image(url=f"https://dev.virtualearth.net/REST/V1/Imagery/Map/Aerial/{json['iss_position']['latitude']}%2C{json['iss_position']['longitude']}/5?mapSize=600,300&format=png&key={tokens['map_key']}")
		await msg.edit(embed=embed)

	@commands.command(name='people_in_space', help='Fetch the number of people currently in space along with their name and space craft information if possible.')
	async def people_in_space(self, ctx):
		embed = discord.Embed(title="Tracking...", color=accent)
		msg = await ctx.send(embed=embed)
		json = use_rest_api('http://api.open-notify.org/astros.json')
		raw_data = json["people"]
		people_list = str()
		for index, item in enumerate(raw_data):
			people_list += f"{json['people'][index]['name']} (Spacecraft: **{json['people'][index]['craft']}**)\n"
		people_list = people_list.rstrip()
		embed = discord.Embed(title=f"There are currently {json['number']} people in space.", color=accent)
		embed.add_field(name="Here's the list:", value=people_list)
		await msg.edit(embed=embed)

extensions = []
if __name__ == '__main__':
	for extension in extensions:
		bot.load_extension(extension)

# adding the cogs
bot.add_cog(coreCommands(bot))
bot.add_cog(spaceCommands(bot))

#keep_alive()


bot.run(tokens['discord'])