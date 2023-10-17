from drawer import (
    Drawer
)

from drawer_matplotlib import (
    PltDrawer
)

import numpy as np

import random

dr: Drawer = PltDrawer()#Drawer()

# nutrition (栄養)
# 描画するオブジェクトのリスト
nutritions: list = []

# entity
# entityの向いている方向(θ [rad]、右方向 0 rad)のリスト
entities_directions: list[float] = []
# [x,y] の組のリスト
entities_coords: list[list] = []
# 描画するオブジェクトのリスト
entities: list = []
entity_types = {
    "normal": {
        "radius": 1,
        "color": "red"
    }
}

# 指定した座標にエンティティを配置する
def add_entity(x:float, y:float, *, direction:float=0, entitytype:str="normal"):
    entities_coords.append([x,y])
    entities_directions.append(direction)
    entities.append(dr.add_circle(x,y,
                               radius=entity_types[entitytype]["radius"],
                               fc=entity_types[entitytype]["color"]))

def add_nutrition(x:float, y:float):
    nutritions.append(dr.add_circle(x,y,radius=0.5,fc="green"))

# ランダムな移動方向 dθ の元となる正規分布
# 平均 0 rad, σ=0.7 radのリスト
_rand_dirs = np.random.normal(0,0.7,100).tolist()
def move_entity(idx:int):
    entities_directions[idx] += _rand_dirs[random.randint(0,99)]
    velocity = random.random()*3
    dx = velocity * np.cos(entities_directions[idx])
    dy = velocity * np.sin(entities_directions[idx])
    newc = [entities_coords[idx][0] + dx, entities_coords[idx][1] + dy]
    entities_coords[idx] = dr.keep_coords_within_bounds(newc, entities_coords)
    entities[idx].center = tuple(entities_coords[idx])



# Initialize function to set up the initial frame
initialized = False
def init():
    global initialized
    if initialized:
        return []
    initialized = True

    init_entities()
    init_nutritions()
    return entities + nutritions

def init_entities():
    for n in range(2):
        x,y = dr.get_random_coords()
        add_entity(x,y,entitytype="normal")

def init_nutritions():
    for n in range(10):
        x,y = dr.get_random_coords()
        add_nutrition(x,y)
        

# Animation function to update the frame
def update(i):
    for n in range(len(entities)):
        move_entity(n)

dr.run(update, init)