import requests
import json
import time
from aiogram import Bot, Dispatcher, executor, types
from datetime import datetime

from config import *

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)


def get_clan_info(clan_tag):
    req = requests.get(FIND_CLAN_ID + clan_tag)
    js = json.loads(str(req.text))
    if js['status'] == 'ok':
        if js['meta']['count'] >= 1:
            clan_id = js['data'][0]['clan_id']
            return get_clan_info_by_id(clan_id)
        else:
            return 'Clan not found'
    else:
        return 'Error'


def get_clan_info_by_id(clan_id):
    req = requests.get(FIND_CLAN_INFO + clan_id)
    js = json.loads(str(req.text))
    answer = f'[{js["data"][str(clan_id)]["tag"]}] - {js["data"][str(clan_id)]["name"]}' \
             f'Motto - {js["data"][str(clan_id)]["motto"]}' \
             f'Creator - {js["data"][str(clan_id)]["creator_name"]}' \
             f'Created at {datetime.utcfromtimestamp(js["data"][str(clan_id)]["created_at"]+3600).strftime("%Y-%m-%d %H:%M:%S")} CET'
    return answer


def get_clan_tag_in_player_info(clan_id):
    req = requests.get(FIND_CLAN_INFO + clan_id)
    js = json.loads(str(req.text))
    return js["data"][str(clan_id)]["tag"]


def get_account_id(nickname):
    req = requests.get(FIND_USER_ID + nickname)
    req = str(req.text)
    js = json.loads(req)
    if js['status'] == 'ok':
        return str(js['data'][0]['account_id'])
    else:
        return 'error'


def get_account_info(nickname):
    if (account_id := get_account_id(nickname)) == 'error':
        return "Nickname entered incorrectly.\nTry like this: /player alex123"
    else:
        req = requests.get(FIND_USER_INFO + account_id)
        req = str(req.text)
        js = json.loads(req)
        clan_id = js["data"][account_id]["clan_id"]
        answer = f'Nickname - {js["data"][account_id]["nickname"]} [{get_clan_tag_in_player_info(clan_id)}],' \
                 f'\nGlobal rating - {js["data"][account_id]["global_rating"]},' \
                 f'\nLast battle time - {datetime.utcfromtimestamp(js["data"][account_id]["last_battle_time"]+3600).strftime("%Y-%m-%d %H:%M:%S")} CET,' \
                 f'\nMaximum damage - {js["data"][account_id]["statistics"]["all"]["max_damage"]},' \
                 f'\nBattles - {js["data"][account_id]["statistics"]["all"]["battles"]},' \
                 f'\nWin rate - {round((int(js["data"][account_id]["statistics"]["all"]["wins"])/int(js["data"][account_id]["statistics"]["all"]["battles"]))*100, 2)}%'
        return answer


def parser(req) -> str:
    req = str(req.text)
    js = json.loads(req)
    answer = ''
    for item in js['data']['results']:
        minutes = (item['registrations'][0]['available_till'] - time.mktime(datetime.now().timetuple())) // 60
        answer += item['translations']['title'] + '   '
        if int(minutes) < 60:
            answer += str(int(minutes)) + ' minutes'
        else:
            answer += str(int(minutes) // 60) + ' hours'
        answer += '\n'
        answer += 'worldoftanks.eu/en/tournaments/' + str(item['registrations'][0]['id']) + '\n\n'
    return answer


def get_tournament_info():
    req = requests.get(TOURNAMENT_GET_URL)
    if str(req.status_code)[0] == '2':
        return parser(req)
    elif str(req.status_code)[0] == '4':
        return f'Client Error - {req.status_code}'
    elif str(req.status_code)[0] == '5':
        return f'Server Error - {req.status_code}'


@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    print(datetime.now(), message.text)
    await message.reply("Hello!\nI am an infobot.\nI can get information about a clan, a player or a tournament.\nSend me /help if you need help.\n")


@dp.message_handler(commands=['help'])
async def send_help(message: types.Message):
    print(datetime.now(), message.text)
    await message.answer("/player <nickname> - player information,\n/clan <clanName> - clan information,\n/tournament - upcoming tournaments.")


@dp.message_handler(commands=['player'])
async def send_player_info(message: types.Message):
    print(datetime.now(), message.text)
    if len(message.text) < 11:
        await message.answer("Nickname entered incorrectly.\nTry like this: /player alex123")
    else:
        await message.answer(get_account_info(message.text[8:]))


@dp.message_handler(commands=['tournament'])
async def send_tournament_info(message: types.Message):
    print(datetime.now(), message.text)
    await message.answer(get_tournament_info())


@dp.message_handler(commands=['clan'])
async def send_clan_info(message: types.Message):
    print(datetime.now(), message.text)
    await message.answer(get_clan_info(message.text[6:]))


@dp.message_handler()
async def echo(message: types.Message):
    print(datetime.now(), message.text)
    await message.answer("Unknown command. /help")


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
