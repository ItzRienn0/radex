#!/usr/bin/env python
# -*- coding: utf-8 -*- 


import discord
from discord.ext import commands, tasks
from config import settings, database
from discord.ext.commands import has_permissions, CheckFailure, BotMissingPermissions
from discord import utils
# - Дискорд
import requests, json
import random
import time
import asyncio
import pymysql
import nacl
from PIL import Image, ImageFont, ImageDraw
from discord_components import *
import io, os
# ~~~~~~~~~~~~~

bot = commands.Bot(command_prefix = settings['prefix'], intents = discord.Intents.all())
bot.remove_command("help")
#LevelingManager = discordSuperUtils.LevelingManager(bot, award_role=True)

try:
	con = pymysql.connect(**database,cursorclass=pymysql.cursors.DictCursor)
	print("< * > Connect to BD < * >")
except Exception as ex:
	print(ex)
		
@bot.event 
async def on_ready():
	await bot.change_presence(activity=discord.Game(name=f"=help | Работает на {len(bot.guilds)} серверах"))
	DiscordComponents(bot)
	print("\n< * > Bot Connected < * >\n\n")

	con.ping() 
	with con.cursor() as cur:
		for guild in bot.guilds:
			try:
				cur.execute(f"SELECT id FROM servers where id={guild.id}")
				if cur.fetchone() == None:
					cur.execute(f"INSERT INTO servers (id, name) VALUES ( {guild.id} , '{guild.name}' )")
				else:
					pass
				con.commit()
			except: pass

@bot.event
async def on_guild_join(guild):
	await bot.change_presence(activity=discord.Game(name=f"=help | Работает на {len(bot.guilds)} серверах"))
	rienno = bot.get_user(456790342512148481)	
	chan = guild.system_channel
	
	p=discord.Embed(title=f"👋 | Я теперь на сервере {guild.name}", description=f"**{guild.owner.mention}, спасибо что добавили меня на ваш сервер\n\nhttps://discord.gg/SjHQMeNPFK - мой основной сервер, там можно получить всю поддержку и не только\n\nПожалуйста проголосуйте за меня: [Нажми](https://radexbot.xyz/vote)\n\n`=help` - список моих команд\n\n❗️❗️❗️ Перед использованием бота настройке конфиг - `=config`**", color=0xbf1cd4)
	p.set_author(name=guild.name, url="https://discord.gg/Uqp32EwByH", icon_url=guild.owner.avatar_url)
	p.set_thumbnail(url=guild.icon_url)
	p.set_footer(text=f"• По вопросам -> Rienn0#4187")

	try:
		await ctx.send(embed=p, components = [Button(style = ButtonStyle.URL, url="https://discord.gg/Uqp32EwByH", label = '⚙️ | Основной сервер')])
	except: pass
		
	await rienno.send(f"{guild.name} добавили к себе бота\nID: {guild.id}")
	con.ping() 
	with con.cursor() as cur:
		cur.execute(f"SELECT id FROM servers where id={guild.id}")
		if cur.fetchone() == None:
			cur.execute(f"INSERT INTO servers (id, name) VALUES ( {guild.id},'{guild.name}' )")
			print(f"{guild.name} добавлен в БД".encode('utf-8'))

		else: pass
		con.commit()

@bot.event
async def on_guild_remove(guild):
	await bot.change_presence(activity=discord.Game(name=f"=help | Работает на {len(bot.guilds)} серверах"))
	rienno = bot.get_user(456790342512148481)
	await rienno.send(f"{guild.name} кикнули бота\nID: {guild.id}")
	con.ping() 
	with con.cursor() as cur:
		try:
			cur.execute(f"SELECT id FROM servers WHERE id={guild.id}")
			cur.execute(f"DELETE FROM servers WHERE id={guild.id}")
			print(f"{guild.name} удален из БД ".encode('utf-8'))
			con.commit()
		except Exception as e:
			print(e)
			pass

@bot.event
async def on_member_remove(member):
	con.ping()
	with con.cursor() as cur:
		try:
			cur.execute(f"SELECT * FROM serverstats_humans WHERE serverid={member.guild.id}")
			fho = cur.fetchone()
			chan_hum = bot.get_channel(fho["channel_id"])
			await chan_hum.edit(name=f"👤 ▸ Люди: {sum(not member.bot for member in member.guild.members)}")
	
			cur.execute(f"SELECT * FROM serverstats_bots WHERE serverid={member.guild.id}")
			fho = cur.fetchone()
			chan_bots = bot.get_channel(fho["channel_id"])
			await chan_bots.edit(name=f"🤖 ▸ Боты: {sum(member.bot for member in member.guild.members)}")

			cur.execute(f"SELECT * FROM serverstats_all WHERE serverid={member.guild.id}")
			fho = cur.fetchone()
			chan_all = bot.get_channel(fho["channel_id"])
			await chan_all.edit(name=f"👥 ▸ Всего: {member.guild.member_count}")
		except:
			pass
	
@bot.event
async def on_member_join(member):
	con.ping() 
	with con.cursor() as cur:
		try:
			cur.execute(f"SELECT gr_chan_id,gr_role_id,gr_choice,gr_text FROM greetings WHERE serverid={member.guild.id}")
			
			fho = cur.fetchone()
			
			channel = bot.get_channel(fho["gr_chan_id"])
			role = discord.utils.get(member.guild.roles, id=fho["gr_role_id"])
			choice = fho["gr_choice"]
			grtext = fho["gr_text"]

			await member.add_roles(role)
			await asyncio.sleep(0.5)
			if choice == "text":
				await channel.send(f"{member.mention}, \n{grtext}")

			if choice == "embed":
				emd = discord.Embed(title="👋 | Новый Участник", description=f"{member.mention},\n{grtext}", color=0xbf1cd4)
				emd.set_author(name=member.guild.name, url="https://discord.gg/Uqp32EwByH", icon_url=member.guild.icon_url)
				emd.set_thumbnail(url=member.avatar_url)
				await channel.send(embed=emd)
		except Exception as e:
			print(e)
			pass

	con.ping() 
	with con.cursor() as cur:
		try:
			cur.execute(f"SELECT * FROM serverstats_bots WHERE serverid={member.guild.id}")
			fho = cur.fetchone()
			chan_hum = bot.get_channel(fho["channel_id"])
			await chan_hum.edit(name=f"🤖 ▸ Боты: {sum(member.bot for member in member.guild.members)}")

			cur.execute(f"SELECT * FROM serverstats_all WHERE serverid={member.guild.id}")
			fho = cur.fetchone()
			chan_bots = bot.get_channel(fho["channel_id"])
			await chan_bots.edit(name=f"👥 ▸ Всего: {member.guild.member_count}")
				
			cur.execute(f"SELECT * FROM serverstats_humans WHERE serverid={member.guild.id}")
			fho = cur.fetchone()
			chan_all = bot.get_channel(fho["channel_id"])
			await chan_all.edit(name=f"👤 ▸ Люди: {sum(not member.bot for member in member.guild.members)}")
		except: pass

@bot.event
async def on_message_delete(message):
	con.ping() 
	with con.cursor() as cur:
		try:
			cur.execute(f"SELECT channel_id FROM logs_channels WHERE serverid={message.guild.id}")
			l_chan = cur.fetchone()["channel_id"]
			logs = bot.get_channel(l_chan)
		except Exception as e:
			pass

	dell=discord.Embed(title=f"🧹 | Удалено сообщение в канале `{message.channel}`",color=0xc10dd9, timestamp = message.created_at)
	dell.set_author(name=message.guild.name, url="https://discord.gg/Uqp32EwByH", icon_url=message.author.avatar_url)
	dell.add_field(name="Текст сообщения: ", value=f"**{message.content}**", inline=True)
	dell.add_field(name="Автор: ", value=f"{message.author.mention}")
	dell.set_thumbnail(url=message.guild.icon_url)
	dell.set_footer(text='• По вопросам -> Rienn0#4187')

	try:
		await logs.send(embed=dell)
	except: pass

@bot.command()
async def help(ctx, arg=None):
	
	if arg == None:

		#gifs = random.choice(["https://cdn.discordapp.com/attachments/936701693146566737/937298438557675550/image_86110315173035913590.gif","https://c.tenor.com/PHYpwqB3dkcAAAAC/city-rp.gif","https://c.tenor.com/105SSzB_tNEAAAAC/anime.gif","https://c.tenor.com/g3TAB8h_QgwAAAAC/good-anime.gif"])

		helpp=discord.Embed(title="🛠 | Помощь по командам (=help)", color=0xbf1cd4, timestamp = ctx.message.created_at)
		helpp.add_field(name="🌟 | Говорящий Бэн | 🌟",value="**`=help ben`**",inline=True)
		helpp.add_field(name="Информация",value="**`=help info`**",inline=True)
		helpp.add_field(name="Модерация",value="**`=help mod`**",inline=True)
		helpp.add_field(name="NSFW",value="**`=help nsfw`**",inline=True)
		helpp.add_field(name="Ролеплей",value="**`=help roleplay`**",inline=True)
		helpp.add_field(name="Свадьбы",value="**`=help marry`**",inline=True)
		helpp.add_field(name="Профиль (=about)",value="**`=help profile`**",inline=True)
		helpp.add_field(name="Развлечения",value="**`=help fun`**",inline=True)
		helpp.add_field(name="Статистика сервера",value="**`=help serverstats`**",inline=True)
		helpp.add_field(name="Другое",value="**`=help other`**",inline=True)
		helpp.add_field(name="Конфиг",value="**`=config`**")
		helpp.set_author(name=ctx.guild.name, url="https://discord.gg/Uqp32EwByH", icon_url=ctx.author.avatar_url)
		helpp.set_thumbnail(url=ctx.guild.icon_url)
		helpp.set_footer(text=f"• Запросил: {ctx.author}")	
		
		await ctx.reply(embed=helpp, components = [Button(style = ButtonStyle.URL, url="https://discord.gg/Uqp32EwByH", label = '⚙️ | Основной сервер')])
		await ctx.message.add_reaction("👍")

	if arg == "info":

		helpp=discord.Embed(title="🛠 | Помощь по командам информации", color=0xbf1cd4, timestamp = ctx.message.created_at)
		helpp.add_field(name="О Участнике",value="**`=about`**",inline=True)
		helpp.add_field(name="О сервере",value="**`=server`**",inline=True)
		helpp.add_field(name="О боте",value="**`=radex`**",inline=True)
		helpp.add_field(name="Аватар участника",value="**`=avatar`**",inline=True)
		helpp.add_field(name="Аватар сервера",value="**`=server_avatar`**",inline=True)
		helpp.set_author(name=ctx.guild.name, url="https://discord.gg/Uqp32EwByH", icon_url=ctx.author.avatar_url)
		helpp.set_thumbnail(url=ctx.guild.icon_url)
		helpp.set_image(url="https://c.tenor.com/J9aS-PlVHmEAAAAC/information-anime.gif")
		helpp.set_footer(text=f"• Запросил: {ctx.author}")		

		msg = await ctx.reply(embed=helpp, mention_author=True)
		await ctx.message.add_reaction("👍")
		await asyncio.sleep(90)
		await msg.delete()

	if arg == "profile":
		
		helpp=discord.Embed(title="🛠 | Помощь по командам настройки профиля ( =about )", color=0xbf1cd4, timestamp = ctx.message.created_at)
		helpp.add_field(name="О себе",value="**`=setbio`**",inline=True)
		helpp.add_field(name="Картинка/гифка в профиль",value="**`=setimg`**",inline=True)
		helpp.set_author(name=ctx.guild.name, url="https://discord.gg/Uqp32EwByH", icon_url=ctx.author.avatar_url)
		helpp.set_thumbnail(url=ctx.guild.icon_url)
		helpp.set_image(url="https://c.tenor.com/efZEOzGIvZMAAAAC/aesthetic-anime.gif")
		helpp.set_footer(text=f"• Запросил: {ctx.author}")		

		msg = await ctx.reply(embed=helpp, mention_author=True)
		await ctx.message.add_reaction("👍")
		await asyncio.sleep(90)
		await msg.delete()

	if arg == "mod":
		
		helpp=discord.Embed(title="🛠 | Помощь по командам модерации", color=0xbf1cd4, timestamp = ctx.message.created_at)
		helpp.add_field(name="Замутить участника",value="**`=mute`**",inline=True)
		helpp.add_field(name="Размутить участника",value="**`=unmute`**",inline=True)
		helpp.add_field(name="Мут-лист",value="**`=mutelist`**",inline=True)
		helpp.add_field(name="Забанить участника",value="**`=ban`**",inline=True)
		helpp.add_field(name="Разбанить участника",value="**`=unban`**",inline=True)
		helpp.add_field(name="Бан-лист",value="**`=banlist`**",inline=True)
		helpp.add_field(name="Очистить чат",value="**`=clear`**",inline=True)
		helpp.set_author(name=ctx.guild.name, url="https://discord.gg/Uqp32EwByH", icon_url=ctx.author.avatar_url)
		helpp.set_thumbnail(url=ctx.guild.icon_url)
		helpp.set_image(url="https://c.tenor.com/xjbj2B8qt54AAAAC/oh-no-no.gif")
		helpp.set_footer(text=f"• Запросил: {ctx.author}")		

		msg = await ctx.reply(embed=helpp, mention_author=True)
		await ctx.message.add_reaction("👍")
		await asyncio.sleep(90)
		await msg.delete()

	if arg == "nsfw":
		
		helpp=discord.Embed(title="🛠 | Помощь по NSFW командам", color=0xbf1cd4, timestamp = ctx.message.created_at)
		helpp.add_field(name="Бубсы",value="**`=boobs`**",inline=True)
		helpp.add_field(name="Асс",value="**`=ass`**",inline=True)
		helpp.add_field(name="NSFW-пикча",value="**`=nsfw`**",inline=True)
		helpp.add_field(name="Аниме/Хентай",value="**`=anime`**",inline=True)
		helpp.set_author(name=ctx.guild.name, url="https://discord.gg/Uqp32EwByH", icon_url=ctx.author.avatar_url)
		helpp.set_thumbnail(url=ctx.guild.icon_url)
		helpp.set_image(url="https://c.tenor.com/C1Iny14iXjoAAAAd/life-sad.gif")
		helpp.set_footer(text=f"• Запросил: {ctx.author}")		

		msg = await ctx.reply(embed=helpp, mention_author=True)
		await ctx.message.add_reaction("👍")
		await asyncio.sleep(90)
		await msg.delete()

	if arg == "roleplay":
		
		helpp=discord.Embed(title="🛠 | Помощь по Ролеплей командам", color=0xbf1cd4, timestamp = ctx.message.created_at)		
		helpp.add_field(name="Поцеловать",value="**`=kiss`**",inline=True)
		helpp.add_field(name="Ударить",value="**`=fight`**",inline=True)
		helpp.add_field(name="Дать пощечину",value="**`=slap`**",inline=True)
		helpp.add_field(name="Интим",value="**`=sex`**",inline=True)
		helpp.add_field(name="Обнять",value="**`=hug`**",inline=True)
		helpp.add_field(name="Убить",value="**`=kill`**",inline=True)
		helpp.set_image(url="https://c.tenor.com/2yyi0BLAa1MAAAAd/welcome-hope.gif")
		helpp.set_author(name=ctx.guild.name, url="https://discord.gg/Uqp32EwByH", icon_url=ctx.author.avatar_url)
		helpp.set_footer(text=f"• Запросил: {ctx.author}")

		msg = await ctx.reply(embed=helpp, mention_author=True)
		await ctx.message.add_reaction("👍")
		await asyncio.sleep(90)
		await msg.delete()

	if arg == "fun":
		
		helpp=discord.Embed(title="🛠 | Помощь по Мини-играм", color=0xbf1cd4, timestamp = ctx.message.created_at)		
		helpp.add_field(name="Угадай число",value="**`=guess_number`**",inline=True)
		helpp.add_field(name="Бросить монетку",value="**`=coin`**",inline=True)
		helpp.add_field(name="Картинка с текстом",value="**`=png`**",inline=True)
		helpp.add_field(name="Ответ на вопрос",value="**`=guru`**",inline=True)
		helpp.add_field(name="Анонимное сообщение",value="**`=send`**",inline=True)
		helpp.add_field(name="Поиск картинки",value="**`=picture`**",inline=True)
		helpp.add_field(name="Насколько вы",value="**`=chance`**",inline=True)
		helpp.set_image(url="https://c.tenor.com/tJGArQutpgIAAAAC/game-controller-gaming.gif")
		helpp.set_author(name=ctx.guild.name, url="https://discord.gg/Uqp32EwByH", icon_url=ctx.author.avatar_url)
		helpp.set_footer(text=f"• Запросил: {ctx.author}")

		msg = await ctx.reply(embed=helpp, mention_author=True)
		await ctx.message.add_reaction("👍")
		await asyncio.sleep(90)
		await msg.delete()

	if arg == "other":

		helpp=discord.Embed(title="🛠 | Помощь по Другим командам", color=0xbf1cd4, timestamp = ctx.message.created_at)		
		helpp.add_field(name="Проверить бота",value="**`=test`**",inline=True)
		helpp.add_field(name="Перевод текста в Embed",value="**`=say`**",inline=True)
		helpp.add_field(name="Поддержать бота",value="**`=donate`**",inline=True)
		helpp.add_field(name="Пригласить бота",value="**`=invite`**",inline=True)
		helpp.add_field(name="Проголосовать за бота",value="**`=vote`**",inline=True)
		helpp.set_image(url="https://c.tenor.com/tgH-TRJmGRMAAAAC/another-bailar.gif")
		helpp.set_author(name=ctx.guild.name, url="https://discord.gg/Uqp32EwByH", icon_url=ctx.author.avatar_url)
		helpp.set_footer(text=f"• Запросил: {ctx.author}")

		msg = await ctx.reply(embed=helpp, mention_author=True)
		await ctx.message.add_reaction("👍")
		await asyncio.sleep(90)
		await msg.delete()

	if arg == "marry": 
		
		helpp=discord.Embed(title="🛠 | Помощь по командам Свадьбы", color=0xbf1cd4, timestamp = ctx.message.created_at)		
		helpp.add_field(name="Сделать предложение",value="**`=marry`**",inline=True)
		helpp.add_field(name="Развестить",value="**`=divorce`**",inline=True)
		helpp.add_field(name="Список женатых",value="**`=marrylist`**",inline=True)
		helpp.set_image(url="https://c.tenor.com/gj75w2kkqngAAAAC/tonikaku-kawaii-tonikaku.gif")
		helpp.set_author(name=ctx.guild.name, url="https://discord.gg/Uqp32EwByH", icon_url=ctx.author.avatar_url)
		helpp.set_footer(text=f"• Запросил: {ctx.author}")

		msg = await ctx.reply(embed=helpp, mention_author=True)
		await ctx.message.add_reaction("👍")
		await asyncio.sleep(90)
		await msg.delete()
	
	if arg == "serverstats":

		helpp=discord.Embed(title="🛠 | Помощь по командам Статистики сервера",description="Создать Голосовые каналы со статистикой участников, ботов и т.д", color=0xbf1cd4, timestamp = ctx.message.created_at)
		helpp.add_field(name="Включить",value="**`=serverstats on`**",inline=True)
		helpp.add_field(name="Выключить",value="**`=serverstats off`**",inline=True)
		helpp.set_author(name=ctx.guild.name, url="https://discord.gg/Uqp32EwByH", icon_url=ctx.author.avatar_url)
		helpp.set_thumbnail(url=ctx.guild.icon_url)
		helpp.set_image(url="https://c.tenor.com/VT9NPWYg5t0AAAAC/mao-amatsuka.gif")
		helpp.set_footer(text=f"• Запросил: {ctx.author}")		

		msg = await ctx.reply(embed=helpp, mention_author=True)
		await ctx.message.add_reaction("👍")
		await asyncio.sleep(90)
		await msg.delete()

	if arg == "ben":
		helpp=discord.Embed(title="🐶 | Говорящий Бэн",description="Отвечает на ваши вопросы в голосовом канале\nПример вопроса: **ты бэн?**", color=0xbf1cd4, timestamp = ctx.message.created_at)
		helpp.add_field(name="Позвонить Бэну",value="**`=ben`**",inline=True)
		helpp.add_field(name="Сбросить трубку",value="**`=ben stop`**",inline=True)
		helpp.set_author(name=ctx.guild.name, url="https://discord.gg/Uqp32EwByH", icon_url=ctx.author.avatar_url)
		helpp.set_thumbnail(url=ctx.guild.icon_url)
		helpp.set_image(url="https://c.tenor.com/KB4ie5CjGG4AAAAd/phone-call.gif")
		helpp.set_footer(text=f"• Запросил: {ctx.author}")		

		msg = await ctx.reply(embed=helpp, mention_author=True)
		await ctx.message.add_reaction("👍")
		await asyncio.sleep(90)
		await msg.delete()

