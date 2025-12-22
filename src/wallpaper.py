import image_gen
import weather_data
import image_load
import datetime

currentWeather = weather_data.GetNow()
cloud = currentWeather['cloud_cover']
day = currentWeather['is_day']
rain = currentWeather['rain']
time = datetime.datetime.now().timestamp()
time = (time / 100) % 84600
image_gen.CreateImages(time, day, cloud / 100, rain)

for i in range(10):
  image_load.LoadImage(i)