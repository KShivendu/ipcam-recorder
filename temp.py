from cv2 import cv2
import threading
# 'http://68.3.132.170:8080/?action=stream'
server_uri = 'data/CDR-Dinner_LAN_800k.mp4'

# vcap = cv2.VideoCapture(server_uri)
# while(1):
#     ret, frame = vcap.read()
#     cv2.imshow('STREAM', frame)
#     cv2.imwrite('data/stream.jpg', frame)
#     cv2.waitKey(1)


def stream_recorder(server_uri, uuid):
    from cv2 import cv2
    # server_uri = 'data/CDR-Dinner_LAN_800k.mp4'
    vcap = cv2.VideoCapture(server_uri)

    while(1):
        flag, frame = vcap.read()
        cv2.imshow('STREAM', frame)
        cv2.imwrite(f'data/{uuid}.jpg', frame)
        if flag:
            break
        cv2.waitKey(1)


url = server_uri
uuid = 'XTQWEQ'
thread = threading.Thread(target=stream_recorder, args=(url, uuid))
thread.start()
