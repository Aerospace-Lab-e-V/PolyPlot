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


def quantity_availability(
        x_axes_quantities,
        y_axes_quantities,
        alpha_points,
        alpha_areas,
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
        x_low_temp = None
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
                        if alpha_areas != None and alpha_areas > 0: 
                            draw_ellipses(
                                x = [x_low_,  x_high_],
                                y = [y_low_,  y_high_],
                                plot_kwargs = {
                                    'facecolor':colors.to_rgba(
                                        current_color,
                                        alpha=alpha_areas
                                        ),
                                    'edgecolor':current_color,
                                    },
                                ax = ax,
                                )
                    elif alpha_points != None and alpha_points > 0:
                        ax.plot(
                            x_low_,
                            y_low_,
                            color = current_color,
                            marker = 'o',
                            alpha = alpha_points
                            )
                    break

    print("x: ", x_low, " - ", x_high, "  ||  y: ", y_low, " - ", y_high)
    return x_low.T, x_high.T, y_low.T, y_high.T



def draw_plot(
        current_layer_number,
        current_master_layer_name,
        layers,
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
        layer_alpha          = layers[current_layer_number]['alpha']
        combined_DATA        = np.zeros(shape=(0,2))

        for category, material_data in data.groupby(layer_name):
            print("====== Layer ", current_layer_number, ": ", category, "  (", layer_name, ") ======")             

            if (category in layer_whitelist and layer_whitelist_flag == True) or (category not in layer_whitelist and layer_whitelist_flag == False):
                if category in material_colors and category not in legend and layer_alpha:   # ° color & legend entry handling
                    current_color = material_colors[category]
                    legend.append(category)
                elif current_color == 0:
                    if 'default' in material_colors:
                        current_color = material_colors['default']
                    else:
                        raise ValueError('You have material categories that have not been assigned a color and no default value. Please add a color to the material_colors dictionary (common_definitions function) and name it "default" or ' + category)                    
                           

                DATA, legend, plotted = draw_plot(      
                        current_layer_number + 1,
                        category,
                        layers,
                        material_data,
                        x_axes_quantities,
                        y_axes_quantities,
                        legend,
                        ax,
                        current_color,
                        material_colors,
                    )
                # print(DATA)
                # print("plotted: ", plotted, "  -  keys: ", data.groupby(layer_name).groups.keys())
                if DATA.shape[0] > 1 and layer_alpha != 0 and layer_alpha != None          \
                and not len(data.groupby(layer_name).groups.keys()) == 1       \
                and plotted == False: # hull not empty  &  visible  &  not identical to layer below if layer below is plotted
                    draw_hull(
                        DATA,
                        scale = 1.04,
                        n_interpolate = 100,
                        interpolation = 'cubic',
                        ax = ax,
                        plot_kwargs = {
                            'color': current_color,
                            'alpha': layer_alpha
                            }
                        )
                    plotted = True

                combined_DATA = np.vstack((combined_DATA, DATA))
                # print("-- Layer ", current_layer_number, " DATA: ", DATA, " combined_DATA: ", combined_DATA) # . combined_DATA[~np.isnan(combined_DATA)]


        if len(data.groupby(layer_name).groups.keys()) > 1:
            plotted = False
                
        return combined_DATA, legend, plotted

            
    # +       recursive exit       +
    else:
        x_low, x_high, y_low, y_high = quantity_availability(   # read data
                x_axes_quantities,
                y_axes_quantities,
                layers[current_layer_number]['alpha_points'],
                layers[current_layer_number]['alpha_areas'],
                current_color,
                data,
                ax
            )

        X = np.append(x_low, x_high)
        Y = np.append(y_low, y_high)
        DATA = np.column_stack((X,Y))
        return DATA, legend, False
