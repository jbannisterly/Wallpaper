import cv2
import datetime
import numpy as np
import random

def LoadRain(time):
  rainPath = 'img_cache/rain'
  rainAIndex = int(time % 10)
  rainBIndex = int((time + 1) % 10)
  fraction = int(time % 1 * 600)
  rainA = cv2.imread(rainPath + str(rainAIndex) + '.png')
  rainB = cv2.imread(rainPath + str(rainBIndex) + '.png')

  rainA = rainA / max(np.max(rainA), 1)
  rainB = rainB / max(np.max(rainB), 1)

  rain = np.concatenate((rainA[fraction:], rainB[:fraction]))

  imagesSize = rainA.shape

  offset = random.randint(0, 100)
  sampleSize = (100, 100)
  rainSample = rainA[offset:sampleSize[0] + offset,:sampleSize[1],:]

  coordFrom = np.float32([[0,0],[sampleSize[0],0],[0,sampleSize[1]],[sampleSize[0],sampleSize[1]]]) 
  coordTo = np.float32([[0,0],[imagesSize[1], 0],[0,imagesSize[0]],[imagesSize[1],imagesSize[0]]])

  transformMatrix = cv2.getPerspectiveTransform(coordFrom,coordTo)    
  rainProj = cv2.warpPerspective(rainSample, transformMatrix, (imagesSize[1],imagesSize[0]))
  rainProj = cv2.blur(rainProj, (10,10))
  rainProj = rainProj ** 2

  rain[int(imagesSize[0] * 4/5):,:,:] = 0
  rain = cv2.blur(rain, (3,3))

  rain = rain + rainProj

  return rain / max(np.max(rain), 1)

def LoadImage(time):
  outputField = cv2.imread('img_cache/output_field.png')
  outputSky = cv2.imread('img_cache/output_sky.png')
  output = outputSky + outputField
  
  rain = LoadRain(time)
  output = output * (1 - rain * 0.5) + rain * 0.5 * 127
  cv2.imwrite('img_out/wallpaper' + str(time) + '.png', output)