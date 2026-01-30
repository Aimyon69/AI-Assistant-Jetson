import cv2
import socket
import time

def initSocketUDP():
    soc=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
    return soc

def push_origin_frame2host(HOST_IP='192.168.55.100',PORT=9999,target_fps=60):
    client_socket=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
    cap=cv2.VideoCapture(0,cv2.CAP_V4L2)
    cap.set(cv2.CAP_PROP_FOURCC,cv2.VideoWriter_fourcc('M','J','P','G'))
    cap.set(cv2.CAP_PROP_FRAME_WIDTH,320)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT,240)
    cap.set(cv2.CAP_PROP_FPS,target_fps)
    print(f"actual para:{cap.get(cv2.CAP_PROP_FRAME_WIDTH)} {cap.get(cv2.CAP_PROP_FRAME_HEIGHT)} {cap.get(cv2.CAP_PROP_FPS)}")
    actual_fps=cap.get(cv2.CAP_PROP_FPS)
    interval=1.0/actual_fps
    while(cap.isOpened()):
        current_time=time.time()
        ret,frame=cap.read()
        if not ret:
            print("error")
            break
        ret,buffer=cv2.imencode('.jpg',frame,[int(cv2.IMWRITE_JPEG_QUALITY),50])
        if ret:
            try:
                client_socket.sendto(buffer.tobytes(),(HOST_IP,PORT)) #tobytes is not necessary,buffer protocol
            except OSError as e:
                print(f"error:{e}")
        end_time=time.time()
        sleep_time=interval-(end_time-current_time)
        if sleep_time>0:
            time.sleep(sleep_time)
    cap.release()
    client_socket.close()

def push_specific_frame2host(frame,socket,HOST_IP='192.168.55.100',PORT=9999):
    ret,buffer=cv2.imencode('.jpg',frame,[int(cv2.IMWRITE_JPEG_QUALITY),50])
    if not ret:
        print('encode fail')
        return
    try:
        socket.sendto(buffer.tobytes(),(HOST_IP,PORT)) #tobytes is not necessary,buffer protocol
    except OSError as e:
        print(f'error:{e}')
    
#待优化重写逻辑
