from drawer import Drawer

import numpy as np

import random

ENTITY_TYPES = {
    "normal": {
        "radius": 1,
        "color": "red",
        "eyesightLength": 5,
        "attackDist": 1,
        "healthPoint": 100
    }
}


NUTRITION_ID = 1
ENTITY_ID = 2

# HPと同じ単位
ENERGY_OF_NUTRITION = 10

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
    # 体力
    entities_health_pt: np.ndarray[float]
    entities_max_health_pt: np.ndarray[float]

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
        self.entities_health_pt = np.arange(0)
        self.entities_max_health_pt = np.arange(0)

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
        self.entities_health_pt = np.append(self.entities_health_pt, ENTITY_TYPES[entitytype]["healthPoint"])
        self.entities_max_health_pt = np.append(self.entities_max_health_pt, ENTITY_TYPES[entitytype]["healthPoint"])

        self.entities.append(self.dr.add_circle(coords,
                                radius=ENTITY_TYPES[entitytype]["radius"],
                                fc=ENTITY_TYPES[entitytype]["color"]))
        
    def remove_entities(self, indices:list[int]):
        # 死亡時に何個nutritionをまき散らすか
        entity_spattering_nutritions = 10

        indices.sort(reverse=True)
        for idx in indices:
            center = self.entities_coords[idx]
            self.dr.remove_object(self.entities.pop(idx))
            self.entities_coords = np.delete(self.entities_coords, idx, axis=0)
            self.entities_directions = np.delete(self.entities_directions, idx)
            self.entities_sight_length = np.delete(self.entities_sight_length, idx)
            self.entities_target_id = np.delete(self.entities_target_id, idx)
            self.entities_target_idx = np.delete(self.entities_target_idx, idx)
            self.entities_attack_dist = np.delete(self.entities_attack_dist, idx)
            self.entities_health_pt = np.delete(self.entities_health_pt, idx)
            self.entities_max_health_pt = np.delete(self.entities_max_health_pt, idx)
            
            # entityの死亡に伴いnutritionをまき散らす
            self.spatter_nutritions(center, entity_spattering_nutritions)
            

    def add_nutrition(self, xy:np.ndarray[float]):
        self.nutritions_coords = np.r_[self.nutritions_coords, xy.reshape(1,2)]
        self.nutritions.append(self.dr.add_circle(xy,radius=0.5,fc="green"))

    def remove_nutritions(self, indices:list[int]):
        indices.sort(reverse=True)
        for idx in indices:
            self.dr.remove_object(self.nutritions.pop(idx))
            self.nutritions_coords = np.delete(self.nutritions_coords, idx, axis=0)
    
    def spatter_nutritions(self, center:np.ndarray[float], count:int):
        """指定された点を中心にnutritionをまき散らす\n
        範囲はcenterを中心とする2x2の正方形の中"""
        for dxy in (np.random.rand(count, 2)*2-1):
            self.add_nutrition(center+dxy)




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

        # entityの新旧座標と、移動速度を求める
        newc = self.dr.keep_coords_within_bounds(newc, self.entities_coords)
        oldc = self.entities_coords[idx]
        spd2 = np.sum(np.square(newc-oldc))

        # entityを移動させる
        self.entities_coords[idx] = newc
        self.entities[idx].center = tuple(self.entities_coords[idx])
        self.tire_entity_by_move(idx, spd2)

    def move_entity(self, idx:int):
        if self.move_entity_for_nutrition(idx):
            return 
        
        self.move_entity_random(idx)
        self.set_entity_target(idx, 0)

    # nutritionの方にentityを移動させる
    def move_entity_for_nutrition(self, idx:int) -> bool:
        """動きがあった場合はTrue、そうでない場合はFalseを返す"""
        # EntityからNutritionsまでの距離が、視野長以下であるかを判定する
        n2o = self.nutritions_coords - self.entities_coords[idx].reshape(1,2)
        n2olen = np.sum(np.square(n2o),1)
        nutisin = n2olen<=np.square(self.entities_sight_length[idx])
        if np.max(nutisin)==False:
            # 視野長以内にnutritionが存在しない
            return False

        close_sight = 0.25
        veryclose = np.where(n2olen<=np.square(self.entities_sight_length[idx]*close_sight))
        if len(veryclose[0])>=1:
            # 十分近い位置にnutritionを見つけた場合は、視野方向に関わらずそちらに移動する
            nidx = veryclose[0][0]
        else:
            # 視野方向と栄養のコサイン角(の実数倍)を計算する
            sightvec = np.array((np.cos(self.entities_directions[idx]), np.sin(self.entities_directions[idx])))
            s2o = (sightvec - self.entities_coords[idx]).reshape(1,2)
            cosangle = s2o @ n2o.T
            where = np.where(cosangle>=0) # 0(左右90°)よりも前
            if len(where[0])==0:
                # 対象が視界内に存在しない
                return False
            #nidx = where[0][np.argmax(cosangle[where])] # 目線(真っすぐ)に最も近いもの
            nidx = where[0][np.argmin(n2olen[where[0]])] # 視界内の最も近いもの

        # 移動する
        maxvelocity = 2
        dxdy = n2o[nidx]
        lendxdy = np.sqrt(np.sum(np.square(dxdy)))
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

    def feed_entity(self, idx, *, count=1):
        """entityにnutritionを与える\n
        count: nutritionの数"""
        self.recover_entity_hp(idx, count*ENERGY_OF_NUTRITION)

    def tire_entity_by_move(self, idx, speedp2:float):
        """移動によりentityのHPを減少させる\n
        speedp2 : 移動量の2乗"""

        # 基礎代謝: （とりあえず）静止時に400ターンで-100(HP)
        basal_metabolism = 0.25
        # 移動速度に対する比率: 速度2で100ターン動き続けて-100(HP)
        ratio = 0.25
        self.reduce_entity_hp(idx, speedp2*ratio + basal_metabolism)
        
    # HPの増加量を指定して増加させる
    def recover_entity_hp(self, idx, value):
        self.entities_health_pt[idx] += value
        if self.entities_health_pt[idx]>self.entities_max_health_pt[idx]:
            self.entities_health_pt[idx] = self.entities_max_health_pt[idx]

    # HPの減少量を指定して減少させる
    def reduce_entity_hp(self, idx, value):
        self.entities_health_pt[idx] -= value



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
        for n in range(30):
            x,y = self.dr.get_random_coords()
            self.add_entity(x,y,entitytype="normal")

    def init_nutritions(self):
        for n in range(500):
            x,y = self.dr.get_random_coords()
            self.add_nutrition(np.array((x,y)))
        
    # Animation function to update the frame
    def update(self, i):
        for n in range(len(self.entities)):
            self.move_entity(n)
        
        self.update_nutritions()
        self.update_entities()
    
    # entityの捕食などを処理する
    def update_nutritions(self):
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

    def update_entities(self):
        # 体力が0以下になったentityを取り除く
        hp0 = np.where(self.entities_health_pt<=0)
        self.remove_entities(list(hp0[0]))

    def run(self):
        self.dr.run(update=self.update, init=self.init)

