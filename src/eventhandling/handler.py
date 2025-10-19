import matplotlib.pyplot as plt 
from matplotlib.widgets import Button

class pick_event_handing:
    def __init__(self, fig, ax, plot, legend, handles):
        self.graphics = plot
        self.fig = fig
        self.ax  = ax
        # legend
        self.entries = legend.legend_handles # + legend.get_lines()
        self.legend_map = dict(zip(self.entries, handles))
        for entry in self.entries:
            entry.set_picker(True)
        # points
        self.annotations = []
        self.btn = Button(plt.axes([.9,0.02,0.05,0.05]), "clear")
        self.btn.on_clicked(self.clr_button)
        print("Event handler setup successful")

        self.fig.canvas.mpl_connect('pick_event', self.handler) 

    def handler(self, event):
        entity = event.artist
        ind = getattr(event, "ind", None)


        if entity  in self.entries:
            self.toggle_visibility(event)
        else:
            self.pick_point(entity, ind)

        self.fig.canvas.draw_idle()

    # ~ display coordinates on click 
    def pick_point(self, point, ind):
        x = point.get_xdata()[ind][0]
        y = point.get_ydata()[ind][0]
        self.annotations.append(self.ax.annotate(f"({x} I {y})", xy=(x,y), fontsize=12))

    def clr_button(self, event):
        for annotation in self.annotations:
            annotation.remove()
        self.annotations.clear()
        self.fig.canvas.draw_idle()


    # ~ visibility toggling from legend 
    def toggle_visibility(self, event):
        entry = event.artist
        
        item = self.map[entry]
        print(item)

        visible = item.get_visible()
        item.set_visible(not visible)
        entry.set_alpha(0.3 if visible else 1)

        self.fig.canvas.draw_idle()



# & for ui: clear class instance if tab closed