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


def filter_data(data, filters, filter_keys):
    plot_datapoint = True
    for filter in filters:
        entry = data[filter["name"]]
        state = None
        for keys in filter_keys:
            if entry in keys["entries"]:
                state = keys["state"]

        if not state in filter["states"]:
            plot_datapoint = False

    return plot_datapoint             


def quantity_availability(
        x_axes_quantities,
        y_axes_quantities,
        filter, 
        filter_keys,
        visible,
        current_color,
        data,
        ax
    ):
    x_low  = np.zeros(shape=(0))
    x_high = np.zeros(shape=(0))
    y_low  = np.zeros(shape=(0))
    y_high = np.zeros(shape=(0))

    x_high_short = np.zeros(shape=(0))
    y_high_short = np.zeros(shape=(0))

    for pos in range(len(data)):                   # cycling position in matereial data for each name
        if filter_data(data.iloc[pos,:], filter, filter_keys) == True:
            for quantity in x_axes_quantities:         # cycling possible names per axes
                if not pd.isna(data[quantity + ' low'].iloc[pos]):
                    x_low_temp  = data[quantity + ' low' ].iloc[pos].copy()
                    x_high_temp = data[quantity + ' high'].iloc[pos].copy()
                    break
            if x_low_temp != None:                     # checking only for y-value if x-value exists
                for quantity in y_axes_quantities:     # cycling possible names per axes
                    if not pd.isna(data[quantity + ' low'].iloc[pos]):
                        x_low_      = x_low_temp
                        y_low_      = data[quantity + ' low' ].iloc[pos].copy()
                        y_high_temp = data[quantity + ' high'].iloc[pos].copy()

                        x_low  = np.append(x_low,   x_low_)
                        y_low  = np.append(y_low,   y_low_)

                        if not( pd.isna(x_high_temp) or pd.isna(x_high_temp)):
                            x_high_ = x_high_temp
                            y_high_ = y_high_temp

                            x_high = np.append(x_high,  x_high_)
                            y_high = np.append(y_high,  y_high_)

                    # +  plot  + 
                            if visible: 
                                linewidth = 1
                                if pd.isna(x_high_):             # low = high for plotting points / lines
                                    x_high_ = x_low_
                                    linewidth = 3
                                if pd.isna(y_high_):
                                    y_high_ = y_low_
                                    linewidth = 3

                                draw_ellipses(
                                    x = [x_low_,  x_high_],
                                    y = [y_low_,  y_high_],
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

                        elif visible:
                            ax.plot(
                                x_low_,
                                y_low_,
                                color = current_color,
                                marker = 'o',
                                alpha = 0.6
                                )
                        break

    print("x: ", x_low, " - ", x_high, "  ||  y: ", y_low, " - ", y_high)
    return x_low.T, x_high.T, y_low.T, y_high.T



def draw_plot(
        current_layer_number,
        current_master_layer_name,
        layers,
        filter,
        filter_keys,
        data,
        x_axes_quantities,
        y_axes_quantities,
        legend,
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

    # +       recursive repetition       +
    if current_layer_number < len(layers) - 1:
        layer_name           = layers[current_layer_number]['name']
        layer_whitelist      = layers[current_layer_number]['whitelist']
        layer_whitelist_flag = layers[current_layer_number]['whitelist_flag']
        layer_visibility     = layers[current_layer_number]['visible']
        combined_DATA        = np.zeros(shape=(0,2))

        for category, material_data in data.groupby(layer_name):
            print("====== Layer ", current_layer_number, ": ", category, "  (", layer_name, ") ======")

            if category in material_colors   and   category not in legend   and   layer_visibility == True:   # ° color & legend entry handling
                current_color = material_colors[category]
                legend.append(category)
            elif current_color == 0:
                if 'default' in material_colors:
                    current_color = material_colors['default']
                else:
                    raise ValueError('You have material categories that have not been assigned a color and no default value. Please add a color to the material_colors dictionary (common_definitions function) and name it "default" or ' + category)                    
                                        

            if (category in layer_whitelist and layer_whitelist_flag == True) or (category not in layer_whitelist and layer_whitelist_flag == False):
                DATA, legend, plotted = draw_plot(      
                        current_layer_number + 1,
                        category,
                        layers,
                        filter,
                        filter_keys,
                        material_data,
                        x_axes_quantities,
                        y_axes_quantities,
                        legend,
                        ax,
                        current_color,
                        material_colors,
                    )

                print(DATA.shape[0])

                if DATA.shape[0] > 1 and layer_visibility == True                              \
                and not (len(data.groupby(layer_name).groups.keys()) == 1 and plotted == False): # hull not empty  &  visible  &  not identical to layer below if layer below is plotted
                    draw_hull(
                        DATA,
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
                    plotted = True

                combined_DATA = np.vstack((combined_DATA, DATA))
                # print("-- Layer ", current_layer_number, " DATA: ", DATA, " combined_DATA: ", combined_DATA) # . combined_DATA[~np.isnan(combined_DATA)]


        if len(data.groupby(layer_name).groups.keys()) > 1:
            plotted == False        # & plotted
                
        return combined_DATA, legend, plotted

            
    # +       recursive exit       +
    else:
        x_low, x_high, y_low, y_high = quantity_availability(   # read data
                x_axes_quantities,
                y_axes_quantities,
                filter, 
                filter_keys,
                layers[current_layer_number]['visible'],
                current_color,
                data,
                ax
            )

        X = np.append(x_low, x_high)
        Y = np.append(y_low, y_high)
        DATA = np.column_stack((X,Y))
        return DATA, legend, False
