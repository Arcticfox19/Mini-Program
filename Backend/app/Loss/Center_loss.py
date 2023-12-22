import torch
import torch.nn as nn
import torch.nn.functional as F


class CenterLoss(nn.Module):
    def __init__(self, feat_dim, num_classes):
        super(CenterLoss, self).__init__()
        self.centers = nn.Parameter(torch.randn(num_classes, feat_dim))
        self.num_classes=num_classes
        #任务3
    def forward(self, x, y):
        '''batch_size = x.size(0)
        distmat = torch.pow(x, 2)+ torch.pow(self.centers, 2)
        distmat = torch.pow(x, 2).sum(dim=1, keepdim=True).expand(batch_size, self.num_classes) + \
                 torch.pow(self.centers, 2).sum(dim=1, keepdim=True).expand(self.num_classes, batch_size).t()
        distmat.addmm_(1, -2, x, self.centers.t())
        classes = torch.arange(self.num_classes).long()
        y = y.unsqueeze(1).expand(batch_size, self.num_classes)
        mask = y.eq(classes.expand(batch_size, self.num_classes))
        dist = distmat * mask.float()
        loss = dist.clamp(min=1e-12, max=1e+12).sum() / batch_size    #not sure'''

        batch_size = x.size(0)
        _features = nn.functional.normalize(x)
        centers_batch = self.centers.index_select(0, y.long())
        loss=torch.sum(torch.pow(_features - centers_batch, 2)) / batch_size


        #任务3
        return loss