@bot.command()
async def donate(ctx):
	helpp=discord.Embed(title="💰 | Поддержать RadexBot деньгами",description="**Чтобы поддержать бота и продлить его жизнь: *[Нажми](https://qiwi.com/n/RIENN0)***\n\n:white_check_mark: | Заранее спасибо за вашу поддержку", color=0xbf1cd4, timestamp = ctx.message.created_at)
	helpp.set_author(name=ctx.guild.name, url="https://discord.gg/Uqp32EwByH", icon_url=ctx.author.avatar_url)
	helpp.set_footer(text=f"• Запросил: {ctx.author}")
	await ctx.send(embed=helpp)

@bot.command()
async def invite(ctx):
	helpp=discord.Embed(title=":white_check_mark: | Пригласить RadexBot",description="**Чтобы добавить бота на свой сервер: *[Нажми](https://discord.com/oauth2/authorize?client_id=919925918024232970&permissions=8&scope=bot)***", color=0xbf1cd4, timestamp = ctx.message.created_at)
	helpp.set_author(name=ctx.guild.name, url="https://discord.gg/Uqp32EwByH", icon_url=ctx.author.avatar_url)
	helpp.set_footer(text=f"• Запросил: {ctx.author}")
	await ctx.send(embed=helpp)

@bot.command()
async def vote(ctx):
	helpp=discord.Embed(title=":white_check_mark: | Проголосовать за RadexBot",description="**Чтобы проголосовать за бота: *[Нажми](https://radexbot.xyz/vote)***\n\nВаш голос поднимет этого бота выше в топ!", color=0xbf1cd4, timestamp = ctx.message.created_at)
	helpp.set_author(name=ctx.guild.name, url="https://discord.gg/Uqp32EwByH", icon_url=ctx.author.avatar_url)
	helpp.set_footer(text=f"• Запросил: {ctx.author}")
	await ctx.send(embed=helpp)

@bot.command()
async def configs(ctx):
	con.ping() 
	with con.cursor() as cur:
		try: 
			cur.execute(f"SELECT roleid FROM muteroles WHERE serverid={ctx.guild.id}")

			fho = cur.fetchone()

			if fho == None:
				m_role = "`Не указана`"
			else: m_role = discord.utils.get(ctx.guild.roles, id=fho["roleid"]).mention
			
			cur.execute(f"SELECT channel_id FROM logs_channels WHERE serverid={ctx.guild.id}")

			fho = cur.fetchone()

			if fho == None:
				l_chan = "`Не указан`"
			else: l_chan = bot.get_channel(fho["channel_id"]).mention

			cur.execute(f"SELECT gr_chan_id FROM greetings WHERE serverid={ctx.guild.id}")

			fho = cur.fetchone()

			if fho == None:
				gr_chan = "`Не указан`"
			else: gr_chan = bot.get_channel(fho["gr_chan_id"]).mention

			cur.execute(f"SELECT gr_choice FROM greetings WHERE serverid={ctx.guild.id}")

			fho = cur.fetchone()

			if fho == None:
				gr_choice = "`Не указан`"
			else: gr_choice = fho["gr_choice"]

			cur.execute(f"SELECT gr_text FROM greetings WHERE serverid={ctx.guild.id}")

			fho = cur.fetchone()

			if fho == None:
				gr_text = "`Не указана`"
			else: gr_text = fho["gr_text"]

			cur.execute(f"SELECT gr_role_id FROM greetings WHERE serverid={ctx.guild.id}")

			fho = cur.fetchone()

			if fho == None:
				gr_role = "`Не указана`"
			else: gr_role = discord.utils.get(ctx.guild.roles, id=fho["gr_role_id"] ).mention
			
			helpp=discord.Embed(title="🛠 | Настройки сервера", color=0xbf1cd4, timestamp = ctx.message.created_at)
			helpp.add_field(name="🔇 | Мут" , value=f"**Мут-роль: \n {m_role} **",inline=True)
			helpp.add_field(name="📋 | Логи" , value=f"**Лог-канал: \n {l_chan} **",inline=True)
			helpp.add_field(name="👋🏻 | Приветствие", value=f"**Роль: \n {gr_role} \nКанал: \n{gr_chan}\n\nТип текста: `{gr_choice}`\nТекст: \n > {gr_text}**",inline=False)
			helpp.set_author(name=ctx.guild.name, url="https://discord.gg/Uqp32EwByH", icon_url=ctx.author.avatar_url)
			helpp.set_thumbnail(url=ctx.guild.icon_url)
			helpp.set_footer(text=f"• Запросил: {ctx.author}")			

			await ctx.reply(embed=helpp, mention_author=True)

		except Exception as e:
			await ctx.reply("```Произошла неизвестная ошибка```", mention_author=True)
			raise e
			return

@bot.command()
async def config(ctx):
	helpp=discord.Embed(title="🛠 | Конфиг сервера", description=f"**[Требуется право Управлением Сервером]\n\n > `=configs` - Проверить текущие настройки**\n\n**`=config_muterole`** -- Установить мут-роль\n**`=config_muterole_reset`** -- Сбросить мут-роль\n\n**`=config_LogChannel`** -- Включить Логи на сервере\n**`=config_LogsChannel_reset`** -- Выключить логи на сервере\n\n**`=config_greetings`** - Настроить приветствие новых участников\n**`=config_greetings_reset`** - Сбросить настройки приветствия", color=0xbf1cd4, timestamp = ctx.message.created_at)
	helpp.set_author(name=ctx.guild.name, url="https://discord.gg/Uqp32EwByH", icon_url=ctx.author.avatar_url)
	helpp.set_thumbnail(url=ctx.guild.icon_url)
	helpp.set_footer(text=f"• Запросил: {ctx.author}")

	msg = await ctx.reply(embed=helpp, mention_author=True)
	await ctx.message.add_reaction("👍")
	await asyncio.sleep(90)
	await msg.delete()

@bot.command()
@has_permissions(manage_guild=True)
async def config_greetings(ctx,gr_role:discord.Role=None,gr_chan:discord.TextChannel=None,gr_choice:str=None,*,gr_text=None):
	if gr_role == None:
		await ctx.reply("```=config_greetings <Роль для новых участников> <Канал для приветствия> <Тип текста: (embed, text)> <Текст приветствия>```", mention_author=True)
		return

	if gr_chan == None:
		await ctx.reply("```=config_greetings <Роль для новых участников> <Канал для приветствия> <Тип текста: (embed, text)> <Текст приветствия>```", mention_author=True)
		return

	if gr_choice == None:
		await ctx.reply("```=config_greetings <Роль для новых участников> <Канал для приветствия> <Тип текста: (embed, text)> <Текст приветствия>```", mention_author=True)
		return

	if gr_text == None:
		await ctx.reply("```=config_greetings <Роль для новых участников> <Канал для приветствия> <Тип текста: (embed, text)> <Текст приветствия>```", mention_author=True)
		return

	choices = ["embed","text","Embed","Text","`Не указан`"]
	if gr_choice not in choices:
		await ctx.reply("```Выберите тип текста: embed , text```", mention_author=True)
		return

	con.ping() 
	with con.cursor() as cur:
		cur.execute(f"SELECT serverid FROM greetings WHERE serverid={ctx.guild.id}")
		if cur.fetchone() == None:
			cur.execute(f"INSERT INTO greetings (serverid , gr_chan_id , gr_role_id , gr_role_name , gr_choice, gr_text) VALUES ( {ctx.guild.id} , {gr_chan.id} ,  {gr_role.id} , '{gr_role.name}' , '{gr_choice}' , '{gr_text}' )")
		else: 
			cur.execute(f"DELETE FROM greetings WHERE serverid={ctx.guild.id}")
			cur.execute(f"INSERT INTO greetings (serverid , gr_chan_id , gr_role_id , gr_role_name , gr_choice, gr_text) VALUES ( {ctx.guild.id} , {gr_chan.id} ,  {gr_role.id} , '{gr_role.name}' , '{gr_choice}' , '{gr_text}' )")

		embed=discord.Embed(title="⚙️ Конфиг | Настройка приветствия",description=f"**Роль для новых участников - {gr_role.mention}\nКанал для приветствия: {gr_chan.mention}\nТип текста: {gr_choice}\n\nПриветственный текст: \n{gr_text}  **", color=0xbf1cd4, timestamp = ctx.message.created_at)
		
		await ctx.reply(embed=embed, mention_author=True)
		con.commit()

@bot.command()
@has_permissions(manage_guild=True)
async def config_greetings_reset(ctx):
	con.ping() 
	with con.cursor() as cur:
		cur.execute(f"SELECT serverid FROM greetings WHERE serverid={ctx.guild.id}")
		if cur.fetchone() == None:
			await ctx.reply("У вас не настроено приветствие", mention_author=True)
			return
		else:
			cur.execute(f"DELETE FROM greetings WHERE serverid={ctx.guild.id}")
			await ctx.reply(embed=discord.Embed(title="⚙️ Конфиг | Настройка приветствия",description="**Настройки приветствия были сброшены**", color=0xbf1cd4, timestamp = ctx.message.created_at), mention_author=True)
		con.commit()

@bot.command()
@has_permissions(manage_guild=True)
async def config_muterole(ctx,role:discord.Role=None):
	if role == None:
		await ctx.reply("Укажи мут-роль (ID или Упоминание)", mention_author=True)
		return

	con.ping() 
	with con.cursor() as cur:
		cur.execute(f"SELECT serverid FROM muteroles WHERE serverid={ctx.guild.id}")
		if cur.fetchone() == None:
			cur.execute(f"INSERT INTO muteroles (serverid, roleid, rolename) VALUES ( {ctx.guild.id},{role.id},'{role.name}' )")
		else:
			cur.execute(f"DELETE FROM muteroles WHERE serverid={ctx.guild.id}")
			cur.execute(f"INSERT INTO muteroles (serverid, roleid, rolename) VALUES ( {ctx.guild.id},{role.id},'{role.name}' )")
		await ctx.reply(embed=discord.Embed(title="⚙️ Конфиг | Установка мут-роли",description=f"Установлена мут-роль - {role.mention}", color=0xbf1cd4, timestamp = ctx.message.created_at), mention_author=True)
		con.commit()

@bot.command()
@has_permissions(manage_guild=True)
async def config_muterole_reset(ctx):
	con.ping() 
	with con.cursor() as cur:
		cur.execute(f"SELECT serverid FROM muteroles WHERE serverid={ctx.guild.id}")
		if cur.fetchone() == None:
			await ctx.reply("У вас не указана мут-роль", mention_author=True)
			return
		else:
			cur.execute(f"DELETE FROM muteroles WHERE serverid={ctx.guild.id}")
			await ctx.reply(embed=discord.Embed(title="⚙️ Конфиг | Сброс мут-роли",description="**Мут-роль была сброшена**", color=0xbf1cd4, timestamp = ctx.message.created_at), mention_author=True)
		con.commit()

@config_muterole_reset.error
async def config_muterole_reset_error(ctx,error):
	if isinstance(error, commands.CheckFailure):
		await ctx.reply("```У вас нет прав на выполнение этой команды```", mention_author=True)

@config_muterole.error
async def config_muterole_error(ctx,error):
	if isinstance(error, commands.CheckFailure):
		await ctx.reply("```У вас нет прав на выполнение этой команды```", mention_author=True)

@config_greetings.error
async def config_greetings_error(ctx,error):
	if isinstance(error, commands.CheckFailure):
		await ctx.reply("```У вас нет прав на выполнение этой команды```", mention_author=True)

@config_greetings_reset.error
async def config_greetings_reset_error(ctx,error):
	if isinstance(error, commands.CheckFailure):
		await ctx.reply("```У вас нет прав на выполнение этой команды```", mention_author=True)


@bot.command()
@has_permissions(manage_guild=True)
async def config_LogsChannel(ctx,channel:discord.TextChannel=None):
	if channel == None:
		await ctx.reply("Укажи канал (ID или Упоминание)", mention_author=True)
		return
	con.ping() 
	with con.cursor() as cur:
		cur.execute(f"SELECT serverid FROM logs_channels WHERE serverid={ctx.guild.id}")
		if cur.fetchone() == None:
			cur.execute(f"INSERT INTO logs_channels (serverid, channel_id, channel_name) VALUES ( {ctx.guild.id},{channel.id},'{channel.name}' )")
		else:
			cur.execute(f"DELETE FROM logs_channels WHERE serverid={ctx.guild.id}")
			cur.execute(f"INSERT INTO logs_channels (serverid, channel_id, channel_name) VALUES ( {ctx.guild.id},{channel.id},'{channel.name}' )")
		await ctx.reply(embed=discord.Embed(title="⚙️ Конфиг | Установка лог-канала",description=f"Вы включили логи в канале - {channel.mention}", color=0xbf1cd4, timestamp = ctx.message.created_at), mention_author=True)
		con.commit()

@bot.command()
@has_permissions(manage_guild=True)
async def config_LogsChannel_reset(ctx):
	con.ping() 
	with con.cursor() as cur:
		cur.execute(f"SELECT serverid FROM logs_channels WHERE serverid={ctx.guild.id}")
		if cur.fetchone() == None:
			await ctx.reply("У вас уже выключены логи", mention_author=True)
			return
		else:
			cur.execute(f"DELETE FROM logs_channels WHERE serverid={ctx.guild.id}")
			await ctx.reply(embed=discord.Embed(title="⚙️ Конфиг | Сброс лог-канала",description="**Вы выключили логи на сервере**", color=0xbf1cd4, timestamp = ctx.message.created_at), mention_author=True)
		con.commit()

@config_LogsChannel.error
async def config_LogsChannel_error(ctx,error):
	if isinstance(error, commands.CheckFailure):
		await ctx.reply("```У вас нет прав на выполнение этой команды```", mention_author=True)

@config_LogsChannel_reset.error
async def config_LogsChannel_reset_error(ctx,error):
	if isinstance(error, commands.CheckFailure):
		await ctx.reply("```У вас нет прав на выполнение этой команды```", mention_author=True)

