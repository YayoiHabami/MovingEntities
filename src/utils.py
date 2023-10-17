import random


# 定数
X_MIN = 0
X_MAX = 100
Y_MIN = 0
Y_MAX = 100

def get_random_coords(*,xmin=X_MIN,xmax=X_MAX,ymin=Y_MIN,ymax=Y_MAX)-> tuple[float]:
    """指定された領域の中でランダムな位置 (x,y) を返す"""
    return random.randrange(X_MIN,X_MAX,1),random.randrange(Y_MIN,Y_MAX,1)