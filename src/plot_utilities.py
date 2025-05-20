# -*- coding: utf-8 -*-
"""
Plot utilities script.
Contains all the misc. functions to generate the ashby plot (not related to the actual ellipses).


@author: Walgren
edit by afffe
"""

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import patches
from matplotlib import colors
from types import SimpleNamespace


from src.plot_convex_hull import(
    draw_ellipses,
    draw_hull,
    )


from src.rotation_aware_annotation import RotationAwareAnnotation
    

def plotting_presets(figure_type:str = 'publication'):
    '''
        Creates plotting presets for font size, marker size,
        and other quality of life presets.


        Parameters
        ----------
        figure_type : str
            Type of figure you would like to create.
            Options are 'publication' or 'presentation'
            Toggles different presets like font family, font size, etc.

        Returns
        -------
        None.
    '''
    #Graphs in a separate window (run in Spyder)
    if 'SPY_PYTHONPATH' in os.environ:
        # see https://stackoverflow.com/questions/32538758/nameerror-name-get-ipython-is-not-defined
        # running inside spyder!
        #Graphs in a separate window
        from IPython import get_ipython
        get_ipython().run_line_magic('matplotlib', 'qt')
        #Graphs inline (ala Jupyter notebook)
        #get_ipython().run_line_magic('matplotlib', 'inline')
    if figure_type.lower() == 'publication':
        # Plot with serif, Times New Roman Font
        plt.rc('font', family='serif')
        plt.rc('font', serif='Times New Roman')
        plt.rcParams.update({'font.size': 10})
        plt.rc('text', usetex='True')
    elif figure_type.lower() == 'presentation':
        #Plot with sans serif, Arial font
        plt.rc('font', family='sans-serif')
        plt.rcParams.update({'font.sans-serif':'Arial'})
        plt.rcParams.update({'font.size': 18})
        plt.rc('text',usetex='False')
    else:
        raise(ValueError,'Options for plotting_presets are publication or presentation')

    # Use Latex to render all fonts (this may interfere with the svg font encoding)
    # plt.rc('text', usetex='True')
    #Use no svg font encoding such that they can be imported as text into inkscape
    # FIXME grab the stack overflow link for this.
    plt.rcParams['svg.fonttype'] = 'none'
    #Modify marker size to make them readable
    plt.rcParams['lines.markersize'] = 10


