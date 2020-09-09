import numpy as np
import random

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
	# - 여기서는 1차 다항식에 맞춰서 fitting 하면 된다.
    lane_func = np.polyfit(ys, xs, 1)
    lane = np.poly1d(lane_func)  # 수식으로 바꿔주기
    
    return lane
	

"""
주어진 선(line)에서 n개의 점을 선택해서 되돌려 주는 함수
"""	
def get_sameples_from_line(bottom_coord, top_coord, n_samples):
	if n_samples < 2:
		assert False, "선택할 샘플의 수는 2보다 크거나 같아야 합니다."
		
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
	
	