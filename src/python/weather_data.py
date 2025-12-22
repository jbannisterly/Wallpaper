import openmeteo_requests
import json
import datetime
import numpy as np

def GetReload():
  try:
    with open('_config', 'r') as configFile:
      data = json.load(configFile)
    return data['reload']
  except Exception as e:
    print(e)
    return False

def GetLocation():
  try:
    with open('_config', 'r') as configFile:
      data = json.load(configFile)
      long = data['long']
      lat = data['lat']
    return (long, lat)
  except Exception as e:
    print(e)
    return (0, 50)

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
  long, lat = GetLocation()
  params = {
	"latitude": lat,
	"longitude": long,
	"minutely_15": weather_params_15,
  "hourly": weather_params_hr,
	"forecast_days": 1,
	"forecast_minutely_15": 96,
  }

  print(params)

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
    print(np.argmax(dataWeather['is_day']))
    print(dataWeather['is_day'])
    with open(filePath, 'w') as outputFile:
      json.dump({'weather' : dataWeather, 'info' : dataInfo}, outputFile)

  except Exception as e:
    print(e)

def CurrentIndex(time: float):
  currentTime = datetime.datetime.now().timestamp()
  deltaTime = currentTime - time
  return int(deltaTime / 900)

def CurrentInterpolation(time: float):  
  currentTime = datetime.datetime.now().timestamp()
  deltaTime = currentTime - time
  return (deltaTime / 900) - int(deltaTime / 900)


def ReadNow(filePath: str):
  with open(filePath, 'r') as inputFile:
    data = json.load(inputFile)
    dataWeather = data['weather']
    index = CurrentIndex(data['info']['time'])
    interpolation = CurrentInterpolation(data['info']['time'])
    print(index)
    print(interpolation)
    dataNow = {}
    for dataKey in dataWeather:
      keyIndex = min(index, len(dataWeather[dataKey]) - 1)
      keyIndexNext = min(index + 1, len(dataWeather[dataKey]) - 1)
      dataNow[dataKey] = dataWeather[dataKey][keyIndex] * (1 - interpolation) + dataWeather[dataKey][keyIndexNext] * interpolation
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
  if (DataExpired(filePath, 2)) or GetReload():
    print("fetching new data...")
    UpdateForecast(filePath)

def GetNow():
  path = 'out/data'
  EnsureFresh(path)
  current = ReadNow(path)
  print(current)
  return current
