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
    data = {}
    for i,weather_param in enumerate(weather_params):
      data[weather_param] = response.Minutely15().Variables(i).ValuesAsNumpy().tolist()
    data['time'] = response.Minutely15().Time()
    with open(filePath, 'w') as outputFile:
      json.dump(data, outputFile)

  except Exception as e:
    print(e)

def CurrentIndex(time: float):
  currentTime = datetime.datetime.now().timestamp()
  deltaTime = currentTime - time
  return int(deltaTime / 900)

def ReadNow(filePath: str):
  with open(filePath, 'r') as inputFile:
    data = json.load(inputFile)
    print(CurrentIndex(data['time']))
  return 0

def DataExpired(filePath):
  with open(filePath, 'r') as inputFile:
    data = json.load(inputFile)
    currentIndex = CurrentIndex(data['time'])
    maxIndex = len(data['rain'])
  return currentIndex >= maxIndex

def GetNow():
  UpdateForecast("out/data")
  return ReadNow("out/data")
  

print(DataExpired("out/data"))

