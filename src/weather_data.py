import openmeteo_requests
import json
import datetime

def hourto15min(data, offset):
  newData = []
  for i in range(len(data) - 1):
    newData += [float(data[i])]
    newData += [float(data[i] * 0.75 + data[i + 1] * 0.25)]
    newData += [float(data[i] * 0.50 + data[i + 1] * 0.50)]
    newData += [float(data[i] * 0.25 + data[i + 1] * 0.75)]

  return newData[offset:]

def UpdateForecast(filePath: str):
  url = "https://api.open-meteo.com/v1/forecast"
  weather_params_15 = ["is_day", "rain", "snowfall", "weather_code"]
  weather_params_hr = ["cloud_cover"]
  params = {
	"latitude": 50,
	"longitude": 0,
	"minutely_15": weather_params_15,
  "hourly": weather_params_hr,
	"forecast_days": 1,
	"forecast_minutely_15": 96,
  }

  client = openmeteo_requests.Client()

  try:
    responses = client.weather_api(url, params = params)
    response = responses[0]
    dataWeather = {}
    dataInfo = {}
    hourlyTimeOffset = int((response.Minutely15().Time() - response.Hourly().Time()) / 900)
    for i,weather_param in enumerate(weather_params_15):
      dataWeather[weather_param] = response.Minutely15().Variables(i).ValuesAsNumpy().tolist()
    for i,weather_param in enumerate(weather_params_hr):
      dataWeather[weather_param] = hourto15min(response.Hourly().Variables(i).ValuesAsNumpy(), hourlyTimeOffset)
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