@bot.command()
@has_permissions(manage_messages=True)
async def mute(ctx, member: discord.Member, time: str, *, reason="Не указана"):
	con.ping() 
	with con.cursor() as cur:
		try:
			cur.execute(f"SELECT roleid FROM muteroles WHERE serverid={ctx.guild.id}")
			rol = cur.fetchone()["roleid"]
		except:
			await ctx.reply("**Не указана мут-роль.** \nУказать: **`=config_muterole Роль`**", mention_author=True)
			return
	
	con.ping() 
	with con.cursor() as cur:
		try:
			cur.execute(f"SELECT channel_id FROM logs_channels WHERE serverid={ctx.guild.id}")
			l_chan = cur.fetchone()["channel_id"]
			logs = bot.get_channel(l_chan)
		except: pass

	muterole = discord.utils.get(ctx.guild.roles, id=rol)

	if ctx.author.top_role.position <= member.top_role.position:
		topro=discord.Embed(title="❌ | Ошибка", description=f"**```Вы не можете замутить человека, чья роль выше или равна вашей```**", color=0xbf1cd4, timestamp = ctx.message.created_at)
		topro.set_author(name=ctx.guild.name, url="https://discord.gg/Uqp32EwByH", icon_url=ctx.author.avatar_url)
		topro.set_footer(text=f"• Запросил: {ctx.author}")	 
		await ctx.reply(embed=topro, mention_author=True)
		await ctx.message.add_reaction("❌")
		return
	if len(time) > 3:
		lenmut=discord.Embed(title="❌ | Ошибка", description=f"```    Неверный срок мута    ```\n\n**`Пример: 1m, 1h, 1d`**", color=0xbf1cd4, timestamp = ctx.message.created_at)
		lenmut.set_author(name=ctx.guild.name, url="https://discord.gg/Uqp32EwByH", icon_url=ctx.author.avatar_url)
		lenmut.set_footer(text=f"• Запросил: {ctx.author}")	 
		await ctx.reply(embed=lenmut, mention_author=True)
		await ctx.message.add_reaction("❌")
		return
	if len(time) < 2:
		await ctx.reply(embed=lenmut, mention_author=True)
		await ctx.message.add_reaction("❌")
		return
	if muterole in member.roles:
		err=discord.Embed(title="❌ | Ошибка", description=f"{member.mention} уже имеет мут", color=0xbf1cd4, timestamp = ctx.message.created_at)
		err.set_author(name=ctx.guild.name, url="https://discord.gg/Uqp32EwByH", icon_url=member.avatar_url)
		err.set_thumbnail(url=ctx.guild.icon_url)
		err.set_footer(text=f"•")
		await ctx.reply(embed=err, mention_author=True)
		await ctx.message.add_reaction("❌")
		return	
	if member.bot == True:
		botmut=discord.Embed(title="❌ | Ошибка", description=f"```    Нельзя замутить бота    ```", color=0xbf1cd4, timestamp = ctx.message.created_at)
		botmut.set_author(name=ctx.guild.name, url="https://discord.gg/Uqp32EwByH", icon_url=ctx.author.avatar_url)
		botmut.set_footer(text=f"• Запросил: {ctx.author}")	 
		await ctx.reply(embed=botmut, mention_author=True)
		await ctx.message.add_reaction("❌")
		return
	if member.id == ctx.author.id:
		smut=discord.Embed(title="❌ | Ошибка", description=f"```    Нельзя замутить самого себя    ```", color=0xbf1cd4, timestamp = ctx.message.created_at)
		smut.set_author(name=ctx.guild.name, url="https://discord.gg/Uqp32EwByH", icon_url=ctx.author.avatar_url)
		smut.set_footer(text=f"• Запросил: {ctx.author}")	 
		await ctx.reply(embed=smut, mention_author=True)
		await ctx.message.add_reaction("❌")
		return

	if time is not None:
		
		if time == "1m":
			time = 60
			mute=discord.Embed(title="🔇 | Мут", description=f"**Участник {member.mention} был успешно замучен.**", color=0xc10dd9, timestamp = ctx.message.created_at)
			mute.set_author(name=ctx.guild.name, url="https://discord.gg/Uqp32EwByH", icon_url=ctx.author.avatar_url)
			mute.set_thumbnail(url=ctx.guild.icon_url)
			mute.add_field(name="Замутил:", value=f"{ctx.author.mention}", inline=False)
			mute.add_field(name="Срок:", value="**`1 минута`**", inline=True)
			mute.add_field(name="Причина:", value=f"**`{reason}`**", inline=True)
			mute.set_footer(text=f"• Запросил: {ctx.author}")
		
		if time == "2m":
			time = 60
			mute=discord.Embed(title="🔇 | Мут", description=f"**Участник {member.mention} был успешно замучен.**", color=0xc10dd9, timestamp = ctx.message.created_at)
			mute.set_author(name=ctx.guild.name, url="https://discord.gg/Uqp32EwByH", icon_url=ctx.author.avatar_url)
			mute.set_thumbnail(url=ctx.guild.icon_url)
			mute.add_field(name="Замутил:", value=f"{ctx.author.mention}", inline=False)
			mute.add_field(name="Срок:", value="**`2 минуты`**", inline=True)
			mute.add_field(name="Причина:", value=f"**`{reason}`**", inline=True)
			mute.set_footer(text=f"• Запросил: {ctx.author}")

		if time == "5m":
			time = 300
			mute=discord.Embed(title="🔇 | Мут", description=f"**Участник {member.mention} был успешно замучен.**", color=0xc10dd9, timestamp = ctx.message.created_at)
			mute.set_author(name=ctx.guild.name, url="https://discord.gg/Uqp32EwByH", icon_url=ctx.author.avatar_url)
			mute.set_thumbnail(url=ctx.guild.icon_url)
			mute.add_field(name="Замутил:", value=f"{ctx.author.mention}", inline=False)
			mute.add_field(name="Срок:", value="**`5 минут`**", inline=True)
			mute.add_field(name="Причина:", value=f"**`{reason}`**", inline=True)
			mute.set_footer(text=f"• Запросил: {ctx.author}")

		if time == "10m":
			time = 600
			mute=discord.Embed(title="🔇 | Мут", description=f"**Участник {member.mention} был успешно замучен.**", color=0xc10dd9, timestamp = ctx.message.created_at)
			mute.set_author(name=ctx.guild.name, url="https://discord.gg/Uqp32EwByH", icon_url=ctx.author.avatar_url)
			mute.set_thumbnail(url=ctx.guild.icon_url)
			mute.add_field(name="Замутил:", value=f"{ctx.author.mention}", inline=False)
			mute.add_field(name="Срок:", value="**`10 минут`**", inline=True)
			mute.add_field(name="Причина:", value=f"**``{reason}``**", inline=True)
			mute.set_footer(text=f"• Запросил: {ctx.author}")
		
		if time == "15m":
			time = 900
			mute=discord.Embed(title="🔇 | Мут", description=f"**Участник {member.mention} был успешно замучен.**", color=0xc10dd9, timestamp = ctx.message.created_at)
			mute.set_author(name=ctx.guild.name, url="https://discord.gg/Uqp32EwByH", icon_url=ctx.author.avatar_url)
			mute.set_thumbnail(url=ctx.guild.icon_url)
			mute.add_field(name="Замутил:", value=f"{ctx.author.mention}", inline=False)
			mute.add_field(name="Срок:", value="**`15 минут`**", inline=True)
			mute.add_field(name="Причина:", value=f"**`{reason}`**", inline=True)
			mute.set_footer(text=f"• Запросил: {ctx.author}")

		if time == "20m":
			time = 1200
			mute=discord.Embed(title="🔇 | Мут", description=f"**Участник {member.mention} был успешно замучен.**", color=0xc10dd9, timestamp = ctx.message.created_at)
			mute.set_author(name=ctx.guild.name, url="https://discord.gg/Uqp32EwByH", icon_url=ctx.author.avatar_url)
			mute.set_thumbnail(url=ctx.guild.icon_url)
			mute.add_field(name="Замутил:", value=f"{ctx.author.mention}", inline=False)
			mute.add_field(name="Срок:", value="**`20 минут`**", inline=True)
			mute.add_field(name="Причина:", value=f"**`{reason}`**", inline=True)
			mute.set_footer(text=f"• Запросил: {ctx.author}")

		if time == "25m":
			time = 1500
			mute=discord.Embed(title="🔇 | Мут", description=f"**Участник {member.mention} был успешно замучен.**", color=0xc10dd9, timestamp = ctx.message.created_at)
			mute.set_author(name=ctx.guild.name, url="https://discord.gg/Uqp32EwByH", icon_url=ctx.author.avatar_url)
			mute.set_thumbnail(url=ctx.guild.icon_url)
			mute.add_field(name="Замутил:", value=f"{ctx.author.mention}", inline=False)
			mute.add_field(name="Срок:", value="**`25 минут`**", inline=True)
			mute.add_field(name="Причина:", value=f"**`{reason}`**", inline=True)
			mute.set_footer(text=f"• Запросил: {ctx.author}")

		if time == "30m":
			time = 1800
			mute=discord.Embed(title="🔇 | Мут", description=f"**Участник {member.mention} был успешно замучен.**", color=0xc10dd9, timestamp = ctx.message.created_at)
			mute.set_author(name=ctx.guild.name, url="https://discord.gg/Uqp32EwByH", icon_url=ctx.author.avatar_url)
			mute.set_thumbnail(url=ctx.guild.icon_url)
			mute.add_field(name="Замутил:", value=f"{ctx.author.mention}", inline=False)
			mute.add_field(name="Срок:", value="**`30 минут`**", inline=True)
			mute.add_field(name="Причина:", value=f"**`{reason}`**", inline=True)
			mute.set_footer(text=f"• Запросил: {ctx.author}")

		if time == "35m":
			time = 2100
			mute=discord.Embed(title="🔇 | Мут", description=f"**Участник {member.mention} был успешно замучен.**", color=0xc10dd9, timestamp = ctx.message.created_at)
			mute.set_author(name=ctx.guild.name, url="https://discord.gg/Uqp32EwByH", icon_url=ctx.author.avatar_url)
			mute.set_thumbnail(url=ctx.guild.icon_url)
			mute.add_field(name="Замутил:", value=f"{ctx.author.mention}", inline=False)
			mute.add_field(name="Срок:", value="**`35 минут`**", inline=True)
			mute.add_field(name="Причина:", value=f"**`{reason}`**", inline=True)
			mute.set_footer(text=f"• Запросил: {ctx.author}")

		if time == "40m":
			time = 2400
			mute=discord.Embed(title="🔇 | Мут", description=f"**Участник {member.mention} был успешно замучен.**", color=0xc10dd9, timestamp = ctx.message.created_at)
			mute.set_author(name=ctx.guild.name, url="https://discord.gg/Uqp32EwByH", icon_url=ctx.author.avatar_url)
			mute.set_thumbnail(url=ctx.guild.icon_url)
			mute.add_field(name="Замутил:", value=f"{ctx.author.mention}", inline=False)
			mute.add_field(name="Срок:", value="**`40 минут`**", inline=True)
			mute.add_field(name="Причина:", value=f"**`{reason}`**", inline=True)
			mute.set_footer(text=f"• Запросил: {ctx.author}")

		if time == "45m":
			time = 2700
			mute=discord.Embed(title="🔇 | Мут", description=f"**Участник {member.mention} был успешно замучен.**", color=0xc10dd9, timestamp = ctx.message.created_at)
			mute.set_author(name=ctx.guild.name, url="https://discord.gg/Uqp32EwByH", icon_url=ctx.author.avatar_url)
			mute.set_thumbnail(url=ctx.guild.icon_url)
			mute.add_field(name="Замутил:", value=f"{ctx.author.mention}", inline=False)
			mute.add_field(name="Срок:", value="**`45 минут`**", inline=True)
			mute.add_field(name="Причина:", value=f"**`{reason}`**", inline=True)
			mute.set_footer(text=f"• Запросил: {ctx.author}")

		if time == "50m":
			time = 3000
			mute=discord.Embed(title="🔇 | Мут", description=f"**Участник {member.mention} был успешно замучен.**", color=0xc10dd9, timestamp = ctx.message.created_at)
			mute.set_author(name=ctx.guild.name, url="https://discord.gg/Uqp32EwByH", icon_url=ctx.author.avatar_url)
			mute.set_thumbnail(url=ctx.guild.icon_url)
			mute.add_field(name="Замутил:", value=f"{ctx.author.mention}", inline=False)
			mute.add_field(name="Срок:", value="**`50 минут`**", inline=True)
			mute.add_field(name="Причина:", value=f"**`{reason}`**", inline=True)
			mute.set_footer(text=f"• Запросил: {ctx.author}")

		if time == "55m":
			time = 3300
			mute=discord.Embed(title="🔇 | Мут", description=f"**Участник {member.mention} был успешно замучен.**", color=0xc10dd9, timestamp = ctx.message.created_at)
			mute.set_author(name=ctx.guild.name, url="https://discord.gg/Uqp32EwByH", icon_url=ctx.author.avatar_url)
			mute.set_thumbnail(url=ctx.guild.icon_url)
			mute.add_field(name="Замутил:", value=f"{ctx.author.mention}", inline=False)
			mute.add_field(name="Срок:", value="**`55 минут`**", inline=True)
			mute.add_field(name="Причина:", value=f"**`{reason}`**", inline=True)
			mute.set_footer(text=f"• Запросил: {ctx.author}")

		if time == "1h":
			time = 3600
			mute=discord.Embed(title="🔇 | Мут", description=f"**Участник {member.mention} был успешно замучен.**", color=0xc10dd9, timestamp = ctx.message.created_at)
			mute.set_author(name=ctx.guild.name, url="https://discord.gg/Uqp32EwByH", icon_url=ctx.author.avatar_url)
			mute.set_thumbnail(url=ctx.guild.icon_url)
			mute.add_field(name="Замутил:", value=f"{ctx.author.mention}", inline=False)
			mute.add_field(name="Срок:", value="**`1 час`**", inline=True)
			mute.add_field(name="Причина:", value=f"**`{reason}`**", inline=True)
			mute.set_footer(text=f"• Запросил: {ctx.author}")

		if time == "2h":
			time = 7200
			mute=discord.Embed(title="🔇 | Мут", description=f"**Участник {member.mention} был успешно замучен.**", color=0xc10dd9, timestamp = ctx.message.created_at)
			mute.set_author(name=ctx.guild.name, url="https://discord.gg/Uqp32EwByH", icon_url=ctx.author.avatar_url)
			mute.set_thumbnail(url=ctx.guild.icon_url)
			mute.add_field(name="Замутил:", value=f"{ctx.author.mention}", inline=False)
			mute.add_field(name="Срок:", value="**`2 часа`**", inline=True)
			mute.add_field(name="Причина:", value=f"**`{reason}`**", inline=True)
			mute.set_footer(text=f"• Запросил: {ctx.author}")

		if time == "3h":
			time = 10800
			mute=discord.Embed(title="🔇 | Мут", description=f"**Участник {member.mention} был успешно замучен.**", color=0xc10dd9, timestamp = ctx.message.created_at)
			mute.set_author(name=ctx.guild.name, url="https://discord.gg/Uqp32EwByH", icon_url=ctx.author.avatar_url)
			mute.set_thumbnail(url=ctx.guild.icon_url)
			mute.add_field(name="Замутил:", value=f"{ctx.author.mention}", inline=False)
			mute.add_field(name="Срок:", value="**`3 часа`**", inline=True)
			mute.add_field(name="Причина:", value=f"**`{reason}`**", inline=True)
			mute.set_footer(text=f"• Запросил: {ctx.author}")

		if time == "4h":
			time = 14400
			mute=discord.Embed(title="🔇 | Мут", description=f"**Участник {member.mention} был успешно замучен.**", color=0xc10dd9, timestamp = ctx.message.created_at)
			mute.set_author(name=ctx.guild.name, url="https://discord.gg/Uqp32EwByH", icon_url=ctx.author.avatar_url)
			mute.set_thumbnail(url=ctx.guild.icon_url)
			mute.add_field(name="Замутил:", value=f"{ctx.author.mention}", inline=False)
			mute.add_field(name="Срок:", value="**`4 часа`**", inline=True)
			mute.add_field(name="Причина:", value=f"**`{reason}`**", inline=True)
			mute.set_footer(text=f"• Запросил: {ctx.author}")

		if time == "5h":
			time = 18000
			mute=discord.Embed(title="🔇 | Мут", description=f"**Участник {member.mention} был успешно замучен.**", color=0xc10dd9, timestamp = ctx.message.created_at)
			mute.set_author(name=ctx.guild.name, url="https://discord.gg/Uqp32EwByH", icon_url=ctx.author.avatar_url)
			mute.set_thumbnail(url=ctx.guild.icon_url)
			mute.add_field(name="Замутил:", value=f"{ctx.author.mention}", inline=False)
			mute.add_field(name="Срок:", value="**`5 часов`**", inline=True)
			mute.add_field(name="Причина:", value=f"**`{reason}`**", inline=True)
			mute.set_footer(text=f"• Запросил: {ctx.author}")

		if time == "6h":
			time = 21600
			mute=discord.Embed(title="🔇 | Мут", description=f"**Участник {member.mention} был успешно замучен.**", color=0xc10dd9, timestamp = ctx.message.created_at)
			mute.set_author(name=ctx.guild.name, url="https://discord.gg/Uqp32EwByH", icon_url=ctx.author.avatar_url)
			mute.set_thumbnail(url=ctx.guild.icon_url)
			mute.add_field(name="Замутил:", value=f"{ctx.author.mention}", inline=False)
			mute.add_field(name="Срок:", value="**`6 часов`**", inline=True)
			mute.add_field(name="Причина:", value=f"**`{reason}`**", inline=True)
			mute.set_footer(text=f"• Запросил: {ctx.author}")

		if time == "7h":
			time = 25200
			mute=discord.Embed(title="🔇 | Мут", description=f"**Участник {member.mention} был успешно замучен.**", color=0xc10dd9, timestamp = ctx.message.created_at)
			mute.set_author(name=ctx.guild.name, url="https://discord.gg/Uqp32EwByH", icon_url=ctx.author.avatar_url)
			mute.set_thumbnail(url=ctx.guild.icon_url)
			mute.add_field(name="Замутил:", value=f"{ctx.author.mention}", inline=False)
			mute.add_field(name="Срок:", value="**`7 часов`**", inline=True)
			mute.add_field(name="Причина:", value=f"**`{reason}`**", inline=True)
			mute.set_footer(text=f"• Запросил: {ctx.author}")

		if time == "8h":
			time = 28800
			mute=discord.Embed(title="🔇 | Мут", description=f"**Участник {member.mention} был успешно замучен.**", color=0xc10dd9, timestamp = ctx.message.created_at)
			mute.set_author(name=ctx.guild.name, url="https://discord.gg/Uqp32EwByH", icon_url=ctx.author.avatar_url)
			mute.set_thumbnail(url=ctx.guild.icon_url)
			mute.add_field(name="Замутил:", value=f"{ctx.author.mention}", inline=False)
			mute.add_field(name="Срок:", value="**`8 часов`**", inline=True)
			mute.add_field(name="Причина:", value=f"**`{reason}`**", inline=True)
			mute.set_footer(text=f"• Запросил: {ctx.author}")

		if time == "9h":
			time = 32400
			mute=discord.Embed(title="🔇 | Мут", description=f"**Участник {member.mention} был успешно замучен.**", color=0xc10dd9, timestamp = ctx.message.created_at)
			mute.set_author(name=ctx.guild.name, url="https://discord.gg/Uqp32EwByH", icon_url=ctx.author.avatar_url)
			mute.set_thumbnail(url=ctx.guild.icon_url)
			mute.add_field(name="Замутил:", value=f"{ctx.author.mention}", inline=False)
			mute.add_field(name="Срок:", value="**`9 часов`**", inline=True)
			mute.add_field(name="Причина:", value=f"**`{reason}`**", inline=True)
			mute.set_footer(text=f"• Запросил: {ctx.author}")

		if time == "10h":
			time == 36000
			mute=discord.Embed(title="🔇 | Мут", description=f"**Участник {member.mention} был успешно замучен.**", color=0xc10dd9, timestamp = ctx.message.created_at)
			mute.set_author(name=ctx.guild.name, url="https://discord.gg/Uqp32EwByH", icon_url=ctx.author.avatar_url)
			mute.set_thumbnail(url=ctx.guild.icon_url)
			mute.add_field(name="Замутил:", value=f"{ctx.author.mention}", inline=False)
			mute.add_field(name="Срок:", value="**`10 часов`**", inline=True)
			mute.add_field(name="Причина:", value=f"**`{reason}`**", inline=True)
			mute.set_footer(text=f"• Запросил: {ctx.author}")

		if time == "15h":
			time = 54000
			mute=discord.Embed(title="🔇 | Мут", description=f"**Участник {member.mention} был успешно замучен.**", color=0xc10dd9, timestamp = ctx.message.created_at)
			mute.set_author(name=ctx.guild.name, url="https://discord.gg/Uqp32EwByH", icon_url=ctx.author.avatar_url)
			mute.set_thumbnail(url=ctx.guild.icon_url)
			mute.add_field(name="Замутил:", value=f"{ctx.author.mention}", inline=False)
			mute.add_field(name="Срок:", value="**`15 часов`**", inline=True)
			mute.add_field(name="Причина:", value=f"**`{reason}`**", inline=True)
			mute.set_footer(text=f"• Запросил: {ctx.author}")

		if time == "20h":
			time = 72000
			mute=discord.Embed(title="🔇 | Мут", description=f"**Участник {member.mention} был успешно замучен.**", color=0xc10dd9, timestamp = ctx.message.created_at)
			mute.set_author(name=ctx.guild.name, url="https://discord.gg/Uqp32EwByH", icon_url=ctx.author.avatar_url)
			mute.set_thumbnail(url=ctx.guild.icon_url)
			mute.add_field(name="Замутил:", value=f"{ctx.author.mention}", inline=False)
			mute.add_field(name="Срок:", value="**`20 часов`**", inline=True)
			mute.add_field(name="Причина:", value=f"**`{reason}`**", inline=True)
			mute.set_footer(text=f"• Запросил: {ctx.author}")

		if time == "24h":
			time = 86000
			mute=discord.Embed(title="🔇 | Мут", description=f"**Участник {member.mention} был успешно замучен.**", color=0xc10dd9, timestamp = ctx.message.created_at)
			mute.set_author(name=ctx.guild.name, url="https://discord.gg/Uqp32EwByH", icon_url=ctx.author.avatar_url)
			mute.set_thumbnail(url=ctx.guild.icon_url)
			mute.add_field(name="Замутил:", value=f"{ctx.author.mention}", inline=False)
			mute.add_field(name="Срок:", value="**`1 день`**", inline=True)
			mute.add_field(name="Причина:", value=f"**`{reason}`**", inline=True)
			mute.set_footer(text=f"• Запросил: {ctx.author}")

		if time == "1d":
			time = 86000
			mute=discord.Embed(title="🔇 | Мут", description=f"**Участник {member.mention} был успешно замучен.**", color=0xc10dd9, timestamp = ctx.message.created_at)
			mute.set_author(name=ctx.guild.name, url="https://discord.gg/Uqp32EwByH", icon_url=ctx.author.avatar_url)
			mute.set_thumbnail(url=ctx.guild.icon_url)
			mute.add_field(name="Замутил:", value=f"{ctx.author.mention}", inline=False)
			mute.add_field(name="Срок:", value="**`1 день`**", inline=True)
			mute.add_field(name="Причина:", value=f"**`{reason}`**", inline=True)
			mute.set_footer(text=f"• Запросил: {ctx.author}")

		if time == "2d":
			time = 172800
			mute=discord.Embed(title="🔇 | Мут", description=f"**Участник {member.mention} был успешно замучен.**", color=0xc10dd9, timestamp = ctx.message.created_at)
			mute.set_author(name=ctx.guild.name, url="https://discord.gg/Uqp32EwByH", icon_url=ctx.author.avatar_url)
			mute.set_thumbnail(url=ctx.guild.icon_url)
			mute.add_field(name="Замутил:", value=f"{ctx.author.mention}", inline=False)
			mute.add_field(name="Срок:", value="**`2 дня`**", inline=True)
			mute.add_field(name="Причина:", value=f"**`{reason}`**", inline=True)
			mute.set_footer(text=f"• Запросил: {ctx.author}")

		if time == "3d":
			time = 259200
			mute=discord.Embed(title="🔇 | Мут", description=f"**Участник {member.mention} был успешно замучен.**", color=0xc10dd9, timestamp = ctx.message.created_at)
			mute.set_author(name=ctx.guild.name, url="https://discord.gg/Uqp32EwByH", icon_url=ctx.author.avatar_url)
			mute.set_thumbnail(url=ctx.guild.icon_url)
			mute.add_field(name="Замутил:", value=f"{ctx.author.mention}", inline=False)
			mute.add_field(name="Срок:", value="**`3 дня`**", inline=True)
			mute.add_field(name="Причина:", value=f"**`{reason}`**", inline=True)
			mute.set_footer(text=f"• Запросил: {ctx.author}")

		if time == "4d":
			time = 345600
			mute=discord.Embed(title="🔇 | Мут", description=f"**Участник {member.mention} был успешно замучен.**", color=0xc10dd9, timestamp = ctx.message.created_at)
			mute.set_author(name=ctx.guild.name, url="https://discord.gg/Uqp32EwByH", icon_url=ctx.author.avatar_url)
			mute.set_thumbnail(url=ctx.guild.icon_url)
			mute.add_field(name="Замутил:", value=f"{ctx.author.mention}", inline=False)
			mute.add_field(name="Срок:", value="**`4 дня`**", inline=True)
			mute.add_field(name="Причина:", value=f"**`{reason}`**", inline=True)
			mute.set_footer(text=f"• Запросил: {ctx.author}")

		if time == "5d":
			time = 432000
			mute=discord.Embed(title="🔇 | Мут", description=f"**Участник {member.mention} был успешно замучен.**", color=0xc10dd9, timestamp = ctx.message.created_at)
			mute.set_author(name=ctx.guild.name, url="https://discord.gg/Uqp32EwByH", icon_url=ctx.author.avatar_url)
			mute.set_thumbnail(url=ctx.guild.icon_url)
			mute.add_field(name="Замутил:", value=f"{ctx.author.mention}", inline=False)
			mute.add_field(name="Срок:", value="**`5 дней`**", inline=True)
			mute.add_field(name="Причина:", value=f"**`{reason}`**", inline=True)
			mute.set_footer(text=f"• Запросил: {ctx.author}")

		if time == "6d":
			time = 518400
			mute=discord.Embed(title="🔇 | Мут", description=f"**Участник {member.mention} был успешно замучен.**", color=0xc10dd9, timestamp = ctx.message.created_at)
			mute.set_author(name=ctx.guild.name, url="https://discord.gg/Uqp32EwByH", icon_url=ctx.author.avatar_url)
			mute.set_thumbnail(url=ctx.guild.icon_url)
			mute.add_field(name="Замутил:", value=f"{ctx.author.mention}", inline=False)
			mute.add_field(name="Срок:", value="**`6 дней`**", inline=True)
			mute.add_field(name="Причина:", value=f"**`{reason}`**", inline=True)
			mute.set_footer(text=f"• Запросил: {ctx.author}")

		if time == "7d":
			time = 604800
			mute=discord.Embed(title="🔇 | Мут", description=f"**Участник {member.mention} был успешно замучен.**", color=0xc10dd9, timestamp = ctx.message.created_at)
			mute.set_author(name=ctx.guild.name, url="https://discord.gg/Uqp32EwByH", icon_url=ctx.author.avatar_url)
			mute.set_thumbnail(url=ctx.guild.icon_url)
			mute.add_field(name="Замутил:", value=f"{ctx.author.mention}", inline=False)
			mute.add_field(name="Срок:", value="**`1 неделя`**", inline=True)
			mute.add_field(name="Причина:", value=f"**`{reason}`**", inline=True)
			mute.set_footer(text=f"• Запросил: {ctx.author}")

		if time == "1w":
			time = 604800
			mute=discord.Embed(title="🔇 | Мут", description=f"**Участник {member.mention} был успешно замучен.**", color=0xc10dd9, timestamp = ctx.message.created_at)
			mute.set_author(name=ctx.guild.name, url="https://discord.gg/Uqp32EwByH", icon_url=ctx.author.avatar_url)
			mute.set_thumbnail(url=ctx.guild.icon_url)
			mute.add_field(name="Замутил:", value=f"{ctx.author.mention}", inline=False)
			mute.add_field(name="Срок:", value="**`1 неделя`**", inline=True)
			mute.add_field(name="Причина:", value=f"**`{reason}`**", inline=True)
			mute.set_footer(text=f"• Запросил: {ctx.author}")

		if time == "2w":
			time = 1209600
			mute=discord.Embed(title="🔇 | Мут", description=f"**Участник {member.mention} был успешно замучен.**", color=0xc10dd9, timestamp = ctx.message.created_at)
			mute.set_author(name=ctx.guild.name, url="https://discord.gg/Uqp32EwByH", icon_url=ctx.author.avatar_url)
			mute.set_thumbnail(url=ctx.guild.icon_url)
			mute.add_field(name="Замутил:", value=f"{ctx.author.mention}", inline=False)
			mute.add_field(name="Срок:", value="**`2 недели`**", inline=True)
			mute.add_field(name="Причина:", value=f"**`{reason}`**", inline=True)
			mute.set_footer(text=f"• Запросил: {ctx.author}")

		if time == "3w":
			time = 1814400
			mute=discord.Embed(title="🔇 | Мут", description=f"**Участник {member.mention} был успешно замучен.**", color=0xc10dd9, timestamp = ctx.message.created_at)
			mute.set_author(name=ctx.guild.name, url="https://discord.gg/Uqp32EwByH", icon_url=ctx.author.avatar_url)
			mute.set_thumbnail(url=ctx.guild.icon_url)
			mute.add_field(name="Замутил:", value=f"{ctx.author.mention}", inline=False)
			mute.add_field(name="Срок:", value="**`3 недели`**", inline=True)
			mute.add_field(name="Причина:", value=f"**`{reason}`**", inline=True)
			mute.set_footer(text=f"• Запросил: {ctx.author}")

	try:
		await member.add_roles(muterole)
		await ctx.reply(embed=mute, mention_author=True)
		try:
			await logs.send(embed=mute)
		except: pass
		await ctx.message.add_reaction("👍")
	
	except Exception as e:
		await ctx.reply(f"```Ошибка выдачи роли. \nПроверьте права бота и переместите его выше мут-роли\n {e}```")
		print(e)
		return


	await asyncio.sleep(time)
	if muterole in member.roles:
		try:
			await member.remove_roles(muterole)
			unmute=discord.Embed(title="🔇 | Мут", description=f"**Срок мута у {member.mention} успешно завершился**", color=0xc10dd9, timestamp = ctx.message.created_at)
			unmute.set_author(name=ctx.guild.name, url="https://discord.gg/Uqp32EwByH", icon_url=member.avatar_url)
			unmute.add_field(name="Причина:", value=f"**`{reason}`**", inline=True)
			unmute.set_thumbnail(url=ctx.guild.icon_url)
			unmute.set_footer(text=f"•")
			
			await ctx.send(member.mention)
			await ctx.send(embed=unmute)
			try:
				await logs.send(embed=mute)
			except: pass
		
		except Exception as e:
			await ctx.reply(f"```Ошибка снятия роли. \nПроверьте права бота и переместите его выше мут-роли\n{e}```", mention_author=True)
			print(e)
			return

	else: return

