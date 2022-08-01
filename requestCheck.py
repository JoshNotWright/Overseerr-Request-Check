import requests
import json

configFile = open('config.json')
configData = json.load(configFile)

overseerrAPIKEY = configData['overseerrAPIKEY']
sonarrAPIKEY = configData['sonarrAPIKEY']
tmdbAPIKEY = configData['tmdbAPIKEY']

overseerrUrlBase = configData['overseerrUrlBase']
sonarrUrlBase = configData['sonarrUrlBase']

sonarrDict = {}
missingFromSonarr = []

overseerrHeaders = {
    'Accept': 'application/json',
    'X-Api-Key': overseerrAPIKEY
    }

sonarrHeaders = {
    'Accept': 'application/json',
    'X-Api-Key': sonarrAPIKEY
}

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def getProcessingRequests():
    response = requests.get(overseerrUrlBase + "/api/v1/request?take=2000&skip=0&filter=processing", headers=overseerrHeaders)
    data = json.loads(response.content)
    idList = []
    for i in data['results']:
        idList.append(i['id'])
    return idList

def checkSeriesStatus(id):
    global missingFromSonarr
    global sonarrDict
    response = requests.get(sonarrUrlBase + "/api/v3/series/" + str(id), headers=sonarrHeaders)
    responseData = json.loads(response.content)
    try:
        if responseData['statistics']['percentOfEpisodes'] == 100.0:
            print(bcolors.OKBLUE + responseData['title'] + ": This series should be marked as available" + bcolors.ENDC)
            return True
        else:
            print(bcolors.BOLD + responseData['title'] + bcolors.ENDC + ": We don't quite have all of those episodes yet")
            return False
    except KeyError:
        missingFromSonarr.append(sonarrDict.get(id))
        
def markRequestComplete(id):
    headers = {
        'accept': 'application/json',
        'Content-Type': 'application/json',
        'X-Api-Key': overseerrAPIKEY
    }
    
    data = { "is4k": False }

    response = requests.post(overseerrUrlBase + "/api/v1/media/" + str(id) + "/available", data=json.dumps(data), headers=headers)
    if response.status_code == 200:
        print(bcolors.OKGREEN + "Marked as completed" + bcolors.ENDC)
        return
    else:
        print(bcolors.FAIL + "Failed to mark as completed!" + bcolors.ENDC)
        print (response.status_code)
        print (response.content)
        return

def getSeriesTitleByTmdbId(id):
    response = requests.get("https://api.themoviedb.org/3/tv/" + str(id) + "?api_key=" + tmdbAPIKEY + "&language=en-US&external_source=imdb_id")
    data = json.loads(response.content)
    return data['name']

def processProcessingRequests():
    global sonarrDict
    global missingFromSonarr

    idList = getProcessingRequests()
    movie = "movie"

    print ("Processing " + str(len(idList)) + " requests...")
    for n in idList:
        response = requests.get(overseerrUrlBase + "/api/v1/request/" + str(n), headers=overseerrHeaders)
        singleRequestData = json.loads(response.content)

        try:
            if movie in singleRequestData['media']['serviceUrl']:
                continue
            else:
                sonarrDict.update({singleRequestData['media']['externalServiceId']: getSeriesTitleByTmdbId(singleRequestData['media']['tmdbId'])})
                if checkSeriesStatus(singleRequestData['media']['externalServiceId']) == True:
                    markRequestComplete(singleRequestData['media']['id'])
                else:
                    continue
        except KeyError:
            print (bcolors.FAIL + "Request ID: " + str(n) + " ran into an error getting data from Overseerr" + bcolors.ENDC)
    
    if len(missingFromSonarr) > 0:
        print (f"{bcolors.WARNING}The following shows have previously been removed from Sonarr, but still have open requests on Overseerr: {', '.join(missingFromSonarr)}{bcolors.ENDC}")
        
processProcessingRequests()