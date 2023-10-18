from drawer import Drawer

import numpy as np

import random

ENTITY_TYPES = {
    "normal": {
        "radius": 1,
        "color": "red",
        "eyesightLength": 10,
        "attackDist": 1
    }
}


NUTRITION_ID = 1
ENTITY_ID = 2

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
    # 現在のターゲットのIDとそのインデックス
    entities_target_id: np.ndarray[int]
    entities_target_idx: np.ndarray[int]
    # 攻撃や捕食の範囲
    entities_attack_dist : np.ndarray[float] 

    def __init__(self, drawer:Drawer) -> None:
        self.nutritions = []
        self.nutritions_coords = np.arange(0).reshape(0,2)
        self.entities = []
        self.entities_directions = np.arange(0)
        self.entities_coords = np.arange(0).reshape(0,2)
        self.entities_sight_length = np.arange(0)
        self.entities_target_id = np.arange(0, dtype=int)
        self.entities_target_idx = np.arange(0, dtype=int)
        self.entities_attack_dist = np.arange(0)

        self.dr = drawer

    # 指定した座標にエンティティを配置する
    def add_entity(self, x:float, y:float, *, direction:float=0, entitytype:str="normal"):
        coords = np.array([x,y])
        self.entities_coords = np.r_[self.entities_coords, coords.reshape(1,2)]
        self.entities_directions = np.append(self.entities_directions, direction)
        self.entities_sight_length = np.append(self.entities_sight_length, ENTITY_TYPES[entitytype]["eyesightLength"])
        self.entities_target_id = np.append(self.entities_target_id, 0)
        self.entities_target_idx = np.append(self.entities_target_idx, 0)
        self.entities_attack_dist = np.append(self.entities_attack_dist, ENTITY_TYPES[entitytype]["attackDist"])

        self.entities.append(self.dr.add_circle(coords,
                                radius=ENTITY_TYPES[entitytype]["radius"],
                                fc=ENTITY_TYPES[entitytype]["color"]))

    def add_nutrition(self, x:float, y:float):
        coords = np.array([x,y])
        self.nutritions_coords = np.r_[self.nutritions_coords, coords.reshape(1,2)]
        self.nutritions.append(self.dr.add_circle(coords,radius=0.5,fc="green"))

    def remove_nutritions(self, indices:list[int]):
        indices.sort(reverse=True)
        for idx in indices:
            self.dr.remove_object(self.nutritions.pop(idx))
            self.nutritions_coords = np.delete(self.nutritions_coords, idx, axis=0)


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
        if self.move_entity_for_nutrition(idx):
            return 
        
        self.move_entity_random(idx)
        self.set_entity_target(idx, 0)

    # nutritionの方にentityを移動させる
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
            if len(where[0])==0:
                # 対象が視界内に存在しない
                return False
            nidx = where[0][np.argmin(ntoolen[where[0]])]

        # 移動する
        maxvelocity = 2
        dxdy = ntoo[nidx]
        lendxdy = np.sqrt(np.sum(np.square(dxdy)))#,1))
        if lendxdy>maxvelocity:
            dxdy *= 2/lendxdy
        ddir = np.arctan2(dxdy[1],dxdy[0])
        self._move_entity(idx,dxy=dxdy,ddirection=ddir)
        # ターゲット設定
        self.set_entity_target(idx, NUTRITION_ID, targetidx=nidx)
        return True
    
    # ランダムな移動方向 dθ の元となる正規分布
    # 平均 0 rad, σ=0.7 radのリスト
    _rand_dirs = np.random.normal(0,0.7,100).tolist()
    def move_entity_random(self, idx:int):
        velocity = random.random()*3
        dxy = velocity * np.array((np.cos(self.entities_directions[idx]), np.sin(self.entities_directions[idx])))
        self._move_entity(idx, dxy=dxy, ddirection=self._rand_dirs[random.randint(0,99)])

    # entityが攻撃/捕食/追跡 対象とするものを設定する
    # entityidx: entitiesのidx
    # targetid/idx: 対象のid,idx
    def set_entity_target(self, entityidx:int, targetid:int, *, targetidx:int=None):
        if targetid==0:
            self.entities_target_id[entityidx] = 0
            self.entities_target_idx[entityidx] = -1
        else:
            self.entities_target_id[entityidx] = targetid
            self.entities_target_idx[entityidx] = targetidx

    def feed_entity(self, idx, *, value=1):
        pass



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
        for n in range(10):
            x,y = self.dr.get_random_coords()
            self.add_entity(x,y,entitytype="normal")

    def init_nutritions(self):
        for n in range(50):
            x,y = self.dr.get_random_coords()
            self.add_nutrition(x,y)
        
    # Animation function to update the frame
    def update(self, i):
        for n in range(len(self.entities)):
            self.move_entity(n)
        
        self.update_nutrition()
    
    # entityの捕食などを処理する
    def update_nutrition(self):
        targetings = np.where(self.entities_target_id==NUTRITION_ID)
        dists = np.full(len(targetings[0]), np.inf)
        for i, idx in enumerate(targetings[0]):
            targetidx = self.entities_target_idx[idx]
            # entityとnutritionの距離を求める
            ncoor = self.nutritions_coords[targetidx]
            ecoor = self.entities_coords[idx]
            nedist = np.sum(np.square(ncoor - ecoor))
            dists[i] = nedist
        
        _target_idx = self.entities_target_idx[targetings]
        removing_nutritions = []
        feeding_entities = []
        for idx in np.unique(_target_idx):
            # 各nutritionについて、上記の自身を発見しているentityの内、最も近いものを探す
            where = np.where(_target_idx==idx)
            minidx = where[0][np.argmin(dists[where])]
            entityidx = targetings[0][minidx]

            if dists[minidx]<=self.entities_attack_dist[entityidx]:
                # 距離が手長以下ならば捕食する
                removing_nutritions.append(idx)
                feeding_entities.append(entityidx)
        
        # 栄養の削除
        self.remove_nutritions(removing_nutritions)
        # entityに餌を与える
        for eidx in feeding_entities:
            self.feed_entity(eidx)

            
            

        
        
    
    def run(self):
        self.dr.run(update=self.update, init=self.init)