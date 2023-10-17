from utils import (
    get_random_coords
)

from abc import ABCMeta, abstractmethod
import random

class Drawer(metaclass=ABCMeta):
    
    # 領域
    X_MIN = 0
    X_MAX = 100
    Y_MIN = 0
    Y_MAX = 100

    @abstractmethod
    def add_object(object:object) -> object:
        pass
    
    @abstractmethod
    def add_circle(x:float, y:float, *, radius:float=1, fc:str="black") -> object:
        pass

    @abstractmethod
    def run(update, init=None):
        """update: 更新関数, init:初期化関数"""
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

    def get_random_coords(self,xmin=X_MIN,xmax=X_MAX,ymin=Y_MIN,ymax=Y_MAX)-> tuple[float]:
        """指定された領域の中でランダムな位置 (x,y) を返す"""
        return random.randrange(xmin,xmax,1),random.randrange(ymin,ymax,1)

