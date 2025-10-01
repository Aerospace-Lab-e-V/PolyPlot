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
        columns,
        modes,
        alpha_points,
        alpha_areas,
        current_color,
        data,
        ax
    ):
    point_list = np.zeros((2, 2, 0))     # [x, y][low, high][datapoints]
    length_col = max(len(columns[:][0]), len(columns[:][1]))

    for data_point in range(len(data)):
        point  = np.full((2, 2, length_col), np.nan)
        coords = np.full((2, 2, 1), np.nan)
        index  = np.full(2, -1)
        for axis, column in enumerate([columns[0], columns[1]]):
            for quantity, quantity_data in enumerate(column):
                if not pd.isna(data[quantity_data + ' low'].iloc[data_point]):
                    point[axis, 0, quantity] = data[quantity_data + ' low' ].iloc[data_point].copy()  # low
                    point[axis, 1, quantity] = data[quantity_data + ' high'].iloc[data_point].copy()  # high

            if   modes[axis] == "max":
                 index[axis] = np.nanargmax(point[axis, 0, :])
            elif modes[axis] == "min":
                 index[axis] = np.nanargmin(point[axis, 0, :]) 
            else:
                 index[axis] = np.argmax(~np.isnan(point[axis, 0, :]))

        if np.all(index[:] >= 0):
            coords[0, :, 0] = point[0, :, index[0]]
            coords[1, :, 0] = point[1, :, index[1]]

            point_list = np.append(point_list, coords, axis=2)   # & np.dstack → remoove 3rd dimension

    # + plot  + 
            if (not np.isnan(point[0, 0, index[0]]) or not np.isnan(point[0, 0, index[0]])) and (alpha_areas != None and alpha_areas > 0): 
                draw_ellipses(
                    x = coords[0, :, 0],
                    y = coords[1, :, 0],
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
                    coords[0, :, 0],
                    coords[1, :, 0],
                    color = current_color,
                    marker = 'o',
                    alpha = alpha_points
                    )

    print(point_list)
    return point_list


def draw_plot(
        current_layer_number,
        current_master_layer_name,
        layers,
        data,
        columns,
        modes,
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
        try:
            layer_name           = layers[current_layer_number]['name']
            layer_whitelist      = layers[current_layer_number]['whitelist']
            layer_whitelist_flag = layers[current_layer_number]['whitelist_flag']
            layer_alpha          = layers[current_layer_number]['alpha']
            combined_DATA        = np.zeros(shape=(1,2))
            plotted = False
        except:
            raise KeyError(f"could not import layer {current_layer_number +1}. Check config.json!")

        for category, material_data in data.groupby(layer_name):
            print("====== Layer ", current_layer_number, ": ", category, "  (", layer_name, ") ======") 

            if pd.isna(category): category == None            

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
                        columns,
                        modes,
                        legend,
                        ax,
                        current_color,
                        material_colors,
                    )
                # print(DATA)
                print("plotted: ", plotted, "  -  keys: ", data.groupby(layer_name).groups.keys())
                if DATA.shape[0] > 1 and layer_alpha != 0 and layer_alpha != None          \
                and not len(data.groupby(layer_name).groups.keys()) == 1       \
                and plotted == False: # hull not empty  &  visible  &  not identical to layer below if layer below is plotted
                    draw_hull(
                        DATA,
                        scale = 1.04,
                        n_interpolate = 100,
                        interpolation = 'alpha',    # alpha or cubic
                        ax = ax,
                        plot_kwargs = {
                            'color': current_color,
                            'alpha': layer_alpha
                            }
                        )
                    plotted = True
                print(combined_DATA, DATA)
                combined_DATA = np.vstack((combined_DATA, DATA))
                # print("-- Layer ", current_layer_number, " DATA: ", DATA, " combined_DATA: ", combined_DATA) # . combined_DATA[~np.isnan(combined_DATA)]


        if len(data.groupby(layer_name).groups.keys()) > 1:
            plotted = False
                
        return combined_DATA, legend, plotted

            
    # +       recursive exit       +
    else:
        point_list = quantity_availability(   # plot individual points
                columns,
                modes,
                layers[current_layer_number]['alpha_points'],
                layers[current_layer_number]['alpha_areas'],
                current_color,
                data,
                ax
            )

        DATA = np.hstack((point_list[:, 0, :], point_list[:, 1, :]))
        DATA = np.transpose(DATA.reshape((DATA.shape[0], -1)))

        return DATA, legend, False
