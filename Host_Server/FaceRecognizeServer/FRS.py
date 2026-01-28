import socket
import struct
import numpy as np
import cv2
import os

face_recognize={
    'IP':'192.168.55.100',
    'PORT':9999
}

class FRS:
    def __init__(self,IP=face_recognize['IP'],PORT=face_recognize['PORT']):
        self.IP=IP
        self.PORT=PORT
        
    def revcall(self,sock,count):
        buf=b''
        while count:
            try:
                newbuf=sock.recv(count)
                if not newbuf:
                    return None
                buf+=newbuf
                count-=len(newbuf)
            except Exception as e:
                print(f'{e}')
                return None
        return buf

    def handle_request(self,msg_str,img):
        if msg_str=='':
            return
        data_list=msg_str.split(' ')
        if len(data_list)==2:
            print('Host')
        else:
            if data_list[0]=='False':
                os.system('rundll32.exe user32.dll,LockWorkStation')
                print('stranger')
            else:
                os.system('rundll32.exe user32.dll,LockWorkStation')
                print('no face')
        
    def server(self):
        server_socket=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        try:
            server_socket.bind((self.IP,self.PORT))
            server_socket.listen(5)
            print('listening')
            while True:
                conn,addr=server_socket.accept()
                try:
                    while True:
                        header_data=self.revcall(conn,8)
                        if header_data is None:
                            break
                        str_len,arr_len=struct.unpack('!II',header_data)
                        msg_str=''
                        if str_len>0:
                            str_bytes=self.revcall(conn,str_len)
                            if str_bytes is None:
                                break
                            msg_str=str_bytes.decode('utf-8')
                        img=None
                        if arr_len>0:
                            img_bytes=self.revcall(conn,arr_len)
                            if img_bytes is None:
                                break
                            img=np.frombuffer(img_bytes,dtype=np.uint8)
                            img=cv2.imdecode(img,cv2.IMREAD_COLOR)
                        self.handle_request(msg_str,img)
                except Exception as e:
                    print('connection abnormality',e)
                finally:
                    conn.close()
                    print('disconnected')
        except Exception as e:
            print('start error',e)
        finally:
            server_socket.close()
