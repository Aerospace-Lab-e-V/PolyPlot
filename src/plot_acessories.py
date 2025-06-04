from matplotlib import patches
import matplotlib.pyplot as plt
import numpy as np


def create_legend(
        legend_items,
        material_colors,
        font_color
        ):
    '''
        Creates a legend located outside the plot bounding box. Currently
        set to the top of the plot.

        Important references:
            Extracting an iterable from a pandas groupby:
                https://stackoverflow.com/questions/28844535/python-pandas-groupby-get-list-of-groups
            Manual legend creation:
                https://stackoverflow.com/questions/39500265/how-to-manually-create-a-legend
            Plotting legends outside the bounding box:
                https://stackoverflow.com/questions/4700614/how-to-put-the-legend-outside-the-plot

        Parameters
        ----------
        material_classes : Iterable list or dict_keys object
            The list of different material classes you wish to display in the
            legend. Commonly found via data.groupby("Category").groups.keys()
        material_colors : DICT
            Dictionary that references the material class to the color you
            wish to display it as.
        Returns
        -------
        None.
    '''
    handles = []

    for item in legend_items:
        patch = patches.Patch(
            color = material_colors[item],
            label = item
            )
        handles.append(patch)
    
    plt.legend(
        handles=handles,
        bbox_to_anchor = (0, 1.02, 1, 0.2),
        loc  = 'lower left',        # & put Legend right of the plot
        mode = 'expand',
        borderaxespad = 0,
        fontsize = 15,
        labelcolor = font_color,
        facecolor = 'none',
        edgecolor = 'none',
        ncol = 5)

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
        x_axis_quantity,
        y_axis_quantity,
        marker_size,
        ax
    ):
    for marker in markers:
        ax.scatter(
            marker[x_axis_quantity],
            marker[y_axis_quantity],
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
        if annotation['arrow'] == 0:
            ax.text(
                annotation['txt_xy'],
                           annotation['text'],
                color    = annotation['txt_color'],
                fontsize = annotation['fontsize'],
            )
        else:
            ax.annotate(
                           annotation['text'],
                xy =       annotation['tip_xy'],
                xytext =   annotation['txt_xy'],
                color  =   annotation['txt_color'],
                fontsize = annotation['fontsize'],
                arrowprops = arrows[annotation['arrow']-1]
            )