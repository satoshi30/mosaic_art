# -*- coding: utf-8 -*-

from PIL import Image
from glob import glob
import argparse
from tqdm import tqdm
import numpy as np
from utils import scale_calc, transform_subimg2array, distance_array_calc
from PIL import ImageStat

parser = argparse.ArgumentParser(description="make_mosaic_art")
parser.add_argument('--main_image_path', default='./main.png', help="The path where the main image is stored")
parser.add_argument('--sub_dir_path', default="./sample_image_sub_dir", help="The dir path where sub images are stored")
parser.add_argument('--sub_extention', default=".jpg", help="extention of sub images")
parser.add_argument('--image_mode', default="RGB", help="Select from the image mode of Pillow Library")
parser.add_argument('--calc_mode', default="per_image", help="Calculation mode to judge similarity, per_image or per_pixel")
parser.add_argument('--img_duplication', default="True", help="Existence of duplication of images used for mosaic art")
parser.add_argument('--save_path', default=None)

def main():
  # 引数を読み込み
  args = parser.parse_args()

  # メインイメージを読み取り、変換
  main_img = Image.open(args.main_image_path)
  main_img = main_img.convert(args.image_mode)
  im_width, im_height = main_img.size

  # サブイメージのパスリストを取得
  sub_files = glob(args.sub_dir_path + "/*" + args.sub_extention)
  # サブイメージの数
  num_sub = len(sub_files)

  # メインイメージ、サブイメージのサイズを計算（ぴったり合うように）
  im_width, im_height, sub_w, sub_h, pixel = scale_calc(im_width, im_height, num_sub)

  # メインイメージをコンバート
  main_img = main_img.convert(args.image_mode)
  # メインイメージをリサイズ
  main_img = main_img.resize((im_width, im_height), resample=Image.NEAREST)

  # サブイメージを配列化
  sub_img_array = transform_subimg2array(args.image_mode, num_sub, sub_w, sub_h, sub_files)
  print(sub_img_array.shape)

  # イメージ毎の距離を計算する
  distance_array = distance_array_calc(args.calc_mode, pixel, num_sub, main_img, sub_w, sub_h, sub_img_array)

  if args.img_duplication == "True":
    # モザイク画像の初期設定
    mosaic_img = Image.new(args.image_mode, (im_width, im_height))
    # print(distance_array)
    for i in tqdm(range(pixel)):
      for j in range(pixel):
        # 距離が最小のインデックスを取得
        sub_index = int(distance_array[i, j, :].argmin())
        # print(sub_index, distance_array[i, j, :].mean())
        # 選択された画像を読み取って処理、貼り付け
        choice_img = Image.open(sub_files[sub_index])
        choice_img = choice_img.convert(args.image_mode)
        choice_img = choice_img.resize((sub_w, sub_h), resample=Image.NEAREST)
        mosaic_img.paste(choice_img, (sub_w*j, sub_h*i))

  elif args.img_duplication == "False":
    # sub_fileのindexの配列を取得
    from utils import pulp_mosaic
    sub_file_index = pulp_mosaic(pixel, pixel, num_sub, distance_array)
    print("The best indexes of subfile were obtained!!")

    # モザイク画像の初期設定
    mosaic_img = Image.new(args.image_mode, (im_width, im_height))
    for i in tqdm(range(pixel)):
      for j in range(pixel):
        # 選択された画像を読み取って処理、貼り付け
        choice_img = Image.open(sub_files[sub_file_index[i, j]])
        choice_img = choice_img.convert(args.image_mode)
        choice_img = choice_img.resize((sub_w, sub_h), resample=Image.NEAREST)
        mosaic_img.paste(choice_img, (sub_w*j, sub_h*i))

  else:
    raise Exception("img_deplication_error!!")

  if args.save_path == None:
    save_path = "./imgm-{}_calcm-{}_dup-{}_subimg-{}{}".format(args.image_mode, args.calc_mode, args.img_duplication, args.sub_dir_path.split("/")[-1], args.sub_extention)
  else:
    save_path = args.save_path
  mosaic_img.save(save_path)
  print("Mosaic art is completed!!")

if __name__ == "__main__":
  main()
