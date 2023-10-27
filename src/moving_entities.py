from objects_manager import ObjectsManager

from drawer_matplotlib import (
    PltDrawer
)

if __name__ == "__main__":
    om = ObjectsManager(PltDrawer(),width=200,height=200,chunkwidth=10)
    om.run()