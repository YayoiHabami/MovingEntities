from drawer import Drawer

import numpy as np

import random

ENTITY_TYPES = {
    "normal": {
        "radius": 1,
        "color": "red",
        "eyesightLength": 10
    }
}

class ObjectsManager():
    dr:Drawer

    # nutrition (栄養)
    # 描画するオブジェクトのリスト
    nutritions: list
    # [x,y] の組のリスト
    nutritions_coords: np.ndarray

    # entity
    # 描画するオブジェクトのリスト
    entities: list
    # entityの向いている方向(θ [rad]、右方向 0 rad)のリスト
    entities_directions: np.ndarray[float]
    # [x,y] の組のリスト
    entities_coords: np.ndarray
    # 視野長のリスト
    entities_sight_length: np.ndarray[float]

    def __init__(self, drawer:Drawer) -> None:
        self.nutritions = []
        self.nutritions_coords = np.arange(0).reshape(0,2)
        self.entities = []
        self.entities_directions = np.arange(0)
        self.entities_coords = np.arange(0).reshape(0,2)
        self.entities_sight_length = np.arange(0)

        self.dr = drawer

    # 指定した座標にエンティティを配置する
    def add_entity(self, x:float, y:float, *, direction:float=0, entitytype:str="normal"):
        coords = np.array([x,y])
        self.entities_coords = np.r_[self.entities_coords, coords.reshape(1,2)]
        self.entities_directions = np.append(self.entities_directions, direction)
        self.entities_sight_length = np.append(self.entities_sight_length, ENTITY_TYPES[entitytype]["eyesightLength"])

        self.entities.append(self.dr.add_circle(coords,
                                radius=ENTITY_TYPES[entitytype]["radius"],
                                fc=ENTITY_TYPES[entitytype]["color"]))

    def add_nutrition(self, x:float, y:float):
        coords = np.array([x,y])
        self.nutritions_coords = np.r_[self.nutritions_coords, coords.reshape(1,2)]
        self.nutritions.append(self.dr.add_circle(coords,radius=0.5,fc="green"))

    # ddirection(方向の差分)およびdirection（方向）はどちらかを選択。ddirectionが優先される
    # dxy（(dx,dy)のndarray）およびxy（(x,y)のndarray）はどちらかを選択。dxyが優先される
    def _move_entity(self, idx:int, *,
                     dxy:np.ndarray=None, xy:np.ndarray=None,
                     ddirection:float=None, direction:float=None):

        if dxy is not None:
            newc = self.entities_coords[idx] + dxy
        else:
            newc = xy
        
        if ddirection is not None:
            self.entities_directions[idx] += ddirection
        else:
            self.entities_directions[idx] = direction

        self.entities_coords[idx] = self.dr.keep_coords_within_bounds(newc, self.entities_coords)
        self.entities[idx].center = tuple(self.entities_coords[idx])

    def move_entity(self, idx:int):
        if not self.move_entity_for_nutrition(idx):
            self.move_entity_random(idx)

    def move_entity_for_nutrition(self, idx:int) -> bool:
        """動きがあった場合はTrue、そうでない場合はFalseを返す"""
        # EntityからNutritionsまでの距離が、視野長以下であるかを判定する
        ntoo = self.nutritions_coords - self.entities_coords[idx].reshape(1,2)
        ntoolen = np.sum(np.square(ntoo),1)
        nutisin = ntoolen<=np.square(self.entities_sight_length[idx])
        if np.max(nutisin)==False:
            # 視野長以内にnutritionが存在しない
            return False

        close_sight = 0.25
        veryclose = np.where(ntoolen<=np.square(self.entities_sight_length[idx]*close_sight))
        if len(veryclose[0])>=1:
            # 十分近い位置にnutritionを見つけた場合は、視野方向に関わらずそちらに移動する
            nidx = veryclose[0][0]
        else:
            # 視野方向と栄養のコサイン角(の実数倍)を計算する
            sightvec = np.array((np.cos(self.entities_directions[idx]), np.sin(self.entities_directions[idx])))
            stoo = (sightvec - self.entities_coords[idx]).reshape(1,2)
            where = np.where((stoo @ ntoo.T)>=0)
            nidx = where[0][np.argmin(ntoolen[where[0]])]

        # 移動する
        maxvelocity = 2
        dxdy = ntoo[nidx]
        lendxdy = np.sqrt(np.sum(np.square(dxdy)))#,1))
        if lendxdy>maxvelocity:
            dxdy *= 2/lendxdy
        ddir = np.arctan2(dxdy[1],dxdy[0])
        self._move_entity(idx,dxy=dxdy,ddirection=ddir)
        return True
    
    # ランダムな移動方向 dθ の元となる正規分布
    # 平均 0 rad, σ=0.7 radのリスト
    _rand_dirs = np.random.normal(0,0.7,100).tolist()
    def move_entity_random(self, idx:int):
        velocity = random.random()*3
        dxy = velocity * np.array((np.cos(self.entities_directions[idx]), np.sin(self.entities_directions[idx])))
        self._move_entity(idx, dxy=dxy, ddirection=self._rand_dirs[random.randint(0,99)])

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