def draw_plot(
        current_layer_number,
        current_master_layer_name,
        layers,
        data,
        x_axis_quantity,
        y_axis_quantity,
        y_axis_quantity_bk,
        y_axis_quantity_bk2,
        y_axis_quantity_bk3,
        ax,
        current_color,
        material_colors,
    ):
    '''
        Plots both the data points (either ellipses if material upper and lower
        bounds are given, or a scatter plot if single points are given) and the
        convex hull around all data points of a given category.

        Parameters
        ----------
        layers: dict
            name: str
                name of the layer
            visible: bool
                togles visibility
            alpha: float
                sets color intensity
        data : pandas dataframe
            dataframe with all material data to be plotted.
            Note that this dataframe must include the column 'Category;'
            which is case sensitive!
        x_axis_quantity : str
            quantity you would like to plot on the x-axis.
        y_axis_quantity : str
            quantity you would like to plot on the y-axis.
        ax : matplotlib.pyplot.axis
            figure axis on which you would like to plot
        material_colors : dict
            key-value pairs of categories and the desired colors
        data_type : str, optional
            Flag for whether the data is defined as ranges (i.e., upper and lower
            bounds) or as values (i.e., single values). The default is 'ranges'.

        Returns
        -------
        None.
    '''
    layer = layers[current_layer_number]['name']
    # print("==== Layer ", current_layer_number, ": ", current_master_layer_name, "  (", layer, ") ====")

    for category, material_data in data.groupby(layer):
        # if layers["whitelist"]
            # print(material_data)
            if category in material_colors:
                current_color = material_colors[category]
            if current_layer_number < len(layers) -1:
                draw_plot(
                    current_layer_number + 1,
                    category,
                    layers,
                    material_data,
                    x_axis_quantity,
                    y_axis_quantity,
                    y_axis_quantity_bk,
                    y_axis_quantity_bk2,
                    y_axis_quantity_bk3,
                    ax,
                    current_color,
                    material_colors,
                    )
            if (current_layer_number < len(layers) -2 and len(material_data) == 1) \
                or layers[current_layer_number]['visible'] == False:
                return
                
            # print("md", material_data)

            if current_color == 0 and layers[current_layer_number]['visible'] == True:
                if 'default' in material_colors:
                    current_color = material_colors['default']
                else:
                    raise ValueError('You have material categories that have not been assigned a color. Please add a color to the material_colors dictionary (common_definitions function) and name it "default" or ' + category)


            x_low        = material_data[x_axis_quantity     + ' low' ].copy()
            x_high       = material_data[x_axis_quantity     + ' high'].copy()
            y_low        = material_data[y_axis_quantity     + ' low' ].copy()
            y_high       = material_data[y_axis_quantity     + ' high'].copy()
            y_low_bk     = material_data[y_axis_quantity_bk  + ' low' ].copy()
            y_high_bk    = material_data[y_axis_quantity_bk  + ' high'].copy()
            y_low_bk2    = material_data[y_axis_quantity_bk2 + ' low' ].copy()
            y_high_bk2   = material_data[y_axis_quantity_bk2 + ' high'].copy()
            y_low_bk3    = material_data[y_axis_quantity_bk3 + ' low' ].copy()
            y_high_bk3   = material_data[y_axis_quantity_bk3 + ' high'].copy()
            # y_low  = np.empty([1, len(material_data)]) 
            # y_high = np.empty([1, len(material_data)]) 

            # for i in range(len(material_data)):
            #     if not pd.isna(material_data[y_axis_quantity + ' low' ].iloc[i]):
            #         y_low[1][i]  = material_data[y_axis_quantity + ' low' ].iloc[i].copy()
            #         y_high[1][i] = material_data[y_axis_quantity + ' high'].iloc[i].copy()
            #     else:
            #         y_low[1][i]  = material_data[y_axis_quantity_bk + ' low' ].iloc[i].copy()
            #         y_high[1][i] = material_data[y_axis_quantity_bk + ' high'].iloc[i].copy()

            # for matrix in [x_l_, x_h_, y_l_, y_h_]:             #3D array: 1D: x/y_low/high ;  2D material_data of one axis ;  3D 
            #     matrix.np.empty([4,len(material_data),1])
            # for matrix in [x_l, x_h, y_l, y_h]:
            #     matrix.np.empty([len(material_data),1])

            # for name in len(x_axis):
            #     x_l_[name] = material_data[name + ' low' ].copy()
            #     x_h_[name] = material_data[name + ' high'].copy()        
            # for name in len(y_axis):
            #     y_l_[name] = material_data[name + ' low' ].copy()
            #     y_h_[name] = material_data[name + ' high'].copy()
            
            for i in range(len(material_data)):
                # for name in len(x_axis):
                #     if not pd.isna(x_l_[name][i]):
                #         x_l[i] = x_l_[name][i]
                #         break
                    
                        
                if pd.isna(y_low.iloc[i]):
                    y_low.iloc[i]  = y_low_bk.iloc[i]
                    y_high.iloc[i] = y_high_bk.iloc[i]
                    if pd.isna(y_low.iloc[i]):
                        y_low.iloc[i]  = y_low_bk2.iloc[i]
                        y_high.iloc[i] = y_high_bk2.iloc[i]
                        if pd.isna(y_low.iloc[i]):
                            y_low.iloc[i]  = y_low_bk3.iloc[i]
                            y_high.iloc[i] = y_high_bk3.iloc[i]


                linewidth = 1
                if pd.isna(x_high.iloc[i]):       # x low = x high for plotting
                    x_high.iloc[i] = x_low.iloc[i]
                    linewidth = 3
                if pd.isna(y_high.iloc[i]):
                    y_high.iloc[i] = y_low.iloc[i]
                    linewidth = 3


                if  (x_low.iloc[i] == x_high.iloc[i]) \
                and (y_low.iloc[i] == y_high.iloc[i]):    # check if high is empty or low = high for both
                    ax.plot(
                        x_low.iloc[i],
                        y_low.iloc[i],
                        color = current_color,
                        marker = 'o',
                        alpha = 0.6
                        )

                else:
                    draw_ellipses(
                            x = [x_low.iloc[i],  x_high.iloc[i]],
                            y = [y_low.iloc[i],  y_high.iloc[i]],
                            plot_kwargs = {
                                'facecolor':colors.to_rgba(
                                    current_color,
                                    alpha=0.25
                                    ),
                                'edgecolor':current_color,
                                'linewidth': linewidth
                                },
                            ax = ax,
                            )
            
                X = np.zeros(shape=(2*len(material_data),2))
                X[:len(material_data),1] = y_low
                X[:len(material_data),0] = x_low

                X[len(material_data):,1] = y_high
                X[len(material_data):,0] = x_high

            
            # print(X)
            draw_hull(
                X,          # & Performance: combine return matrix instead of reading out again
                scale = 1.05,
                padding = 'scale',
                n_interpolate = 100,
                interpolation = 'cubic',
                ax = ax,
                plot_kwargs = {
                    'color': current_color,
                    'alpha': layers[current_layer_number]['alpha']
                    }
                )


