import matplotlib.pyplot as plt 
from matplotlib.widgets import Button


class pick_event_handing:
    # & for ui: clear class instance if tab closed
    def __init__(self, fig, ax, graphics):
        self.fig = fig
        self.ax  = ax
        self.map_legend = graphics.legend.map       # dict(zip(self.entries, handles))
        # ~ legend
        self.entries = graphics.legend.handles      #+ legend.get_lines()
        for entry in graphics.legend.legend.legend_handles:
            entry.set_picker(True)
        # ~ points
        self.point_label = point_label(ax, graphics.points)

        print("Event handler setup successful")
        self.fig.canvas.mpl_connect('pick_event', self.handler) 


    def handler(self, event):
        entity = event.artist
        ind = getattr(event, "ind", None)

        if entity.get_label() in self.map_legend:  # visibility togleing from legend
            self.toggle_visibility(entity)
        else:                                      # point labeling
            self.point_label.change_point(entity, ind)

        self.fig.canvas.draw_idle()


    # : visibility toggling from legend :
    def toggle_visibility(self, entry):
        group = self.map_legend[entry.get_label()][1:]      # [1:] exclude legend patch
        patch = self.map_legend[entry.get_label()][0 ]
        
        visible = group[0].element[0]._visible
        entry.set_alpha(0.3 if visible else 1)

        for item in group:
            item.element[0]._visible = not visible


    # : display coordinates on click :
class point_label():
    def __init__(self, ax, point_list):
        self.ax = ax
        self.last_point = None
        self.last_alpha = None
        self.annotation = None
        self.point_list = point_list

    def change_point(self, clicked_point, ind):
        x = clicked_point.get_xdata()[ind][0]
        y = clicked_point.get_ydata()[ind][0]

        if self.last_point == clicked_point:
            self.annotation.remove()
            self.annotation = None
            self.last_point = None
            clicked_point._alpha = self.last_alpha

        else:
            if self.annotation is not None:         
                self.annotation.remove()
                self.annotation = None
                self.last_point._alpha = self.last_alpha
            
            self.last_alpha = clicked_point._alpha
            self.last_point = clicked_point

            selected_point = self.find_point(clicked_point)
            label = self.create_label(selected_point, x,y)

            self.annotation = self.ax.annotate(label, xy=(x,y), xycoords='data', xytext=(0,5), textcoords='offset points', ha='center', va='bottom', fontsize=12)
            clicked_point._alpha = 1


    def find_point(self, clicked_point):
        for points in self.point_list:
            for point in points.element:
                if point == clicked_point:
                    return points
        return None

    
    def create_label(self, selected_point, x,y):
        print(selected_point, x,y)
        label = ""
        for category in selected_point.hirachie:
            label += f"{category}, "
            print(label)
        label += (f"\n({x} I {y})")

        return label