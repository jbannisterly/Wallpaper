import cv2
import numpy as np
import os.path
import noise

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
  grad = (1 - GenRadial([100, 420])) ** 2 * 0.5 + (1 - GenVertical(200)) * 0.5
  sky = np.zeros((600, 800, 3))
  sky[:,:,1] = grad * 0.8
  sky[:,:,2] = grad * 0.6
  sky[:,:,0] = 1
  cv2.imwrite(skyBasePath, sky * 255)

def GenCloud(scale, cover, offset, outputid = ''):
  n1 = np.ones((600, 800))
  n2 = np.ones((600, 800))
  for i in range(600):
    for j in range(800):
      n1[i][j] = noise.snoise3(i / scale + offset[0], j / scale + offset[1], 2.2 + offset[2])
      n2[i][j] = noise.snoise3(i / scale + offset[0], j / scale + offset[1], 1 + offset[2])

  n1 = n1 * 0.5 + 0.5
  n2 = n2 * 0.5 + 0.5

  n1 = n1 * cover
  n2 = n2 * (1 - cover)

  cloud = np.clip(n1 - n2, 0, 1) ** 0.7

  cv2.imwrite('img/cloud' + outputid + '.png', cloud * 255)

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

def GenImage(basePath, lightLevel):
  base = cv2.imread(basePath)
  baseSky = cv2.imread(skyBasePath)
  baseMaskField = cv2.imread(maskFieldPath)
  baseMaskSky = cv2.imread(maskSkyPath)

  outputSky = baseMaskSky * baseSky
  outputSky = cv2.cvtColor(outputSky, cv2.COLOR_RGB2HSV)
  outputSky[:,:,1] = outputSky[:,:,1] * (lightLevel * 0.7 + 0.3)
  outputSky[:,:,2] = outputSky[:,:,2] * (lightLevel * 0.9 + 0.1)
  outputSky = cv2.cvtColor(outputSky, cv2.COLOR_HSV2RGB)


  outputField = baseMaskField * base
  outputField = cv2.cvtColor(outputField, cv2.COLOR_RGB2HSV)
  outputField[:,:,1] = outputField[:,:,1] * (lightLevel * 0.6 + 0.4)
  outputField[:,:,2] = outputField[:,:,2] * (lightLevel * 0.8 + 0.2)
  outputField = cv2.cvtColor(outputField, cv2.COLOR_HSV2RGB)


  output = outputSky + outputField

  cv2.imwrite('out/output' + str(lightLevel * 10) + '.png', output)

if not os.path.isfile(maskSkyPath) or True:
  GenMask(imagePath)
if not os.path.isfile(skyBasePath) or True:
  GenSky()

for i in range(11):
  GenImage(imagePath, (i + 1) / 10)

for i in range(10):
  GenCloud(150, i / 20, [0, i / 3, i / 5], str(i))