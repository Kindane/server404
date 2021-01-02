import discord
import random


def random_color():
	return random.randint(0x000000, 0xffffff)


def hex_to_int(string):
	if string is None:
		return None
	string = string.replace('#', '')
	return eval(f"0x{string}")


def permission_error(ctx):
	embed = discord.Embed(title='Ошибка!', color=0xff0000)
	embed.description = f'{ctx.author.mention}, у вас недостаточно прав для использования этой команды!'
	return embed


def day_name(day):
	day = str(day)
	if day.endswith('11') or day.endswith('12') or day.endswith('13') or day.endswith('14'):
		return f'{day} дней'
	elif day.endswith('1'):
		return f'{day} день'
	elif day.endswith('2') or day.endswith('3') or day.endswith('4'):
		return f'{day} дня'
	else:
		return f'{day} дней'
