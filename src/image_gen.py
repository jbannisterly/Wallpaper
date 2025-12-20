import cv2
import numpy as np

imagePath = 'img/base.png'

base = cv2.imread(imagePath)
baseHSV = cv2.cvtColor(base, cv2.COLOR_RGB2HSV)
baseH = baseHSV[:,:,0]
baseS = baseHSV[:,:,1]
baseV = baseHSV[:,:,2]

baseMask = (np.where(baseH > 20, 1, 0) + np.where(baseV < 70, 1, 0)) * (1 - (np.where(baseS < 50, 1, 0) * np.where(baseV > 100, 1, 0)))
baseMaskField = np.where(baseMask > 0, 1, 0)
baseMaskSky = np.where(baseMask > 0, 0, 1)

cv2.imwrite('img/base_mask_field.png', baseMaskField)
cv2.imwrite('img/base_mask_sky.png', baseMaskField)
