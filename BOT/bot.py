# 404 not found bot. v3.0
# encoding: utf-8
# home/kindane/Desktop/404 Not Found
import discord
from discord.ext import commands

import json
import requests

import datetime
import random

from secondary import hex_to_int, random_color, permission_error, day_name

with open('config.json') as file:
	config = json.loads(file.read())

TOKEN = config['bot']['token']
PREFIX = config['bot']['prefix']
roles_for_reactions = dict()

client = commands.Bot(command_prefix=PREFIX, intents=discord.Intents.all())
client.remove_command('help')


# СОБЫТИЯ=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-

@client.event
async def on_command_error(ctx, error):
	if isinstance(error, commands.CommandNotFound):
		await ctx.send(embed=discord.Embed(description=f'{ctx.author.mention}, команда не найдена!', color=0xff0000))


# Готовность к запуску!
@client.event
async def on_ready():
	print('Бот начал свою работу в ' +
	      str(datetime.datetime.now().strftime(r'%d %B %Y / %H:%M:%S')))
	activity = discord.Activity(
		type=discord.ActivityType.playing,
		name='Персональный бот сервера 404 not found | {}help'.format(PREFIX))
	await client.change_presence(activity=activity)
	count = 0

	for guild in client.guilds:
		if guild.id == 535151585265713172:
			for member in guild.members:
				if not member.bot:
					count += 1

	channel = client.get_channel(config['not_found']['servers']['Участники'])
	name_count = int(channel.name.split(' ')[1])
	if name_count != count:
		await channel.edit(name='Участники {}'.format(count))


# Человек пришёл на сервер
@client.event
async def on_member_join(member):
	main = client.get_channel(config['not_found']['servers']['Новости'])
	rules = client.get_channel(config['not_found']['servers']['Правила'])
	communications = client.get_channel(config['not_found']['servers']['Общение'])
	roles = client.get_channel(config['not_found']['servers']['Роли'])
	greetings = client.get_channel(config['not_found']['servers']['Кукусики'])
	start_role = discord.utils.get(
		member.guild.roles, id=config['not_found']['roles']['Small Error'])

	description = f'''
	Приветик!
	**__Мы рады, что ты зашёл на наш сервер)__
	Чтобы понять, куда вам идти - воспользуйтесь этим меню:
	:heart:{main.mention}
	:heart:{rules.mention}
	:heart:{communications.mention}

	Чтобы изменить свои роли - воспользуйтесь
	:heart:{roles.mention} **
	'''
	embed = discord.Embed(
		title=':heart:404 NOT FOUND:heart:!',
		description=description,
		color=random_color())

	embed.set_image(url='https://i.gifer.com/RhbX.gif')
	embed.set_thumbnail(url=member.avatar_url)

	await member.add_roles(start_role)
	await greetings.send(member.mention, embed=embed)

	if not member.bot:
		channel = client.get_channel(config['not_found']['servers']['Участники'])
		count = int(channel.name.split(' ')[1])
		await channel.edit(name='Участники {}'.format(count + 1))


# Человек вышел с сервера
@client.event
async def on_member_remove(member):
	if not member.bot:
		channel = client.get_channel(config['not_found']['servers']['Участники'])
		count = int(channel.name.split(' ')[1])
		await channel.edit(name='Участники {}'.format(count - 1))


# Пользователь поставил реакцию
@client.event
async def on_raw_reaction_add(payload):
	member = payload.member
	if member == client.user:
		return None

	if payload.message_id in roles_for_reactions.keys():
		role = roles_for_reactions[payload.message_id][payload.emoji.name]
		await member.add_roles(role)
	else:
		return


# Пользователь убрал реакцию
@client.event
async def on_raw_reaction_remove(payload):
	guild = client.get_guild(payload.guild_id)
	member = guild.get_member(payload.user_id)

	if member == client.user:
		return

	if payload.message_id in roles_for_reactions.keys():
		role = roles_for_reactions[payload.message_id][payload.emoji.name]
		await member.remove_roles(role)


