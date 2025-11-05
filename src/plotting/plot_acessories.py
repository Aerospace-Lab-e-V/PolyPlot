import matplotlib.pyplot as plt
import numpy as np

def draw_guideline(
        guidelines,
        x_min,
        x_max,
        y_min,
        y_max,
        ax,
    ):
    '''
        Draws guideline for material index.

        Parameters
        ----------
        guideline : dict
            x : float (optional)      x or y must be given
                power of the material index (and thus the guideline)
                e.g., 1 for E/rho, 3 for E^(1/3)/rho.
            y : float (optional)
                x-axis limits ([low, high])
            m : float (optional)
                y_intercept of the guideline.
                This gets tricky if your x- and y-axis limits do not include 1.0.
                The default is 1.0.
            string : string to display and label the guideline
            string_position : location to start the string
        x_min, x_max: float
            definition area
        ax : matplotlib axis object
            The current plotting axis.

        Returns
        -------
        None.
    '''
    num_points = 5
    for guideline in guidelines:

        x = guideline['x']
        y = guideline['y']
        m = guideline['m']

        if m == False:  # horizontal
            x_values = np.linspace(x_min, x_max, num_points)
            y_values = np.ones(num_points)* y
        elif m == True: # vertical
            x_values = np.ones(num_points)* x
            y_values = np.linspace(y_min, y_max, num_points)
        else:                                                   # & semilog
            x_values = np.linspace(x_min, x_max, num_points)
            y_intercept = (y- (m*x))
            y_values = m*x_values + y_intercept

        ax.plot(
            x_values,
            y_values,
            linestyle = guideline['linestyle'],
            linewidth = guideline['linewidth'],
            color     = guideline['color'    ],
            )

        if m == True:
            label_angle = np.pi/2
        else:
            label_angle = np.arctan(m)

        if guideline['string_above'] == True:
            label_normal_angle = label_angle + np.pi/2
        else: 
            label_normal_angle = label_angle - np.pi/2

        x_text = x + np.cos(label_normal_angle)*guideline['string_padding']
        y_text = y + np.sin(label_normal_angle)*guideline['string_padding']

        ax.text(
            x_text,
            y_text, 
            guideline['string'], 
            fontsize=guideline['fontsize'],
            rotation=np.rad2deg(label_angle), 
            rotation_mode='anchor',
            transform_rotates_text=True)



def draw_colored_areas(
    colored_areas,
    ax
    ):
    '''
        colors the backgrounf of specific areas

        Parameters
        ----------
        colored_areas : dict
            x : list
                x-coordinates of edgeponts
            y : list
                y-coordinates corresponding to the given x-coordinates above
            color : char
                specifies color of the area
            alpha : float between 0 and 1
                intensity of the color
        ax : matplotlib axis object
            The current plotting axis.

        Returns
        -------
        None.
    '''
    for colored_area in colored_areas:
        x         = colored_area['x']
        y         = colored_area['y']
        color     = colored_area['color']
        alpha     = colored_area['alpha']

        ax.fill(
            x, 
            y, 
            color = color, 
            alpha = alpha
            )


# :  MARKER  : 
class marker:
    def __init__(self, annotations, material_colors, plotted_axes, ax):
        self.annotations_raw = annotations[1:]
        self.annotations     = []
        self.material_colors = material_colors
        self.font_size       = annotations[0]['font_size'  ]
        self.marker_size     = annotations[0]['marker_size']
        self.ax = ax
        self.annotation_position(plotted_axes)

    def annotation_position(self, plotted_axes):
        for annotation in self.annotations_raw:
            values = [None, None]
            for key, value in annotation['axes'].items():
                for axe in plotted_axes:
                    if axe == key:
                        values[plotted_axes.index(axe)] = value

            if values[0] != None and values[1] != None:
                annotation['values'] = values
                self.annotations.append(annotation)    


    def create_annotation(self, plot_scale):
        print(self.annotations)
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
                        marker = marker.get('marker_symbol','+'),
                        s = self.marker_size * marker.get('size_factor', 1),
                    )
                                    
            text = annotation['text']
            color = self.get_color(text['color'])
            arrow = annotation.get('arrow', None)
            if arrow == None:           # ~ Label 
                self.ax.text(
                    x        = text['rel_pos'][0] * plot_scale[0] + values[0],
                    y        = text['rel_pos'][1] * plot_scale[1] + values[1],
                    s        = text['name'],
                    color    = color,
                    fontsize = self.font_size,
                    ha       = "center"
                )
            else:                        # ~ Arrow 
                self.ax.annotate(
                    s           = text['name'],
                    xy          = values,
                    xytext      = text['rel_pos'] * plot_scale + values,
                    color       = color,
                    fontsize    = self.font_size,
                    arrowprops  = arrows[arrow],
                    plot_kwargs = {'ha': 'center'}
                )
            print(f"marker: {text['name']} @ {values}")


    def get_color(self, color):
        if color in self.material_colors:
            return self.material_colors[color] 
        else:
            return color
    
    def limits(self, dim):
        ret = [np.nan, np.nan]
        for annotation in self.annotations:
            ret[0] = np.nanmin([ret[0], annotation['values'][dim]])
            ret[1] = np.nanmax([ret[1], annotation['values'][dim]])

        return ret
