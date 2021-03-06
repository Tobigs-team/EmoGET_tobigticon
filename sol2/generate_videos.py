"""
Copyright (C) 2017 NVIDIA Corporation.  All rights reserved.
Licensed under the CC BY-NC-ND 4.0 license (https://creativecommons.org/licenses/by-nc-nd/4.0/legalcode).

Sergey Tulyakov, Ming-Yu Liu, Xiaodong Yang, Jan Kautz, MoCoGAN: Decomposing Motion and Content for Video Generation
https://arxiv.org/abs/1707.04993

Generates multiple videos given a model and saves them as video files using ffmpeg

Usage:
    generate_videos.py [options] <model> <input_img> <target_class> <output_folder>

Options:
    -n, --num_videos=<count>                number of videos to generate [default: 1]
    -o, --output_format=<ext>               save videos as [default: gif]
    -f, --number_of_frames=<count>          generate videos with that many frames [default: 16]

    --ffmpeg=<str>                          ffmpeg executable (on windows should be ffmpeg.exe). Make sure
                                            the executable is in your PATH [default: ffmpeg]
"""

import os
import numpy as np
import imageio
import docopt
import torch
import torchvision
import cv2
from PIL import Image

from trainers import videos_to_numpy


if __name__ == "__main__":
    print("hi")
    args = docopt.docopt(__doc__)
    
    # generate_videos.py <model> <input_img> <target class> <output_folder>
    # ex) generate_videos.py ./generator.pt ./input_img.png disgust ./ouput
    # target clss = disgust / happiness / surprise
    generator = torch.load(args["<model>"], map_location={'cuda:0': 'cpu'})
    generator.eval()
    num_videos = int(args['--num_videos'])
    output_folder = args['<output_folder>']
    img_path = args['<input_img>']
    target_class = args['<target_class>'] #class로 입력
    number_of_frames = int(args['--number_of_frames'])


    # model input에 맞게 image 변환
    img = Image.open(img_path)
    img = img.resize((64, 64), Image.LANCZOS)
    img_tmp = np.array(img)

    image = torchvision.transforms.functional.to_tensor(img_tmp)
    image=image.unsqueeze(0)
    
    # class -> one hot
    if target_class == "disgust" :
        target_class_onehot = torch.from_numpy(np.array([1,0,0]))
    elif target_class == "happiness" :
        target_class_onehot = torch.from_numpy(np.array([0,1,0])) 
    else :
        target_class_onehot = torch.from_numpy(np.array([0,0,1]))

    # model input에 맞게 변환
    target_class_onehot = target_class_onehot.repeat(number_of_frames,1)
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    for i in range(num_videos): # 뽑을 video 수 만큼 iter
        v, _ = generator.sample_videos(image,1, target_class_onehot,number_of_frames)
        video = videos_to_numpy(v).squeeze().transpose((1, 2, 3, 0))

        imageio.mimsave(os.path.join(output_folder, "mine.gif"), video)
       
        
        print("save!")