@bot.command()
async def leave_guild(ctx,servid:discord.Guild):
	if ctx.author.id == 456790342512148481:
		if servid:
			try:
				await servid.leave()
				await ctx.reply(f"Я вышел с {servid}", mention_author=True)
			except: pass
	else: return

@bot.command()
@has_permissions(manage_messages=True)
async def unmute(ctx,member:discord.Member,*, reason="Не указана"):
	con.ping() 
	with con.cursor() as cur:
		try:
			cur.execute(f"SELECT roleid FROM muteroles WHERE serverid={ctx.guild.id}")
			rol = cur.fetchone()["roleid"]
		except:
			await ctx.reply("**Не указана мут-роль.** \nУказать: **`=config_muterole Роль`**", mention_author=True)
			return
	con.ping() 
	with con.cursor() as cur:
		try:
			cur.execute(f"SELECT channel_id FROM logs_channels WHERE serverid={ctx.guild.id}")
			l_chan = cur.fetchone()["channel_id"]
			logs = bot.get_channel(l_chan)
		except Exception as e:
			print(e)
			pass

	muterole = discord.utils.get(ctx.message.guild.roles, id=rol)

	if muterole in member.roles:
		try:
			unmute=discord.Embed(title="🔇 | Размут", description=f"**{member.mention} был успешно размучен.**", color=0xc10dd9, timestamp = ctx.message.created_at)
			unmute.set_author(name=ctx.guild.name, url="https://discord.gg/Uqp32EwByH", icon_url=member.avatar_url)
			unmute.add_field(name="Размутил:", value=f"{ctx.author.mention}", inline=True)
			unmute.add_field(name="Причина:", value=f"**`{reason}`**", inline=True)
			unmute.set_thumbnail(url=ctx.guild.icon_url)
			unmute.set_footer(text=f"•")
			
			await member.remove_roles(muterole)
			await ctx.message.add_reaction("👍")
			await ctx.reply(embed=unmute, mention_author=True)
			try:
				await logs.send(embed=unmute)
			except: pass
			return
		except:
			await ctx.reply(f"```Ошибка снятия роли. \nПроверьте права бота и переместите его выше мут-роли\n{e}```", mention_author=True)
			print(e)
			return
	else:
		unmuteerr=discord.Embed(title="❌ | Ошибка", description=f"**{member.mention} не имеет мута.**", color=0xc10dd9, timestamp = ctx.message.created_at)
		unmuteerr.set_author(name=ctx.guild.name, url="https://discord.gg/Uqp32EwByH", icon_url=member.avatar_url)
		unmuteerr.set_thumbnail(url=ctx.guild.icon_url)
		unmuteerr.set_footer(text=f"•")
		await ctx.message.add_reaction("❌")
		await ctx.reply(embed=unmuteerr, mention_author=True)

@bot.command()
async def mutelist(ctx):
	con.ping() 
	with con.cursor() as cur:
		try:
			cur.execute(f"SELECT roleid FROM muteroles WHERE serverid={ctx.guild.id}")
			rol = cur.fetchone()["roleid"]
		except:
			await ctx.reply("**Не указана мут-роль.** \nУказать: **`=config_muterole Роль`**", mention_author=True)
			return
	
	muterole = discord.utils.get(ctx.message.guild.roles, id=rol)
	
	server = ctx.message.guild
	await ctx.reply("🙈 | Список замученных участников", mention_author=True)    
	for member in server.members:
		if muterole in member.roles:
			await ctx.send(f">>> **{member} | ID: `{member.id}`**")	

@bot.command()
@has_permissions(manage_messages=True)
async def clear(ctx, amount: int, reason="Не указана"):
	con.ping() 
	with con.cursor() as cur:
		try:
			cur.execute(f"SELECT channel_id FROM logs_channels WHERE serverid={ctx.guild.id}")
			l_chan = cur.fetchone()["channel_id"]
			logs = bot.get_channel(l_chan)
		except Exception as e:
			print(e)
			pass
	guildname = ctx.guild.name
	avatar_urll = ctx.author.avatar_url
	if amount < 1:
		await ctx.reply("> ```Введите количество сообщений больше 0```", mention_author=True)
		await ctx.message.add_reaction("❌")
		return
	if amount > 100:
		await ctx.reply("> ```Введите количество сообщений меньше 100```", mention_author=True)
		await ctx.message.add_reaction("❌")
		return

	try:
		clr=discord.Embed(title="🧹 | Очистка сообщений", description=f"Очищено сообщений: **{amount}**", color=0xc10dd9, timestamp = ctx.message.created_at)
		clr.set_author(name=guildname, url="https://discord.gg/Uqp32EwByH", icon_url=avatar_urll)
		clr.add_field(name="Очистил: ", value=ctx.author.mention, inline=True)
		clr.add_field(name="Причина: ", value=f"**`{reason}`**", inline=True)
		clr.add_field(name="Канал: ", value=ctx.channel.mention)
		clr.set_thumbnail(url=ctx.guild.icon_url)
		clr.set_footer(text=f"• Запросил: {ctx.author}")

	
		await ctx.channel.purge(limit=amount)
		try:
			await logs.send(embed=clr)
		except: pass
		await ctx.send(embed=clr)
	except Exception as e:
			await ctx.reply(f"```Ошибка\nПроверьте права бота\n{e}```", mention_author=True)
			print(e)
			return

@bot.command()
@has_permissions(ban_members = True)
@commands.bot_has_permissions(ban_members=True)
async def ban(ctx,member:discord.Member=None,*,reason="Не указана"):
	if member == None: return await ctx.reply("```=ban Участник Причина```")

	con.ping() 
	with con.cursor() as cur:
		try:
			cur.execute(f"SELECT channel_id FROM logs_channels WHERE serverid={ctx.guild.id}")
			l_chan = cur.fetchone()["channel_id"]
			logs = bot.get_channel(l_chan)
		except Exception as e:
			print(e)
			pass
	reasons = f"{reason} By {ctx.author}"
	

	if member.id == ctx.author.id:
		smut=discord.Embed(title="❌ | Ошибка", description=f"```    Нельзя забанить самого себя    ```", color=0xbf1cd4, timestamp = ctx.message.created_at)
		smut.set_author(name=ctx.guild.name, url="https://discord.gg/Uqp32EwByH", icon_url=ctx.author.avatar_url)
		smut.set_footer(text=f"• Запросил: {ctx.author}")	 
		await ctx.reply(embed=smut, mention_author=True)
		await ctx.message.add_reaction("❌")
		return

	if member.bot == True:
		botban=discord.Embed(title="❌ | Ошибка", description=f"```    Нельзя забанить бота    ```", color=0xbf1cd4, timestamp = ctx.message.created_at)
		botban.set_author(name=ctx.guild.name, url="https://discord.gg/Uqp32EwByH", icon_url=ctx.author.avatar_url)
		botban.set_footer(text=f"• Запросил: {ctx.author}")	 
		await ctx.reply(embed=botban, mention_author=True)
		await ctx.message.add_reaction("❌")
		return
	
	if ctx.author.top_role.position <= member.top_role.position:
		topro=discord.Embed(title="❌ | Ошибка", description=f"**```Вы не можете забанить человека, чья роль выше или равна вашей```**", color=0xbf1cd4, timestamp = ctx.message.created_at)
		topro.set_author(name=ctx.guild.name, url="https://discord.gg/Uqp32EwByH", icon_url=ctx.author.avatar_url)
		topro.set_footer(text=f"• Запросил: {ctx.author}")	 
		await ctx.reply(embed=topro, mention_author=True)
		await ctx.message.add_reaction("❌")		
		return

	bann=discord.Embed(title="🔪 | Бан", description=f"**Участник {member.mention} был успешно забанен.\nID Участника: `{member.id}`**", color=0xc10dd9)
	bann.set_author(name=ctx.guild.name, url="https://discord.gg/Uqp32EwByH", icon_url=ctx.author.avatar_url)
	bann.set_thumbnail(url=ctx.guild.icon_url)
	bann.add_field(name="Забанил:", value=f"{ctx.author.mention}", inline=False)
	bann.add_field(name="Причина:", value=f"**`{reason}`**", inline=True)
	bann.set_footer(text=f"• Запросил: {ctx.author}")

	mesbann=discord.Embed(title="🔪 | Бан", description=f"**Вы были забанены на сервере {ctx.guild.name}**", color=0xc10dd9)
	mesbann.set_author(name=ctx.guild.name, url="https://discord.gg/Uqp32EwByH", icon_url=ctx.author.avatar_url)
	mesbann.set_thumbnail(url=ctx.guild.icon_url)
	mesbann.add_field(name="Забанил:", value=f"{ctx.author.mention}", inline=False)
	mesbann.add_field(name="Причина:", value=f"**`{reason}`**", inline=True)
	mesbann.set_footer(text=f"• По вопросам писать -> Rienn0#4187")

	try:
		await member.send(embed=mesbann)
	except: pass

	try:
		await ctx.guild.ban(member, reason=reasons)
		await ctx.message.add_reaction("👍")
		try:
			await logs.send(embed=bann)
		except: pass
		await ctx.reply(embed=bann)
	except Exception as e:
		await ctx.reply(f"```Ошибка\nПроверьте права бота\n{e}```")
		return

@bot.command()
@has_permissions(ban_members = True)
async def unban(ctx, *, member):
	banned_users = await ctx.guild.bans()
	member_name, member_discriminator = member.split('#')
	con.ping() 
	with con.cursor() as cur:
		try:
			cur.execute(f"SELECT channel_id FROM logs_channels WHERE serverid={ctx.guild.id}")
			l_chan = cur.fetchone()["channel_id"]
			logs = bot.get_channel(l_chan)
		except Exception as e:
			print(e)
			pass
	
	for ban_entry in banned_users:
		user = ban_entry.user

		if (user.name, user.discriminator) == (member_name, member_discriminator):
			try:
				await ctx.guild.unban(user, reason=f"by {ctx.author}")
				await ctx.message.add_reaction("👍")
    
				unbann=discord.Embed(title="🙀 | Разбан", description=f"**Модератор {ctx.author.mention} разбанил {user.mention}**", color=0xc10dd9, timestamp = ctx.message.created_at)
				unbann.set_author(name=ctx.guild.name, url="https://discord.gg/Uqp32EwByH", icon_url=ctx.author.avatar_url)
				unbann.set_thumbnail(url=ctx.guild.icon_url)
				unbann.set_footer(text=f"• Запросил: {ctx.author}")
			
				await ctx.reply(embed=unbann, mention_author=True)
				try:
					await logs.send(embed=unbann)
				except: pass
			except Exception as e:
				await ctx.reply(f"```Ошибка\nПроверьте права бота\n{e}```", mention_author=True)
				print(e)
				return

@bot.command()
async def banlist(ctx):
	bans = await ctx.guild.bans()
	loop = [f"{u[1]} (ID: {u[1].id})" for u in bans]
	_list = "\r\n".join([f"[{str(num).zfill(2)}] {data}" for num, data in enumerate(loop, start=1)])
	await ctx.send(f"**:gem: Список забаненых участников {ctx.guild.name}**\n```\n{_list}```")

@unban.error
async def unban_error(ctx,error):
	if isinstance(error, commands.CheckFailure):
		await ctx.reply("```У вас нет прав на выполнение этой команды```", mention_author=True)
	if isinstance(error, commands.MissingRequiredArgument):
		await ctx.reply("```=unban Ник#Дискриминатор```", mention_author=True)
		
@clear.error
async def clear_error(ctx,error):
	if isinstance(error, commands.CheckFailure):
		await ctx.reply("```У вас нет прав на выполнение этой команды```", mention_author=True)
	if isinstance(error, commands.MissingRequiredArgument):
		await ctx.reply("```=clear Кол-во сообщений``` -- **Очистка сообщений без указания причины**", mention_author=True)
		await ctx.send("```=clear Кол-во сообщений Причина``` -- **Очистка сообщений с указанием причины**")

@mute.error
async def mute_error(ctx, error):
	if isinstance(error, commands.CheckFailure):
		await ctx.reply("```У вас нет прав на выполнение этой команды```", mention_author=True)
	if isinstance(error, commands.MissingRequiredArgument):
		await ctx.reply("```=mute @Участник Срок``` -- **Мут без указания причины**", mention_author=True)
		await ctx.send("```=mute @Участник Срок Причина``` -- **Мут с указанием причины**")

@ban.error
async def ban_error(ctx, error):
	if isinstance(error, commands.BotMissingPermissions):
		return await ctx.reply("```Боту необходимо право BAN_MEMBERS для выполнения этой команды```")
	if isinstance(error, commands.CheckFailure):
		return await ctx.reply("```У вас нет прав на выполнение этой команды```", mention_author=True)

@unmute.error
async def unmute_error(ctx, error):
	if isinstance(error, commands.CheckFailure):
		await ctx.reply("```У вас нет прав на выполнение этой команды```", mention_author=True)
	if isinstance(error, commands.MissingRequiredArgument):
		await ctx.reply("```=unmute @Участник``` -- **Размут без указания причины**", mention_author=True)
		await ctx.send("```=unmute @Участник Причина``` -- **Размут с указанием причины**")

