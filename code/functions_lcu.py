from lcu_driver import Connector
import threading
import time
import asyncio

from requests.sessions import session

def return_variable_not_list(function):
    def inside():
        temp_list = []
        function(temp_list)
        variable = temp_list[0]
        return variable
    return inside


def get_champions_owned(champions):
    connector = Connector()

    # fired when LCU API is ready to be used
    @connector.ready
    async def connect(connection):
        print('LCU API is ready to be used.')

        # check if the user is already logged into his account

        summoner2 = await connection.request('get', '/lol-champions/v1/owned-champions-minimal')
        data = await summoner2.json()

        for row in data:
            if row['ownership']['owned'] == True:
                champions.append({'name': row['name'], 'id': row['id']})
        #print(champions)


    # fired when League Client is closed (or disconnected from websocket)
    @connector.close
    async def disconnect(_):
        print('The client have been closed!')

    # starts the connector
    connector.start()


def get_pickable_champions_aram(champions):
    connector = Connector()

    # fired when LCU API is ready to be used
    @connector.ready
    async def connect(connection):
        print('LCU API is ready to be used.')
        try:
            session_raw = await connection.request('get', '/lol-champ-select/v1/session')
            session_json = await session_raw.json()
            # print(session_json)

            for id in session_json['benchChampionIds']:
                if id not in champions:
                    champions.append(id)
            
            for row in session_json['myTeam']:
                if row['championId'] not in champions:
                    champions.append(row['championId'])
        except:
            print('ARAM lobby not active.')
        


    # fired when League Client is closed (or disconnected from websocket)
    @connector.close
    async def disconnect(_):
        print('The client have been closed!')
        await connector.stop()

    # starts the connector
    connector.start()

@return_variable_not_list
def check_if_aram_lobby(checking_bit):
    connector = Connector()

    # fired when LCU API is ready to be used
    @connector.ready
    async def connect(connection):
        try:
            session = await connection.request('get', '/lol-champ-select/v1/session')
            session_json = await session.json()
            if session_json['benchEnabled'] == True:
                checking_bit.append(True)
            else:
                checking_bit.append(False)
        except:
            checking_bit.append(False)

    # fired when League Client is closed (or disconnected from websocket)
    @connector.close
    async def disconnect(_):
        #print('The client have been closed!')
        await connector.stop()

    # starts the connector
    connector.start()


def get_pickable_champions_aram_continuous(champions):
    connector = Connector()

    # fired when LCU API is ready to be used
    @connector.ready
    async def connect(connection):
        print('LCU API is ready to be used.')


    # fired when League Client is closed (or disconnected from websocket)
    @connector.close
    async def disconnect(_):
        print('The client have been closed!')
        await connector.stop()


    # subscribe to '/lol-summoner/v1/current-summoner' endpoint for the UPDATE event
    # when an update to the user happen (e.g. name change, profile icon change, level, ...) the function will be called
    @connector.ws.register('/lol-champ-select/v1/session', event_types=('UPDATE',))
    async def check_champions(connection, event):
        summoner2 = await connection.request('get', '/lol-champ-select/v1/session')
        session = await summoner2.json()

        for id in session['benchChampionIds']:
            if id not in champions:
                champions.append(id)
        
        for row in session['myTeam']:
            if row['championId'] not in champions:
                champions.append(row['championId'])

        # f = open('champion_ids.txt', 'a')
        # f.write(str(champions) + '\n')
        # f.close()
        

    # starts the connector
    connector.start()

    #print(xd['actions'][0][0]['championId']) #aktualnie wybrany champion dla /lol-champ-select/v1/session
        # for i in range (5):
        #     if xd['actions'][0][i]['championId'] not in champions:
        #         champions.append(xd['actions'][0][i]['championId'])


        # for i in range (5):
        #     if xd['actions'][0][i]['championId'] not in champions:
        #         champions.append(xd['actions'][0][i]['championId'])

        # summoner3 = await connection.request('get', '/lol-champ-select/v1/pickable-champion-ids')
        # #print(summoner3.json())
        # # print(xd)
        # xd2 = await summoner3.text()
        # f = open('pickable_blind.txt', 'a')
        # f.write(xd2)
        # f.close()


@return_variable_not_list
def get_summoner_name(summonerName):
    connector = Connector()

    # fired when League Client is closed (or disconnected from websocket)
    @connector.close
    async def disconnect(_):
        #print('The client have been closed!')
        await connector.stop()

    # fired when LCU API is ready to be used
    @connector.ready
    async def connect(connection):
        session = await connection.request('get', '/lol-summoner/v1/current-summoner')
        session_json = await session.json()
        summonerName.append(session_json['displayName'])


    # starts the connector
    connector.start()


def test():
    from random import randint

    connector = Connector()
    async def set_random_icon(connection):
        # random number of a chinese icon
        random_number = randint(50, 78)
        # make the request to set the icon
        icon = await connection.request('put', '/lol-summoner/v1/current-summoner/icon',
        data={'profileIconId': random_number})
        # if HTTP status code is 201 the icon was applied successfully
        if icon.status == 201:
            print(f'Chinese icon number {random_number} was set correctly.')
        else:
            print('Unknown problem, the icon was not set.')

        # fired when LCU API is ready to be used
    @connector.ready
    async def connect(connection):
        print('LCU API is ready to be used.')
        # check if the user is already logged into his account
        summoner = await connection.request('get', '/lol-summoner/v1/current-summoner')
        if summoner.status != 200:
            print('Please login into your account to change your icon and restart the script...')
        else:
            print('Setting new icon...')
        await set_random_icon(connection)
        
        # fired when League Client is closed (or disconnected from websocket)
    @connector.close
    async def disconnect(_):
        print('The client have been closed!')
    # starts the connector
    
    connector.start()

@return_variable_not_list
def get_summoner_icon_id(iconId):
    connector = Connector()

    # fired when League Client is closed (or disconnected from websocket)
    @connector.close
    async def disconnect(_):
        #print('The client have been closed!')
        await connector.stop()

    # fired when LCU API is ready to be used
    @connector.ready
    async def connect(connection):
        session = await connection.request('get', '/lol-summoner/v1/current-summoner')
        session_json = await session.json()
        iconId.append(session_json['profileIconId'])


    # starts the connector
    connector.start()



# print(get_summoner_name())