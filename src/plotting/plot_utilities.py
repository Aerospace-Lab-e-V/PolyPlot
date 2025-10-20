import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import colors
from types import SimpleNamespace

from .plot_hull import plotter_graphics
from .formatting import legend


def property_availability(
        data,
        data_point,
        columns, 
        modes, 
        length_col
    ):
    point  = np.full((2, 2, length_col), np.nan)
    index  = np.full(2, -1)

    for axis, column in enumerate([columns[0], columns[1]]):
        for property, property_data in enumerate(column):
            if not pd.isna(data[property_data + ' low'].iloc[data_point]):
                point[axis, 0, property] = data[property_data + ' low' ].iloc[data_point].copy()  # low
                point[axis, 1, property] = data[property_data + ' high'].iloc[data_point].copy()  # high
        
        if not np.all(np.isnan(point[axis, 0, :])):
            if   modes[axis] == "max":      # & ignoring high value
                index[axis] = np.nanargmax(point[axis, 0, :])
            elif modes[axis] == "min":
                index[axis] = np.nanargmin(point[axis, 0, :]) 
            else:
                index[axis] = np.argmax(~np.isnan(point[axis, 0, :]))
    return index, point



def single_values(
        graphics,
        data,
        columns,
        modes,
        alpha_points,
        alpha_areas,
        current_color,
        category,
    ):
    length_col = max(len(columns[:][0]), len(columns[:][1]))
    point_list = np.full((1, 2), np.nan)     # [x, y][low, high][datapoints]

    for data_point in range(len(data)):
        coords = np.full((2, 2), np.nan)
        index, point = property_availability(data, data_point, columns, modes, length_col)

        if False: # & specific data  (/density)
            index_rel, point_rel = property_availability(data_point, columns, modes, data)
            # & / ...

        else:
            if np.any(index[:] == -1): 
                graphics.add_point_skipped()
                print("⚠ skip")
            else:
                graphics.add_point_plotted()
                # label = graphics.create_label(category[...]) 

                coords[0, :] = point[0, :, index[0]] # x
                coords[1, :] = point[1, :, index[1]] # y

                point_list = np.vstack((point_list, coords[:,0]))  # add low
                if not np.all(pd.isna(coords[:, 1])):
                    point_list = np.vstack((point_list, coords[:,1]))   # add high if not empty in both dimensions

                # + plot  + 
                    if alpha_areas != None and alpha_areas > 0:
                        if np.isnan(coords[0,1]): coords[0,1] = coords[0,0]
                        if np.isnan(coords[1,1]): coords[1,1] = coords[1,0]

                        graphics.draw_ellipses(
                                np.transpose(coords),
                                category,
                                scale = 1.05,
                                plot_kwargs = {
                                    # 'facecolor':colors.to_rgba(current_color,alpha=alpha_areas),
                                    'color':current_color,
                                    'alpha':alpha_areas,
                                    'picker':8,
                                    },
                                value_ranges = True
                            )
                elif alpha_points != None and alpha_points > 0:
                    graphics.plot(
                            coords[0, :],
                            coords[1, :],
                            color = current_color,
                            alpha = alpha_points,
                            category = category,
                        )

    point_list = point_list[1: ,:] # remove placeholder on beginning
    print("x: ", np.transpose(point_list[:, 0]))
    print("y: ", np.transpose(point_list[:, 1]))
    return point_list


def draw_plot(
    graphics,
    data,
    columns,
    modes,
    material_colors,
    layers,
    algorithm,
    current_layer_number,
    category,
    current_color,
    legend,

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
        x_axes_property : str
            property you would like to plot on the x-axes.
        y_axes_property : str
            property you would like to plot on the y-axes.
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
            layer_whitelist_flag = layers[current_layer_number]['whitelist_flag']
            layer_whitelist      = layers[current_layer_number]['whitelist']
            layer_alpha          = layers[current_layer_number]['alpha']
            combined_DATA        = np.full((1, 2), np.nan)      # & leer erstelen?
            plotted = False
        except:
            raise KeyError(f"could not import layer {current_layer_number +1}. Check config.json!")

        for category, material_data in data.groupby(layer_name):
            if pd.isna(category): category == None            
            print("====== Layer ", current_layer_number, ": ", category, "  (", layer_name, ") ======") 


            if (category     in layer_whitelist and layer_whitelist_flag == True) or \
               (category not in layer_whitelist and layer_whitelist_flag == False):
                if category in material_colors and category not in legend and layer_alpha:   # ° color & legend entry handling
                    current_color = material_colors[category]
                    graphics.legend.append_category(category, current_color)
                    legend.append(category)

    


                DATA, plotted = draw_plot(
                        graphics,
                        material_data,
                        columns,
                        modes,
                        material_colors,
                        layers,
                        algorithm,
                        current_layer_number + 1,
                        category,
                        current_color,
                        legend,
                    )

                # print(DATA)
                # print("plotted: ", plotted, "  -  keys: ", data.groupby(layer_name).groups.keys())
                if DATA.shape[0] > 1 and layer_alpha > 0 and layer_alpha != None          \
                and not len(data.groupby(layer_name).groups.keys()) == 1       \
                and plotted == False: # hull not empty  &  visible  &  not identical to layer below if layer below is plotted
                    graphics.draw_hull(
                            DATA,
                            category,
                            interpolation = algorithm,    # alpha or cubic
                            scale = 1.05,
                            plot_kwargs = {
                                'color': current_color,
                                'alpha': layer_alpha,
                                'label': category,
                                },
                        )
                    plotted = True

                combined_DATA = np.vstack((combined_DATA, DATA))

                # print("-- Layer ", current_layer_number, " DATA: ", DATA, " combined_DATA: ", combined_DATA) # . combined_DATA[~np.isnan(combined_DATA)]


        if len(data.groupby(layer_name).groups.keys()) > 1:
            plotted = False
                
        return combined_DATA[1:,:], plotted

            
    # +       recursive exit       +
    else:
        DATA = single_values(   # plot individual points
                graphics,
                data,
                columns,
                modes,
                layers[current_layer_number]['alpha_points'],
                layers[current_layer_number]['alpha_areas'],
                current_color,
                legend[-1]
            )
        return DATA, False




""" 
class:
    skipped & plotted count ++
    additional data per point


"""