@bot.command()
async def radex(ctx):
	bt = bot.get_user(919925918024232970)	

	st = discord.Embed(title="📟 | RadexBot", color=0xbf1cd4,description="[Веб-сайт](https://radexbot.xyz/) | [Пригласить](https://discord.com/oauth2/authorize?client_id=919925918024232970&permissions=8&scope=bot) | [Проголосовать](https://boticord.top/bot/919925918024232970)")
	st.add_field(name="Сервера",value=f"**`{len(bot.guilds)}`**",inline=True)
	st.add_field(name="Команды",value=f"**`{len(bot.commands)}`**",inline=True)
	st.add_field(name="Задержка",value=f"**`{round(bot.latency * 1000)} мс`**")
	st.set_author(name=ctx.guild.name, url="https://discord.gg/Uqp32EwByH", icon_url=ctx.author.avatar_url)
	st.set_thumbnail(url=bt.avatar_url)
	st.set_footer(text=f"• Разработчик -> Rienn0#4187")

	await ctx.reply(embed=st, mention_author=True)

@bot.command()
async def test(ctx): await ctx.reply(f"Задержка: **{round(bot.latency * 1000)} мс**", mention_author=True)

@bot.command()
async def guru(ctx,*,answer):
	qs = ["Ответ: Да! ✅ ","Ответ: Может быть 🤨", "Ответ: Вероятно 😮", "Ответ: Довольно маленький шанс 👆","Ответ: Пиздец маленький шанс 😱😱", "Ответ: Неттт 😎 😩 😧"]

	embed=discord.Embed(title="🤠 | Вопрос у Гуру", description=f"**Вопрос: `{answer}`**\n\n**{random.choice(qs)}**", color=0xbf1cd4, timestamp = ctx.message.created_at)
	embed.set_author(name=ctx.guild.name, url="https://discord.gg/Uqp32EwByH", icon_url=ctx.author.avatar_url)
	embed.set_thumbnail(url=ctx.guild.icon_url)
	embed.set_footer(text=f"• Запросил: {ctx.author}")
	await ctx.reply(embed=embed, mention_author=True)	 	

@bot.command()
async def say(ctx,zagol,*,text):
	embed=discord.Embed(title=f"{zagol}", description=f"{text}", color=0xbf1cd4, timestamp = ctx.message.created_at)
	embed.set_author(name=ctx.guild.name, url="https://discord.gg/Uqp32EwByH", icon_url=ctx.author.avatar_url)
	embed.set_footer(text=f"• Запросил: {ctx.author}")
	await ctx.reply(embed=embed, mention_author=True)


@bot.command()
@commands.cooldown(1, 10, commands.BucketType.user)
async def picture(ctx,*,search):
	url = f"https://pixabay.com/api/?key=25302167-a0b099d9c680790490a967ff0&q={search}&image_type=photo&per_page=200&pretty=true"
	req = requests.get(url) 
	total = req.json()["totalHits"]
	
	if total < 200:
		totalimg = total - 1
	
	elif total >= 200:
		totalimg = 200

	embed1=discord.Embed(title=f"👀 | Поиск картинки",description=f"**{ctx.author.mention}, изображение по запросу `{search}` не найдено**", color=0xbf1cd4, timestamp = ctx.message.created_at)
	embed1.set_author(name=ctx.guild.name, url="https://discord.gg/Uqp32EwByH", icon_url=ctx.author.avatar_url)
	embed1.set_footer(text=f"• Запросил: {ctx.author}")
	
	if total == 0:
		await ctx.reply(embed=embed1, mention_author=True)
		picture.reset_cooldown(ctx)
		return

	hit = random.randint(0,totalimg)

	dicts = req.json()["hits"]
	s = json.dumps(dicts)
	image = json.loads(s)

	embed=discord.Embed(title=f"👀 | Поиск картинки [{hit}/{totalimg}]", color=0xbf1cd4, timestamp = ctx.message.created_at)
	embed.set_author(name=ctx.guild.name, url="https://discord.gg/Uqp32EwByH", icon_url=ctx.author.avatar_url)
	embed.set_image(url=image[hit]["largeImageURL"])
	embed.set_footer(text=f"• Запросил: {ctx.author}")
	await ctx.reply(embed=embed, mention_author=True)

@bot.command()
async def avatar(ctx,member:discord.User=None):
	if member == None:
		member = ctx.author

	embed =	discord.Embed(title=f"Аватар Пользователя {member}", color=0xbf1cd4, timestamp = ctx.message.created_at)
	embed.set_image(url=member.avatar_url)
	await ctx.reply(embed=embed, mention_author=True)

@avatar.error
async def avatar_error(ctx,error):
	if isinstance(error, commands.UserNotFound):
		return await ctx.reply("```Участник не найден\n=avatar Участник```", mention_author=True)

@bot.command()
async def send(ctx,member:discord.Member=None,*,msgg=None):
	try:
		await ctx.message.delete()
	except: pass

	if member == None:
		await ctx.send("```=send Участник Сообщение```")
		return
	if msgg == None:
		await ctx.send("```=send Участник Сообщение```")
		return
	
	text = f"Вам пришло анонимное сообщение с сервера {ctx.guild.name}\nТекст сообщения: **{msgg}**"

	try:
		await member.send(text)
		await ctx.send(f"```Сообщение было отправлено {member}```")
	except:
		return await ctx.send(f"```Нет прав отправить сообщение {member}```") 	
	
@bot.command()
async def server(ctx):

	original_data = ctx.guild.created_at.strftime('%#d %B %Y')

	data = original_data.split(" ")

	if data[1] == "January": month = "января"
	if data[1] == "February": month = "февраля"
	if data[1] == "March": month = "марта"
	if data[1] == "April": month = "апреля"
	if data[1] == "May": month = "мая"
	if data[1] == "June": month = "июня"
	if data[1] == "July": month = "июля"
	if data[1] == "August": month = "августа"
	if data[1] == "September": month = "сентября"
	if data[1] == "October": month = "октября"
	if data[1] == "November": month = "ноября"
	if data[1] == "December": month = "декабря"


	embed=discord.Embed(title=f"🔎 | Информация о сервере {ctx.guild.name}", description=f"**Владелец сервера: {ctx.guild.owner.mention}**", color=0xbf1cd4, timestamp = ctx.message.created_at)
	embed.add_field(name="💬 | Каналы: ",value=f"**Текстовые:** **`{len(ctx.guild.text_channels)}`**\n**Голосовые:** **`{len(ctx.guild.voice_channels)}`**\n**Всего:** **`{len(ctx.guild.channels)}`\nКатегории: `{len(ctx.guild.categories)}`**",inline=True)
	embed.add_field(name="👥 | Участники: ",value=f"**Люди: `{sum(not member.bot for member in ctx.guild.members)}`\nБоты: `{sum(member.bot for member in ctx.guild.members)}`\nВсего: `{ctx.guild.member_count}`**")
	embed.add_field(name="💎 | Бусты сервера:",value=f"**Уровень буста: `{ctx.guild.premium_tier}/3`\nВсего бустов: `{ctx.guild.premium_subscription_count}/14`**")
	embed.add_field(name="🔧 | Другое: ",value=f"**Количество ролей: `{len(ctx.guild.roles)}`\nДата создания: `{data[0]} {month} {data[2]}`\nID Сервера: `{ctx.guild.id}`**")
	
	embed.set_author(name=ctx.guild.name, url="https://discord.gg/Uqp32EwByH", icon_url=ctx.author.avatar_url)
	embed.set_thumbnail(url=ctx.guild.icon_url)
	embed.set_image(url=ctx.guild.banner_url)
	embed.set_footer(text=f"• Запросил: {ctx.author}")
	await ctx.reply(embed=embed, mention_author=True)

@bot.command()
async def setbio(ctx,*,bi=None):
	if bi == None:
		await ctx.reply("```=setbio Текст```", mention_author=True)
		return

	con.ping()
	with con.cursor() as cur:
		cur.execute(f"SELECT member_id FROM bio WHERE member_id={ctx.author.id}")
		if cur.fetchone() == None:
			cur.execute(f"INSERT INTO bio (serverid, member_id, member_name, bio) VALUES ( {ctx.guild.id} , {ctx.author.id} , '{ctx.author.name}' , '{bi}' )")
		else:
			cur.execute(f"DELETE FROM bio WHERE member_id={ctx.author.id}")
			cur.execute(f"INSERT INTO bio (serverid, member_id, member_name, bio) VALUES ( {ctx.guild.id} , {ctx.author.id} , '{ctx.author.name}' , '{bi}' )")

		emd = discord.Embed(title="📝 | Информация о себе",description=f"**Информация о себе успешно сменена, введите `=about`**\n\n{bi}", color=0xbf1cd4, timestamp = ctx.message.created_at)
		emd.set_author(name=ctx.guild.name, url="https://discord.gg/Uqp32EwByH", icon_url=ctx.author.avatar_url)
		emd.set_footer(text=f"• Запросил: {ctx.author}")	
		await ctx.reply(embed=emd, mention_author=True)
		con.commit()

@bot.command()
async def setimg(ctx,url=None):
	if url == None:
		await ctx.reply("```=setimg Ссылка на изображение/гифку```", mention_author=True)
		return
	try:
		r = requests.get(url)
		r_code = r.status_code

		if r_code == 200:
			con.ping()
			with con.cursor() as cur:
				cur.execute(f"SELECT member_id FROM images WHERE member_id={ctx.author.id}")
				if cur.fetchone() == None:
					cur.execute(f"INSERT INTO images (serverid, member_id, member_name, url) VALUES ( {ctx.guild.id} , {ctx.author.id} , '{ctx.author.name}' , '{url}' )")
				else:
					cur.execute(f"DELETE FROM images WHERE member_id={ctx.author.id}")
					cur.execute(f"INSERT INTO images (serverid, member_id, member_name, url) VALUES ( {ctx.guild.id} , {ctx.author.id} , '{ctx.author.name}' , '{url}' )")

			emd = discord.Embed(title="📝 | Настройка профиля ( =about )",description=f"**Информация о себе успешно сменена, введите `=about`**", color=0xbf1cd4, timestamp = ctx.message.created_at)
			emd.set_author(name=ctx.guild.name, url="https://discord.gg/Uqp32EwByH", icon_url=ctx.author.avatar_url)
			emd.set_image(url=url)
			emd.set_footer(text=f"• Запросил: {ctx.author}")	
			await ctx.reply(embed=emd, mention_author=True)
			con.commit()
		else:
			await ctx.reply("```Ошибка. Введите нормальную ссылку.```", mention_author=True)
			return
	except Exception as e:
		print(e)
		await ctx.reply(f"```Ошибка. Введите нормальную ссылку.\n{e}```", mention_author=True)
		return

@bot.command(aliases=["about","info","profile"])
async def __about(ctx,member : discord.Member=None):
	if member is None:
		member = ctx.author
	
	with con.cursor() as cur:
		try:
			cur.execute(f"SELECT bio FROM bio WHERE member_id={member.id}")
			a_bi = cur.fetchone()["bio"]
		except:
			a_bi = ""

	with con.cursor() as cur:
		try:
			cur.execute(f"SELECT url FROM images WHERE member_id={member.id}")
			img = cur.fetchone()["url"]
		except:
			img = "https://radexbot.xyz"

	original_data = member.created_at.strftime("%a %#d %B %Y")

	data = original_data.split(" ")

	if data[0] == "Mon": day = "Понедельник,"
	if data[0] == "Tue": day = "Вторник,"
	if data[0] == "Wed": day = "Среда,"
	if data[0] == "Thu": day = "Четверг,"
	if data[0] == "Fri": day = "Пятница,"
	if data[0] == "Sat": day = "Суббота,"
	if data[0] == "Sun": day = "Воскресенье,"

	if data[2] == "January": month = "января"
	if data[2] == "February": month = "февраля"
	if data[2] == "March": month = "марта"
	if data[2] == "April": month = "апреля"
	if data[2] == "May": month = "мая"
	if data[2] == "June": month = "июня"
	if data[2] == "July": month = "июля"
	if data[2] == "August": month = "августа"
	if data[2] == "September": month = "сентября"
	if data[2] == "October": month = "октября"
	if data[2] == "November": month = "ноября"
	if data[2] == "December": month = "декабря"
	
	original_datat = member.joined_at.strftime("%a %#d %B %Y")

	datat = original_datat.split(" ")

	if datat[0] == "Mon": dayt = "Понедельник,"
	if datat[0] == "Tue": dayt = "Вторник,"
	if datat[0] == "Wed": dayt = "Среда,"
	if datat[0] == "Thu": dayt = "Четверг,"
	if datat[0] == "Fri": dayt = "Пятница,"
	if datat[0] == "Sat": dayt = "Суббота,"
	if datat[0] == "Sun": dayt = "Воскресенье,"

	if datat[2] == "January": montht = "января"
	if datat[2] == "February": montht = "февраля"
	if datat[2] == "March": montht = "марта"
	if datat[2] == "April": montht = "апреля"
	if datat[2] == "May": montht = "мая"
	if datat[2] == "June": montht = "июня"
	if datat[2] == "July": montht = "июля"
	if datat[2] == "August": montht = "августа"
	if datat[2] == "September": montht = "сентября"
	if datat[2] == "October": montht = "октября"
	if datat[2] == "November": montht = "ноября"
	if datat[2] == "December": montht = "декабря"


	embed=discord.Embed(title=f" 🔎 | Информация о {member} ", description=f"**Никнейм: `{member.display_name}`**\n**Дискриминант: `#{member.discriminator}`\nID Пользователя: `{member.id}`**\n\n{a_bi}", color=0xbf1cd4, timestamp = ctx.message.created_at)
	embed.set_author(name=ctx.guild.name, url="https://discord.gg/Uqp32EwByH", icon_url=ctx.guild.icon_url)
	embed.add_field(name="Присоединился: ", value=f"**`{dayt} {datat[1]} {montht} {datat[3]}`**", inline=True)
	embed.add_field(name="Регистрация Аккаунта: ",value=f"**`{day} {data[1]} {month} {data[3]}`**", inline=True)
	
	activit = member.status
	if activit == discord.Status.online:
		act = "🟢 | В сети"
	if activit == discord.Status.offline:
		act = "⚫️ | Не в сети"
	if activit == discord.Status.idle:
		act = "🌙 | Не активен"
	if activit == discord.Status.dnd:
		act = "⛔️ | Не беспокоить"

	embed.add_field(name="Активность: ",value=act, inline=False)
	
	if member.activity == None:
		stat = "**`Не Указан`**"
	else:
		stat = member.activities[0].name
	
	m = "**`Не замужем`**"
	
	con.ping() 
	with con.cursor() as cur:
		try:
			cur.execute(f"SELECT member_2_id,timestamp FROM marries WHERE member_1_id={member.id} AND serverid={ctx.guild.id}")
			fho = cur.fetchone()
			
			tms = fho["timestamp"]
			m2 = bot.get_user(fho["member_2_id"]).mention

			tim = round(time.time() - tms)
			time_format = time.strftime("%W д : %H час : %M мин : %S сек", time.gmtime(tim))

			m = " В браке с " + m2 + f"\nВремя брака: **`{time_format}`**"
		except Exception as e:
			pass
	
	con.ping()
	with con.cursor() as cur:
		try:
			cur.execute(f"SELECT member_1_id,timestamp FROM marries WHERE member_2_id={member.id} AND serverid={ctx.guild.id}")
			fho = cur.fetchone()
			
			tms = fho["timestamp"]
			m2 = bot.get_user(fho["member_1_id"]).mention

			tim = round(time.time() - tms) 
			time_format = time.strftime("%W д : %H час : %M мин : %S сек", time.gmtime(tim))
			
			m = " В браке с " + m2 + f"\nВремя брака: **`{time_format}`**"
		except Exception as e:
			pass

	embed.add_field(name="Уникальный статус: ", value=stat, inline=False)
	embed.add_field(name="Роль: ",value=member.top_role.mention, inline=True)
	embed.add_field(name="Позиция роли: ",value=member.top_role.position, inline=True)
	embed.add_field(name="Семейное положение: ",value=m,inline=False)
	embed.set_thumbnail(url=member.avatar_url)
	embed.set_image(url=img)
	embed.set_footer(text=f"• Запросил: {ctx.author}")
	await ctx.reply(embed=embed, mention_author=True)

@bot.command()
@commands.cooldown(1, 10, commands.BucketType.user)
async def boobs(ctx):
	if ctx.message.channel.is_nsfw():
		searches = random.choice(["boobs","hboobs"])
		req = requests.get("https://nekobot.xyz/api/image?type=boobs") 
		image = req.json()	

		embed=discord.Embed(title=f"👀 | Поиск картинки", color=0xbf1cd4, timestamp = ctx.message.created_at)
		embed.set_author(name=ctx.guild.name, url="https://discord.gg/Uqp32EwByH", icon_url=ctx.author.avatar_url)
		embed.set_image(url=image["message"])
		embed.set_footer(text=f"• Запросил: {ctx.author}")

		await ctx.reply(embed=embed, mention_author=True)
	else:
		await ctx.reply("Данную команду можно использовать только в NSFW-канале", mention_author=True)
		boobs.reset_cooldown(ctx)
	
@bot.command()
@commands.cooldown(1, 10, commands.BucketType.user)
async def ass(ctx):
	if ctx.message.channel.is_nsfw():
		searches = random.choice(["ass","pussy","hanal","hass"])
		url = f"https://nekobot.xyz/api/image?type={searches}"
		req = requests.get(url) 
		image = req.json()

		embed=discord.Embed(title=f"👀 | Поиск картинки", color=0xbf1cd4, timestamp = ctx.message.created_at)
		embed.set_author(name=ctx.guild.name, url="https://discord.gg/Uqp32EwByH", icon_url=ctx.author.avatar_url)
		embed.set_image(url=image["message"])
		embed.set_footer(text=f"• Запросил: {ctx.author}")

		await ctx.reply(embed=embed, mention_author=True)
			
	else:
		await ctx.reply("Данную команду можно использовать только в NSFW-канале", mention_author=True)
		ass.reset_cooldown(ctx)

@bot.command()
@commands.cooldown(1, 10, commands.BucketType.user)
async def nsfw(ctx):
	if ctx.message.channel.is_nsfw():
		searches = random.choice(['hass','hmidriff','pgif','4k','hentai','holo','hneko','hkitsune','anal','hanal','gonewild','ass','pussy','paizuri','tentacle','hboobs'])
		url = f"https://nekobot.xyz/api/image?type={searches}"
		req = requests.get(url) 
		image = req.json()

		embed=discord.Embed(title=f"👀 | Поиск картинки",description=searches, color=0xbf1cd4, timestamp = ctx.message.created_at)
		embed.set_author(name=ctx.guild.name, url="https://discord.gg/Uqp32EwByH", icon_url=ctx.author.avatar_url)
		embed.set_image(url=image["message"])
		embed.set_footer(text=f"• Запросил: {ctx.author}")

		await ctx.reply(embed=embed, mention_author=True)
			
	else:
		await ctx.reply("Данную команду можно использовать только в NSFW-канале", mention_author=True)
		sexy.reset_cooldown(ctx)

@bot.command()
@commands.cooldown(1, 10, commands.BucketType.user)
async def anime(ctx):
	if ctx.message.channel.is_nsfw():
		searches = random.choice(['hentai','hboobs','hanal','paizuri','hmidriff','hneko','hkitsune',"hthigh"])
		url = f"https://nekobot.xyz/api/image?type={searches}"
		req = requests.get(url) 
		image = req.json()

		embed=discord.Embed(title=f"👀 | Поиск картинки",description=searches, color=0xbf1cd4, timestamp = ctx.message.created_at)
		embed.set_author(name=ctx.guild.name, url="https://discord.gg/Uqp32EwByH", icon_url=ctx.author.avatar_url)
		embed.set_image(url=image["message"])
		embed.set_footer(text=f"• Запросил: {ctx.author}")

		await ctx.reply(embed=embed, mention_author=True)
			
	else:
		await ctx.reply("Данную команду можно использовать только в NSFW-канале", mention_author=True)
		anime.reset_cooldown(ctx)

