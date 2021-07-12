from functions_lcu import get_champions_owned, get_summoner_name
import psutil, time

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

print(check_if_LeagueClient_is_active())




