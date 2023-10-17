from utils import (
    X_MIN, X_MAX, Y_MIN, Y_MAX,
    get_random_coords
)

import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.artist import Artist
import numpy as np

import random


# Create the figure and axis
fig, ax = plt.subplots(figsize=(6,6))
ax.set_xlim(X_MIN, X_MAX)
ax.set_ylim(Y_MIN, Y_MAX)
ax.set_xticks([])
ax.set_yticks([])



# nutrition (栄養)
nutritions: list[plt.Circle] = []

# entity
# entityの向いている方向(θ [rad]、右方向 0 rad)のリスト
entities_directions: list[float] = []
# [x,y] の組のリスト
entities_coords: list[list] = []
entities: list[plt.Circle] = []
entity_types = {
    "normal": {
        "radius": 1,
        "color": "red"
    }
}

# グラフ上にオブジェクトを追加する
def add_object(object:Artist):
    ax.add_patch(object)

# 描画用の円形オブジェクトを取得する
def get_circle(x:float, y:float, *, radius:float=1, fc:str="black") -> plt.Circle:
    return plt.Circle((x,y), radius, fc=fc)

# 指定した座標にエンティティを配置する
def add_entity(x:float, y:float, *, direction:float=0, entitytype:str="normal"):
    entities_coords.append([x,y])
    entities_directions.append(direction)
    entities.append(get_circle(x,y,
                               radius=entity_types[entitytype]["radius"],
                               fc=entity_types[entitytype]["color"]))
    add_object(entities[-1])

# ランダムな移動方向 dθ の元となる正規分布
# 平均 0 rad, σ=0.7 radのリスト
_rand_dirs = np.random.normal(0,0.7,100).tolist()
def move_entity(idx:int):
    entities_directions[idx] += _rand_dirs[random.randint(0,99)]
    velocity = random.random()*3
    dx = velocity * np.cos(entities_directions[idx])
    dy = velocity * np.sin(entities_directions[idx])
    newc = [entities_coords[idx][0] + dx, entities_coords[idx][1] + dy]
    entities_coords[idx] = keep_coords_within_bounds(newc, entities_coords)
    entities[idx].center = tuple(entities_coords[idx])

def keep_coords_within_bounds(new_coords:list[float], old_coords:list[float]) -> list[float]:
    if new_coords[0]>X_MAX:
        new_coords[0] = X_MAX
    elif new_coords[0]<X_MIN:
        new_coords[0] = X_MIN

    if new_coords[1]>Y_MAX:
        new_coords[1] = Y_MAX
    elif new_coords[1] < X_MIN:
        new_coords[1] = X_MIN

    return new_coords

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
        x,y = get_random_coords()
        add_entity(x,y,entitytype="normal")

def init_nutritions():
    for n in range(10):
        x,y = get_random_coords()
        nutritions.append(get_circle(x,y,radius=0.5,fc="green"))
        add_object(nutritions[-1])
        

# Animation function to update the frame
def update(i):
    for n in range(len(entities)):
        move_entity(n)

# Create the animation
anim = FuncAnimation(fig, update, init_func=init, frames=100)#, blit=True)

# Display the animation
plt.show()
