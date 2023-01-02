import requests
import json
import time
from aiogram import Bot, Dispatcher, executor, types
from datetime import datetime


API_TOKEN = '5979369026:AAEm8sQpY55cJLDwsoepkFhwe0PRt5MaqA4'
FIND_USER_ID = 'https://api.worldoftanks.eu/wot/account/list/?application_id=8809f3163f5b1a36feba6f0a2884d885&search='
FIND_USER_INFO = 'https://api.worldoftanks.eu/wot/account/info/?application_id=8809f3163f5b1a36feba6f0a2884d885&account_id='
TOURNAMENT_GET_URL = 'https://worldoftanks.eu/tmsis/api/v1/lobby/?filter%5Bstatus%5D=upcoming%2Cregistration_started&filter%5Bmin_players%5D=&filter%5Btag_id%5D=&filter%5Blanguage%5D=ru&page%5Bnumber%5D=1&page%5Bsize%5D=10'

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)


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
        answer = f'Nickname - {js["data"][account_id]["nickname"]} [<TODO: CLAN>],' \
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
    await message.answer('TODO')


@dp.message_handler()
async def echo(message: types.Message):
    print(datetime.now(), message.text)
    await message.answer("Unknown command. /help")


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