# Команды=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-

# Очистить кол-во сообщений в чате
@client.command()
@commands.has_permissions(administrator=True)
async def clear(ctx, amount: int):
	await ctx.channel.purge(limit=amount)


# Перевернуть строку
@client.command(name='reverse')
async def _reverse(ctx, *string):
	sentense = ' '.join(string)
	if len(sentense) == 0:
		await ctx.send('Вы должны сказать что я должен перевернуть:\n**{}reverse `<Предложение>`**'.format(PREFIX))
		return None
	await ctx.send(sentense[::-1])


# Подбрось монетку
@client.command()
async def flip(ctx):
	embed = discord.Embed(title='Орёл/Решка', color=random_color())
	embed.description = random.choice(['**Выпал орёл**', '**Выпала решка**'])
	embed.set_image(url='https://i.gifer.com/Ilp.gif')
	await ctx.send(embed=embed)


# Спроси ответ у шара!
@client.command()
async def ball(ctx, *question):
	question = ' '.join(question)
	if len(question) == 0:
		await ctx.send('Вы должны спросить у меня что-то:\n **{}ball `<Вопрос>`**'.format(PREFIX))
		return None
	answers = [
		'Да', 'Нет', 'Возможно', 'Спроси ещё раз', 'Точно нет', 'Точно да', 'Спроси позже',
		'Шансы хорошие', 'Непонятно', 'Неясно', 'Духи говорят нет', 'Думаю нет', 'Думаю да',
		'Не могу сказать', 'Без сомнений', 'Инфа сотка', 'Духи говорят да']
	answer = random.choice(answers)
	embed = discord.Embed(
		title='Магический шар:magic_wand:',
		description=f'{question}\n\n-**{answer}**',
		color=random_color())
	embed.set_image(url='https://i.gifer.com/7kHM.gif')
	await ctx.send(embed=embed)


# Жалоба
@client.command()
async def report(ctx, member: discord.Member, *reason: str):
	# do not delete message!
	channel = client.get_channel(config['not_found']['servers']['Репорт'])

	try:
		proof = ctx.message.attachments[0].proxy_url
	except Exception as e:
		await ctx.channel.send('Вы должны предоставить доказательства (см. {}help)'.format(PREFIX))
		print(e)
		return None

	reason = ' '.join(reason)
	if len(reason) == 0:
		await ctx.send(
			f'{member.mention}, вы должны указать причину репорта:\n {PREFIX}report `<Пользователь>` **`<Причина>`**')
		return

	if proof.endswith('.png'):
		proof_type = 'Фото'
	elif proof.endswith('.mp4'):
		proof_type = 'Видео'
	else:
		proof_type = 'Неизвестно'

	description = f'''
	Жалобу отправил: {ctx.message.author.mention}

	Нарушитель: {member.mention}

	ID нарушителя: {member.id}

	Причина: `{reason}`

	Пруфы: ({proof_type})\n{proof}

	'''

	embed = discord.Embed(
		title=f'Жалоба на {member}',
		description=description,
		color=random_color())

	embed.set_thumbnail(url=ctx.author.avatar_url)
	embed.set_image(url=proof)
	await channel.send(embed=embed)
	await ctx.send(f'{ctx.author.mention}, ваша жалоба была успешно отправлена, ожидайте ответа')


# Предложить идею
@client.command()
async def idea(ctx, *_idea: str):
	channel = client.get_channel(config['not_found']['servers']['Предложка'])
	author = ctx.author
	_idea = ' '.join(_idea)
	if len(_idea) == 0:
		await ctx.send('Вы должны предложить какую-то идею:\n **{}idea `<Ваша идея>`**'.format(PREFIX))
		return None
	embed = discord.Embed(title='Новая идея!', color=0x00ff00)
	description = f'''	
	Идея:\n`{_idea}`

	Автор идеи: {author.mention}
	'''
	embed.description = description
	embed.set_thumbnail(url=ctx.author.avatar_url)
	await ctx.message.delete()
	await channel.send(embed=embed)
	await ctx.send(f'{ctx.author.mention}, ваша идея была успешно отправлена, спасибо за ваше предложение')


