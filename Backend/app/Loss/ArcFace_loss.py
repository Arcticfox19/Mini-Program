import torch
import torch.nn as nn
import torch.nn.functional as F


class ArcFaceLoss(nn.Module):
    # def __init__(self, feat_dim, num_class):
    #     super(ArcFaceLoss, self).__init__()
    #
    #     #任务3
    # def forward(self, x, y):
    #
    #     #任务3
    #     return loss

    def __init__(self, feat_dim, num_class):
        super(ArcFaceLoss, self).__init__()
        self.w = nn.Parameter(torch.randn(feat_dim, num_class))

    def forward(self, x,y):
        # 特征与权重 归一化
        m=10
        s=10
        #特征和参数在特征维度上标准化
        # x=F.normalize(x,dim=1)
        # w=F.normalize(self.w,dim=0)
        # cosa=torch.matmul(x,w)/(torch.sqrt(torch.sum(torch.pow(x,2))))*torch.sqrt(torch.sum(torch.pow(w,2)))
        # a=torch.acos(cosa)
        # loss=torch.exp(s*torch.cos(a+m))/(torch.sum(torch.exp(s*cosa),dim=1,keepdim=True))
        #       -torch.exp(s*cosa)+torch.exp(s*torch.cos(a+m))
        batch_size = x.size(0)
        _features = nn.functional.normalize(x, dim=1)
        _w = nn.functional.normalize(self.w, dim=0)
        theta = torch.acos(torch.matmul(_features, _w) / 10)  # /10防止下溢
        numerator = torch.exp(s * torch.cos(theta + m))
        denominator = torch.sum(torch.exp(s * torch.cos(theta)), dim=1, keepdim=True) - torch.exp(
            s * torch.cos(theta)) +numerator
        loss=-torch.sum(torch.log(torch.div(numerator, denominator)))/ batch_size


        return loss