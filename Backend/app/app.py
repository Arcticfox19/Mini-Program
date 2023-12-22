import base64
from flask import Flask, request, jsonify, render_template, url_for,send_file
from flask_cors import *
from argparse import ArgumentParser
import imageio
from skimage.transform import resize
from demo import make_animation,find_best_frame,load_checkpoints
from skimage import img_as_ubyte
import os
import time

app = Flask(__name__)

CORS(app, supports_credentials=True)

@app.route('/getSrcImg', methods=["POST"])
def get_srcImg():
    '''接收传来的图片'''
    params_file = request.files['srcImg']
    params_file.save("srcImg.jpg")
    return "后端接收到图片"

@app.route('/getDriveVideo', methods=["POST"])
def get_driveVideo():
    '''接收传来的视频'''
    params_file = request.files['driveVideo']
    params_file.save("driveVideo.avi")
    return "后端接收到视频"

@app.route('/getImg1', methods=["POST"])
def get_Img1():
    '''接收传来的图片'''
    params_file = request.files['Img1']
    params_file.save("Img1.jpg")
    return "后端接收到图片"

@app.route('/getImg2', methods=["POST"])
def get_Img2():
    '''接收传来的图片'''
    params_file = request.files['Img2']
    params_file.save("Img2.jpg")
    return "后端接收到图片"


@app.route('/verify', methods=["GET"])
def verify():
    isSame = "False"
    # 处理传来的两张图片，进行人脸验证
    import torch
    import os
    from model import Model
    from torchvision import transforms as T
    from data_preprocess import image_preprocess
    # image to tensor
    normalize = T.Normalize(mean=[0.5], std=[0.5])
    image_transforms = T.Compose([
        T.Resize((160, 160)),
        T.ToTensor(),
        normalize])
    if __name__ == '__main__':
        ver_thre = 0.4199  # 人脸验证是否匹配阈值,替换为训练最后一轮输出的阈值
        pretrained_path = 'arcface_model.path'  # 替换为训练产生的trained_model.path路径
        image1 = 'Img1.jpg'  # 测试图片1
        image2 = 'Img2.jpg'  # 测试图片2
        # image preprocess
        image1 = image_preprocess(image1)
        image2 = image_preprocess(image2)
        image1 = image_transforms(image1)
        image2 = image_transforms(image2)
        images_pair = torch.cat((image1.unsqueeze(0), image2.unsqueeze(0)), dim=0)

        model = Model()
        # load pretrain model
        if os.path.isfile(pretrained_path):
            print("=> loading pretrained '{}'".format(pretrained_path))
            pretained = torch.load(pretrained_path, map_location=torch.device('cpu'))
            model_dict = model.state_dict()
            state_dict = {k: v for k, v in pretained.items() if k in model_dict.keys()}
            model_dict.update(state_dict)
            model.load_state_dict(model_dict)
            print("=> loaded pretrained '{}'".format(pretrained_path))
        else:
            print(" path is wrong")

        model.eval()
        _, _, pair_cls = model(images_pair)
        # 判断是否匹配
        pair_result = (pair_cls <= ver_thre)
        # print('Similarity score is:' + str(1 - pair_cls.item()))
        # print('Face verification result:' + str(pair_result.item()))
        isSame=str(pair_result.item())
    return isSame

@app.route('/faceChange/<count>/', methods=["GET"])
def face_change(count):
    #number=time.gmtime()
    #处理传来的两张图片,假设生成换脸后的图片为resImg.jpg

    parser = ArgumentParser()
    parser.add_argument("--config", required="./config/vox-adv-256.yaml", help="path to config")
    parser.add_argument("--checkpoint", default='./vox-adv-cpk.pth.tar', help="path to checkpoint to restore")

    parser.add_argument("--source_image", default='./srcImg.jpg', help="path to source image")
    parser.add_argument("--driving_video", default='driveVideo.avi', help="path to driving video")
   # parser.add_argument("--result_video", default='./result.mp4', help="path to output")
    parser.add_argument("--result_video", default='./result'+count+ '.mp4', help="path to output")

    parser.add_argument("--relative", dest="relative", action="store_true",
                        help="use relative or absolute keypoint coordinates")
    parser.add_argument("--adapt_scale", dest="adapt_scale", action="store_true",
                         help="adapt movement scale based on convex hull of keypoints")

    parser.add_argument("--find_best_frame", dest="find_best_frame", action="store_true",
                        help="Generate from the frame that is the most alligned with source. (Only for faces, requires face_aligment lib)")

    parser.add_argument("--best_frame", dest="best_frame", type=int, default=None,
                        help="Set frame to start from.")

    parser.add_argument("--cpu", dest="cpu", action="store_true", help="cpu mode.")

    parser.set_defaults(relative=False)
    parser.set_defaults(adapt_scale=False)

    opt = parser.parse_args()

    source_image = imageio.imread(opt.source_image)
    reader = imageio.get_reader(opt.driving_video)
    fps = 25
    driving_video = []
    try:
        for im in reader:
             driving_video.append(im)
    except RuntimeError:
        pass
    reader.close()

    source_image = resize(source_image, (256, 256))[..., :3]
    driving_video = [resize(frame, (256, 256))[..., :3] for frame in driving_video]
    generator, kp_detector = load_checkpoints(config_path=opt.config, checkpoint_path=opt.checkpoint, cpu=opt.cpu)

    if opt.find_best_frame or opt.best_frame is not None:
        i = opt.best_frame if opt.best_frame is not None else find_best_frame(source_image, driving_video, cpu=opt.cpu)
        print("Best frame: " + str(i))
        driving_forward = driving_video[i:]
        driving_backward = driving_video[:(i + 1)][::-1]
        predictions_forward = make_animation(source_image, driving_forward, generator, kp_detector,
                                              relative=opt.relative, adapt_movement_scale=opt.adapt_scale, cpu=opt.cpu)
        predictions_backward = make_animation(source_image, driving_backward, generator, kp_detector,
                                               relative=opt.relative, adapt_movement_scale=opt.adapt_scale, cpu=opt.cpu)
        predictions = predictions_backward[::-1] + predictions_forward[1:]
    else:
        predictions = make_animation(source_image, driving_video, generator, kp_detector, relative=opt.relative,
                                      adapt_movement_scale=opt.adapt_scale, cpu=opt.cpu)
    #result_video_path=os.getcwd() + '/result.mp4'
    imageio.mimsave(opt.result_video, [img_as_ubyte(frame) for frame in predictions], fps=fps)

    # with open("result.mp4", 'rb') as file:
    #     res = file.read()  # 转换为二进制流
    #     res = base64.b64encode(res)   # 转为base64码

    # print(os.getcwd())  # 获取main函数所在运行文件目录
    # path = os.getcwd() + '/result.mp4'
    # print(path.type())
    # return path
    return "ok"


@app.route('/getVideo/<count>/',methods=["GET"])
def get_video(count):
    if os.path.exists("result" + count + ".mp4"):
        return send_file("result"+ count + ".mp4")
    import sys
    sys.exit()


@app.route('/queryVideo/<count>/',methods=["GET"])
def query_video(count):
    #if os.path.exists("result.mp4"):
    if os.path.exists("result"+ count + ".mp4"):
        return "换脸视频已经生成"
    import sys
    sys.exit()

if __name__=='__main__':
    # host设置为0.0.0.0，以使服务器在外部可用
    app.run(host = '0.0.0.0', port = 8088)