# Пожаловаться на баг
@client.command()
async def bug(ctx, *_bug: str):
	channel = client.get_channel(config['not_found']['servers']['Баги'])
	author = ctx.author
	_bug = ' '.join(_bug)
	if len(_bug) == 0:
		await ctx.send('Вы должны описать в чём состоит баг:\n **{}bug `<Что не так>`**'.format(PREFIX))
		return None
	embed = discord.Embed(title='Найден баг!', color=0xff0000)
	description = f'''	
		Баг:\n`{_bug}`

		Нашёл: {author.mention}
		'''
	embed.description = description
	embed.set_thumbnail(url=ctx.author.avatar_url)
	await ctx.message.delete()
	await channel.send(embed=embed)
	await ctx.send(f'{ctx.author.mention}, ваша находка была успешно отправлена! Спасибо за помощь, будет исправлено')


# Отправить отзыв
@client.command()
async def feedback(ctx, *_feedback: str):
	channel = client.get_channel(config['not_found']['servers']['Отзывы'])
	author = ctx.author
	_feedback = ' '.join(_feedback)
	if len(_feedback) == 0:
		await ctx.send('Вы должны написать отзыв:\n **{}feedback `<Отзыв>`**'.format(PREFIX))
		return None
	embed = discord.Embed(title='Новый отзыв', color=random_color())
	description = f'''	
			Отзыв:\n`{_feedback}`

			Автор отзыва: {author.mention}
			'''
	embed.description = description
	embed.set_thumbnail(url=ctx.author.avatar_url)
	await ctx.message.delete()
	await channel.send(embed=embed)
	await ctx.send(f'{ctx.author.mention}, ваш отзыв был успешно отправлен! Спасибо за ваш отзыв)')


# Помощь при использовании
@client.command(name='help')
async def help_message(ctx):
	await ctx.message.delete()
	description_adm = '''
	**{p}reaction** `<id сообщения>` `<реакция>` `<роль>`
	При нажатии на реакцию пользователь даётся <роль>
	Использовать в том же чате, где и находится сообщение

	**{p}info** `<@Пользователь>`
	Узнать информацию о пользователе.

	**{p}clear** `<Количество>`
	очистить `<Количество>` сообщений в чате


	**{p}ban** `<@Пользователь>` `<Причина(можно не указывать)>`
	Выдать бан пользователю

	**{p}unban** `<Пользователь>`
	Разбанить пользователя. Для корректной работы пользователя отмечать не недо.
	пример: {p}unban UserName#0000
	(Чтобы так сделать, отметьте пользователя
	и перед ним поставьте спец-символ \" \\ \", после чего удалите @ и спец-символ.)

	**{p}kick** `<@Пользователь>` `<Причина(можно не указывать)>`
	Кикнуть пользователя

	**{p}mute** `<@Пользователь>` `<Причина(можно не указывать)>`
	Ограничить пользователю возможность отправлять сообщения
	и подключаться к голосовым каналам

	**{p}unmute** `<@Пользователь>`
	Дать пользователю возможность отправлять сообщения
	и подключаться к голосовым каналам
	'''.format(p=PREFIX)

	description = '''	
	**{p}report** `<@Пользователь>` `<Причина>`
	__Для подачи жалобы на пользователя нужно:__
	Отправить скриншот-доказательство и в поле "Добавить комментарий" написать эту команду

	**{p}feedback `<Отзыв>`**
	Отправить отзыв серверу
	
	**{p}bug `<Баг>`**
	Сообщить администрации о баге
	
	**{p}idea `<Идея>`**
	Предложить идею по развитию сервера
	
	**{p}flip**
	Подбрось монетку
	
	**{p}reverse** `<Предложение>`
	переворачивает заданное предложение
	
	**{p}ball `<Вопрос>`**
	Спроси у шара свою судьбу
	
	**{p}me**
	Выводит информацию о вас
	'''.format(p=PREFIX)

	embed = discord.Embed(title='Помощь Администрации',
	                      description=description_adm, color=0x0066CC)
	await ctx.send(embed=embed)
	embed2 = discord.Embed(title='Помощь обычным пользователям',
	                       description=description, color=0x0066CC)
	await ctx.send(embed=embed2)


