#!/usr/bin/env python
# Martin Kersner, m.kersner@gmail.com
# 2016/03/11

from __future__ import print_function
caffe_root = 'code/'
import sys
sys.path.insert(0, caffe_root + 'python')

import os
import numpy as np
from PIL import Image as PILImage
import matplotlib.pyplot as plt
import caffe

from utils import pascal_palette_invert, pascal_mean_values
from segmenter import Segmenter

def main():
  img_size = 505

  gpu_id, net_path, model_path, img_paths = process_arguments(sys.argv)
  palette = pascal_palette_invert()
  net = Segmenter(net_path, model_path, gpu_id)

  for img_path in img_paths:
    img, cur_h, cur_w = preprocess_image(img_path, img_size)
    segm_result = net.predict([img])
    segm_post = postprocess_segmentation(segm_result, cur_h, cur_w, palette)
    
    concatenate = True
    segm_name = os.path.basename(img_path).split('.')[0]+'-label.png'
    save_result(segm_post, segm_name, concatenate, img_path)

def preprocess_image(img_path, img_size):
  if not os.path.exists(img_path):
    print(img_path)
    return None, 0, 0

  input_image = 255 * caffe.io.load_image(img_path)
  
  image = PILImage.fromarray(np.uint8(input_image))
  image = np.array(image)
  
  mean_vec = np.array([103.939, 116.779, 123.68], dtype=np.float32)
  reshaped_mean_vec = mean_vec.reshape(1, 1, 3);
  preprocess_img = image[:,:,::-1]
  preprocess_img = preprocess_img - reshaped_mean_vec
  
  # Pad as necessary
  cur_h, cur_w, cur_c = preprocess_img.shape
  pad_h = img_size - cur_h
  pad_w = img_size - cur_w
  preprocess_img = np.pad(preprocess_img, pad_width=((0, pad_h), (0, pad_w), (0, 0)), mode = 'constant', constant_values = 0)

  return preprocess_img, cur_h, cur_w

def postprocess_segmentation(segmentation, cur_h, cur_w, palette):
  segmentation_tmp = segmentation[0:cur_h, 0:cur_w]
  postprocess_img = PILImage.fromarray(segmentation_tmp)
  postprocess_img.putpalette(palette)

  return postprocess_img

def process_arguments(argv):
  gpu_id     = None
  net_path   = None
  model_path = None 
  img_paths  = None 

  if len(argv) >= 5:
    gpu_id     = int(argv[1])
    net_path   = argv[2]
    model_path = argv[3]
    img_paths  = argv[4:]
  else:
    help()

  return gpu_id, net_path, model_path, img_paths

def save_result(output_img, img_name, concatenate, input_img):
  if concatenate == False:
    output_img.save(img_name)
  else:
    input_img = PILImage.open(input_img)
    w = input_img.size[0] + output_img.size[0]
    h = input_img.size[1]

    concatate_img = PILImage.new("RGB", (w, h))
    concatate_img.paste(input_img, (0, 0))
    concatate_img.paste(output_img, (input_img.size[0], 0))

    concatate_img.save(img_name)

def help():
  print('Usage: python deeplab.py GPU_ID NET MODEL IMAGE\n'
        'GPU_ID specifies gpu number used for computation.\n'
        'NET file describing network (prototxt extension).\n'
        'MODEL file generated by caffe (caffemodel extension).\n'
        'IMAGE one image has to be passed as argument.'
        , file=sys.stderr)

  exit()

if __name__ == '__main__':
  main()
