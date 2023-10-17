import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import numpy as np

import random

# 定数
X_MIN = 0
X_MAX = 100
Y_MIN = 0
Y_MAX = 100

# Create the figure and axis
fig, ax = plt.subplots(figsize=(6,6))
ax.set_xlim(X_MIN, X_MAX)
ax.set_ylim(Y_MIN, Y_MAX)
ax.set_xticks([])
ax.set_yticks([])

entity_types = {
    "normal": {
        "radius": 1,
        "color": "red"
    }
}

# [x,y] の組のリスト
entities_coords: list[list] = []
entities: list[plt.Circle] = []

# 指定した座標にエンティティを配置する
def add_entity(x:float, y:float, *, entitytype:str="normal"):
    print("hello")
    entities_coords.append([x,y])
    entities.append(plt.Circle((x,y),
                               entity_types[entitytype]["radius"],
                               fc=entity_types[entitytype]["color"]))
    ax.add_patch(entities[-1])

def move_entity(idx:int):
    dx = random.random()*4-2
    dy = random.random()*4-2
    newc = [entities_coords[idx][0] + dx, entities_coords[idx][1] + dy]
    entities_coords[idx] = keep_coords_within_bounds(newc, entities_coords)
    entities[idx].center = tuple(entities_coords[idx])

def keep_coords_within_bounds(new_coords:list[float], old_coords:list[float]) -> list[float]:
    if new_coords[0]>X_MAX:
        new_coords[0] = X_MAX
    elif new_coords[0]<X_MIN:
        new_coords = X_MIN

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

    for n in range(2):
        x = random.randrange(X_MIN,X_MAX,1)
        y = random.randrange(Y_MIN,Y_MAX,1)
        add_entity(x,y,entitytype="normal")
    return entities

# Animation function to update the frame
def update(i):
    for n in range(len(entities)):
        move_entity(n)
    return entities

# Create the animation
anim = FuncAnimation(fig, update, init_func=init, frames=300, blit=True)

# Display the animation
plt.show()
