import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.artist import Artist
from matplotlib.patches import (Rectangle)
import noise
import numpy as np

import math


class EasyPlt:
    X_MIN = 0
    X_MAX = 100
    Y_MIN = 0
    Y_MAX = 100

    def __init__(self) -> None:
        self.fig, self.ax = plt.subplots(figsize=(6,6))
        self.update_bounds_limit()
        self.ax.set_xticks([])
        self.ax.set_yticks([])
    
    def update_bounds_limit(self, *, xmin=None, xmax=None, ymin=None, ymax=None):
        # 値の更新
        updated = False
        if xmin is not None:
            self.X_MIN = xmin
            updated = True
        if xmax is not None:
            self.X_MAX = xmax
            updated = True
        if ymin is not None:
            self.Y_MIN = ymin
            updated = True
        if ymax is not None:
            self.Y_MAX = ymax
            updated = True
        
        if updated:
            self.ax.set_xlim(self.X_MIN, self.X_MAX)
            self.ax.set_ylim(self.Y_MIN, self.Y_MAX)

    def add_object(self, object:Artist):
        self.ax.add_patch(object)

    def init_anim(self):
        return []

    def update(self, i):
        return []
    
    def run(self, enable_anim=False):
        if enable_anim:
            self.anim = FuncAnimation(self.fig, self.update, init_func=self.init_anim, frames=100)

        plt.show()

    def save(self, filepath:str):
        plt.savefig(filepath)

def init_world(count:int=5, chunk_width=20) -> EasyPlt:
    """count: chunkが縦横方向に何個並ぶか"""
    xmin,xmax,ymin,ymax = 0,chunk_width*count,0,chunk_width*count
    ep = EasyPlt()
    ep.update_bounds_limit(xmin=xmin,xmax=xmax,ymin=ymin,ymax=ymax)
    return ep


def get_random_color(i,j):
    color = "#"
    color += format(i*20+j*30+50,'x').zfill(2)
    color += format((i**2)*10,'x').zfill(2)
    color += format((j*3)**2+30, 'x').zfill(2)
    return color
# チャンクで区切った領域にそれぞれ別の色を付ける実験
def test_mapping_rectangles():
    cw, count = 10, 20
    ep = init_world(count, cw)

    rects = [[]]
    for i in range(count):
        _rects = []
        for j in range(count):
            color = get_random_color(i,j)
            print(color)
            rect = Rectangle(xy=(cw*i,cw*j), width=cw, height=cw, fc=color)
            ep.add_object(rect)
            _rects.append(rect)
        rects.append(_rects)

    ep.run()

# パーリンノイズによる地形生成のテスト
# とりあえず半分弱を緑地、半分強を砂地とした
# 100パターン生成したので"Pictures/entities"を参照のこと
colors = [
    # 緑地深部 (4)
    "#008822","#099128","#119a2d","#1aa333",
    # 緑地 (6)
    "#22AC38","#34b034","#46b430","#59b82c","#6bbb27","#7dbf23",
    # 緑地縁部 (9)
    "#8FC31F","#97c61b","#9fc917","#a7cc13","#afcf10","#b7d20c","#bfd508","#c7d804","#CFDB00",
    # 砂地 (23)
    "#FFDD77","#FFDD77","#FFDD77","#FFDD77","#FFDD77","#FFDD77","#FFDD77","#FFDD77","#FFDD77","#FFDD77",
    "#FFDD77","#FFDD77","#FFDD77","#FFDD77","#FFDD77","#FFDD77","#FFDD77","#FFDD77","#FFDD77","#FFDD77",
    "#FFDD77","#FFDD77"
]
def pnoise(x:float,y:float, seed:int,*,wavecount:int=5,octaves:int=3,persistence:float=0.3):
    """2次元のパーリンノイズを出力する\n
    x,y: 正規化されたx,y座標、x,y∈[0,1]\n
    seed: シード値\n
    wavecount: 小さいほど変化が乏しくなる（波幅が大きくなる）"""
    # (https://py3.hateblo.jp/entry/2014/02/21/160642) を参照
    return noise.pnoise2(x*wavecount,y*wavecount, base=seed,
                               octaves=octaves, persistence=persistence)
def test_mapping_with_pnoise(seed:int, enable_run=True):
    cw, count = 20, 20
    ep = init_world(count, cw)

    # パーリンノイズ用変数
    colorscount = len(colors)
    rects = [[]]
    for i in range(count):
        _rects = []
        for j in range(count):
            pn = pnoise(i/count,j/count,seed)
            color = colors[int((pn+1)*colorscount/2)]
            rect = Rectangle(xy=(cw*i,cw*j), width=cw, height=cw, fc=color, alpha=0.5)
            ep.add_object(rect)
            _rects.append(rect)
        rects.append(_rects)

    if enable_run:
        ep.run()
    #ep.save(f"C:/users/nggen/pictures/entities/seed_{str(seed).zfill(4)}.png")
def for99mapping():
    for i in range(100):
        test_mapping_with_pnoise(i,False)
        print("finish",i,"printing")


DEEP_MEADOWS = 2
MEADOWS = 1
PERIPHERAL_MEADOWS = 3
DESERT = 0
def get_chunk_type(eigenvalue:float) -> int:
    """チャンクの型を計算する"""
    if eigenvalue<=3:
        return DEEP_MEADOWS
    if eigenvalue<=9:
        return MEADOWS
    if eigenvalue<=18:
        return PERIPHERAL_MEADOWS
    return DESERT
class Chunk():
    eigenvalue:float
    """気候を決定するノイズから計算された実数値"""
    chunk_type: int
    width: int
    bottom: int
    left: int
    patch: Rectangle

    def __init__(self, value:float, width:int, left:int, bottom:int) -> None:
        """value:ノイズから生成された値 [-1,1]\n
        left/bottom: 左下の(x,y)座標"""
        self.eigenvalue = (value+1)*len(colors)/2
        self.patch = Rectangle(xy=(left,bottom), 
                               width=width, height=width, 
                               fc=colors[int(self.eigenvalue)], 
                               alpha=0.5)
        self.chunk_type = get_chunk_type(self.eigenvalue)

def test_chunk(seed=72):
    cw, count = 10, 100
    ep = init_world(count, cw)
    
    # チャンクを生成
    chunks:list[list[Chunk]] = [[]]
    for i in range(count):
        _chunks = []
        for j in range(count):
            pn = pnoise(i/count,j/count,seed)
            chunk = Chunk(pn, cw, cw*i,cw*j)

            ep.add_object(chunk.patch)
            _chunks.append(chunk)
        chunks.append(_chunks)

    ep.run()

def main():
    #test_mapping_rectangles()
    #test_mapping_with_pnoise(72)
    #for99mapping()
    test_chunk()


if __name__ == "__main__":
    main()