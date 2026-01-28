import cv2 as cv
from .camera_config import camera_para
import numpy as np

class Not_Found(Exception):
    pass

def find_camera():
    index=None
    for i in range(11):
        cap=cv.VideoCapture(i,cv.CAP_V4L2)
        if cap.isOpened() and cap.read()[0]:
            index=i
            print(f'successfully found camera:{index}')
            cap.release()
            break
        cap.release()
    if index is None:
        raise Not_Found()
    return index

def init_camera():
    '''
    Returns:
        out:fail-None,success-cap
    '''
    camera_index=None
    try:
        camera_index=find_camera()
    except Not_Found as e:
        print("camera error")
        return None
    cap=cv.VideoCapture(camera_index,cv.CAP_V4L2)
    cap.set(cv.CAP_PROP_FOURCC,cv.VideoWriter_fourcc(camera_para['encode'][0],camera_para['encode'][1],camera_para['encode'][2],camera_para['encode'][3]))
    cap.set(cv.CAP_PROP_FRAME_WIDTH,camera_para['width'])
    cap.set(cv.CAP_PROP_FRAME_HEIGHT,camera_para['height'])
    cap.set(cv.CAP_PROP_FPS,camera_para['fps'])
    return cap
    
def draw_rec(frame,boxes):
    for box in boxes:
        x1,y1,x2,y2,_=box.astype(int)
        cv.rectangle(frame,(x1,y1),(x2,y2),(0,0,255),2)
    return frame
