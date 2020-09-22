import cv2


video_filename = 'driving-curve.mp4'
save_image_directory = '../frames_in'

vidcap = cv2.VideoCapture(video_filename)
success,image = vidcap.read()

count = 0

while success:
  cv2.imwrite(save_image_directory + '/' + str(count) + '.jpg', image)     # save frame as JPEG file      
  success,image = vidcap.read()
  #print('Read a new frame: ', success)
  count += 1

print('Done')  

# EOF