#  Узнать информацию о пользователе
@client.command()
@commands.has_permissions(administrator=True)
async def info(ctx, member: discord.Member):
	await ctx.message.delete()
	roles = list()
	for role in member.roles:
		if role.name != '@everyone':
			roles.append(role.mention)
	roles = '\n'.join(roles[::-1])

	now = datetime.datetime.now()
	difference = now - member.joined_at  # timedelta

	description = f'''
	Имя: {member.name}

	ID: {member.id}

	Роли:\n{roles}

	Самая высокая роль: {member.top_role.mention}

	Уже на сервере: {day_name(difference.days)}

	Время присоединения: {member.joined_at.strftime(r'%d %B %Y / %H:%M:%S')}

	Время создания аккаунта: {member.created_at.strftime(r'%d %B %Y / %H:%M:%S')}
	'''

	embed = discord.Embed(
		title=member.nick, description=description, color=0xCC0052)
	embed.set_thumbnail(url=member.avatar_url)

	await ctx.send(embed=embed)


# Показывает информацию о себе
@client.command()
async def me(ctx):
	member = ctx.author
	await ctx.message.delete()
	roles = list()
	for role in member.roles:
		if role.name != '@everyone':
			roles.append(role.mention)
	roles = '\n'.join(roles[::-1])

	now = datetime.datetime.now()
	difference = now - member.joined_at  # timedelta

	description = f'''
	Имя: {member.name}

	ID: {member.id}

	Роли:\n{roles}

	Самая высокая роль: {member.top_role.mention}

	Уже на сервере: {day_name(difference.days)}

	Время присоединения: {member.joined_at.strftime(r'%d %B %Y / %H:%M:%S')}

	Время создания аккаунта: {member.created_at.strftime(r'%d %B %Y / %H:%M:%S')}
	'''

	embed = discord.Embed(
		title=member.nick, description=description, color=0xCC0052)
	embed.set_thumbnail(url=member.avatar_url)

	await ctx.send(embed=embed)


@client.command()
@commands.has_permissions(administrator=True)
async def reaction(ctx, message_id: int, react, role: discord.Role):
	"""
	Добавляет реакцию на сообщение, при нажатии
	которого пользователю даётся role.
	При удалении реакции пользователем у него
	убирается role
	"""
	message = await ctx.channel.fetch_message(message_id)
	try:
		await message.add_reaction(react)
		if message_id not in roles_for_reactions.keys():
			roles_for_reactions[message_id] = {react: role}
		else:
			roles_for_reactions[message_id].update({react: role})
		await ctx.message.delete()
	except Exception as e:
		await ctx.send(f'ERROR! {e}')
		return


# Забанить
@client.command()
@commands.has_permissions(administrator=True)
async def ban(ctx, member: discord.Member, *, reason='Не указано'):
	await ctx.message.delete()

	emb = discord.Embed(title='БАН!', color=0xff0000)
	emb.description = f'Пользователь {member.mention} был забанен администратором {ctx.author.mention}\nПричина: {reason}'
	emb.set_thumbnail(url=member.avatar_url)

	await member.ban(reason=reason)
	await ctx.send(embed=emb)


