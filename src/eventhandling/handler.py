import matplotlib.pyplot as plt 
from matplotlib.widgets import Button


class pick_event_handing:
    def __init__(self, fig, ax, graphics):
        self.fig = fig
        self.ax  = ax

        # legend
        self.entries = graphics.legend.handles      #+ legend.get_lines()
        self.map_legend = graphics.legend.map       # dict(zip(self.entries, handles))
        for entry in graphics.legend.legend.legend_handles:
            entry.set_picker(True)

        # points
        self.annotations = None
        print("Event handler setup successful")

        self.fig.canvas.mpl_connect('pick_event', self.handler) 


    def handler(self, event):
        entity = event.artist
        ind = getattr(event, "ind", None)

        if entity.get_label() in self.map_legend:  # frame['colors'] - label
            self.toggle_visibility(entity)
        else:
            self.pick_point(entity, ind)

        self.fig.canvas.draw_idle()


    # ~ display coordinates on click 
    def pick_point(self, point, ind):
        x = point.get_xdata()[ind][0]
        y = point.get_ydata()[ind][0]
        if self.annotations != None:
            self.annotations.remove()
        self.annotations = self.ax.annotate(f"({x} I {y})", xy=(x,y), fontsize=12)



    # ~ visibility toggling from legend 
    def toggle_visibility(self, entry):
        group = self.map_legend[entry.get_label()]

        visible = group[0].get_visible()
        entry.set_alpha(0.3 if visible else 1)

        for item in group:
            item.set_visible(not visible)


# & for ui: clear class instance if tab closed