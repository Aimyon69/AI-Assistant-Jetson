from .retinaface import RetinaFace
import numpy as np
import torch
from .config import cfg_mnet
from collections import OrderedDict
import cv2 as cv
from math import ceil
from torchvision.ops import nms
from utils.camera.camera_config import camera_para

class RetinaFaceDetector:
    def __init__(self,model_path):
        self.device='cuda' if torch.cuda.is_available() else 'cpu'
        self.model=RetinaFace(cfg=cfg_mnet,phase='test').to(self.device)
        self.prior_box=self.priorBox().to(self.device)
        self.scale=torch.tensor([camera_para['width'],camera_para['height']]).to(self.device)
        self.score_thres=0.8
        state_dict=torch.load(model_path,map_location=self.device,weights_only=True)
        new_state_dict=OrderedDict()
        for k,v in state_dict.items():
            module_name=k[:7]
            if module_name=='module.':
                module_name=k[7:]
            else:
                module_name=k
            new_state_dict[module_name]=v
        self.model.load_state_dict(new_state_dict)
        self.model.eval()

    def test_output(self,img_path):
        img=cv.imread(img_path,cv.IMREAD_COLOR)
        img=np.float32(img)
        img-=(104,117,123)
        img=img.transpose(2,0,1)
        img=torch.from_numpy(img)
        img=img.unsqueeze(0)
        img=img.to(self.device)
        output=self.model(img)
        print(len(output))
        for v in output:
            print(v.shape)
        print(output[0][0][0])

    def priorBox(self):
        prior_box=list()
        img_width=camera_para['width']
        img_height=camera_para['height']
        for k,step in enumerate(cfg_mnet['steps']):
            feature_x=ceil(img_width/step)
            feature_y=ceil(img_height/step)
            grid_y,grid_x=torch.meshgrid(torch.arange(feature_y),torch.arange(feature_x),indexing='ij')
            cx=(grid_x+0.5)*step/img_width #notice:Naturalization
            cy=(grid_y+0.5)*step/img_height
            cx=cx.unsqueeze(-1) #[H,W,1]
            cy=cy.unsqueeze(-1)
            min_sizes=cfg_mnet['min_sizes'][k]
            min_sizes=torch.tensor(min_sizes,dtype=torch.float32)
            fw=min_sizes/img_width
            fh=min_sizes/img_height
            cx=cx.expand(-1,-1,len(min_sizes)) #[H,W,A]
            cy=cy.expand(-1,-1,len(min_sizes))
            fw=fw.view(1,1,len(min_sizes))
            fw=fw.expand(feature_y,feature_x,-1) #[H,W,A]
            fh=fh.view(1,1,len(min_sizes))
            fh=fh.expand(feature_y,feature_x,-1)
            boxes=torch.stack([cx,cy,fw,fh],dim=3)
            boxes=boxes.view(-1,4)
            prior_box.append(boxes)
        return torch.cat(prior_box,dim=0)

    def decode(self,loc,priors):
        iboxes,_,iland=loc
        iboxes.squeeze_(0)
        iland.squeeze_(0)
        boxes=torch.cat(((priors[:,:2]+iboxes[:,:2]*cfg_mnet['variance'][0]*priors[:,2:])*self.scale,
                        (priors[:,2:]*torch.exp(iboxes[:,2:]*cfg_mnet['variance'][1])*self.scale)
        ),dim=1)
        boxes[:,:2]-=boxes[:,2:]/2
        boxes[:,2:]+=boxes[:,:2]
        land=torch.cat(((priors[:,:2]+iland[:,:2]*cfg_mnet['variance'][0]*priors[:,2:])*self.scale,
                        (priors[:,:2]+iland[:,2:4]*cfg_mnet['variance'][0]*priors[:,2:])*self.scale,
                        (priors[:,:2]+iland[:,4:6]*cfg_mnet['variance'][0]*priors[:,2:])*self.scale,
                        (priors[:,:2]+iland[:,6:8]*cfg_mnet['variance'][0]*priors[:,2:])*self.scale,
                        (priors[:,:2]+iland[:,8:10]*cfg_mnet['variance'][0]*priors[:,2:])*self.scale,
        ),dim=1)
        result=torch.cat((boxes,land),dim=1)
        result[:,0::2]=result[:,0::2].clamp(min=0,max=camera_para['width'])
        result[:,1::2]=result[:,1::2].clamp(min=0,max=camera_para['height'])
        return result
    
    def detect(self,frame):
        '''
        Args:
            img:numpy
        '''
        if frame.shape[0]!=camera_para['height'] or frame.shape[1]!=camera_para['width']:
                print('camera param dont match')
                return None
        img=np.float32(frame)
        img-=(104,117,123)
        img=img.transpose(2,0,1)
        img=torch.from_numpy(img)
        img=img.unsqueeze(0)
        img=img.to(self.device)
        with torch.no_grad():
            output=self.model(img)
        result=self.decode(output,self.prior_box)
        scores=output[1].squeeze(0)
        scores=scores[:,1]
        index=scores>self.score_thres
        result=result[index]
        scores=scores[index]
        keep=nms(result[:,0:4],scores,iou_threshold=0.3)
        result=result[keep]
        scores=scores[keep]
        if result.shape[0]==0:
            return None
        scores=scores.unsqueeze(1)
        return result.cpu().numpy()
        