@nsfw.error
async def nsfw_error(ctx,error):
	if isinstance(error, commands.CommandOnCooldown):
		time = str(round(error.retry_after, 2))

		if time < str(1):
			tim = time + " секунду"
		if time < str(5):
			tim = time + " секунды"
		if time >= str(5):
			tim = time + " секунд"

		await ctx.reply(f'**{ctx.author.mention}, эту команду можно использовать через `{tim}`**', mention_author=True)

@boobs.error
async def boobs_error(ctx,error):
	if isinstance(error, commands.CommandOnCooldown):
		time = str(round(error.retry_after, 2))

		if time < str(1):
			tim = time + " секунду"
		if time < str(5):
			tim = time + " секунды"
		if time >= str(5):
			tim = time + " секунд"

		await ctx.reply(f'**{ctx.author.mention}, эту команду можно использовать через `{tim}`**', mention_author=True)

@ass.error
async def ass_error(ctx,error):
	if isinstance(error, commands.CommandOnCooldown):
		time = str(round(error.retry_after, 2))

		if time < str(1):
			tim = time + " секунду"
		if time < str(5):
			tim = time + " секунды"
		if time >= str(5):
			tim = time + " секунд"

		await ctx.reply(f'**{ctx.author.mention}, эту команду можно использовать через `{tim}`**', mention_author=True)

@say.error
async def say_error(ctx,error):
	if isinstance(error,commands.MissingRequiredArgument):
		await ctx.reply("```=say Заголовок Текст```")

@guru.error
async def guru_error(ctx, error):
	if isinstance(error, commands.MissingRequiredArgument):
		await ctx.reply("```=guru Вопрос```")

@__about.error
async def __about_error(ctx,error):
	if isinstance(error, commands.MissingRequiredArgument):
		await ctx.reply("```=about @Участник``` -- **Показать информацию о @Участник**", mention_author=True)
		await ctx.send("```=about ``` - **Показать информацию о себе**")
	if isinstance(error, commands.MemberNotFound):
		await ctx.reply("```=about @Участник``` -- **Показать информацию о @Участник**", mention_author=True)
		await ctx.send("```=about ``` - **Показать информацию о себе**")

@picture.error
async def picture_error(ctx,error):
	if isinstance(error, commands.MissingRequiredArgument):
		await ctx.reply("```=picture Запрос``` -- **Поиск картинки по запросу**", mention_author=True)
		picture.reset_cooldown(ctx)
	if isinstance(error, commands.CommandOnCooldown):
		time = str(round(error.retry_after, 2))

		if time < str(1):
			tim = time + " секунду"
		if time < str(5):
			tim = time + " секунды"
		if time >= str(5):
			tim = time + " секунд"

		await ctx.reply(f'**{ctx.author.mention}, эту команду можно использовать через `{tim}`**', mention_author=True)

@bot.command()
async def create_invite(ctx, server_id: int=None):
	if server_id == None: return await ctx.send("Введи ID сервера. Кста доступно только Rienn0")
	if ctx.author.id == 456790342512148481:
		guild = bot.get_guild(server_id)
		invite = await guild.text_channels[0].create_invite(max_age=300, max_uses=100, temporary=False)
		await ctx.send(f"https://discord.gg/{invite.code}")
	else: return await ctx.reply("не обязан :-1:")

@bot.command()
@commands.cooldown(1, 10, commands.BucketType.user)
async def kiss(ctx, member:discord.Member=None):
	if member == None:
		await ctx.reply("```Укажи Пользователя```", mention_author=True)
		kiss.reset_cooldown(ctx)
		return
	if member == ctx.author: 
		await ctx.reply("```Укажи Пользователя. На себе нельзя```", mention_author=True)
		kiss.reset_cooldown(ctx)
		return

	acts = random.choice([" поцеловал "," засосал "," засосал с языком ", " поцеловал в щечку "])
	gifs = random.choice(["https://c.tenor.com/wDYWzpOTKgQAAAAC/anime-kiss.gif", "https://c.tenor.com/el8DHxNp9IsAAAAC/kiss-anime-love.gif", "https://c.tenor.com/16MBIsjDDYcAAAAC/love-cheek.gif", "https://c.tenor.com/F02Ep3b2jJgAAAAC/cute-kawai.gif"])

	emb = discord.Embed(title="💋 | Поцелуй", description=f"**{ctx.author.mention}{acts}{member.mention}**", color=0xbf1cd4, timestamp = ctx.message.created_at)
	emb.set_author(name=ctx.guild.name, url="https://discord.gg/Uqp32EwByH", icon_url=ctx.author.avatar_url)
	emb.set_image(url=gifs)
	emb.set_footer(text=f"• Запросил: {ctx.author}")

	await ctx.send(embed=emb)

@bot.command()
@commands.cooldown(1, 10, commands.BucketType.user)
async def fight(ctx,member:discord.Member=None):
	if member == None:
		await ctx.reply("```Укажи Пользователя```", mention_author=True)
		return 
	if member == ctx.author: 
		await ctx.reply("```Укажи Пользователя. На себе нельзя```", mention_author=True)
		fight.reset_cooldown(ctx)
		return

	gifs = random.choice(["https://c.tenor.com/Qs9NYCf1b4YAAAAM/shida-midori-midori.gif","https://c.tenor.com/OTqIFOVS7OkAAAAS/ora.gif","https://c.tenor.com/PLNYW7jBkUsAAAAC/jojos-bizarre-adventure-anime.gif","https://c.tenor.com/LytxJSf81m4AAAAC/ora-beatdown-oraoraora.gif","https://c.tenor.com/ucmhE4FHoFcAAAAC/fight-smash.gif", "https://c.tenor.com/w3_5V8KfRO4AAAAC/kick-anime.gif", "https://c.tenor.com/EdV_frZ4e_QAAAAC/anime-naruto.gif", "https://c.tenor.com/pGW875D5IEwAAAAd/anime-pillow-fight.gif"])
	acts = random.choice([" ударил ", " ударил по лицу ", " избил ", " избил до полусмерти "])


	emb = discord.Embed(title="👊  | Удар", description=f"**{ctx.author.mention}{acts}{member.mention}**", color=0xbf1cd4, timestamp = ctx.message.created_at)
	emb.set_author(name=ctx.guild.name, url="https://discord.gg/Uqp32EwByH", icon_url=ctx.author.avatar_url)
	emb.set_image(url=gifs)
	emb.set_footer(text=f"• Запросил: {ctx.author}")

	await ctx.send(embed=emb)

@bot.command()
@commands.cooldown(1, 10, commands.BucketType.user)
async def slap(ctx,member:discord.Member=None):
	if member == None:
		await ctx.reply("```Укажи Пользователя```", mention_author=True)
		return 
	if member == ctx.author: 
		await ctx.reply("```Укажи Пользователя. На себе нельзя```", mention_author=True)
		slap.reset_cooldown(ctx)
		return

	gifs = random.choice(["https://c.tenor.com/XiYuU9h44-AAAAAC/anime-slap-mad.gif","https://c.tenor.com/Ws6Dm1ZW_vMAAAAC/girl-slap.gif","https://c.tenor.com/E3OW-MYYum0AAAAC/no-angry.gif","https://c.tenor.com/eU5H6GbVjrcAAAAC/slap-jjk.gif","https://c.tenor.com/PeJyQRCSHHkAAAAC/saki-saki-mukai-naoya.gif"])
	acts = random.choice([" дал пощечину ", " ударил по щеке ", " щлепнул ", " сильно ударил по щеке "])

	emb = discord.Embed(title=":raised_hand: | Пощечина", description=f"**{ctx.author.mention}{acts}{member.mention}**", color=0xbf1cd4, timestamp = ctx.message.created_at)
	emb.set_author(name=ctx.guild.name, url="https://discord.gg/Uqp32EwByH", icon_url=ctx.author.avatar_url)
	emb.set_image(url=gifs)
	emb.set_footer(text=f"• Запросил: {ctx.author}")

	await ctx.send(embed=emb)

@bot.command()
async def marry(ctx,member:discord.Member=None):
	
	if member == None: return await ctx.reply("```=marry Участник```", mention_author=True)
	if member == ctx.author: return await ctx.reply("```Нельзя жениться на себе```", mention_author=True)
	if member.bot == True: return await ctx.reply("```Нельзя жениться на боте```", mention_author=True)
	
	con.ping() 
	with con.cursor() as cur:
		cur.execute(f"SELECT member_1_id FROM marries WHERE member_1_id={ctx.author.id} AND serverid={ctx.guild.id}")
		if cur.fetchone() == None: 
			pass
		else: 
			await ctx.reply("```Вы уже женаты. Развестить: =divorce```", mention_author=True)
			return

	con.ping() 
	with con.cursor() as cur:
		cur.execute(f"SELECT member_2_id FROM marries WHERE member_2_id={ctx.author.id} AND serverid={ctx.guild.id}")
		if cur.fetchone() == None: 
			pass
		else: 
			await ctx.reply("```Вы уже женаты. Развестить: =divorce```", mention_author=True)
			return	

	con.ping() 
	with con.cursor() as cur:
		cur.execute(f"SELECT member_1_id FROM marries WHERE member_1_id={member.id} AND serverid={ctx.guild.id}")
		if cur.fetchone() == None: 
			pass
		else: 
			await ctx.reply(f"```{member.nick} уже в бракосочетании ```", mention_author=True)
			return


	con.ping() 
	with con.cursor() as cur:
			cur.execute(f"SELECT member_2_id FROM marries WHERE member_2_id={member.id} AND serverid={ctx.guild.id}")
			if cur.fetchone() == None: 
				pass
			else: 
				await ctx.reply(f"```{member.nick} уже в бракосочетании```", mention_author=True)
				return

	
	yes = '✅'
	no = '❌'
	valid_reactions = ['✅' , '❌']
		
	em=discord.Embed(title="💍 | Свадьба",description=f"**{ctx.author.mention} попросил(а) руку и сердце у {member.mention}.**", color=0xbf1cd4, timestamp = ctx.message.created_at)
	em.set_author(name=ctx.guild.name, url="https://discord.gg/Uqp32EwByH", icon_url=ctx.author.avatar_url)
	em.set_image(url="https://c.tenor.com/dN7YwB1OLZ8AAAAC/ring-anime-wedding.gif")
	em.set_footer(text=f"• Запросил: {ctx.author}")		

	mar = await ctx.reply(embed=em, mention_author=True)
	await mar.add_reaction(yes)
	await mar.add_reaction(no)

	def check(reaction, user):
		return user == member and str(reaction.emoji) in valid_reactions
	
	try:
		reaction, user = await bot.wait_for('reaction_add', timeout=60.0, check=check)
	except asyncio.TimeoutError:
		await ctx.reply(f"{ctx.author.mention}, {member.mention} не ответил на ваше предложение, время вышло.", mention_author=True)
		await mar.delete()
		return

	if str(reaction.emoji) == yes:
		con.ping() 
		with con.cursor() as cur:
			cur.execute(f"INSERT INTO marries (serverid , member_1_id , member_1_name , member_2_id , member_2_name, timestamp) VALUES ( {ctx.guild.id} , {ctx.author.id} ,  '{ctx.author.name}' , {member.id} , '{member.name}' , {time.time()} )")

		embed=discord.Embed(title="💍 | Свадьба",description=f"**🎉 | Поздравляем, {ctx.author.mention} женился(ась) на {member.mention}.**", color=0xbf1cd4, timestamp = ctx.message.created_at)
		embed.set_author(name=ctx.guild.name, url="https://discord.gg/Uqp32EwByH", icon_url=ctx.author.avatar_url)
		embed.set_image(url="https://c.tenor.com/UnSlrdcbV9kAAAAC/anime-ring.gif")
		embed.set_footer(text=f"• Запросил: {ctx.author}")		
		
		try:
			await mar.delete()
		except: pass
		await ctx.send(embed=embed)
		con.commit()	
		return
	else:
		embb=discord.Embed(title="💍 | Свадьба",description=f"**{no} | {member.mention} отказался(ась) от предложения {ctx.author.mention}**", color=0xbf1cd4, timestamp = ctx.message.created_at)
		embb.set_author(name=ctx.guild.name, url="https://discord.gg/Uqp32EwByH", icon_url=ctx.author.avatar_url)
		embb.set_image(url="https://c.tenor.com/HUewq2uQi30AAAAC/anime-crying.gif")
		embb.set_footer(text=f"• Запросил: {ctx.author}")		
		
		try:
			await mar.delete()
		except: pass
		await ctx.reply(embed=embb, mention_author=True)
		return

@bot.command()
async def divorce(ctx):
	con.ping() 
	with con.cursor() as cur:
		cur.execute(f"SELECT * FROM marries WHERE member_1_id={ctx.author.id} AND serverid={ctx.guild.id}")
		if cur.fetchone() == None: 
			cur.execute(f"SELECT * FROM marries WHERE member_2_id={ctx.author.id} AND serverid={ctx.guild.id}")
			if cur.fetchone() == None: 
				await ctx.reply("```Вы не женаты!!```", mention_author=True)
				return
		else: 
			pass
	
	con.ping() 
	with con.cursor() as cur:
		try:
			cur.execute(f"SELECT member_2_id, timestamp FROM marries WHERE member_1_id={ctx.author.id} AND serverid={ctx.guild.id}")
			fho = cur.fetchone()

			m2 = bot.get_user(fho["member_2_id"])
			tms = fho["timestamp"]

			cur.execute(f"DELETE FROM marries WHERE member_1_id={ctx.author.id} AND serverid={ctx.guild.id}")
			
			tim = round(time.time() - tms)
			time_format = time.strftime("%W д : %H час : %M мин : %S сек", time.gmtime(tim))

			emd = discord.Embed(title="😭 | Развод",description=f"**Вы успешно развелись с {m2.mention}\nВремя брака: `{time_format}`**", color=0xbf1cd4, timestamp = ctx.message.created_at)
			emd.set_author(name=ctx.guild.name, url="https://discord.gg/Uqp32EwByH", icon_url=ctx.author.avatar_url)
			emd.set_image(url="https://c.tenor.com/-hppYfdFZYEAAAAC/anime-divorce.gif")
			emd.set_footer(text=f"• Запросил: {ctx.author}")				
		
			await ctx.reply(embed=emd, mention_author=True)
			con.commit()
		except Exception as e:
			#raise e
			pass
	
	con.ping() 
	with con.cursor() as cur:
		try:
			cur.execute(f"SELECT member_1_id, timestamp FROM marries WHERE member_2_id={ctx.author.id} AND serverid={ctx.guild.id}")
			fho = cur.fetchone()

			m2 = bot.get_user(fho["member_1_id"])
			tms = fho["timestamp"]

			cur.execute(f"DELETE FROM marries WHERE member_2_id={ctx.author.id} AND serverid={ctx.guild.id}")
			
			tim = round(time.time() - tms)
			time_format = time.strftime("%W д : %H час : %M мин : %S сек", time.gmtime(tim))
			
			emd = discord.Embed(title="😭 | Развод",description=f"**Вы успешно развелись с {m2.mention}\nВремя брака: `{time_format}`**", color=0xbf1cd4, timestamp = ctx.message.created_at)
			emd.set_author(name=ctx.guild.name, url="https://discord.gg/Uqp32EwByH", icon_url=ctx.author.avatar_url)
			emd.set_image(url="https://c.tenor.com/-hppYfdFZYEAAAAC/anime-divorce.gif")
			emd.set_footer(text=f"• Запросил: {ctx.author}")				
		
			await ctx.reply(embed=emd, mention_author=True)
			con.commit()
		except Exception as e:
			#raise e
			pass

@bot.command()
async def marrylist(ctx):
	con.ping()
	with con.cursor() as cur:
		try: 
			cur.execute(f"SELECT * FROM marries WHERE serverid={ctx.guild.id}")

			fho = cur.fetchall()

			start = 0
			await ctx.reply(f"**💍 | Список свадеб сервера {ctx.guild.name}\n**", mention_author=True)
			for row in fho:
				member1 = bot.get_user(row["member_1_id"])
				member2 = bot.get_user(row["member_2_id"])
				tms = row["timestamp"] 
				
				tim = round(time.time() - tms)
				time_format = time.strftime("%W д : %H час : %M мин : %S сек", time.gmtime(tim))
				
				start += 1
				await ctx.send(f" > **{start}) `{member1}` и `{member2}` | Время брака: `{time_format}`**")
		except Exception as e:
			raise e
			return

@bot.command()
async def childrengqg5(ctx,member:discord.Member=None):
	if member == None: return await ctx.send("```Укажите участника. \n=children Участник```")

	con.ping() 
	with con.cursor() as cur:
		cur.execute(f"SELECT * FROM marries WHERE member_1_id={ctx.author.id} AND serverid={ctx.guild.id}")
		if cur.fetchone() == None: 
			cur.execute(f"SELECT * FROM marries WHERE member_2_id={ctx.author.id} AND serverid={ctx.guild.id}")
			if cur.fetchone() == None: 
				await ctx.reply("```Вы не женаты\nЖениться: =marry Участник```", mention_author=True)
				return
		else: 
			pass

	con.ping() 
	with con.cursor() as cur:
		cur.execute(f"SELECT * FROM childrens WHERE children_id={member.id} AND serverid={ctx.guild.id}")
		if cur.fetchone() == None: pass
		else: return await ctx.send(f"```{member.name} уже является ребенком другой семьи```")

	yes = '✅'
	no = '❌'
	valid_reactions = ['✅' , '❌']
		
	em=discord.Embed(title="👶 | Ребенок",description=f"**{ctx.author.mention} предложил {member.mention} стать ребенком его семьи**", color=0xbf1cd4, timestamp = ctx.message.created_at)
	em.set_author(name=ctx.guild.name, url="https://discord.gg/Uqp32EwByH", icon_url=ctx.author.avatar_url)
	em.set_image(url="https://c.tenor.com/74ynu6RmxpcAAAAC/anime.gif")
	em.set_footer(text=f"• Запросил: {ctx.author}")		

	mar = await ctx.reply(embed=em, mention_author=True)
	await mar.add_reaction(yes)
	await mar.add_reaction(no)

	def check(reaction, user):
		return user == member and str(reaction.emoji) in valid_reactions
	
	try:
		reaction, user = await bot.wait_for('reaction_add', timeout=60.0, check=check)
	except asyncio.TimeoutError:
		await ctx.reply(f"{ctx.author.mention}, {member.mention} не ответил на ваше предложение, время вышло.", mention_author=True)
		await mar.delete()
		return

	if str(reaction.emoji) == yes:
		con.ping()
		with con.cursor() as cur:
			cur.execute(f"SELECT * FROM marries WHERE member_1_id={ctx.author.id} AND serverid={ctx.guild.id}")
			if cur.fetchone() == None:
				cur.execute(f"SELECT * FROM marries WHERE member_2_id={ctx.author.id} AND serverid={ctx.guild.id}")
				if cur.fetchone() == None: return
				else:
					fho = cur.fetchone()
					m1 = bot.get_user(fho["member_1_id"])
					m2 = bot.get_user(fho["member_2_id"])
			else:
				fho = cur.fetchone()
				m1 = bot.get_user(fho["member_1_id"])
				m2 = bot.get_user(fho["member_2_id"])
				
		cur.execute(f"INSERT INTO childrens (serverid , children_id , children_name , member_1_name , member_1_id, member_2_name, member_2_id) VALUES ( {ctx.guild.id} , {member.id} , '{member.name}', '{m1.name}', {m1.id} , '{m2.name}',{m2.id})")
		
		embed=discord.Embed(title="👶 | Ребенок",description=f"**🎉 | Поздравляем, {member.mention} стал ребенком семьи {m1.mention} и {m2.mention}**", color=0xbf1cd4, timestamp = ctx.message.created_at)
		embed.set_author(name=ctx.guild.name, url="https://discord.gg/Uqp32EwByH", icon_url=ctx.author.avatar_url)
		embed.set_image(url="https://c.tenor.com/WAqtGGGmaqIAAAAM/carry-kid.gif")
		embed.set_footer(text=f"• Запросил: {ctx.author}")	
		
		try:
			await mar.delete()
		except: pass
		await ctx.send(embed=embed)
		start_time = time.time()
		con.commit()	
		return	

	else:
		embb=discord.Embed(title="👶 | Ребенок",description=f"**{no} | {member.mention} отказался(ась) от предложения {ctx.author.mention}**", color=0xbf1cd4, timestamp = ctx.message.created_at)
		embb.set_author(name=ctx.guild.name, url="https://discord.gg/Uqp32EwByH", icon_url=ctx.author.avatar_url)
		embb.set_image(url="https://c.tenor.com/vYKBcl-EwKgAAAAM/shiroi-suna-no-aquatope-the-aquatope-on-white-sand.gif")
		embb.set_footer(text=f"• Запросил: {ctx.author}")		
		
		try:
			await mar.delete()
		except: pass
		await ctx.reply(embed=embb, mention_author=True)
		return

