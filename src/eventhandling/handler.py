import matplotlib.pyplot as plt 
from matplotlib.widgets import Button


class pick_event_handing:
    def __init__(self, fig, ax, graphics):
        self.fig = fig
        self.ax  = ax
        self.graphics = graphics
        self.hulls          = graphics.hulls
        self.map_legend     = graphics.legend.map       # dict(zip(self.entries, handles))
        self.point_label    = point_label(ax, graphics.points)

        self.fig.canvas.mpl_connect('pick_event', self.handler)
        print("Event handler setup successful")


    def handler(self, event):
        entity = event.artist
        point = self.point_label.find_point(entity)
        print(entity, point)
        
        if point == None:  # visibility togleing from legend
            self.toggle_visibility(entity)
        else:                                      # point labeling
            self.point_label.change_point(point)

        self.fig.canvas.draw_idle()
        


    # : visibility toggling from legend :
    def toggle_visibility(self, entry):
        label = entry.get_label()
        group   = self.map_legend[label][1:]
        new_state = not group[0].visible  # bool
        for handle in self.graphics.legend.legend.legend_handles:
            if handle._label == label:
                handle.set_alpha(1 if new_state else 0.3)           

        for item in group:
            for i in range(len(item.element)):
                item.element[i].set_visible(new_state)

                if new_state == True:
                    item.element[i].set_picker(item.picker)
                else:
                    item.element[i].set_picker(item.picker_nvis)

        group[0].visible = new_state


    # : display coordinates on click :
class point_label():
    def __init__(self, ax, point_list):
        self.ax = ax
        self.last_point = None
        self.annotation = None
        self.point_list = point_list

    def change_point(self, point):
        if self.last_point == point:
            self.rm_last_point()

        else:
            if self.annotation != None:         
                self.rm_last_point()

            # & mehrere Punkte übereinander anzeigen
            self.annotation = self.ax.annotate(point.label, xy=point.label_pos, xycoords='data', xytext=(0,5), textcoords='offset points', ha='center', va='bottom', fontsize=12)
            point.element[0].set_alpha(1)

            self.last_point = point
    
    def rm_last_point(self):
        self.annotation.remove()
        self.annotation = None
        self.last_point.element[0]._alpha = self.last_point.alpha


    def find_point(self, clicked_point):
        for points in self.point_list:
            for point in points.element:
                if point == clicked_point:
                    return points

        return None