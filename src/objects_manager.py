from drawer import Drawer

import numpy as np

import random

ENTITY_TYPES = {
    "normal": {
        "radius": 1,
        "color": "red"
    }
}

class ObjectsManager():
    dr:Drawer

    # nutrition (栄養)
    # 描画するオブジェクトのリスト
    nutritions: list

    # entity
    # entityの向いている方向(θ [rad]、右方向 0 rad)のリスト
    entities_directions: list[float]
    # [x,y] の組のリスト
    entities_coords: list[list]
    # 描画するオブジェクトのリスト
    entities: list

    def __init__(self, drawer:Drawer) -> None:
        self.nutritions = []
        self.entities_directions = []
        self.entities_coords = []
        self.entities = []

        self.dr = drawer

    # 指定した座標にエンティティを配置する
    def add_entity(self, x:float, y:float, *, direction:float=0, entitytype:str="normal"):
        self.entities_coords.append([x,y])
        self.entities_directions.append(direction)
        self.entities.append(self.dr.add_circle(x,y,
                                radius=ENTITY_TYPES[entitytype]["radius"],
                                fc=ENTITY_TYPES[entitytype]["color"]))

    def add_nutrition(self, x:float, y:float):
        self.nutritions.append(self.dr.add_circle(x,y,radius=0.5,fc="green"))

    # ランダムな移動方向 dθ の元となる正規分布
    # 平均 0 rad, σ=0.7 radのリスト
    _rand_dirs = np.random.normal(0,0.7,100).tolist()
    def move_entity(self, idx:int):
        self.entities_directions[idx] += self._rand_dirs[random.randint(0,99)]
        velocity = random.random()*3
        dx = velocity * np.cos(self.entities_directions[idx])
        dy = velocity * np.sin(self.entities_directions[idx])
        newc = [self.entities_coords[idx][0] + dx, self.entities_coords[idx][1] + dy]
        self.entities_coords[idx] = self.dr.keep_coords_within_bounds(newc, self.entities_coords)
        self.entities[idx].center = tuple(self.entities_coords[idx])

    # Initialize function to set up the initial frame
    initialized = False
    def init(self):
        if self.initialized:
            return []
        self.initialized = True

        self.init_entities()
        self.init_nutritions()
        return self.entities + self.nutritions

    def init_entities(self):
        for n in range(2):
            x,y = self.dr.get_random_coords()
            self.add_entity(x,y,entitytype="normal")

    def init_nutritions(self):
        for n in range(10):
            x,y = self.dr.get_random_coords()
            self.add_nutrition(x,y)
            

    # Animation function to update the frame
    def update(self, i):
        for n in range(len(self.entities)):
            self.move_entity(n)
    
    def run(self):
        self.dr.run(update=self.update, init=self.init)