# Разбанить
@client.command()
@commands.has_permissions(administrator=True)
async def unban(ctx, *, user):
	"""
	Для Нормальной работы в функцию нужно передавать:
	user_name#discr
	Для его получения нужно:
	mention пользователя, потом экранировать это
	и удалить собачку в имени
	"""
	await ctx.message.delete()
	banned_user = None
	banned_users = await ctx.guild.bans()
	for ban_entry in banned_users:
		banned_user = ban_entry.user
		if str(banned_user) == user:
			await ctx.guild.unban(banned_user)
			break
	if banned_user is not None:
		embed = discord.Embed(title=f'Разбанен {banned_user.name}', color=0x00ff00)
		embed.description = f"Пользователь {banned_user.mention} был успешно разбанен администратором {ctx.author.mention}"
		embed.set_thumbnail(url=banned_user.avatar_url)
		await ctx.send(embed=embed)


# Кикнуть
@client.command()
@commands.has_permissions(administrator=True)
async def kick(ctx, member: discord.Member, *, reason='Не указано'):
	await ctx.message.delete()
	await member.kick(reason=reason)
	embed = discord.Embed(title='Кик', color=0xffff00)
	embed.description = f'''
	Пользователь {member.mention} Был кикнул администратором {ctx.message.author.mention}
	
	Причина: {reason}
	'''
	embed.set_thumbnail(url=member.avatar_url)
	await ctx.send(embed=embed)


# Замутить
@client.command()
@commands.has_permissions(administrator=True)
async def mute(ctx, member: discord.Member, *, reason='Не указано'):
	await ctx.message.delete()
	role = discord.utils.get(ctx.channel.guild.roles,
	                         id=config['not_found']['roles']['Muted'])
	await member.add_roles(role)
	embed = discord.Embed(title='Мут', color=0x000000)
	embed.description = f'''
	Администратор {ctx.author.mention} выдал мут пользователю {member.mention}

	Причина: {reason}
	'''
	embed.set_thumbnail(url=member.avatar_url)
	await ctx.send(embed=embed)


# Размутить
@client.command()
@commands.has_permissions(administrator=True)
async def unmute(ctx, member: discord.Member):
	await ctx.message.delete()
	role = discord.utils.get(ctx.channel.guild.roles,
	                         id=config['not_found']['roles']['Muted'])
	await member.remove_roles(role)
	embed = discord.Embed(title='Мут', color=0x00ff00)
	embed.description = f'''Администратор {ctx.author.mention} забрал мут у пользователя {member.mention}'''
	embed.set_thumbnail(url=member.avatar_url)
	await ctx.send(embed=embed)


# Отправить сообщение в чат с помощью JSONa
@client.command()
@commands.has_permissions(administrator=True)
async def send(ctx):
	"""
{
	"channel id": 765240357154717696,
	"text": "Тестовое сообщение by Kindane",
	"embed": {
		"title": null,
		"author":
			{
			"name":"",
			"url":"",
			"icon_url":""
			},

		"url": null,
		"description": null,
		"color": "#00ff00",
		"image": "",
		"thumbnail": ""
	}
}
	"""
	data = requests.get(ctx.message.attachments[0].url).json()
	await ctx.message.delete()
	try:
		channel = discord.utils.get(
			ctx.channel.guild.text_channels, id=data['channel id'])
		text = data['text']
		if data['embed'] is None:
			await channel.send(text)
			return None
		embed = discord.Embed(
			title=data['embed']['title'],
			description=data['embed']['description'],
			color=hex_to_int(data['embed']['color']),
			url=data['embed']['url'],
			author=data['embed']['author'])

		embed.set_image(url=data['embed']['image'])
		embed.set_thumbnail(url=data['embed']['thumbnail'])
		embed.set_author(
			name=data['embed']['author']['name'],
			icon_url=data['embed']['author']['icon_url'],
			url=data['embed']['author']['url'])

		await channel.send(text, embed=embed)
	except Exception as e:
		await ctx.send('ERROR!\n`{}`'.format(e))


