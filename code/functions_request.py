from lcu_driver import Connector
import requests
from requests.auth import HTTPBasicAuth
from requests.sessions import session

port = '62342'
password = '_VVDokVR_mW-0igYELgJBw'


def get_champions_owned(port, password) -> list:
    response = requests.get("https://127.0.0.1:" + port + "/lol-champions/v1/owned-champions-minimal", auth= HTTPBasicAuth('riot', password))
    
    data = response.json()
    champions = []

    for row in data:
        if row['ownership']['owned'] == True:
            champions.append({'name': row['name'], 'id': row['id']})
    
    return champions



def get_pickable_champions_aram(port, password) -> list:
    try:
        response = requests.get("https://127.0.0.1:" + port + "/lol-champ-select/v1/session", auth= HTTPBasicAuth('riot', password))
        session_json = response.json()

        champions = []

        for id in session_json['benchChampionIds']:
            if id not in champions:
                champions.append(id)
        
        for row in session_json['myTeam']:
            if row['championId'] not in champions:
                champions.append(row['championId'])
        
        return champions
    except:
        print('ARAM lobby not active.')
        return
    

def check_if_aram_lobby(port, password) -> bool:
    try:
        session = requests.get("https://127.0.0.1:" + port + "/lol-champ-select/v1/session", auth= HTTPBasicAuth('riot', password))
        session_json = session.json()
        if session_json['benchEnabled'] == True:
            return True
        else:
            return False
    except:
        return False


def get_summoner_name(port, password) -> str:
    session = requests.get("https://127.0.0.1:" + port + "/lol-summoner/v1/current-summoner", auth= HTTPBasicAuth('riot', password))
    return session.json()['displayName']


def get_summoner_icon_id(port, password) -> str:
    session = requests.get("https://127.0.0.1:" + port + "/lol-summoner/v1/current-summoner", auth= HTTPBasicAuth('riot', password))
    return session.json()['profileIconId']


def get_how_many_chests_available(port, password):  # nie działa ta funkcja
    session = requests.get("https://127.0.0.1:" + port + "/lol-collections​/v1​/inventories​/chest-eligibility", auth= HTTPBasicAuth('riot', password))
    return session.json()
        
