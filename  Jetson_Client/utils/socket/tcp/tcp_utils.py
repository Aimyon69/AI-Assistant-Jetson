import socket
import struct
import numpy as np
import time
import cv2

def initSocketTCP(IP,PORT):
    times=10
    while(times):
        client_socket=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        client_socket.settimeout(5)
        try:
            client_socket.connect((IP,PORT))
            client_socket.settimeout(None)
            return client_socket
        except Exception as e:
            print(f'{e}')
            client_socket.close()
            times-=1
            time.sleep(0.5)
            continue
    return None

def send_data(IP,PORT,message_str,data_array=None):
    client=initSocketTCP(IP,PORT)
    if client is None:
        print('socket init fail')
        return False
    try:
        str_bytes=message_str.encode('utf-8')
        if data_array is not None:
            ret,encoded_img=cv2.imencode('.jpg',data_array,[cv2.IMWRITE_JPEG_QUALITY,70])
            if not ret:
                print('encode fail')
                return False
            arr_bytes=encoded_img.tobytes()
            len_arr=len(arr_bytes)
        else:
            arr_bytes=b''
            len_arr=0
        header=struct.pack('!II',len(str_bytes),len_arr)
        client.sendall(header+str_bytes+arr_bytes)
    except Exception as e:
        print(f'{e}')
        return False
    client.close()
    return True