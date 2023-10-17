from objects_manager import ObjectsManager

from drawer_matplotlib import (
    PltDrawer
)

if __name__ == "__main__":
    om = ObjectsManager(PltDrawer())
    om.run()