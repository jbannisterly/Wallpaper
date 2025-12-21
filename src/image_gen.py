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

def ProjectCloud(cloud):
  coordFrom = np.float32([[0,0],[800,0],[0,600],[800,600]]) 
  coordTo = np.float32([[-1200,0],[2000, 0],[0,400],[800,400]])

  transformMatrix = cv2.getPerspectiveTransform(coordFrom,coordTo)    
  return cv2.warpPerspective(cloud, transformMatrix,(800,600))

def GenCloud(scale, cover, offset):
  n1 = np.ones((600, 800))
  n2 = np.ones((600, 800))
  z1 = offset[2] + 2.2
  z2 = offset[2] + 1
  invScale = 1 / scale
  for i in range(600):
    ii = i / scale + offset[0]
    ii4 = ii * 4
    jj = offset[1]
    for j in range(800):
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

def GenImage(time, basePath, lightLevel, cloudLevel):
  base = cv2.imread(basePath)
  baseSky = cv2.imread(skyBasePath)
  baseMaskField = cv2.imread(maskFieldPath)
  baseMaskSky = cv2.imread(maskSkyPath)

  cloudDetails = GenCloud(50, 1, [0, time, time])
  outputCloud = GenCloud(150, cloudLevel * 2, [0, time, time + 10])
  outputCloud = np.float32(outputCloud)
  baseSky = baseSky * (1 - outputCloud[:,:,np.newaxis]) + outputCloud[:,:,np.newaxis] * 255 * (1 - cloudLevel * 0.2)  * (cloudDetails[:,:,np.newaxis] * 0.1 + 0.9)

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

  output = outputSky + outputField

  cv2.imwrite('out/output.png', output)

def CreateImages(time, lightLevel, cloudLevel):
  if not os.path.isfile(maskSkyPath):
    GenMask(imagePath)
  if not os.path.isfile(skyBasePath):
    GenSky()
  GenImage(time, imagePath, lightLevel, cloudLevel)
