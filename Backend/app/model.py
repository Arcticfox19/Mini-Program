from mobilenet import MobileNetV1
import torch
import torch.nn as nn
from torch.nn import functional as F
# from Loss.arcface import ArcFace
from Loss.Softmax_loss import SoftmaxLoss
from Loss.Center_loss import CenterLoss
from Loss.ArcFace_loss import ArcFaceLoss
import math
def distance(embeddings1, embeddings2, distance_metric=1):
    if distance_metric==0:
        # Euclidian distance
        diff = torch.subtract(embeddings1, embeddings2)
        dist = torch.sum(torch.square(diff),1)
    elif distance_metric==1:
        # Distance based on cosine similarity
        dot = torch.sum(torch.multiply(embeddings1, embeddings2), axis=1)
        norm = torch.linalg.norm(embeddings1, axis=1) * torch.linalg.norm(embeddings2, axis=1)
        similarity = dot / norm
        dist = torch.arccos(similarity) / math.pi
    else:
        raise 'Undefined distance metric %d' % distance_metric

    return dist
class ContrastiveLoss(nn.Module):
    def __init__(self, margin=1.0):
        super(ContrastiveLoss, self).__init__()
        self.margin = margin

    def forward(self, output1, output2, label):
        euclidean_distance = F.pairwise_distance(output1, output2)
        loss_contrastive = torch.mean((label) * torch.pow(euclidean_distance, 2) + (1-label) * torch.pow(torch.clamp(self.margin - euclidean_distance, min=0.0), 2))

        return loss_contrastive
class Model(nn.Module):
    def __init__(self,  dropout_keep_prob=0.5, embedding_size=128, num_classes=37, head=None,pretrain='facenet'):
        super(Model, self).__init__()
        embedding_size=embedding_size
        self.backbone = MobileNetV1()
        self.head=head
        if self.head=='ArcFaceLoss':
            self.Head= ArcFaceLoss(embedding_size, num_classes)
        elif self.head=='CenterLoss':
            self.Head=CenterLoss(embedding_size,num_classes)
        self.Dropout = nn.Dropout(1 - dropout_keep_prob)
        self.Bottleneck = nn.Linear(1024, embedding_size, bias=False)
        self.last_bn = nn.BatchNorm1d(embedding_size, eps=0.001, momentum=0.1, affine=True)
        self.softmaxloss=SoftmaxLoss(embedding_size,num_classes)


    def forward(self, x,y=None):

        b,c,h,w= x.shape

        x=self.backbone(x)
        x=self.Bottleneck(x)
        x=self.last_bn(x)
        #训练
        if self.training:
            softmax_loss = self.softmaxloss(x, y)
            #其他loss
            # if self.head is not None:
            #     head_loss=self.Head(x,y)
            if self.head == 'ArcFaceLoss':
                head_loss = self.Head(x,y)
            elif self.head == 'CenterLoss':
                head_loss = self.Head(x,y)#*0.01+self.softmaxloss(x, y)
            else:
                head_loss=torch.tensor(0.)
            #softmax loss
            #softmax_loss = self.softmaxloss(x, y)
            #pair_cls只在测试中生成，所以这里直接置0
            pair_cls = torch.tensor(0.)
        #验证&测试
        else:
            x1=x[:b//2]
            x2 = x[b // 2:]
            pair_cls= distance(x1,x2,distance_metric=1).squeeze(-1)
            head_loss = torch.tensor(0.)
            softmax_loss = torch.tensor(0.)

        return head_loss,softmax_loss,pair_cls


