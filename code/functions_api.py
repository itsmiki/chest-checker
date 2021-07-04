from requests.models import Response
from riotwatcher import LolWatcher
import asyncio

api_key = 'secret_api_key'
lol_watcher = LolWatcher(api_key)

miki = "uX0sDT_aEj4CzpYItA-aGDtRXFagBvcR2E5-ZlIUyUWZY0U"


def get_chest_info(region, encryptedSummonerId):
    champion_dict = {'887': 'Gwen', '266': 'Aatrox', '103': 'Ahri', '84': 'Akali', '12': 'Alistar', '32': 'Amumu', '34': 'Anivia', '1': 'Annie', '22': 'Ashe', '136': 'Aurelion Sol', '268': 'Azir', '432': 'Bard', '53': 'Blitzcrank', '63': 'Brand', '201': 'Braum', '51': 'Caitlyn', '164': 'Camille', '69': 'Cassiopeia', '31': 'Cho`Gath', '42': 'Corki', '122': 'Darius', '131': 'Diana', '119': 'Draven', '36': 'Dr Mundo', '245': 'Ekko', '60': 'Elise', '28': 'Evelynn', '81': 'Ezreal', '9': 'Fiddlesticks', '114': 'Fiora', '105': 'Fizz', '3': 'Galio', '41': 'Gangplank', '86': 'Garen', '150': 'Gnar', '79': 'Gragas', '104': 'Graves', '120': 'Hecarim', '74': 'Heimerdinger', '420': 'Illaoi', '39': 'Irelia', '427': 'Ivern', '40': 'Janna', '59': 'Jarvan IV', '24': 'Jax', '126': 'Jayce', '202': 'Jhin', '222': 'Jinx', '429': 'Kalista', '43': 'Karma', '30': 'Karthus', '38': 'Kassadin', '55': 'Katarina', '10': 'Kayle', '85': 'Kennen', '121': 'Kha`Zix', '203': 'Kindred', '240': 'Kled', '96': 'Kog`Maw', '7': 'Leblanc', '64': 'Lee Sin', '89': 'Leona', '127': 'Lissandra', '236': 'Lucian', '117': 'Lulu', '99': 'Lux', '54': 'Malphite', '90': 'Malzahar', '57': 'Maokai', '11': 'Master Yi', '21': 'Miss Fortune', '62': 'Wukong', '82': 'Mordekaiser', '25': 'Morgana', '267': 'Nami', '75': 'Nasus', '111': 'Nautilus', '76': 'Nidalee', '56': 'Nocturne', '20': 'Nunu & Willump', '2': 'Olaf', '61': 'Orianna', '80': 'Pantheon', '78': 'Poppy', '133': 'Quinn', '33': 'Rammus', '421': 'Rek`Sai', '58': 'Renekton', '107': 'Rengar', '92': 'Riven', '68': 'Rumble', '13': 'Ryze', '113': 'Sejuani', '35': 'Shaco', '98': 'Shen', '102': 'Shyvana', '27': 'Singed', '14': 'Sion', '15': 'Sivir', '72': 'Skarner', '37': 'Sona', '16': 'Soraka', '50': 'Swain', '134': 'Syndra', '223': 'Tahm Kench', '163': 'Taliyah', '91': 'Talon', '44': 'Taric', '17': 'Teemo', '412': 'Thresh', '18': 'Tristana', '48': 'Trundle', '23': 'Tryndamere', '4': 'Twisted Fate', '29': 'Twitch', '77': 'Udyr', '6': 'Urgot', '110': 'Varus', '67': 'Vayne', '45': 'Veigar', '161': 'Vel`Koz', '254': 'Vi', '112': 'Viktor', '8': 'Vladimir', '106': 'Volibear', '19': 'Warwick', '101': 'Xerath', '5': 'Xin Zhao', '157': 'Yasuo', '83': 'Yorick', '154': 'Zac', '238': 'Zed', '115': 'Ziggs', '26': 'Zilean', '143': 'Zyra', '498': 'Xayah', '497': 'Rakan', '141': 'Kayn', '516': 'Ornn', '142': 'Zoe', '145': 'Kai`Sa', '555': 'Pyke', '518': 'Neeko', '517': 'Sylas', '350': 'Yuumi', '246': 'Qiyana', '235': 'Senna', '523': 'Aphelios', '875': 'Sett', '876': 'Lillia', '777': 'Yone', '360': 'Samira', '147': 'Seraphine', '526': 'Rell', '234': 'Viego'}
    response = lol_watcher.champion_mastery.by_summoner(region, encryptedSummonerId)
    chest_info = []
    for record in response:
        chest_info.append({'championName': champion_dict[str(record['championId'])], 'championId': record['championId'],  'chestGranted': record['chestGranted']})
    return chest_info

def get_champion_icon_link(championId):
    return 'https://raw.communitydragon.org/latest/plugins/rcp-be-lol-game-data/global/default/v1/champion-icons/' + championId + '.png'

def get_encryptedSummonerId(region, summoner_name):
    response = lol_watcher.summoner.by_name(region, summoner_name)
    return response['id']


# print(get_encryptedSummonerId('eun1', 'Meth is Good'))

# result = get_chest_info('eun1', miki)

# for x in result:
#     print(str(x))
