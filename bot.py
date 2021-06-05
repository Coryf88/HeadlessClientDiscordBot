import logging, discord, discord.ext.commands, datetime, pytz, os, discord_slash, armaServer

def tdFormat(td_object):
	seconds = int(td_object.total_seconds())

	if seconds == 0:
		return 'Now'

	negative = seconds < 0
	if negative:
		seconds = abs(seconds)

	parts = []
	for periodName, periodSeconds in [('year', 31536000), ('month', 2592000), ('day', 86400), ('hour', 3600), ('minute', 60), ('second', 1)]:
		if seconds >= periodSeconds:
			periodValue, seconds = divmod(seconds, periodSeconds)
			parts.append(f'{periodValue} {periodName}{"s" if periodValue > 1 else ""}')

	if len(parts) > 1:
		parts[-1] = 'and ' + parts[-1]

	return ', '.join(parts) + (' ago' if negative else '')

def timeUntilHour(tzname, hour, *days):
	tz = pytz.timezone(tzname)
	now = datetime.datetime.now(tz)
	dateNow = now.date()
	nextDatetime = sorted([tz.localize(datetime.datetime.combine(dateNow + datetime.timedelta((day - dateNow.weekday()) % 7), datetime.time(hour))) for day in sorted(days)])[0]
	return tdFormat(nextDatetime - now)

def main():
	# 'guildA,guildB'
	guilds = [int(l) for l in os.getenv('DISCORD_GUILDS').split(',')]
	# 'guildA:guildARoleA;guildB:guildBRoleA,guildBRoleB'
	serverControlPermissions = {int(l.split(':', 1)[0]): discord_slash.utils.manage_commands.create_multi_ids_permission([int(l) for l in l.split(':', 1)[1].split(',')], discord_slash.model.SlashCommandPermissionType.ROLE, True) for l in os.getenv('DISCORD_SERVER_CONTROLLERS').split(';')} if os.getenv('DISCORD_SERVER_CONTROLLERS') else {}

	bot = discord.ext.commands.Bot(command_prefix='%', intents=discord.Intents.default())
	slash = discord_slash.SlashCommand(bot, sync_commands=True)

	server = armaServer.ArmaServer()

	@bot.event
	async def on_ready():
		await bot.change_presence(activity=discord.Game(name='Arma 3'))

	@slash.slash(guild_ids=guilds)
	async def preops(ctx):
		"""Time until Pre-OPs."""
		await ctx.send(timeUntilHour('Europe/London', 18, 1, 5))

	@slash.slash(guild_ids=guilds)
	async def ops(ctx):
		"""Time until OPs."""
		await ctx.send(timeUntilHour('Europe/London', 19, 1, 5))

	@slash.slash(guild_ids=guilds)
	async def spreops(ctx):
		"""Time until Special Pre-OPs."""
		await ctx.send(timeUntilHour('Europe/London', 18, 6))

	@slash.slash(guild_ids=guilds)
	async def sops(ctx):
		"""Time until Special OPs."""
		await ctx.send(timeUntilHour('Europe/London', 19, 6))

	@slash.slash(guild_ids=guilds)
	async def bpreops(ctx):
		"""Time until Burger Pre-OPs."""
		await ctx.send(timeUntilHour('America/New_York', 19, 3))

	@slash.slash(guild_ids=guilds)
	async def bops(ctx):
		"""Time until Burger OPs."""
		await ctx.send(timeUntilHour('America/New_York', 20, 3))

	@slash.slash(guild_ids=guilds)
	async def cas(ctx):
		"""Close Air Support Briefing Form (9-Line)."""
		await ctx.send('''**Close Air Support Briefing Form (9-Line)**
1. IP/BP: "\_\_\_\_"
2. Heading: "\_\_\_\_" Offset: "\_\_\_\_(left/right)"
3. Distance: "\_\_\_\_"
4. Target elevation: "\_\_\_\_"
5. Target description: "\_\_\_\_"
6. Target location: "\_\_\_\_"
7. Type mark: "\_\_\_\_" Code: "\_\_\_\_" Laser to target line: "\_\_\_\_ degrees"
8. Location of friendlies: "\_\_\_\_" Position marked by: "\_\_\_\_"
9. Egress: "\_\_\_\_" Remarks (As appropriate): "\_\_\_\_"''')

	@slash.slash(guild_ids=guilds, default_permission=False, permissions=serverControlPermissions)
	async def status(ctx):
		"""Arma 3 Server Status."""
		await ctx.defer()
		await ctx.send(server.status())

	@slash.slash(guild_ids=guilds, default_permission=False, permissions=serverControlPermissions)
	async def start(ctx):
		"""Start Arma 3 Server."""
		await ctx.defer()
		await ctx.send(server.start())

	@slash.slash(guild_ids=guilds, default_permission=False, permissions=serverControlPermissions)
	async def stop(ctx):
		"""Stop Arma 3 Server."""
		await ctx.defer()
		await ctx.send(server.stop())

	@slash.slash(guild_ids=guilds, default_permission=False, permissions=serverControlPermissions)
	async def restart(ctx):
		"""Restart Arma 3 Server."""
		await ctx.defer()
		await ctx.send(server.restart())

	@slash.slash(guild_ids=guilds, default_permission=False, permissions=serverControlPermissions, options=[
		discord_slash.utils.manage_commands.create_option(name="preset",
			description="The preset to change to.",
			option_type=discord_slash.model.SlashCommandOptionType.STRING,
			required=True,
			choices=[
				discord_slash.utils.manage_commands.create_choice(name='Normal', value=''),
				discord_slash.utils.manage_commands.create_choice(name='World War 2', value='ww2'),
				#discord_slash.utils.manage_commands.create_choice(name='Vietnam', value='vietnam'),
				discord_slash.utils.manage_commands.create_choice(name='S.O.G. Prairie Fire', value='sog'),
				discord_slash.utils.manage_commands.create_choice(name='Joint Op', value='jop')
			]
		)
	])
	async def preset(ctx, preset: str):
		"""Change Arma 3 Server Preset."""
		await ctx.defer()
		await ctx.send(server.preset(preset))

	bot.run(os.getenv('DISCORD_TOKEN'))

if __name__ == '__main__':
	logging.basicConfig(filename='bot.log', filemode='w', encoding='utf-8', level=logging.INFO)

	try:
		main()
	except:
		logging.exception('Exception')
