import numpy as np
import random
from os.path import isfile, join
import os
import re
from tqdm import tqdm_notebook
import cv2

"""
입력으로 들어오는 사진의 크기가, 내가 원하는 크기가 아닐 수 있다. 이를 대비하여 목표로 하는(target) 사진 크기를
미리 정해놓고, 만약 입력으로 들어오는 사진의 크기가 내가 원하는 크기가 아니면 resize 해서 사진 크기를 변경하자
"""
target_height = 270
target_width = 480

"""
Frame mask 라는 것을 만들어서, 이미지에 덮어 씌운 다음에 mask 밖의 그림은 다 지워버리고 
mask 내부의 그림만 이용해서 차선을 탐지할 것이다. 이때 frame mask 크기를 얼마로 할 것인지를
설정하기 위해서 frame 왼쪽의 하단, 상단, 그리고 frame 오른쪽의 상단, 하단의 좌표를
아래와 같이 설정하였다.
"""
mask_left_bottom = [0, target_height]
mask_left_top = [220, 160]
mask_right_top = [360, 160]
mask_right_bottom = [target_width, target_height]


"""
아무런 차선도 탐지하지 못한 경우에는 직전에 탐지한 차선을 재사용하는데,
직전에 탐지한 차선이 없는 경우에는 frame mask로 사용한 선(line)을 직전에 탐지한
차선인것으로 취급해서 사용할 것이다. 따라서, frame mask에 해당하는 선을 미리 계산해 둘 필요가 있는데
이 함수가 그 역할을 한다.
"""
def frame_mask_lane(bottom_coord, top_coord):
    assert len(bottom_coord) == 2  # (x,y)로 저장이 되어 있을터이니, 2개가 저장되어 있어야 함
    assert len(top_coord) == 2  # (x,y)로 저장이 되어 있을터이니, 2개가 저장되어 있어야 함
    
    xs, ys = [], []
    xs.append(bottom_coord[0])
    xs.append(top_coord[0])
    ys.append(bottom_coord[1])
    ys.append(top_coord[1])
    
    #
    # 주의 : y 좌표를 x 좌표 위치에 넣어서 fitting 을 한다!!
    # - 여기서는 무조건 1차 다항식에 맞춰서 fitting 하면 된다.
    lane_func = np.polyfit(ys, xs, 1) # 다항식에 맞춰서 fitting 하기
    lane = np.poly1d(lane_func)  # 수식으로 바꿔주기

    return lane


"""
주어진 선(line)에서 n개의 점을 선택/샘플링해서 리턴해 주는 함수
"""	
def get_sameples_from_line(bottom_coord, top_coord, n_samples):
    if n_samples < 2:
        #assert False, "선택할 샘플의 수는 2보다 크거나 같아야 합니다."
        print("선택할 샘플의 수는 2보다 크거나 같아야 합니다.")
        n_samples = 2

    # bottom_coord : 선의 한쪽 끝
    # top_coord : 선의 다른 쪽 끝
    # n_samples : 선에서 몇개의 샘플(= 점, x,y)을 고를 것인지
    samples = []  # 선택한 샘플의 좌표 [x,y]

    # 기본적으로, 선의 양 끝쪽을 무조건 샘플에 포함
    samples.append(bottom_coord)
    samples.append(top_coord)
    n_samples -= 2

    y_min = min([bottom_coord[1], top_coord[1]])
    y_max = max([bottom_coord[1], top_coord[1]])

    lane = frame_mask_lane(bottom_coord, top_coord)
    for i in range(n_samples):
        # 랜덤으로 y 값을 하나 고르고
        y = random.uniform(y_min, y_max)

        # y 값에 대응하는 x 값을 찾고
        x = lane(y)

        # [x,y]를 샘플에 추가
        samples.append([x,y])

    return samples


"""
차선 탐지된 이미지를 묶어서 비디오로 만들기
"""
def make_video_from_images(dir_path_img_frames_write, dir_path_video_out, video_out_filename):
    # specify frames per second
    fps = 30.0

    # get file names of the frames
    files = [f for f in os.listdir(dir_path_img_frames_write) 
             if isfile(join(dir_path_img_frames_write, f))]
    files.sort(key=lambda f: int(re.sub('\D', '', f)))

    # Next, we will get all the frames with the detected lane into a list:
    frame_list = []

    for i in tqdm_notebook(range(len(files))):
        filename = dir_path_img_frames_write + files[i]
        #reading each files
        img = cv2.imread(filename)
        height, width, layers = img.shape
        size = (width,height)

        #inserting the frames into an image array
        frame_list.append(img)
        
    # Finally, we can now combine the frames into a video by using the code below:

    # write the video
    path_out = dir_path_video_out + video_out_filename
    out = cv2.VideoWriter(path_out,cv2.VideoWriter_fourcc(*'DIVX'), fps, size)

    for i in range(len(frame_list)):
        # writing to a image array
        out.write(frame_list[i])

    out.release()
    
    
"""
Read Video Frames
비디오 : https://www.youtube.com/watch?reload=9&v=KWJaBJYJIjI
Frames : 비디오 촬영 영상을 연속된 이미지로 변경 해 놓은 것 (사진파일 다수)

비디오를 직접 입력으로 받지 않고, 비디오를 사진으로 변환한 다음에
사진 파일을 입력으로 받아서 처리한다.
"""
def read_image_frames(dir_path_img_frames_read, target_height, target_width):
    col_frames = os.listdir(dir_path_img_frames_read)
    col_frames.sort(key=lambda f: int(re.sub('\D', '', f)))

    # load frames
    col_images=[]
    for i in tqdm_notebook(col_frames):
        img = cv2.imread(dir_path_img_frames_read + i)

        # 이미지를 고정된 크기로 변경
        # 입력으로 들어오는 이미지가, 내가 원하는 크기가 아니면, 내가 원하는 크기로 변경
        height, width = img.shape[:2]
        if (height != target_height) or (width != target_width):
            #img = img.resize(img, dsize=(target_width, target_height))
            img = cv2.resize(img, dsize=(target_width, target_height))
            
        col_images.append(img)

    # 읽어온 사진 파일 검증
    num_images = len(col_images)
    height, width = col_images[0].shape[:2]
    print('num images read : ', num_images)
    print('image shape : ', height, width)
    print('done')
    
    return col_images

