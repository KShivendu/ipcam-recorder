import logging
from cv2 import cv2


def record_stream_task():
    """
    Starts a recording
    """
    filepath = 'saved_demo.mp4'
    logging.info(f"Save location : {filepath}")

    try:
        vcap = cv2.VideoCapture(
            'http://192.168.43.1:4747/video?320x240')  # 'demo.mp4'
        # fourcc = cv2.VideoWriter_fourcc(*'MP4V')

        fw = int(vcap.get(3))
        fh = int(vcap.get(4))

        print(fw, fh)
        
        out = cv2.VideoWriter('output.mp4',
                              cv2.VideoWriter_fourcc(*'MP4V'), 20.0, (fw, fh))

        print("Starting writer")

        while vcap.isOpened():
            flag, frame = vcap.read()
            if flag:
                out.write(frame)
                cv2.imshow('Frame', frame)
                if cv2.waitKey(1) & 0xFF == ord('s'):
                    break
            else:
                break

    except:
        logging.error("SOMETHING WENT WRONG")
        exit()


record_stream_task()
