from .RetinaFace.RetinaFaceDetector import RetinaFaceDetector
from .MobileFaceNet.MobileFacenetDetector import MobileFacenetDetector
import os
import cv2 as cv
import numpy as np
from utils.camera.camera_utils import init_camera
from utils.socket.tcp.tcp_utils import send_data
from utils.socket.socket_config import sock_face_config
import time
from utils.camera.camera_config import camera_para
from utils.Hostcontrol_utils.check_pc_status import is_pc_online
from utils.Hostcontrol_utils.CH9329Controller import CH9329Controller
from utils.Hostcontrol_utils.password import password

class FaceRecognition:
    def __init__(self):
        current_file_path=os.path.abspath(__file__)
        self.current_dir=os.path.dirname(current_file_path)
        self.face_db_dir = os.path.join(self.current_dir, 'face_db')
        self.score_thres=0.4
        retina_path=os.path.join(self.current_dir,'weights','mobilenet0.25_Final.pth')
        facenet_path=os.path.join(self.current_dir,'weights','068.ckpt')
        self.remodel=RetinaFaceDetector(retina_path)
        self.famodel=MobileFacenetDetector(facenet_path)
        self.known_names=[]
        self.known_features=[]
        self.load_face_db()
        self.REFERENCE_FACIAL_POINTS_96x112=np.array([
            [30.2946, 51.6963],
            [65.5318, 51.6963],
            [48.0252, 71.7366],
            [33.5493, 92.3655],
            [62.7299, 92.3655]
        ],dtype=np.float32)

    def face_alignment(self,frame,landmarks_list):
        face_list=[]
        for landmarks in landmarks_list:
            reshaped_landmarks=landmarks.reshape(5,2)
            M,_=cv.estimateAffinePartial2D(reshaped_landmarks,self.REFERENCE_FACIAL_POINTS_96x112,method=cv.LMEDS)
            warped=cv.warpAffine(frame,M,(96,112),borderValue=0.0)
            face_list.append(warped)
        return face_list
    
    def load_face_db(self):
        if not os.path.exists(self.face_db_dir):
            os.makedirs(self.face_db_dir)
            return
        self.known_names=[]
        self.known_features=[]
        for filename in os.listdir(self.face_db_dir):
            if filename.endswith('.npy'):
                path=os.path.join(self.face_db_dir,filename)
                try:
                    feature=np.load(path)
                    self.known_features.append(feature)
                    self.known_names.append(filename.split('.')[0])
                except Exception as e:
                    print(f'{e}')
            
    def recognize(self,frame):
        results=self.remodel.detect(frame)
        if results is None:
            return None
        face_list=self.face_alignment(frame,results[:,4:])
        feature_list=self.famodel.detect(face_list)
        name='None'
        max_score=-1
        for feature in feature_list:
            for index,known_feature in enumerate(self.known_features):
                score=np.sum(feature*known_feature)
                if score>self.score_thres and score>max_score:
                    max_score=score
                    name=self.known_names[index]
        return (True if name!='None' else False,name)

    def register_face(self,name,img_path):
        save_dir='face_db'
        dir=os.path.join(self.current_dir,save_dir)
        if not os.path.exists(dir):
            os.makedirs(dir)
        img=cv.imread(img_path)
        img=cv.resize(img,(camera_para['width'],camera_para['height']))
        if img is None:
            print('loading pic fail')
            return 
        boxes=self.remodel.detect(img)
        if boxes is None:
            print('no face')
            return
        face_list=self.face_alignment(img,boxes[:,4:])
        feature_list=self.famodel.detect(face_list)
        for index,feature in enumerate(feature_list):
            save_path=os.path.join(dir,name+f'{index}'+'.npy')
            np.save(save_path,feature)
        self.load_face_db()

    def run(self):
        con=CH9329Controller()
        pre_state=False
        loss=0
        stranger=0
        on=0
        Host_IP=sock_face_config['IP']
        Port=sock_face_config['PORT']
        cap=init_camera()
        if cap is None:
            return
        while(cap.isOpened()):
            ret,frame=cap.read()
            if not ret:
                print('capture fail')
                continue
            result=self.recognize(frame)
            if result is not None:
                if not result[0] and pre_state:
                    stranger+=1
                    if stranger==5:
                        if send_data(Host_IP,Port,'stranger',frame):
                            pre_state=False
                            loss=stranger=on=0
                elif result[0] and not pre_state:
                    on+=1
                    if on==2:
                        if is_pc_online(Host_IP):
                            con.type_string('\n')
                            con.type_string(password)
                        else:
                            pass
                        pre_state=True
                        loss=stranger=on=0
            else:
                if pre_state:
                    loss+=1
                    if loss==5:
                        if send_data(Host_IP,Port,'locked'):
                            pre_state=False
                            loss=stranger=on=0
            time.sleep(1)

                            

                    






                
            



        