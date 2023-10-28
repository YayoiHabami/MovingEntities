
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.artist import Artist

from drawer import (
    Drawer
)

class PltDrawer(Drawer):

    def __init__(self) -> None:
        self.fig, self.ax = plt.subplots(figsize=(6,6))
        self.ax.set_xlim(self.X_MIN, self.X_MAX)
        self.ax.set_ylim(self.Y_MIN, self.Y_MAX)
        self.ax.set_xticks([])
        self.ax.set_yticks([])

        super().__init__()

    def update_bounds_limit(self, *, xmin:int=None, xmax:int=None, ymin:int=None, ymax:int=None):
        updated = False
        if xmin is not None:
            self.X_MIN = xmin
            updated = True
        if xmax is not None:
            self.X_MAX = xmax
            updated = True
        if ymin is not None:
            self.Y_MIN = ymin
            updated = True
        if ymax is not None:
            self.Y_MAX = ymax
            updated = True
        
        if updated:
            self.ax.set_xlim(self.X_MIN, self.X_MAX)
            self.ax.set_ylim(self.Y_MIN, self.Y_MAX)
    
    def add_object(self, object:Artist) -> Artist:
        self.ax.add_patch(object)
        return object
    
    def add_circle(self, xy, *, radius: float = 1, fc: str = "black") -> object:
        return self.add_object(plt.Circle((xy[0],xy[1]), radius, fc=fc))

    anim:FuncAnimation = None
    def run(self, update, init=None):
        # Create the animation
        self.anim = FuncAnimation(self.fig, update, init_func=init, frames=100)#, blit=True)

        # Display the animation
        plt.show()
    
    def stop(self):
        self.anim.event_source.stop()
    
    def close(self):
        plt.close('all')

    def remove_object(self, object:Artist):
        object.remove()