import numpy as np

from abc import ABCMeta, abstractmethod
import random



class Drawer(metaclass=ABCMeta):
    
    # 領域
    X_MIN:int = 0
    X_MAX:int = 100
    Y_MIN:int = 0
    Y_MAX:int = 100

    @abstractmethod
    def update_bounds_limit(self, *, xmin:int=None, xmax:int=None, 
                            ymin:int=None, ymax:int=None):
        """境界値の更新"""
        pass

    @abstractmethod
    def add_object(self, object:object) -> object:
        pass
    
    @abstractmethod
    def add_circle(self, xy, *, radius:float=1, fc:str="black") -> object:
        pass

    @abstractmethod
    def remove_object(self, object):
        pass

    @abstractmethod
    def run(self, update, init=None):
        """update: 更新関数, init:初期化関数"""
        pass

    @abstractmethod
    def stop(self):
        pass

    @abstractmethod
    def close(self):
        pass

    def keep_coords_within_bounds(self, new_coords:list[float], old_coords:list[float]) -> list[float]:
        if new_coords[0]>self.X_MAX:
            new_coords[0] = self.X_MAX
        elif new_coords[0]<self.X_MIN:
            new_coords[0] = self.X_MIN

        if new_coords[1]>self.Y_MAX:
            new_coords[1] = self.Y_MAX
        elif new_coords[1] < self.X_MIN:
            new_coords[1] = self.X_MIN

        return new_coords

    def get_random_coords(self,xmin:float=None,xmax:float=None,ymin:float=None,ymax:float=None,*,count=1)-> np.ndarray[float]:
        """指定された領域の内、有効な範囲についてランダムな位置 (x,y) を返す\n
        指定されない場合は描画領域全体を対象とする"""
        xmin = self.X_MIN if xmin is None else xmin
        xmax = self.X_MAX if xmax is None else xmax
        ymin = self.Y_MIN if ymin is None else ymin
        ymax = self.Y_MAX if ymax is None else ymax

        xs = (xmax-xmin)*np.random.rand(count) + xmin
        ys = (ymax-ymin)*np.random.rand(count) + ymin
        return np.c_[xs,ys]