@bot.command()
@commands.cooldown(1, 10, commands.BucketType.user)
async def sex(ctx,member:discord.Member=None):
	if member == None: return await ctx.reply("```Укажи Пользователя```", mention_author=True)
	
	if member == ctx.author: 
		await ctx.reply("```Укажи Пользователя. На себе нельзя```", mention_author=True)
		sex.reset_cooldown(ctx)
		return
	
	#con.ping() 
	#with con.cursor() as cur:
	#	cur.execute(f"SELECT * FROM marries WHERE member_1_id={member.id} AND serverid={member.id}")
	#	if cur.fetchone() == None:
#
#			cur.execute(f"SELECT * FROM marries WHERE member_2_id={member.id} AND serverid={member.id}")
#			if cur.fetchone() == None: 
#				pass
#			else: return await ctx.reply(f"```{member.name} состоит в браке. Действие отменено```", mention_author=True)
#		else: return await ctx.reply(f"```{member.name} состоит в браке. Действие отменено```", mention_author=True)


	gifs = random.choice(["https://c.tenor.com/Hu-DzekBgw0AAAAC/sex.gif","https://c.tenor.com/i7S2Taae5H8AAAAC/sex-anime.gif","https://c.tenor.com/a2uZH5UXBc8AAAAM/kyoko-kyouko.gif","https://c.tenor.com/R8W1vh6X6uMAAAAM/anime-love.gif"])
	acts = random.choice([" совершил половой акт с "," трахнул "," переспал c ", " залез в постель к "])
	
	emb = discord.Embed(title="🔞 | Половой акт", description=f"**{ctx.author.mention}{acts}{member.mention}**", color=0xbf1cd4, timestamp = ctx.message.created_at)
	emb.set_author(name=ctx.guild.name, url="https://discord.gg/Uqp32EwByH", icon_url=ctx.author.avatar_url)
	emb.set_image(url=gifs)
	emb.set_footer(text=f"• Запросил: {ctx.author}")

	await ctx.send(embed=emb)

@bot.command()
@commands.cooldown(1, 10, commands.BucketType.user)
async def hug(ctx,member:discord.Member=None):
	if member == None:
		await ctx.reply("```Укажи Пользователя```", mention_author=True)
		return 
	if member == ctx.author: 
		await ctx.reply("```Укажи Пользователя. На себе нельзя```", mention_author=True)
		hug.reset_cooldown(ctx)
		return
	gifs = random.choice(["https://c.tenor.com/1T1B8HcWalQAAAAC/anime-hug.gif","https://c.tenor.com/4n3T2I239q8AAAAC/anime-cute.gif","https://c.tenor.com/mmQyXP3JvKwAAAAC/anime-cute.gif","https://c.tenor.com/SXk-WqF6PpQAAAAC/anime-hug.gif"])
	acts = random.choice([" обнял ", " зажал в обьятиях ", " обнимает ", " прижал к себе "])

	emb = discord.Embed(title="❤️ | Обнятия", description=f"**{ctx.author.mention}{acts}{member.mention}**", color=0xbf1cd4, timestamp = ctx.message.created_at)
	emb.set_author(name=ctx.guild.name, url="https://discord.gg/Uqp32EwByH", icon_url=ctx.author.avatar_url)
	emb.set_image(url=gifs)
	emb.set_footer(text=f"• Запросил: {ctx.author}")

	await ctx.send(embed=emb)		

@bot.command()
@commands.cooldown(1, 10, commands.BucketType.user)
async def kill(ctx,member:discord.Member=None):
	if member == None:
		await ctx.reply("```Укажи Пользователя```", mention_author=True)
		return 
	if member == ctx.author: 
		await ctx.reply("```Укажи Пользователя. На себе нельзя```", mention_author=True)
		kill.reset_cooldown(ctx)
		return

	gifs = random.choice(["https://c.tenor.com/py184W4488kAAAAC/anime.gif","https://c.tenor.com/_3i8LBmRpWQAAAAC/akame-ga-kill-anime.gif","https://c.tenor.com/ZKyywOPBcpwAAAAC/akame-akame-ga-k-ill.gif","https://c.tenor.com/_aMkVJcxClIAAAAM/yu-yu-hakusho-anime.gif"])
	acts = random.choice([" убил ", " закопал ", " замочил "," отправил в могилу ", " ударил насмерть "])

	emb = discord.Embed(title="🩸 | Убийство", description=f"**{ctx.author.mention}{acts}{member.mention}**", color=0xbf1cd4, timestamp = ctx.message.created_at)
	emb.set_author(name=ctx.guild.name, url="https://discord.gg/Uqp32EwByH", icon_url=ctx.author.avatar_url)
	emb.set_image(url=gifs)
	emb.set_footer(text=f"• Запросил: {ctx.author}")

	await ctx.send(embed=emb)		

@kiss.error
async def kiss_error(ctx,error):
	if isinstance(error, commands.CommandOnCooldown):
		time = str(round(error.retry_after, 2))

		if time < str(1):
			tim = time + " секунду"
		if time < str(5):
			tim = time + " секунды"
		if time >= str(5):
			tim = time + " секунд"

		await ctx.reply(f'**{ctx.author.mention}, эту команду можно использовать через `{tim}`**', mention_author=True)

@fight.error
async def fight_error(ctx,error):
	if isinstance(error, commands.CommandOnCooldown):
		time = str(round(error.retry_after, 2))

		if time < str(1):
			tim = time + " секунду"
		if time < str(5):
			tim = time + " секунды"
		if time >= str(5):
			tim = time + " секунд"

		await ctx.reply(f'**{ctx.author.mention}, эту команду можно использовать через `{tim}`**', mention_author=True)

@slap.error
async def slap_error(ctx,error):
	if isinstance(error, commands.CommandOnCooldown):
		time = str(round(error.retry_after, 2))

		if time < str(1):
			tim = time + " секунду"
		if time < str(5):
			tim = time + " секунды"
		if time >= str(5):
			tim = time + " секунд"

		await ctx.reply(f'**{ctx.author.mention}, эту команду можно использовать через `{tim}`**', mention_author=True)

@sex.error
async def sex_error(ctx,error):
	if isinstance(error, commands.CommandOnCooldown):
		time = str(round(error.retry_after, 2))

		if time < str(1):
			tim = time + " секунду"
		if time < str(5):
			tim = time + " секунды"
		if time >= str(5):
			tim = time + " секунд"

		await ctx.reply(f'**{ctx.author.mention}, эту команду можно использовать через `{tim}`**', mention_author=True)

@hug.error
async def hug_error(ctx,error):
	if isinstance(error, commands.CommandOnCooldown):
		time = str(round(error.retry_after, 2))

		if time < str(1):
			tim = time + " секунду"
		if time < str(5):
			tim = time + " секунды"
		if time >= str(5):
			tim = time + " секунд"

		await ctx.reply(f'**{ctx.author.mention}, эту команду можно использовать через `{tim}`**', mention_author=True)

@kill.error
async def kill_error(ctx,error):
	if isinstance(error, commands.CommandOnCooldown):
		time = str(round(error.retry_after, 2))

		if time < str(1):
			tim = time + " секунду"
		if time < str(5):
			tim = time + " секунды"
		if time >= str(5):
			tim = time + " секунд"

		await ctx.reply(f'**{ctx.author.mention}, эту команду можно использовать через `{tim}`**', mention_author=True)


@bot.command()
@commands.cooldown(1, 60, commands.BucketType.guild)
async def guess_number(ctx,num1:int=None,num2:int=None, time:float=None):
	if num1 is None: 
		await ctx.reply("```=guess_number [От(Число)] [До(Число)] [Время игры(Минуты)]```", mention_author=True)
		guess_number.reset_cooldown(ctx)
		return
	
	if num2 is None: 
		await ctx.reply("```=guess_number [От(Число)] [До(Число)] [Время игры(Минуты)]```", mention_author=True)
		guess_number.reset_cooldown(ctx)
		return

	if time is None: 
		await ctx.reply("```=guess_number [От(Число)] [До(Число)] [Время игры(Минуты)]```", mention_author=True)
		guess_number.reset_cooldown(ctx)
		return
	
	if num2 > 1000: 
		await ctx.reply("```Максимум до 1000``` ", mention_author=True)
		guess_number.reset_cooldown(ctx)
		return

	if time > 5: 
		await ctx.reply("```Игра может длится максимум 5 минут```", mention_author=True)
		guess_number.reset_cooldown(ctx)
		return

	if num1 > num2:
		await ctx.reply("```Первое число должно быть меньше второго```", mention_author=True)
		guess_number.reset_cooldown(ctx)
		return
	
	try:
		win_number = str(random.randint(num1,num2))
		timeout = time * 60
	except Exception as e: return await ctx.reply(f"```Ошибка загадки числа\n{e}```", mention_author=True)

	emb = discord.Embed(title="❓ | Угадай число", description=f"**Я загадал число от `{num1}` до `{num2}`\n\nИгра длится: `{time} мин`\n```Первый кто напишет его в чат - победил```**", color=0xbf1cd4, timestamp = ctx.message.created_at)
	msg = await ctx.reply(embed=emb, mention_author=True)

	def check(message: discord.Message):
		return message.content == win_number and message.channel == ctx.channel 

	try:
		confirm = await bot.wait_for('message', check=check, timeout=timeout)
	except asyncio.TimeoutError:
		await ctx.send(embed=discord.Embed(title="❓ | Угадай число", description=f"**Время вышло, игра завершена\n\n🎲 | Загаданное число: `{win_number}`**", color=0xbf1cd4, timestamp = ctx.message.created_at))
		try:
			await msg.delete()
		except: pass
		guess_number.reset_cooldown(ctx)
		return

	try:
		await msg.delete()
	except: pass
	await ctx.send(embed=discord.Embed(title="❓ | Угадай число", description=f"**Победитель определен, игра завершена\n\n:tada: | Победитель: {confirm.author.mention}\n🎲 | Загаданное число: `{win_number}`**", color=0xbf1cd4, timestamp = ctx.message.created_at))
	guess_number.reset_cooldown(ctx)

@guess_number.error
async def guess_number_error(ctx,error):
	if isinstance(error, commands.CommandOnCooldown):
		await ctx.reply(f'**{ctx.author.mention} , новую игру можно создать через `{round(error.retry_after)} сек`  или завершите текущую**', mention_author=True)
		guess_number.reset_cooldown(ctx)
	if isinstance(error, commands.BadArgument):
		await ctx.reply("```=guess_number [От(Число)] [До(Число)] [Время игры(Минуты)]```", mention_author=True)
		guess_number.reset_cooldown(ctx)

@bot.command()
async def coinflip(ctx):
	coin = random.choice(["выпал `Орел`","выпала `Решка`"])
	if coin == "выпал `Орел`": coinpng = "https://randomall.ru/img/coin0.png"
	if coin == "выпала `Решка`": coinpng = "https://randomall.ru/img/coin1.png"

	embed = discord.Embed(title=":coin: | Бросить монетку", description=f"**{ctx.author.mention}, бросил монетку, {coin}**", color=0xbf1cd4, timestamp = ctx.message.created_at, mention_author=True)
	embed.set_image(url=coinpng)
	await ctx.reply(embed=embed)

@bot.command()
async def coin(ctx):
	coin = random.choice(["выпал `Орел`","выпала `Решка`"])
	if coin == "выпал `Орел`": coinpng = "https://randomall.ru/img/coin0.png"
	if coin == "выпала `Решка`": coinpng = "https://randomall.ru/img/coin1.png"

	embed = discord.Embed(title=":coin: | Бросить монетку", description=f"**{ctx.author.mention}, бросил монетку, {coin}**", color=0xbf1cd4, timestamp = ctx.message.created_at, mention_author=True)
	embed.set_image(url=coinpng)
	await ctx.reply(embed=embed)

@bot.command()
async def png(ctx, member:discord.Member=None , * ,text=None):
	if member == None: return await ctx.reply("```=png [@Участник] [Текст]```")
	if text == None: await ctx.reply("```=png [@Участник] [Текст]```")
	if len(text) > 30: return await ctx.reply(f"```Текст должен быть меньше 30 символов. У вас: {len(text)}```")

	url = str(member.avatar_url)[:-10]
	
	if str(member.avatar_url) == "https://cdn.discordapp.com/embed/avatars/1.png":
		url = "https://sun9-72.userapi.com/impg/9lclTP6JBkU2ct-MsUHD3FXFXywHfoAGcRvjLA/B1WD4dYIqN4.jpg?size=128x128&quality=95&sign=75d4e85e748c3606b134beb6e93e934c&type=album"
	
	if str(member.avatar_url) == "https://cdn.discordapp.com/embed/avatars/2.png":
		url = "https://sun9-76.userapi.com/impg/G9UaB6gfWt63A8VYLuUs5Fd5ISkwHifRbWwD1Q/xHwONZCYZXY.jpg?size=128x128&quality=95&sign=d5a328d15ec3e4d22aca1be87ba4cfbd&type=album"

	if str(member.avatar_url) == "https://cdn.discordapp.com/embed/avatars/3.png":
		url = "https://sun9-48.userapi.com/impg/qLSTIhI2BW8Rk4iCYfEHCJKgkH_8A3_PG0oEhw/MWS5lUf0Amg.jpg?size=128x128&quality=95&sign=34fc53ec874e36c4b94f0c34e6cf5b2d&type=album"

	if str(member.avatar_url) == "https://cdn.discordapp.com/embed/avatars/4.png":
		url = "https://sun9-26.userapi.com/impg/qkWrP5J-8V-6qqBq_avZ3LghkmEVHS7cw9D2qA/_SjV8msliIU.jpg?size=128x128&quality=95&sign=3a481185115df2873c13a2c1609b0fba&type=album"

	if str(member.avatar_url) == "https://cdn.discordapp.com/embed/avatars/5.png":
		url = "https://sun9-75.userapi.com/impg/bDPuj-gJg4riX5yTBy82DCjGQUcKmhbQA5FUtQ/8c2ba0lGkOw.jpg?size=128x128&quality=95&sign=a8ce16a9e8562961317ad69c86368b88&type=album"

	try:
		img = Image.new("RGBA", (500,200),"#fff")

		headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.99 Safari/537.36 OPR/83.0.4254.46 (Edition Yx GX)'}

		response = requests.get(url, headers=headers, stream=True)
		response = Image.open(io.BytesIO(response.content))
		response = response.convert('RGBA')

		img.paste(response, (20,35) )
		idraw = ImageDraw.Draw(img) 

		if member.nick: name = str(member.nick)
		else: name = str(member.name)

		sizef = 44

		if len(name) >= 13:
			sizef = 30

		if len(name) >= 14:
			sizef = 27

		if len(name) >= 19:
			sizef = 19
		
		if len(name) >= 21:
			sizef = 17
		
		if len(name) >= 27:
			sizef = 13
		
		if len(name) >= 29:
			sizef = 12

		headline = ImageFont.truetype("fonts/Quivira.ttf", size = sizef)
		undertext = ImageFont.truetype("fonts/Quivira.ttf", size = 20)
		watermark = ImageFont.truetype("fonts/arial.ttf",size=15)

		idraw.text( (180, 50), name, font = headline, fill=("#115227f7"))
		idraw.text( (180, 120), text, font = undertext, fill=("#1a1a1aa8"))
		idraw.text( (400, 180), "radexbot.xyz", font = watermark, fill=("#424242d9"))
		idraw.rectangle((20,35,146,163), outline=(0,0,0))

		choch = random.randint(1,1000)

		img.save(f'{member.id}_{choch}.png')
		await ctx.reply(file = discord.File(fp = f'{member.id}_{choch}.png'))

		await asyncio.sleep(0.5)
		os.remove(f'{member.id}_{choch}.png')
	except Exception as e:
		raise e
		#await ctx.reply(f"```Произошла ошибка.\n{e}```")
		return

#@png.error
#async def png_error(ctx,error):
#	if isinstance(error, commands.MemberNotFound):
#		return await ctx.reply(f"```Участник не найден\n=png [@Участник] [Текст]```", mention_author=True)

