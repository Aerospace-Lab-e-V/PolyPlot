import matplotlib.pyplot as plt
import numpy as np

def draw_guideline(guidelines, x_min, x_max, y_min, y_max, font_color, ax):
    num_points = 1000
    for guideline in guidelines:

        x = guideline.get('x', False)
        y = guideline.get('y', False)
        m = guideline.get('m', False)
        if x == False or y == False or m == False:
            print("❗ x, y or m not specified for guideline")

        if x == None:    # horizontal
            x_values = np.linspace(x_min, x_max, num_points)
            y_values = np.ones(num_points)* y
        elif y == None:  # vertical
            x_values = np.ones(num_points)* x
            y_values = np.linspace(y_min, y_max, num_points)
        else:             # & semilog
            x_values = np.linspace(x_min, x_max, num_points)
            y_intercept = (y- (m*x))
            y_values = m*x_values + y_intercept

        print(f"guideline: {guideline.get('label',"")} @ [{x_values[0]}|{y_values[0]}] - [{x_values[-1]}|{y_values[-1]}]")


        ax.plot(
            x_values,
            y_values,
            **guideline.get("line_props", {}) # & test and fix
            )

        if y == None:
            label_angle = np.pi/2
        else:
            label_angle = np.arctan(m)

        if guideline.get('label_above',True) == True:
            label_normal_angle = label_angle + np.pi/2
        else: 
            label_normal_angle = label_angle - np.pi/2

        x_text = x + np.cos(label_normal_angle)*guideline.get('label_padding',6)
        y_text = y + np.sin(label_normal_angle)*guideline.get('label_padding',6)

        ax.text(
            x_text,
            y_text, 
            guideline.get('label',""), 
            color=guideline.get("font_color",font_color),
            fontsize=guideline.get('fontsize', 18),
            rotation=np.rad2deg(label_angle), 
            rotation_mode='anchor',
            transform_rotates_text=True)



def draw_colored_areas(colored_areas, ax):
    for colored_area in colored_areas:
        x         = colored_area['x']
        y         = colored_area['y']
        color     = colored_area['color']       # & .get(,'default')
        alpha     = colored_area.get('alpha',0.2)

        if len(x) != len(y) or len(x) == 0 or len(y) == 0:
            print("❗ x & y array have different sizes or length 0 unable to print colored area")
            break

        ax.fill(
            x, 
            y, 
            color = color, 
            alpha = alpha
            )


# :  MARKER  : 
class marker:
    def __init__(self, annotations, material_colors, abs_axes, rel_axes, ax):
        self.annotations_raw = annotations[1:]
        self.annotations     = []
        if len(self.annotations_raw):
            self.material_colors = material_colors
            self.font_size       = annotations[0].get('font_size',18)
            self.marker_size     = annotations[0].get('marker_size',330)
            self.ax = ax
            self.annotation_position(abs_axes, rel_axes)

    def annotation_position(self, abs_axes, rel_axes):
        for annotation in self.annotations_raw:
            values = [None, None]
            for dim in [0,1]: # dimensions
                values[dim] = self.get_pos(abs_axes[dim], annotation['axes'])
                if rel_axes[dim] != None and values[dim] != None:        # rellative
                    value = self.get_pos(rel_axes[dim], annotation['axes'])
                    if value != None:  values[dim] /= value
                    else:              values[dim]  = None

            if values[0] != None and values[1] != None:
                annotation['values'] = values
                self.annotations.append(annotation)  

    def get_pos(self, plt_axe, ann_axes):
        for key, value in ann_axes.items():
            if plt_axe == key:
                return value


    def create_annotations(self, plot_size):
        if len(self.annotations_raw) == 0: 
            return
        for annotation in self.annotations: 
            values = annotation['values']

            if values[0] != None and values[1] != None:
                marker = annotation['marker']
                if marker != None:     # ~ Marker 
                    color = self.get_color(marker['color'])

                    self.ax.scatter(
                        values[0],
                        values[1],
                        c = color,
                        marker = marker.get('marker_symbol','o'),
                        s = self.marker_size * marker.get('size_factor', 1),
                        edgecolors = self.get_color(marker.get('edgecolors',"black")),
                        linewidths = marker.get('linewidths', 0)
                    )

            text = annotation['text']
            font_size = text.get('font_size', self.font_size)
            color = self.get_color(text.get('color','default'))
            arrow = annotation.get('arrow', None)
            # print("label pos:", plot_size.x.offset(text['rel_pos'][0], values[0]) , plot_size.y.offset(text['rel_pos'][1], values[1]))
            if arrow == None:           # ~ Label 
                self.ax.text(
                    x        = plot_size.x.offset(values[0], text['rel_pos'][0]),
                    y        = plot_size.y.offset(values[1], text['rel_pos'][1]),
                    s        = text.get('name',""),
                    color    = color,
                    fontsize = self.font_size,
                    ha       = "center"
                )
            else:                        # ~ Arrow 
                self.ax.annotate(        # & shrink shortens arrow on both ends
                    text        = text.get('name',""),
                    xy          = values,
                    xytext      = [plot_size.x.offset(values[0], text['rel_pos'][0]), \
                                   plot_size.y.offset(values[1], text['rel_pos'][1])],
                    color       = color,
                    fontsize    = self.font_size,
                    arrowprops  = annotation['arrow'],
                    # kwargs      = {'ha': 'center'}
                )
            print(f"marker: {text['name']} @ {values}")


    def get_color(self, color):
        if color in self.material_colors:
            return self.material_colors[color] 
        else:
            return color
    
    def limits(self, dim):
        ret = [np.nan, np.nan]
        if len(self.annotations) > 0: 
            for annotation in self.annotations:
                ret[0] = np.nanmin([ret[0], annotation['values'][dim]])
                ret[1] = np.nanmax([ret[1], annotation['values'][dim]])
        return ret


