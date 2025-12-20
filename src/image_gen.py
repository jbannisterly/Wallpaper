import cv2
import numpy as np
import os.path

imagePath = 'img/base.png'
maskFieldPath = 'img/base_mask_field.png'
maskSkyPath = 'img/base_mask_sky.png'
skyBasePath = 'img/base_sky.png'

def GenRadial(centre):
  grid = np.indices((800, 600)).swapaxes(0, 2)
  xdif = centre[0] - grid[:,:,0]
  ydif = centre[1] - grid[:,:,1]
  radial = np.sqrt(xdif * xdif + ydif * ydif)
  return radial / np.max(radial)

def GenVertical(height):
  grid = np.indices((800, 600)).swapaxes(0, 2)
  ydif = height - grid[:,:,1]
  return ydif / np.max(ydif)

def GenSky():
  grad = (1 - GenRadial([100, 420])) ** 2 + (1 - GenVertical(400))
  sky = np.zeros((600, 800, 3))
  sky[:,:,1] = grad * 0.6
  sky[:,:,2] = grad * 0.6
  sky[:,:,0] = 1
  cv2.imwrite(skyBasePath, sky * 255)

def GenMask(imagePath):
  print('reloading mask')
  base = cv2.imread(imagePath)
  baseHSV = cv2.cvtColor(base, cv2.COLOR_RGB2HSV)
  baseH = baseHSV[:,:,0]
  baseS = baseHSV[:,:,1]
  baseV = baseHSV[:,:,2]

  baseMask = (np.where(baseH > 20, 1, 0) + np.where(baseV < 70, 1, 0)) * (1 - (np.where(baseS < 50, 1, 0) * np.where(baseV > 100, 1, 0)))
  baseMaskField = np.where(baseMask > 0, 1, 0)
  baseMaskSky = np.where(baseMask > 0, 0, 1)

  cv2.imwrite(maskFieldPath, baseMaskField)
  cv2.imwrite(maskSkyPath, baseMaskSky)

def GenImage(basePath):
  base = cv2.imread(basePath)
  baseSky = cv2.imread(skyBasePath)
  baseMaskField = cv2.imread(maskFieldPath)
  baseMaskSky = cv2.imread(maskSkyPath)

  output = base * baseMaskField + baseMaskSky * baseSky

  cv2.imwrite('out/output.png', output)

if not os.path.isfile(maskSkyPath) or True:
  GenMask(imagePath)
if not os.path.isfile(skyBasePath) or True:
  GenSky()
GenImage(imagePath)