@bot.command()
@has_permissions(manage_guild = True)
async def serverstats(ctx, arg:str=None):
	if arg == None:

		helpp=discord.Embed(title="🛠 | Помощь по командам Статистики сервера",description="Создать Голосовые каналы со статистикой участников, ботов и т.д", color=0xbf1cd4, timestamp = ctx.message.created_at)
		helpp.add_field(name="Включить",value="**`=serverstats on`**",inline=True)
		helpp.add_field(name="Выключить",value="**`=serverstats off`**",inline=True)
		helpp.set_author(name=ctx.guild.name, url="https://discord.gg/Uqp32EwByH", icon_url=ctx.author.avatar_url)
		helpp.set_thumbnail(url=ctx.guild.icon_url)
		helpp.set_image(url="https://c.tenor.com/VT9NPWYg5t0AAAAC/mao-amatsuka.gif")
		helpp.set_footer(text=f"• Запросил: {ctx.author}")		

		msg = await ctx.reply(embed=helpp, mention_author=True)
		await ctx.message.add_reaction("👍")
		await asyncio.sleep(90)
		await msg.delete()

	if arg == "on":
		con.ping()
		with con.cursor() as cur:
			cur.execute(f"SELECT * FROM serverstats_humans WHERE serverid={ctx.guild.id}")
			if cur.fetchone() == None:
				cur.execute(f"SELECT * FROM serverstats_bots WHERE serverid={ctx.guild.id}")
				if cur.fetchone() == None:
					cur.execute(f"SELECT * FROM serverstats_all WHERE serverid={ctx.guild.id}")
					if cur.fetchone() == None: pass
					else: return await ctx.reply("```У вас уже включена статистика.\nОтключить: =serverstats off```")
				else: return await ctx.reply("```У вас уже включена статистика.\nОтключить: =serverstats off```")
			else: return await ctx.reply("```У вас уже включена статистика.\nОтключить: =serverstats off```")

		con.ping()
		with con.cursor() as cur:
			category = await ctx.guild.create_category("[ 📈 ] Статистика сервера", overwrites=None ,position=0)
			
			chan_hum = await ctx.guild.create_voice_channel(f"👤 ▸ Люди: {sum(not member.bot for member in ctx.guild.members)}", overwrites=None, category=category, reason=None)
			await chan_hum.set_permissions(ctx.guild.default_role, connect=False)
		
			cur.execute(f"INSERT INTO serverstats_humans (serverid,channel_id,category_id) VALUES ( {ctx.guild.id} , {chan_hum.id} , {category.id} )")

			chan_bots = await ctx.guild.create_voice_channel(f"🤖 ▸ Боты: {sum(member.bot for member in ctx.guild.members)}", overwrites=None, category=category, reason=None)
			await chan_bots.set_permissions(ctx.guild.default_role, connect=False)
			
			cur.execute(f"INSERT INTO serverstats_bots (serverid,channel_id,category_id) VALUES ( {ctx.guild.id} , {chan_bots.id} , {category.id} )")

			chan_all = await ctx.guild.create_voice_channel(f"👥 ▸ Всего: {ctx.guild.member_count}", overwrites=None, category=category, reason=None)
			await chan_all.set_permissions(ctx.guild.default_role, connect=False)
			
			cur.execute(f"INSERT INTO serverstats_all (serverid,channel_id,category_id) VALUES ( {ctx.guild.id} , {chan_all.id} , {category.id} )")

			con.commit()

			helpp=discord.Embed(title="👤 | Статистика сервера",description="✅ | Статистика успешно включена.", color=0xbf1cd4, timestamp = ctx.message.created_at)
			helpp.set_author(name=ctx.guild.name, url="https://discord.gg/Uqp32EwByH", icon_url=ctx.author.avatar_url)
			helpp.set_thumbnail(url=ctx.guild.icon_url)
			helpp.set_footer(text=f"• Установил: {ctx.author}")		
			await ctx.reply(embed=helpp)
			return

	if arg == "off":
		con.ping()
		with con.cursor() as cur:
			cur.execute(f"SELECT * FROM serverstats_humans WHERE serverid={ctx.guild.id}")
			if cur.fetchone() == None: return await ctx.reply("```У вас не включена статистика.\nВключить: =serverstats on```")
			else:
				cur.execute(f"SELECT * FROM serverstats_bots WHERE serverid={ctx.guild.id}")
				if cur.fetchone() == None: return await ctx.reply("```У вас не включена статистика.\nВключить: =serverstats on```")
				else:
					cur.execute(f"SELECT * FROM serverstats_all WHERE serverid={ctx.guild.id}")
					if cur.fetchone() == None: return await ctx.reply("```У вас не включена статистика.\nВключить: =serverstats on```")
					else: pass

		con.ping()
		with con.cursor() as cur:
			try:
				cur.execute(f"SELECT * FROM serverstats_humans WHERE serverid={ctx.guild.id}")
				fho = cur.fetchone()
				chan_hum = bot.get_channel(fho["channel_id"])
				category = bot.get_channel(fho["category_id"])
			except: pass

			try:
				cur.execute(f"SELECT * FROM serverstats_bots WHERE serverid={ctx.guild.id}")
				fho = cur.fetchone()
				chan_bots = bot.get_channel(fho["channel_id"])
			except: pass

			try:
				cur.execute(f"SELECT * FROM serverstats_all WHERE serverid={ctx.guild.id}")
				fho = cur.fetchone()
				chan_all = bot.get_channel(fho["channel_id"])
			except: pass

			try: cur.execute(f"DELETE FROM serverstats_humans WHERE serverid={ctx.guild.id}")
			except: pass
			
			try:
				await chan_hum.delete()
			except: pass

			try: cur.execute(f"DELETE FROM serverstats_bots WHERE serverid={ctx.guild.id}")
			except: pass

			try: await chan_bots.delete()
			except: pass

			try: cur.execute(f"DELETE FROM serverstats_all WHERE serverid={ctx.guild.id}")
			except: pass

			try: await chan_all.delete()
			except: pass

			try:
				await category.delete()
			except: pass

			helpp=discord.Embed(title="👤 | Статистика сервера",description="✅ | Статистика успешно выключена", color=0xbf1cd4, timestamp = ctx.message.created_at)
			helpp.set_author(name=ctx.guild.name, url="https://discord.gg/Uqp32EwByH", icon_url=ctx.author.avatar_url)
			helpp.set_thumbnail(url=ctx.guild.icon_url)
			helpp.set_footer(text=f"• Установил: {ctx.author}")		
			await ctx.reply(embed=helpp)
			con.commit()
			return

@serverstats.error
async def serverstats_error(ctx, error):
	if isinstance(error, commands.CheckFailure):
		await ctx.reply("```Необходимо право Управлением Сервером для выполнения этой команды```", mention_author=True)

@bot.command()
async def server_avatar(ctx):
	embed =	discord.Embed(title=f"Аватар сервера {ctx.guild.name}", color=0xbf1cd4, timestamp = ctx.message.created_at)
	embed.set_image(url=ctx.guild.icon_url)
	await ctx.reply(embed=embed)

@bot.command()
@has_permissions(manage_messages=True)
async def gstart134(ctx,tim=None,winners:int=None,*,prize=None):
	if prize == None: return await ctx.reply("```=gstart [Длительность] [Кол-во победителей] [Приз] ```")
	if tim == None: return await ctx.reply("```=gstart [Длительность] [Кол-во победителей] [Приз] ```")
	if winners == None: return await ctx.reply("```=gstart [Длительность] [Кол-во победителей] [Приз] ```")
	if winners == 0: return await ctx.reply("```Победителей должно быть больше 0```")

	await ctx.message.delete()

	def convert(time):
		global unit
		pos = ["s","m","h","d"]

		time_dict = {"s" : 1, "m" : 60, "h" : 3600 , "d" : 3600*24}

		unit = time[-1]

		if unit not in pos:
			return -1
		try:
			val = int(time[:-1])
		except:
			return -2

		return val * time_dict[unit]

	duration = convert(tim)

	if unit == "s": emb_dur = tim.replace("s"," ") + "сек." 
	if unit == "m": emb_dur = tim.replace("m"," ") + "мин."
	if unit == "h": emb_dur = tim.replace("h"," ") + "час."
	if unit == "d": emb_dur = tim.replace("d"," ") + "дн."

	if time == -1: return await ctx.reply("```Неверно введена длительность конкурса\n\nПримеры:\n1s - 1 секунда\n1m - 1 минута\n1h - 1 час\n1d - 1 день```")
	elif time == -2: return await ctx.reply("```Время должно быть целым числом.\n\nПримеры:\n1s - 1 секунда\n1m - 1 минута\n1h - 1 час\n1d - 1 день```")

	gembed=discord.Embed(title=f":tada:  | Конкурс на **`{prize}`**", color=0xbf1cd4)
	gembed.add_field(name="Запустил: ",value=ctx.author.mention,inline=True)
	gembed.add_field(name="Длительность: ",value=f"**`{emb_dur}`**",inline=True)
	gembed.add_field(name="Победителей: ",value=f"**`{winners}`**",inline=True)
	gembed.set_author(name=ctx.guild.name, url="https://discord.gg/Uqp32EwByH", icon_url=ctx.author.avatar_url)
	gembed.set_thumbnail(url=ctx.guild.icon_url)
	gembed.set_footer(text=f"Для участия нажмите на реакцию '👍'")	

	msg = await ctx.send(embed=gembed)
	await msg.add_reaction("👍")

	await asyncio.sleep(duration)

	new_msg = await ctx.channel.fetch_message(msg.id)

	dic_users = []
	dic_winers = ""
	
	user_list = [u for u in await new_msg.reactions[0].users().flatten() if u != bot.user]

	for user in user_list:
		dic_users.append(user.mention)

	st = 1
	while st <= winners:
		winer_choice = random.choice(dic_users)

		if winer_choice not in dic_winers: 
			dic_winers += winer_choice
			print(winer_choice)
		else: 
			st = 1
			print(f"{winer_choice} скипнут")

		st += 1

	if len(user_list) == 0:
		em = discord.Embed(title = f'❌ | Конкурс на **`{prize}`** завершен',description=f"**Никто не учавствовал в конкурсе**", color=0xbf1cd4, timestamp = ctx.message.created_at)
		em.set_author(name=ctx.guild.name, url="https://discord.gg/Uqp32EwByH", icon_url=ctx.author.avatar_url)
		em.set_thumbnail(url=ctx.guild.icon_url)
		em.set_footer(text=f"• Запустил: {ctx.author}")
		return await msg.edit(embed = em)

	elif len(user_list) <= winners:
		em = discord.Embed(title = f'❌ | Конкурс на **`{prize}`** завершен',description=f"**Недостаточно участников**", color=0xbf1cd4, timestamp = ctx.message.created_at)
		em.set_author(name=ctx.guild.name, url="https://discord.gg/Uqp32EwByH", icon_url=ctx.author.avatar_url)
		em.set_thumbnail(url=ctx.guild.icon_url)
		em.set_footer(text=f"• Запустил: {ctx.author}")
		return await msg.edit(embed = em)

	pl = "Победители: " if winners != 1 else "Победитель: " 

	gend=discord.Embed(title=f":tada:  | Конкурс на **`{prize}`** завершен",description=f"**ID Конкурса: {msg.id}**" ,color=0xbf1cd4, timestamp = ctx.message.created_at)
	gend.add_field(name=pl,value=dic_winers,inline=False)
	gend.add_field(name="Запустил: ",value=ctx.author.mention,inline=False)
	gend.set_author(name=ctx.guild.name, url="https://discord.gg/Uqp32EwByH", icon_url=ctx.author.avatar_url)
	gend.set_thumbnail(url=ctx.guild.icon_url)
	gend.set_footer(text=f"• Участий: {len(user_list)}")

	plural = "выйграли" if winners != 1 else "выйграл"
	
	await msg.edit(embed = gend)
	await ctx.send(f"**:tada: | Поздравляем\n\n{dic_winers} {plural} `{prize}`**")

@gstart134.error
async def gstart_error134(ctx, error):
	if isinstance(error, commands.MissingPermissions):
		return await ctx.send("```Необходимо право MANAGE_MESSAGES для выполнения этой команды")
   
@bot.command()
@has_permissions(manage_messages = True)
async def reroll134(ctx, id_ : int=None, winners:int=None):
	if id_ == None: return await ctx.reply("```=reroll [ID Конкурса] [Кол-во победителей]```")
	if winners == 0: return await ctx.reply("```Победителей должно быть больше 0```")
	if winners == None: return await ctx.reply("```=reroll [ID Конкурса] [Кол-во победителей]```")

	try:
		new_msg = await ctx.guild.fetch_message(id_)
	except: return await ctx.reply("```ID Конкурса введен неверно```")

	dic_users = []
	dic_winers = ""
	
	user_list = [u for u in await new_msg.reactions[0].users().flatten() if u != bot.user]

	for user in user_list:
		dic_users.append(user.mention)

	st = 1
	while st <= winners:
		winer_choice = random.choice(dic_users)

		if winer_choice not in dic_winers: 
			dic_winers += winer_choice
			print(winer_choice)
		else: 
			st = 1
			print(f"{winer_choice} скипнут")

		st += 1

	pl = "Победители: " if winners != 1 else "Победитель: "
	plu = "выйграли" if winners != 1 else "выйграл"
	plural = "Новые победители" if winners != 1 else "Новый победитель"

	await ctx.send(f"**:tada: | {plural}\n\n{dic_winers} {plu} `{prize}`**")

@reroll134.error
async def reroll_error134(ctx, error):
	if isinstance(error, commands.MissingPermissions):
		return await ctx.send("```Необходимо право MANAGE_MESSAGES для выполнения этой команды")

@bot.command()
async def ben(ctx,arg=None):
	global vc
	if arg == None:
		voice_state = ctx.author.voice
		if voice_state == None: 
			await ctx.reply("```Зайдите в голосовой канал```")
			status = False
			return

		try:
			voice_client = discord.utils.get(bot.voice_clients, guild=ctx.guild)
			voice_channel = ctx.author.voice.channel
			vc = await voice_channel.connect()
		except Exception as e:
			if voice_client:
				return await ctx.reply(f"```С Бэном уже разговаривают. Линия занята```")
			else: 
				return await ctx.reply(f"```Произошла Ошибка при подключении бота в голосовой канал\n{e}```")

		try:
			vc.play(discord.FFmpegPCMAudio(executable="bin/ffmpeg", source="ben/startben.mp3", options = "-loglevel panic") )
		except Exception as e: 
			await ctx.reply(f"```Произошла ошибка воспроизведения. Попробуйте еще раз\n{e}```")
			await vc.disconnect()
			return

		await ctx.reply("Вы позвонили Бэну, он слушает ваш вопрос...")

		status = True
		while status:			
			sounds = random.choice(["ben/yes.mp3","ben/laugh.mp3","ben/no.mp3","ben/buee.mp3"])
			choch = ["ты как то связан с даркнетом?","ты как то связан с даркнетом","ты как то связан с даркнетом?","Ты как то связан с даркнетом?","ты как то связан с даркнетом","Ты как то связан с даркнетом?","ты связан с даркнетом?","ты связан с даркнетом","Ты связан с даркнетом?","ты как-то связан с дарк нетом","ты как-то связан с дарк нетом"]
			s_rand = random.choice(["ben/nanana.mp3","ben/newspaper.mp3","ben/burp.mp3","ben/grr.mp3"])
			amogus = "ben/amogus.mp3"

			try:
				def check(m): return m.author == ctx.author and m.channel == ctx.channel
				
				msg = await bot.wait_for('message', timeout=15.0, check=check)
			except asyncio.TimeoutError:
				vc.play(discord.FFmpegPCMAudio(executable="bin/ffmpeg", source="ben/benstop.mp3", options = "-loglevel panic"))
				await asyncio.sleep(0.8)
				await ctx.reply("Ben сбросил трубку\nПерезвонить: **=ben**")
				await vc.disconnect()
				return
						
			if msg.content == "=ben stop":
				try:
					status = False
					await ctx.reply("Вы сбросили трубку... \nПерезвонить: **=ben**")
					await vc.disconnect()
					return
				except Exception as e: return await ctx.reply(e)

			elif msg.content in choch:
				try:
					vc.play(discord.FFmpegPCMAudio(executable="bin/ffmpeg", source="ben/maslo.mp3",options = "-loglevel panic"))
					await asyncio.sleep(4)
					vc.stop()
				except: pass

			else:
				try:
					vc.play(discord.FFmpegPCMAudio(executable="bin/ffmpeg", source=sounds, options = "-loglevel panic"))
					await asyncio.sleep(4)
					vc.stop()
				except: pass

			try:
				proc = random.randint(1,100)

				if proc == 1:
					try:
						vc.play(discord.FFmpegPCMAudio(executable="bin/ffmpeg", source=amogus, options = "-loglevel panic"))
						await asyncio.sleep(7)
						vc.stop()
					except: pass

				if proc >= 90:
					try:
						vc.play(discord.FFmpegPCMAudio(executable="bin/ffmpeg", source=s_rand, options = "-loglevel panic"))
						await asyncio.sleep(1)
						vc.stop()
					except: pass

				if proc == 58:
					try:
						vc.play(discord.FFmpegPCMAudio(executable="bin/ffmpeg", source=s_rand, options = "-loglevel panic"))
						await asyncio.sleep(1)
						vc.stop()
					except: pass

				if proc == 25:
					try:
						vc.play(discord.FFmpegPCMAudio(executable="bin/ffmpeg", source=s_rand, options = "-loglevel panic"))
						await asyncio.sleep(1)
						vc.stop()
					except: pass

				if proc == 72:
					try:
						vc.play(discord.FFmpegPCMAudio(executable="bin/ffmpeg", source=s_rand, options = "-loglevel panic"))
						await asyncio.sleep(1)
						vc.stop()
					except: pass

				if proc == 85:
					try:
						vc.play(discord.FFmpegPCMAudio(executable="bin/ffmpeg", source=s_rand, options = "-loglevel panic"))
						await asyncio.sleep(1)
						vc.stop()
					except: pass

				if proc == 11:
					try:
						vc.play(discord.FFmpegPCMAudio(executable="bin/ffmpeg", source=s_rand, options = "-loglevel panic"))
						await asyncio.sleep(1)
						vc.stop()
					except: pass

				if proc <= 15:
					try:
						vc.play(discord.FFmpegPCMAudio(executable="bin/ffmpeg", source=s_rand, options = "-loglevel panic"))
						await asyncio.sleep(1)
						vc.stop()
					except: pass
			except: pass

@bot.command()
async def chance(ctx,*,name=None):
	if name == None: return await ctx.reply("```=chance [Текст]```")

	proc = random.randint(1, 100)

	helpp=discord.Embed(title=f"💯 | Насколько вы {name}",description=f"**Вы `{name}` на {proc}%**", color=0xbf1cd4, timestamp = ctx.message.created_at)
	helpp.set_author(name=ctx.guild.name, url="https://discord.gg/Uqp32EwByH", icon_url=ctx.author.avatar_url)
	helpp.set_footer(text=f"• Запросил: {ctx.author}")		

	await ctx.reply(embed=helpp)

@bot.command()
async def еблан(ctx,member:discord.Member):
	await ctx.send(f"{member.mention} мда, не общайся как еблан!")

@bot.event
async def on_message(message):

	chance = random.randint(1,100)

	if chance < 50:
		con.ping()
		with con.cursor() as cur:
			try:
				cur.execute(f"SELECT * FROM serverstats_humans WHERE serverid={message.guild.id}")
				fho = cur.fetchone()
				chan_hum = bot.get_channel(fho["channel_id"])
				await chan_hum.edit(name=f"👤 ▸ Люди: {sum(not member.bot for member in message.guild.members)}")
		
				cur.execute(f"SELECT * FROM serverstats_bots WHERE serverid={message.guild.id}")
				fho = cur.fetchone()
				chan_bots = bot.get_channel(fho["channel_id"])
				await chan_bots.edit(name=f"🤖 ▸ Боты: {sum(member.bot for member in message.guild.members)}")

				cur.execute(f"SELECT * FROM serverstats_all WHERE serverid={message.guild.id}")
				fho = cur.fetchone()
				chan_all = bot.get_channel(fho["channel_id"])
				await chan_all.edit(name=f"👥 ▸ Всего: {message.guild.member_count}")
			except Exception as e:
				pass

	await bot.process_commands(message)

@bot.command()
async def dj(ctx,member:discord.Member):
	if ctx.guild.id == 934286397144170617:
		king = discord.utils.get(member.guild.roles, id=949344223386284032)

		if king in ctx.author.roles:
			role = discord.utils.get(member.guild.roles, id=949329390280523786)
			await member.add_roles(role)
			await ctx.reply(f"{member.mention} теперь DJ")
		else: return await ctx.reply("Вы не Король DJ")


@bot.command()
async def undj(ctx,member:discord.Member):
	if ctx.guild.id == 934286397144170617:
		king = discord.utils.get(member.guild.roles, id=949344223386284032)

		if king in ctx.author.roles:
			role = discord.utils.get(member.guild.roles, id=949329390280523786)
			await member.remove_roles(role)
			await ctx.reply(f"{member.mention} больше не DJ")
		else: return await ctx.reply("Вы не Король DJ")

@bot.command()
async def мда(ctx):
	if ctx.author.id == 456790342512148481:
		await ctx.author.add_roles(discord.utils.get(ctx.guild.roles, id=936238643188756510))

@bot.command()
async def topic(ctx):
	topic_list = [
	"С кем мечтаешь поужинать?",
	"Как бы ты себя охарактеризовал(a)?",
	"Самое большое сожаление?",
	"Какой злодей тебе симпатизирует?",
	"Что любишь на завтрак?",
	"О чем ты думаешь сейчас?",
	"Как долго думаешь проживешь?",
	"Какой сверхспособностью вы бы хотели обладать?",
	"Допустим, что жизнь после смерти существует. Как бы выглядели ад и рай, если бы их придумали вы?",
	"Самое любимое, яркое и веселое детское воспоминание?",
	"Какой предмет тебе давался лучше всего?",
	"Какие у тебя были или есть прозвища?",
	"Что ты считаешь самым важным в жизни?",
	"На что обращаешь внимание при знакомстве с человеком?",
	"На какой возраст себя ощущаешь?",
	"Kакая ваша любимая история?",
	"Сколько времени ты можешь провести без интернета?",
	"Выбираешь высокий интеллект или красоту?",
	"Какой твой самый героический поступок?",
	"Как относишься к политике?",
	"Какой цвет волос ты бы хотел иметь?",
	"Самое большое достижение в жизни?",
	"Первый секс",
	"RadexBot",
	"Роблокс",
	"Фортнайт",
	"Контер стрике"
	"Самая лучшая машина?",
	"Как выглядят идеальные день и ночь?",
	"",


	]



bot.run(settings['token'])
