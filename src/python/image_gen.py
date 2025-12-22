import cv2
import numpy as np
import os.path
import noise

imagePath = 'img_input/base.png'
maskFieldPath = 'img_input/base_mask_field.png'
maskSkyPath = 'img_input/base_mask_sky.png'
skyBasePath = 'img_input/base_sky.png'
global imagesSize
imagesSize = (1,1,1)

def GenRadial(centre, imagesSize):
  grid = np.indices((imagesSize[1], imagesSize[0])).swapaxes(0, 2)
  xdif = centre[0] - grid[:,:,0]
  ydif = centre[1] - grid[:,:,1]
  radial = np.sqrt(xdif * xdif + ydif * ydif)
  return radial / np.max(radial)

def GenVertical(height, imagesSize):
  grid = np.indices((imagesSize[1], imagesSize[0])).swapaxes(0, 2)
  ydif = height - grid[:,:,1]
  print("grid shape " + str(grid.shape))
  return ydif / np.max(ydif)

def GenSky():
  base = cv2.imread(imagePath)
  imagesSize = base.shape

  grad = (1 - GenRadial([imagesSize[0] / 6, imagesSize[1] * 21 / 40], imagesSize)) ** 2 * 0.5 + (1 - GenVertical(imagesSize[0] / 6, imagesSize)) * 0.5
  sky = np.zeros((imagesSize[0], imagesSize[1], 3))
  sky[:,:,1] = grad * 0.8
  sky[:,:,2] = grad * 0.6
  sky[:,:,0] = 1
  cv2.imwrite(skyBasePath, sky * 255)

def ProjectCloud(cloud):
  coordFrom = np.float32([[0,0],[imagesSize[1],0],[0,imagesSize[0]],[imagesSize[1],imagesSize[0]]]) 
  coordTo = np.float32([[imagesSize[1] * -1.5,0],[imagesSize[1] * 2.5, 0],[0,imagesSize[0] / 2],[imagesSize[1],imagesSize[0] / 2]])

  transformMatrix = cv2.getPerspectiveTransform(coordFrom,coordTo)    
  return cv2.warpPerspective(cloud, transformMatrix,(imagesSize[1],imagesSize[0]))

def GenCloud(scale, cover, offset):
  n1 = np.ones((imagesSize[0], imagesSize[1]))
  n2 = np.ones((imagesSize[0], imagesSize[1]))
  z1 = offset[2] + 2.2
  z2 = offset[2] + 1
  invScale = 1 / scale
  for i in range(imagesSize[0]):
    ii = i / scale + offset[0]
    ii4 = ii * 4
    jj = offset[1]
    for j in range(imagesSize[1]):
      jj += invScale
      n1[i][j] = noise.snoise3(ii, jj, z1) + noise.snoise3(ii4, jj * 4, z1) * 0.3
      n2[i][j] = noise.snoise3(ii, jj, z2)

  n1 = n1 * 0.5 + 0.5
  n2 = n2 * 0.5 + 0.5

  n1 = n1 * cover
  n2 = n2 * (1 - cover)

  cloud = np.clip(n1 - n2, 0, 1)
  cloud = ProjectCloud(cloud)
  return cloud

def GenRain(time, rainLevel, seed=0):
  rnd = np.ones((imagesSize[0],imagesSize[1]))
  for i in range(imagesSize[0]):
    for j in range(imagesSize[1]):
      rnd[i][j] = noise.snoise3(i / 80 + time * 20, j / 2, seed)

  rain = rnd > (1 - rainLevel * 0.5)

  return rain

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

  baseMaskField = cv2.blur(baseMaskField, (3,3))
  baseMaskSky = 1 - baseMaskField

  cv2.imwrite(maskFieldPath, baseMaskField)
  cv2.imwrite(maskSkyPath, baseMaskSky)

def GenImage(time, basePath, lightLevel, cloudLevel, rainLevel):
  base = cv2.imread(basePath)
  baseSky = cv2.imread(skyBasePath)
  baseMaskField = cv2.imread(maskFieldPath)
  baseMaskSky = cv2.imread(maskSkyPath)

  cloudDetails = GenCloud(50, 1, [0, time, time])
  outputCloud = GenCloud(150, cloudLevel * 2, [0, time, time + 10])
  outputCloud = np.float32(outputCloud)
  combinedCloud = outputCloud[:,:,np.newaxis] * 255 * (1 - cloudLevel * 0.2)  * (cloudDetails[:,:,np.newaxis] * 0.1 + 0.9)
  baseSky = baseSky * (1 - outputCloud[:,:,np.newaxis]) + combinedCloud * (lightLevel * 0.5 + 0.5)

  # cv2.imwrite('img/sky.png', cloudDetails)

  outputSky = baseMaskSky * baseSky
  outputSky = cv2.cvtColor(np.float32(outputSky), cv2.COLOR_RGB2HSV)
  outputSky[:,:,1] = outputSky[:,:,1] * (lightLevel * 0.7 + 0.3)
  outputSky[:,:,2] = outputSky[:,:,2] * (lightLevel * 0.9 + 0.1)
  outputSky = cv2.cvtColor(np.float32(outputSky), cv2.COLOR_HSV2RGB)

  outputField = baseMaskField * base
  outputField = cv2.cvtColor(outputField, cv2.COLOR_RGB2HSV)
  outputField[:,:,1] = outputField[:,:,1] * (lightLevel * 0.6 + 0.4 - cloudLevel * 0.4)
  outputField[:,:,2] = outputField[:,:,2] * (lightLevel * 0.8 + 0.2)
  outputField = cv2.cvtColor(outputField, cv2.COLOR_HSV2RGB) * (1 - cloudLevel * 0.3)
 
  rain = []

  for i in range(10):
    rain.append(GenRain(time, rainLevel, i))

  cv2.imwrite('img_cache/output_field.png', outputField)
  cv2.imwrite('img_cache/output_sky.png', outputSky)
  for i in range(10):
    cv2.imwrite('img_cache/rain' + str(i) + '.png', rain[i] * 255)

def CreateImages(time, lightLevel, cloudLevel, rainLevel):
  if not os.path.isfile(maskSkyPath) or True:
    GenMask(imagePath)
  if not os.path.isfile(skyBasePath) or True:
    GenSky()
  GenImage(time, imagePath, lightLevel, cloudLevel, rainLevel)

# CreateImages(0, 1, 1, 0.5)