def create_legend(
        # data,
        # layers,
        material_classes,
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
    # for layer in layers:
    #     if layer['visible' == True]:
    #         for category, material_data in data.groupby(layer):
                

    # make a manual legend
    for material_class in material_classes:
        patch = patches.Patch(
            color = material_colors[material_class],
            label = material_class
            )
        handles.append(patch)

    # place legend outside the plot     # ToDo put Legend right of the plot
    
    plt.legend(
        handles=handles,
        bbox_to_anchor = (0, 1.02, 1, 0.2),
        loc  = 'lower left',
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
        limit: 4x4 float array
            area shown on the plot
        ax : matplotlib axis object
            The current plotting axis.

        Returns
        -------
        None.
    '''
    num_points = 4
    for guideline in guidelines:

        x = guideline['x']
        y = guideline['y']
        m = guideline['m']

        if x == None and m == None: # horizontal
            x_values = np.linspace(y_min, y_max, num_points)
            y_values = np.ones(num_points)* y
        elif y == None and m == None: # vertical
            x_values = np.ones(num_points)* x
            y_values = np.linspace(x_min ,x_max, num_points)
        else:            
            x_values = np.linspace(x_min, x_max, num_points)
            y_intercept = (y- (m*x))
            # semilog: a∙x^m
            y_values = m*x_values + y_intercept

        ax.plot(
            x_values,
            y_values,
            linestyle = guideline['linestyle'],
            linewidth = guideline['linewidth'],
            color     = guideline['color'    ],
            )

        # Create an annotation on the line to denote the equation
        # The spacing of this line takes a bit (xytext variable),
        # because the units are 1/72 in
        # FIXME generalize the xytext placement?
        RotationAwareAnnotation(
            guideline['string'],
            xy=guideline['string_position'],
            p=(x_values[3], y_values[3]),
            pa = (x_values[0], y_values[0]),
            ax=ax,
            xytext=(0,0),
            textcoords="offset points",
            va="top"
            )



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
            ),


def common_definitions():
    '''
        Creates two dictionaries for colors and units (labeling).
        Add the units that you wish to see in the world (Ghandhi, 1913)

        Returns
        -------
        units : dict
            Dictionary with key-value pairs for each quantity and its
            respective SI unit. Keys are case sensitive.
            Could maybe be a way to just grab this
            from a preexisting python package.

        material_colors : dict
            key-value pairs for each category of material and the respective
            color in which you wish to see it plotted. Keys are case sensitive.
    '''
    # common units for labeling the axes. These are case sensitive.
    units = {
        'Density': 'kg/m$^3$',
        'Tensile Strength': 'MPa',
        "Young Modulus": 'GPa',
        "Fracture Toughness": r"MPa$\sqrt{\text{m}}$",
        "Thermal Conductivity": r"W/m$\cdot$K",
        "Thermal expansion": "1$^-6$/m",
        "Resistivity": r"$\Omega \cdot$m",
        "Poisson": "-",
        "Poisson difference": "-",
        "Melting Point": "°C",
        "Deflection Temperature at 1.8 MPa 264 psi": "°C",
        "Tensile Strength at Break": "MPa"
        }

    material_colors = {
        'ABS': '#219DD3',	
        'PA12':'#7BBFD9',	
        'PEEK':'#D69D20',	
        'PLA': '#E3B768',	
        'PET': '#3BD420',	
        'PETG':'#85E064',	
        'PPSU':'#B52ED6',	
        'PPS': '#CE82E0',

        'PA11':'#219DD3',	
        'POM': '#7BBFD9',	
        'PP':  '#D69D20',	
        'PVDF':'#E3B768',	
        'PC':  '#3BD420',	
        'PEI': '#85E064',	
        'PA6': '#B52ED6',	
        'PPA': '#CE82E0',

        'PA': "red",
        'PET':"black",
        '':   "white",
        }
#  'blue', 'orange', 'red', 'green', 'purple', 'Brown', 'pink', 'grey', 'black', 'white'
    return units, material_colors
