# -*- coding: utf-8 -*-

from tqdm import tqdm
from PIL import Image, ImageStat
import numpy as np

def scale_calc(im_width, im_height, n_files):
  pixel = int(np.sqrt(n_files))
  sub_w = im_width // pixel
  sub_h = im_height // pixel
  im_width = sub_w * pixel
  im_height = sub_h * pixel
  return im_width, im_height, sub_w, sub_h, pixel


def transform_subimg2array(image_mode, num_sub, sub_w, sub_h, sub_files):
  print("transforming sub images to array")

  # image_modeからarrayのshapeを計算
  if image_mode == "RGBA":
    sub_img_array = np.empty((num_sub, sub_h, sub_w, 4))
  elif image_mode == "RGB":
    sub_img_array = np.empty((num_sub, sub_h, sub_w, 3))
  elif image_mode == "L":
    sub_img_array = np.empty((num_sub, sub_h, sub_w))
  else:
    raise Exception("image_mode_error!!")

  i = 0
  for sub_img_path in tqdm(sub_files):
    sub_img = Image.open(sub_img_path)
    sub_img = sub_img.convert(image_mode)
    sub_img = sub_img.resize((sub_w, sub_h), resample=Image.NEAREST)
    sub_img_array[i] = np.asarray(sub_img)
    i += 1

  print("All sub images are transformed to array!!")
  return sub_img_array


def distance_array_calc(calc_mode, pixel, num_sub, main_img, sub_w, sub_h, sub_img_array):
  # ループでメイン画像を切り取って、距離を計算する、合計した値を保管
  print("calculating distances")
  distance_array = np.zeros((pixel, pixel, num_sub))
  if calc_mode == "per_image":
    sub_img_array = sub_img_array.mean(axis=2).mean(axis=1)

  for i in tqdm(range(pixel)):
    for j in range(pixel):
      # イメージをクロップ (left, top, right, bottom)
      im_crop = main_img.crop((sub_w*j, sub_h*i, sub_w*(j+1), sub_h*(i+1)))

      # arrayへ変換
      im_crop_array = np.asarray(im_crop)[np.newaxis]

      if calc_mode == "per_image":
        im_crop_array = im_crop_array.mean(axis=2).mean(axis=1)
        distance = sub_img_array - im_crop_array
        distance = np.power(distance, 2)

        if distance.ndim > 1:
          distance = distance.sum(axis=1)
        distance_array[i, j, :] = distance

      elif calc_mode == "per_pixel":
        distance = sub_img_array - im_crop_array
        distance = np.power(distance, 2)
        distance = distance.mean(axis=2).mean(axis=1)

        if distance.ndim > 1:
          distance = distance.sum(axis=1)
        distance_array[i, j, :] = distance

  print("All distances are completly calculated!!")
  print("distance array shape : {}".format(distance_array.shape))
  return distance_array


# モザイクアート作成時に全体の距離が最小になる組み合わせのインデックスリストを返す
# 引数は縦、横、奥行, 最小値のパターンを求めたいボックス
def pulp_mosaic(v_num, h_num, ch_num, box_array):
  from pulp import LpProblem, lpSum, lpDot, value, LpStatus
  from ortoolpy import addbinvars
  import time
  start = time.time()
  print("Calculate the optimal combination")
  print("Variables : {}".format(v_num*h_num*ch_num))
  if box_array.shape != (v_num, h_num, ch_num):
    raise Exception("shape does not match!!")
  #　変数宣言
  variable = np.array(addbinvars(v_num, h_num, ch_num))
  # 目的関数の最小化
  prob = LpProblem()
  # 目的関数の設定
  prob += (box_array * variable).sum()
  # 制約条件の設定
  for ch in range(ch_num):
    prob += variable[:, :, ch].sum() <= 1
  for v in range(v_num):
    for h in range(h_num):
      prob += variable[v, h, :].sum() == 1
  # 問題を解く
  prob.solve()
  if LpStatus[prob.status] != "Optimal":
    raise Exception("could not be optimized!!")
  else:
    print("status = " + LpStatus[prob.status])
  # 最適化された変数の値を抽出
  opt_var = np.vectorize(value)(variable).astype(int)
  # 全体で最小となるインデックスの組み合わせ
  bit_index = np.empty((v_num, h_num), dtype=np.int32)
  for v in range(v_num):
    for h in range(h_num):
      bit_index[v, h] = np.where(opt_var[v, h, :] == 1)[0]
  elapsed_time = time.time() - start
  print("elapsed_time:{0}".format(elapsed_time) + "[sec]")
  return bit_index
