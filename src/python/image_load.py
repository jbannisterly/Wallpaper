import cv2
import datetime
import numpy as np

def LoadRain(time):
  rainPath = 'img_cache/rain'
  rainAIndex = int(time % 10)
  rainBIndex = int((time + 1) % 10)
  fraction = int(time % 1 * 600)
  rainA = cv2.imread(rainPath + str(rainAIndex) + '.png')
  rainB = cv2.imread(rainPath + str(rainBIndex) + '.png')

  rain = np.concatenate((rainA[fraction:], rainB[:fraction]))

  return rain


def LoadImage(time):
  outputField = cv2.imread('img_cache/output_field.png')
  outputSky = cv2.imread('img_cache/output_sky.png')
  output = outputSky + outputField
  
  rain = LoadRain(time)
  output = output * (1 - rain * 0.5) + rain * 0.5

  cv2.imwrite('img_out/wallpaper' + str(time) + '.png', output)