import psutil, time, asyncio

def check_if_LeagueClient_is_active():
    '''
    Check if there is any running process that contains the given name processName.
    '''
    processName = 'LeagueClient'
    #Iterate over the all the running process
    for proc in psutil.process_iter():
        try:
            # Check if process name contains the given name string.
            if processName.lower() in proc.name().lower():
                try:
                    return True
                except:
                    return False
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return False


import re
from subprocess import check_output


def find_LoL_path():
    output = check_output("wmic PROCESS WHERE name='LeagueClientUx.exe' GET commandline", shell=True).decode()
    return re.search(r'--install-directory=(.*?)" ', output).group(1)

def get_port_and_password(path):
    f = open(path + '\lockfile', 'r')
    lista = f.read().split(":")
    return lista[2], lista[3]





