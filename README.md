# rail2kml

[国土数値情報](https://nlftp.mlit.go.jp/ksj/)の鉄道線形データをKMLファイルで出力するプログラム。  
任意の駅間での抽出が可能。
作成したKMLファイルは、[Googleマイマップ](https://www.google.co.jp/intl/ja/maps/about/mymaps/)などで表示させることが可能。

## 使い方

### 線形データのダウンロード

[国土数値情報](https://nlftp.mlit.go.jp/ksj/)より、[「鉄道（ライン）」](https://nlftp.mlit.go.jp/ksj/gml/datalist/KsjTmplt-N02-v2_3.html)のデータをダウンロード。  
解凍すると、線形（RaillroadSection）と駅（Station）のデータが複数の形式で入っている。  
今回使うのは、線形と駅データのシェイプファイル（拡張子が.shpと.dbfのファイル）。

### 実行

#### バッチファイルによる簡単な実行方法（Windowsのみ）

1. [Python 3](https://www.python.org/) をダウンロードして、インストール。（最新版で恐らく大丈夫。動作確認は Python 3.9.5 で実施。）
1. ``setup_venv.cmd``を実行し、実行環境を作成。（初回のみ）
1. ``run.cmd``を実行し、アプリケーションを起動。

#### Windows以外での実行方法（上記バッチファイルでやっていることの説明）

実行には [Python 3](https://www.python.org/) が必要。（Python 3.9.5 で動作確認済み。）  
必要なパッケージは``requirements.txt``の通り。  
以下を実行するとインストールされる。  
この際、[仮想環境](https://docs.python.org/ja/3/library/venv.html)を作成することを推奨。

``` [bash]
pip install -r requirements.txt
```

後は``app.py``を以下のように実行すると、アプリケーションが起動する。  

``` [bash]
python3 app.py
```

### 注意

[国土数値情報](https://nlftp.mlit.go.jp/ksj/)は、[利用規約](https://nlftp.mlit.go.jp/ksj/other/agreement.html)にしたがって使用すること。  

## 出典

[パッチファイル（patch/patch.json）](patch/patch.json)は、「国土数値情報（鉄道データ）」（国土交通省）（[https://nlftp.mlit.go.jp/ksj/gml/datalist/KsjTmplt-N02-v2_3.html](https://nlftp.mlit.go.jp/ksj/gml/datalist/KsjTmplt-N02-v2_3.html)）を加工して作成。  
