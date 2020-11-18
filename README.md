# このリポジトリについて
Pythonのプログラムにて、モザイクアートを作成します

Original Image             |  Mosaic Art
:-------------------------:|:-------------------------:
![](main.png)  |  ![](imgm-RGBA_calcm-per_pixel_dup-True_subimg-trainA.png)


# 動作させる
1 このリポジトリをclone
```
  git clone https://github.com/satoshi30/mosaic_art.git
```
2 必要なライブラリをinstall
```
  cd mosaic_art
  pip install -r requirements.txt
```

3 main.pyを実行するとモザイクアートが作成できます
```
  python main.py
```

4 main.pyのオプション
```
  --main_image_path
    モザイク写真にする画像ファイルのパスを指定

  --sub_dir_path
    モザイク写真に組み込む画像ファイルが格納されているディレクトリのパスを指定

  --sub_extention
    sub_dir_pathに格納されている画像ファイルに拡張子を指定

  --image_mode
    PillowのImageモードに対応　"RGB", "RGBA", "L"から選択

  --calc_mode
    "per_image" or "per_pixel"
      "per_image" 画像毎に平均値を計算し、比較
      "per_pixel" ピクセル毎に平均値を計算し、比較

  --img_duplication
    True or False
    モザイク写真に組み込む画像の重複の可否
    True 元の画像との距離の差が最小になる画像をあてはめていくいく
    False  pulpのアルゴリズムで組み合わせた画像と元の画像で距離の和が最小になるように計算
      requirements_pulp.txtをインストール
      画像枚数が多いと計算に時間がかかるのでおすすめしません

  --save_path
    保存先のパスを指定、指定しない場合はpwdに保存
