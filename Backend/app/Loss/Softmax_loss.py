import torch
import torch.nn as nn
import torch.nn.functional as F


class SoftmaxLoss(nn.Module):
    def __init__(self, feat_dim, num_class):
        super(SoftmaxLoss, self).__init__()
        self.w=nn.Parameter(torch.Tensor(feat_dim,num_class))
        self.b=nn.Parameter(torch.Tensor(1,num_class))
        nn.init.xavier_normal_(self.w)
        nn.init.constant_(self.b,0.)
        #任务3
    def forward(self, x, y):
        logits=x.mm(self.w)+self.b
        logits = logits.squeeze(-1)
        loss=F.cross_entropy(logits,y)
        #任务3
        return loss
