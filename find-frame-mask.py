"""
영상별로 카메라 위치가 달라서, 서로 다른 영상에는 서로 다른 frame mask를 사용해야 한다.
"""

import numpy as np
#import random
#from os.path import isfile, join
#import os
#import re
import cv2
import hallym_utils as hu
import matplotlib.pyplot as plt


# 테스트할 사진 경로 및 이름
input_image = "resource/set1001/frames_in/0.jpg"

# 이미지 불러오기
img = cv2.imread(input_image)

# 이미지 크기 확인
height, width = img.shape[:2]

# 타겟 이미지 크기를 미리 저장
target_height = hu.target_height
target_width = hu.target_width

if (height != target_height) or (width != target_width):  # 원히는 크기가 아니면
    # 이미지 크기를 원하는 크기로 변경
    img = cv2.resize(img, dsize=(target_width, target_height))

# frame mask에 사용할 4개의 좌표값
k_alpha, k_beta, k_gamma = 50, min([210,int(target_width/2)]), 0.6
mask_left_bottom = [k_alpha, target_height]
mask_left_top = [k_beta, int(target_height * k_gamma)]
mask_right_top = [target_width-k_beta, int(target_height * k_gamma)]
mask_right_bottom = [target_width-k_alpha, target_height]        

# create a zero array
stencil = np.zeros_like(img[:,:,0])

# specify coordinates of the polygon
polygon = np.array([mask_left_bottom, mask_left_top, mask_right_top, mask_right_bottom])

# fill polygon with ones
cv2.fillConvexPoly(stencil, polygon, 1)

# 결과를 화면에 표시 : 아무것도 없는 화면에 다각형의 흰색 + 나머지 검은색 생성
# plot polygon
#plt.figure(figsize=(10,10))
#plt.imshow(stencil, cmap= "gray")
#plt.show()

# 이렇게 생성한 다각형을, 실제 도로 사진 위에 덮기
# apply polygon as a mask on the frame
img = cv2.bitwise_and(img[:,:,0], img[:,:,0], mask=stencil)

# plot masked frame
plt.figure(figsize=(10,10))
plt.imshow(img, cmap= "gray")
plt.show()

print('done')