from .mobilefacenet import MobileFacenet
import torch
import cv2 as cv
import numpy as np
import torch.nn.functional as f
from collections import OrderedDict

class MobileFacenetDetector:
    def __init__(self,model_path):
        self.device='cuda' if torch.cuda.is_available() else 'cpu' 
        self.model=MobileFacenet().to(self.device)
        self.model.load_state_dict(self.state_init(model_path))
        self.model.eval()

    def state_init(self,model_path):
        state=torch.load(model_path,weights_only=True)
        state=state['net_state_dict']
        new_state=OrderedDict()
        for k,v in state.items():
            name=k[:7]
            if name=='module.':
                name=k[7:]
            else:
                name=k
            new_state[name]=v
        return new_state
            
    def detect(self,face_list):
        face_process=[]
        for face in face_list:
            face_resize=cv.resize(face,(96,112))
            face_resize=cv.cvtColor(face_resize,cv.COLOR_BGR2RGB)
            face_resize=face_resize.astype(np.float32)
            face_resize=(face_resize-127.5)/128
            face_resize=face_resize.transpose(2,0,1)
            face_resize=torch.from_numpy(face_resize)
            face_process.append(face_resize)
        face_tensor=torch.stack(face_process,dim=0).to(self.device)
        with torch.no_grad():
            output=self.model(face_tensor)
        output=f.normalize(output,2,1)
        output=output.cpu().numpy()
        return output
        
    