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
            fontsize=guideline["fontsize"],
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

def create_marker(
        markers,
        x_axis_quantities,
        y_axis_quantities,
        marker_size,
        ax
    ):
    for marker in markers:
        values = [None, None]
        for i, axes in enumerate([x_axis_quantities, y_axis_quantities]):
            for quantity in axes:
                try:
                    values[i] =  marker[quantity]
                    break
                except:
                    pass

        if values[:] != None:
            ax.scatter(
                values[0],
                values[1],
                c = marker['color'],
                edgecolors ='k',
                marker = marker['marker'],
                s = marker_size * marker['size_factor'],
                )


def create_annotation(
        annotations,
        arrows,
        ax
    ):
    for annotation in annotations:
        if annotation['arrow'] == False or annotation['arrow'] == None:
            ax.text(
                x        = annotation['txt_xy'][0],
                y        = annotation['txt_xy'][1],
                s        = annotation['text'],
                color    = annotation['txt_color'],
                fontsize = annotation['fontsize'],
            )
        else:
            ax.annotate(
                s        = annotation['text'],
                xy =       annotation['tip_xy'],
                xytext =   annotation['txt_xy'],
                color  =   annotation['txt_color'],
                fontsize = annotation['fontsize'],
                arrowprops = arrows[annotation['arrow']]
            )