import logging, discord, discord.ext.commands, datetime, pytz, os, discord_slash

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

def timeUntilHour(hour):
	tz = pytz.timezone('Europe/London')
	now = datetime.datetime.now(tz)
	timeOps = datetime.time(hour)
	dateNow = now.date()
	tuesdayOps = tz.localize(datetime.datetime.combine(dateNow + datetime.timedelta((1 - dateNow.weekday()) % 7), timeOps))
	saturdayOps = tz.localize(datetime.datetime.combine(dateNow + datetime.timedelta((5 - dateNow.weekday()) % 7), timeOps))

	return tdFormat((tuesdayOps if tuesdayOps < saturdayOps else saturdayOps) - now)

def main():
	# 'guildA,guildB'
	guilds = [int(l) for l in os.getenv('DISCORD_GUILDS').split(',')]

	bot = discord.ext.commands.Bot(command_prefix='%', intents=discord.Intents.default())
	slash = discord_slash.SlashCommand(bot, sync_commands=True)

	@bot.event
	async def on_ready():
		await bot.change_presence(activity=discord.Game(name='Arma 3'))

	@bot.command()
	async def preops(ctx):
		"""Time until Pre-OPs."""
		await ctx.send(timeUntilHour(18))

	@slash.slash(name="preops", guild_ids=guilds)
	async def _preops(ctx):
		"""Time until Pre-OPs."""
		await preops(ctx)

	@bot.command()
	async def ops(ctx):
		"""Time until OPs."""
		await ctx.send(timeUntilHour(19))

	@slash.slash(name="ops", guild_ids=guilds)
	async def _ops(ctx):
		"""Time until OPs."""
		await ops(ctx)

	bot.run(os.getenv('DISCORD_TOKEN'))

if __name__ == '__main__':
	logging.basicConfig(filename='bot.log', filemode='w', encoding='utf-8', level=logging.INFO)

	try:
		main()
	except:
		logging.exception('Exception')
