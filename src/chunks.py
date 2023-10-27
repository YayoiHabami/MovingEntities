from matplotlib.patches import Rectangle
import noise

# 定数
DEEP_MEADOWS = 2
MEADOWS = 1
PERIPHERAL_MEADOWS = 3
DESERT = 0

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



# クラス
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


# 関数
def pnoise(x:float,y:float, seed:int,*,wavecount:int=5,octaves:int=3,persistence:float=0.3):
    """2次元のパーリンノイズを出力する\n
    x,y: 正規化されたx,y座標、x,y∈[0,1]\n
    seed: シード値\n
    wavecount: 小さいほど変化が乏しくなる（波幅が大きくなる）"""
    # (https://py3.hateblo.jp/entry/2014/02/21/160642) を参照
    return noise.pnoise2(x*wavecount,y*wavecount, base=seed,
                               octaves=octaves, persistence=persistence)

def get_chunk_type(eigenvalue:float) -> int:
    """チャンクの型を計算する"""
    if eigenvalue<=3:
        return DEEP_MEADOWS
    if eigenvalue<=9:
        return MEADOWS
    if eigenvalue<=18:
        return PERIPHERAL_MEADOWS
    return DESERT

def create_chunks(chunk_width:int, world_width:int, world_height:int,*, seed:int=72) -> list[list[Chunk]]:
    xcount = int(world_width/chunk_width)
    ycount = int(world_height/chunk_width)

    # チャンクを生成
    chunks:list[list[Chunk]] = []
    for i in range(xcount):
        _chunks = []
        for j in range(ycount):
            pn = pnoise(i/xcount,j/ycount,seed)
            chunk = Chunk(pn, chunk_width, chunk_width*i,chunk_width*j)

            _chunks.append(chunk)
        chunks.append(_chunks)

    return chunks