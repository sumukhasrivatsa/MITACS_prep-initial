
from cmath import cos
import torch.nn.functional as F
from torch.distributions import Uniform
import torch.nn as nn
import torch
import numpy as np

class netA(nn.Module):
    def __init__(self):
        super(netA, self).__init__()
    
        
        self.mean = torch.tensor(0)
        self.std = torch.tensor(0)


        ########### ACTUAL NETA
        self.fc_loc = nn.Sequential(
                nn.Linear(6, 8),
                nn.ReLU(),
                nn.Dropout(0.2),
                nn.Linear(8, 6  ),
                nn.ReLU(),
                nn.Dropout(0.2),
                nn.Linear(6,1)
            )
       

    def transform_images(self,images,labels):
        self.images=images
        self.labels=labels
        bs = self.images.shape[0]
        
        self.uniform = Uniform(low=-torch.ones(1, 6), high=torch.ones(1, 6))
        #print(self.uniform)
        noise = self.uniform.rsample()
        self.noise=noise.repeat(bs,1)
        
        
        #print(noise)
        # get transformation matrix
        
        self.affinematrix,self.inverse_matrix= self.get_rotation_matrix()

    
        # compute transformation grid
        self.grids = F.affine_grid(self.affinematrix, self.images.size(), align_corners=True)
        
        # apply transformation
        self.x = F.grid_sample(self.images, self.grids, align_corners=True)
        
        
        return self.x,self.labels,self.affinematrix,self.inverse_matrix

    def get_rotation_matrix(self):
        identitymatrix = torch.eye(2, 3)
        #print(identitymatrix)
        identitymatrix = identitymatrix.unsqueeze(0)
        #print(identitymatrix)
        identitymatrix = identitymatrix.repeat(self.noise.shape[0], 1, 1)
        #print(identitymatrix)

        identitymatrix2 = torch.eye(2, 3)
        #print(identitymatrix)
        identitymatrix2 = identitymatrix2.unsqueeze(0)
        #print(identitymatrix)
        identitymatrix2 = identitymatrix2.repeat(self.noise.shape[0], 1, 1)
        
        self.theta = self.fc_loc(self.noise)
        ###THETA IS NOT IN DEGREE OR RADIANS SO IM ASSUMING IT IS IN RADIANS 

        inverse_matrix=identitymatrix2
        
        affinematrix = identitymatrix
        
        #print(self.theta[0])
        #print(torch.sin(self.theta)[0])
        #print(-torch.sin(self.theta[0]))
        
        
        #self.inverse_matrix=identitymatrix
       
        affinematrix[:, 0, 0] = torch.cos(self.theta[0])
        affinematrix[:, 0, 1] = torch.sin(self.theta[0])
        affinematrix[:, 1, 0] = -torch.sin(self.theta[0])
        affinematrix[:, 1, 1] = torch.cos(self.theta[0])
        
        inverse_matrix[:, 0, 0] = torch.cos(self.theta[0])
        inverse_matrix[:, 0, 1] = -torch.sin(self.theta[0])
        inverse_matrix[:, 1, 0] = torch.sin(self.theta[0])
        inverse_matrix[:, 1, 1] = torch.cos(self.theta[0])
        
       

      
        
        return affinematrix,inverse_matrix