# Обоработка ошибок=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-


# Обработчик ошибок команды clear
@clear.error
async def clear_error(ctx, error):
	if isinstance(error, commands.MissingRequiredArgument):
		await ctx.send(
			embed=discord.Embed(
				description=f'{ctx.author.mention}, вы должны ввести целое число!',
				color=0xff0000))
	elif isinstance(error, commands.MissingPermissions):
		await ctx.send(embed=permission_error(ctx))


# Обработчик ошибок команды reaction
@reaction.error
async def reaction_error(ctx, error):
	embed = discord.Embed(title='Ошибка', color=0xff0000)
	if isinstance(error, commands.MissingPermissions):
		embed.description = f'{ctx.author.mention}, у вас недостаточно прав для использования данной команды!'

	elif isinstance(error, commands.BotMissingPermissions):
		embed.description = 'Бот не может выдовать роли, которые выше него по значению'

	elif isinstance(error, commands.MissingRequiredArgument):
		embed.description = 'Вы должны указать все параметры! (см. {}help)'.format(
			PREFIX)

	elif isinstance(error, commands.BadArgument):
		embed.description = 'Вы указали неправильный аргумент! (см. {}help)'.format(
			PREFIX)

	else:
		embed.description = error

	await ctx.send(embed=embed)


# Обработчик ошибок команды ban
@ban.error
async def ban_error(ctx, error):
	if isinstance(error, commands.MissingPermissions):
		await ctx.send(embed=permission_error(ctx))
	elif isinstance(error, commands.MissingRequiredArgument):
		await ctx.send(embed=discord.Embed(
			title='Ошибка!',
			color=0xff0000,
			description='Вы должны указать кого вы хотите забанить'))


# Обработчик ошибок команды unban
@unban.error
async def unban_error(ctx, error):
	if isinstance(error, commands.MissingPermissions):
		await ctx.send(embed=permission_error(ctx))
	elif isinstance(error, commands.MissingRequiredArgument):
		await ctx.send(embed=discord.Embed(
			title='Ошибка!',
			color=0xff0000,
			description='Вы должны указать кого вы хотите разбанить'))


# Обработчик ошибок команды kick
@kick.error
async def kick_error(ctx, error):
	if isinstance(error, commands.MissingPermissions):
		await ctx.send(embed=permission_error(ctx))
	elif isinstance(error, commands.MissingRequiredArgument):
		await ctx.send(embed=discord.Embed(
			title='Ошибка!',
			color=0xff0000,
			description='Вы должны указать кого вы хотите кикнуть'))


# Обработчик ошибок команды mute
@mute.error
async def mute_error(ctx, error):
	if isinstance(error, commands.MissingPermissions):
		await ctx.send(embed=permission_error(ctx))
	elif isinstance(error, commands.MissingRequiredArgument):
		await ctx.send(embed=discord.Embed(
			title='Ошибка!',
			color=0xff0000,
			description='Вы должны указать кого вы хотите замутить'))


# Обработчик ошибок команды unmute
@unmute.error
async def unmute_error(ctx, error):
	if isinstance(error, commands.MissingPermissions):
		await ctx.send(embed=permission_error(ctx))
	elif isinstance(error, commands.MissingRequiredArgument):
		await ctx.send(embed=discord.Embed(
			title='Ошибка!',
			color=0xff0000,
			description='Вы должны указать кого вы хотите размутить'))


# Обработчик ошибок команды report
@report.error
async def report_error(ctx, error):
	if isinstance(error, commands.MissingRequiredArgument):
		await ctx.send(embed=discord.Embed(
			title='Ошибка!',
			color=0xff0000,
			description=f'Вы должны указать все аргументы! (см.{PREFIX}help)'))


client.run(TOKEN)
