import image_gen
import weather_data
import image_load
import datetime
import os.path

def GetNGen():
  nGen = 10
  if os.path.isfile('temp/lowpower') or os.path.isfile('temp/noanimate'):
    nGen = 1
  return nGen

nGen = GetNGen()
currentWeather = weather_data.GetNow()
cloud = currentWeather['cloud_cover']
day = currentWeather['is_day']
rain = currentWeather['rain']
time = datetime.datetime.now().timestamp()
time = (time / 100) % 84600
image_gen.CreateImages(time, day, cloud / 100, rain, nGen)

for i in range(nGen):
  image_load.LoadImage(i)