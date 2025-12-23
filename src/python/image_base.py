import cv2
import numpy as np
import os

imagePath = 'img_input/base.png'
maskFieldPath = 'img_input/base_mask_field.png'
maskSkyPath = 'img_input/base_mask_sky.png'
skyBasePath = 'img_input/base_sky.png'
skyNightBasePath = 'img_input/base_night_sky.png'

def GenSkyGrad(imagesSize):
  grad = (1 - GenRadial([imagesSize[0] / 6, imagesSize[1] * 25 / 40], imagesSize)) ** 0.7 * 0.5
  grad += (1 - GenVertical(imagesSize[0] * 4 / 6, imagesSize)) * 0.5
  return grad

def GenRadial(centre, imagesSize):
  grid = np.indices((imagesSize[1], imagesSize[0])).swapaxes(0, 2)
  xdif = centre[0] - grid[:,:,0]
  ydif = centre[1] - grid[:,:,1]
  radial = np.sqrt(xdif * xdif + ydif * ydif)
  return radial / np.max(radial)

def GenVertical(height, imagesSize):
  grid = np.indices((imagesSize[1], imagesSize[0])).swapaxes(0, 2)
  ydif = np.maximum(height - grid[:,:,1], 0)
  print("grid shape " + str(grid.shape))
  return ydif / np.max(ydif)

def GenMask(imagePath):
  print('reloading mask')
  base = cv2.imread(imagePath)
  imagesSize = base.shape
  print(imagesSize)
  baseHSV = cv2.cvtColor(base, cv2.COLOR_RGB2HSV)
  baseH = baseHSV[:,:,0]
  baseS = baseHSV[:,:,1]
  baseV = baseHSV[:,:,2]

  baseMask = (np.where(baseH > 20, 1, 0) + np.where(baseV < 70, 1, 0)) * (1 - (np.where(baseS < 50, 1, 0) * np.where(baseV > 100, 1, 0)))
  baseMaskField = np.where(baseMask > 0, 1, 0)

  baseMaskSky = 1 - baseMaskField

  cv2.imwrite(maskFieldPath, baseMaskField)
  cv2.imwrite(maskSkyPath, baseMaskSky)


def GenSkyNight(imagesSize):
  grad = GenSkyGrad(imagesSize)

  sky = np.random.random(imagesSize) * 255

  skyV = sky[:,:,2] > 250
  skyS = sky[:,:,1] < 15
  skyBright = skyV * skyS
  
  sky = np.float32(sky * skyBright[:,:,np.newaxis])

  sky[:,:,1] /= 100

  sky = cv2.cvtColor(sky, cv2.COLOR_HSV2RGB) / 255
  sky = cv2.GaussianBlur(sky, (1,5), 0.8) + cv2.GaussianBlur(sky, (5,1), 0.8) + cv2.GaussianBlur(sky, (7,7), 0.3)

  sky = np.pow(sky, 0.1)

  grad = (grad / np.max(grad))

  sky[:,:,0] += grad * 0.01 + (1 - grad) * 0.2
  sky[:,:,1] += grad * 0.1
  sky[:,:,2] += grad * 0.2

  cv2.imwrite(skyNightBasePath, sky * 255)

def GenSkyDay(imagesSize):
  grad = GenSkyGrad(imagesSize)

  sky = np.zeros((imagesSize[0], imagesSize[1], 3))
  sky[:,:,1] = grad * 0.8
  sky[:,:,2] = grad * 0.6
  sky[:,:,0] = 1
  cv2.imwrite(skyBasePath, sky * 255)


def GenSky():
  base = cv2.imread(imagePath)
  imagesSize = base.shape
  GenSkyDay(imagesSize)
  GenSkyNight(imagesSize)

if not os.path.isfile(maskSkyPath) or True:
  GenMask(imagePath)
if not os.path.isfile(skyBasePath) or True:
  GenSky()

a = cv2.imread(skyNightBasePath)
b = cv2.imread(maskSkyPath)
c = cv2.imread(imagePath)
d = cv2.imread(maskFieldPath)
cv2.imwrite('img_input/debug.png', a * b + c * d)