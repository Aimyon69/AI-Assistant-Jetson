import cv2
import socket
import numpy as np

def receive_frame(HOST_IP='0.0.0.0',PORT=9999):
    server_socket=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
    server_socket.bind((HOST_IP,PORT))
    server_socket.settimeout(5.0)
    try:
        while True:
            try:
                img_data,addr=server_socket.recvfrom(65536)
                img=np.frombuffer(img_data,dtype=np.int8)
                img=cv2.imdecode(img,cv2.IMREAD_COLOR)
                if img is None:
                    print("data destroyed")
                else:
                    cv2.imshow("Jetson_frame",img)
                    if cv2.waitKey(1)&0xff==ord('1'):
                        break
            except socket.timeout as e:
                print(f"timeout:{e}")
    except KeyboardInterrupt:
        print("keyInterrupt halt")
    finally:
        server_socket.close()
        cv2.destroyAllWindows()
if __name__=="__main__":
    receive_frame()