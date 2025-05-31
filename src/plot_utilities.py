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


def quantity_availability(
        x_axes_quantities,
        y_axes_quantities,
        data
    ):
    x_low  = np.zeros(shape=(0))
    x_high = np.zeros(shape=(0))
    y_low  = np.zeros(shape=(0))
    y_high = np.zeros(shape=(0))

    x_high_short = np.zeros(shape=(0))
    y_high_short = np.zeros(shape=(0))

    for pos in range(len(data)):                   # cycling position in matereial data for each name
        x_low_temp = None
        for quantity in x_axes_quantities:         # cycling possible names per axes
            if not pd.isna(data[quantity + ' low'].iloc[pos]):
                x_low_temp  = data[quantity + ' low' ].iloc[pos].copy()
                x_high_temp = data[quantity + ' high'].iloc[pos].copy()
                break
        if x_low_temp != None:                     # checking only fr y-value if x-value exists
            for quantity in y_axes_quantities:     # cycling possible names per axes
                if not pd.isna(data[quantity + ' low'].iloc[pos]):
                    x_low  = np.append(x_low,  x_low_temp )
                    x_high = np.append(x_high, x_high_temp)
                    y_low  = np.append(y_low,  data[quantity + ' low' ].iloc[pos].copy())
                    y_high = np.append(y_high, data[quantity + ' high'].iloc[pos].copy())
                    break

    # for pos in range(len(x_low)):   # clear nan rows
    #     if not (np.isnan(x_high[pos]) and np.isnan(y_high[pos])):
    #         x_high_short = np.append(x_high_short, x_high[pos])
    #         y_high_short = np.append(y_high_short, y_high[pos])

    
    print("x: ", x_low, " - ", x_high, "  ||  y: ", y_low, " - ", y_high)
    return x_low.T, x_high.T, y_low.T, y_high.T
    # return x_low.T, x_high_short.T, y_low.T, y_high_short.T 


def plot_points(
        x_low, 
        x_high,
        y_low,
        y_high,
        current_color,
        ax
    ):
    datapoints = len(x_low)
    for i in range(datapoints):
        if pd.isna(x_high[i]) and pd.isna(y_high[i]):    #if low = high draw point
            ax.plot(
                x_low[i],
                y_low[i],
                color = current_color,
                marker = 'o',
                alpha = 0.6
                )
        else:
            linewidth = 1
            if pd.isna(x_high[i]):             # low = high for plotting points / lines
                x_high[i] = x_low[i]
                linewidth = 3
            if pd.isna(y_high[i]):
                y_high[i] = y_low[i]
                linewidth = 3

            draw_ellipses(
                x = [x_low[i],  x_high[i]],
                y = [y_low[i],  y_high[i]],
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



def draw_plot(
        current_layer_number,
        current_master_layer_name,
        layers,
        data,
        x_axes_quantities,
        y_axes_quantities,
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
        x_axes_quantity : str
            quantity you would like to plot on the x-axes.
        y_axes_quantity : str
            quantity you would like to plot on the y-axes.
        ax : matplotlib.pyplot.axes
            figure axes on which you would like to plot
        material_colors : dict
            key-value pairs of categories and the desired colors
        data_type : str, optional
            Flag for whether the data is defined as ranges (i.e., upper and lower
            bounds) or as values (i.e., single values). The default is 'ranges'.

        Returns
        -------
        None.
    '''
    layer_name = layers[current_layer_number]['name']
    whitelist = layers[current_layer_number]['whitelist']
    whitelist_flag = layers[current_layer_number]['whitelist_flag']

    combined_DATA = np.zeros(shape=(0,2))

    for category, material_data in data.groupby(layer_name):
        print("====== Layer ", current_layer_number, ": ", category, "  (", layer_name, ") ======")

        if category in material_colors:
            current_color = material_colors[category]
        if current_layer_number < len(layers) -2:
            DATA = draw_plot(
                    current_layer_number + 1,
                    category,
                    layers,
                    material_data,
                    x_axes_quantities,
                    y_axes_quantities,
                    ax,
                    current_color,
                    material_colors,
                )

        # color checking
        if current_color == 0 and layers[current_layer_number]['visible'] == True:
            if 'default' in material_colors:
                current_color = material_colors['default']
            else:
                raise ValueError('You have material categories that have not been assigned a color. Please add a color to the material_colors dictionary (common_definitions function) and name it "default" or ' + category)
        
        
        if current_layer_number == len(layers)-1 \
        and ((category     in whitelist and whitelist_flag == True)  \
        or   (category not in whitelist and whitelist_flag == False)):
            x_low, x_high, y_low, y_high = quantity_availability(
                    x_axes_quantities,
                    y_axes_quantities,
                    material_data
                )

            if layers[current_layer_number]['visible'] == True:
                plot_points(
                    x_low, 
                    x_high,
                    y_low,
                    y_high,
                    current_color,
                    ax
                )

            X = np.append(x_low, x_high)    	# & nan handling (_high)
            Y = np.append(y_low, y_high)
            DATA = np.column_stack((X,Y))
            combined_DATA = np.vstack((combined_DATA, DATA))        # & check for NO new data to prevent identical hulls
            print("rows:", DATA.shape[0], "; columns:", DATA.shape[1])
            print("DATA: ", DATA)
            print("combined DATA: ", combined_DATA)


    if not combined_DATA.shape[0] == 0                 \
    and layers[current_layer_number]['visible'] == True:
        draw_hull(
            combined_DATA,
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

    if current_layer_number != 0:
        return combined_DATA



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
