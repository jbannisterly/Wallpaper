import openmeteo_requests
import json
import datetime

def UpdateForecast(filePath: str):
  url = "https://api.open-meteo.com/v1/forecast"
  weather_params = ["is_day", "rain", "weather_code"]
  params = {
	"latitude": 50,
	"longitude": 0,
	"minutely_15": weather_params,
	"forecast_days": 1,
	"forecast_minutely_15": 96,
  }

  client = openmeteo_requests.Client()

  try:
    responses = client.weather_api(url, params = params)
    response = responses[0]
    dataWeather = {}
    dataInfo = {}
    for i,weather_param in enumerate(weather_params):
      dataWeather[weather_param] = response.Minutely15().Variables(i).ValuesAsNumpy().tolist()
    dataInfo['time'] = response.Minutely15().Time()
    with open(filePath, 'w') as outputFile:
      json.dump({'weather' : dataWeather, 'info' : dataInfo}, outputFile)

  except Exception as e:
    print(e)

def CurrentIndex(time: float):
  currentTime = datetime.datetime.now().timestamp()
  deltaTime = currentTime - time
  return int(deltaTime / 900)

def ReadNow(filePath: str):
  with open(filePath, 'r') as inputFile:
    data = json.load(inputFile)
    dataWeather = data['weather']
    index = CurrentIndex(data['info']['time'])
    dataNow = {}
    for dataKey in dataWeather:
      keyIndex = min(index, len(dataWeather[dataKey]) - 1)
      dataNow[dataKey] = dataWeather[dataKey][keyIndex]
  return dataNow

def DataExpired(filePath, timeAllowed):
  try:
    with open(filePath, 'r') as inputFile:
      data = json.load(inputFile)
      currentIndex = CurrentIndex(data['info']['time'])
      maxIndex = len(data['weather']['rain'])
    return currentIndex >= maxIndex or currentIndex > timeAllowed * 4
  except Exception as e:
    print(e)
    return True

def EnsureFresh(filePath):
  if (DataExpired(filePath, 2)):
    print("fetching new data...")
    UpdateForecast(filePath)

def GetNow():
  path = 'out/data'
  EnsureFresh(path)
  return ReadNow(path)

print(GetNow())
