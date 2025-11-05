import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import colors
from types import SimpleNamespace

from .plot_hull import plotter_graphics

class data_handling(): 
    def __init__(self, graphics, frame):
        self.graphics        = graphics
        self.absolute        = parse_data(frame, frame["x_quantity"],     frame["y_quantity"],     True )
        self.relative        = parse_data(frame, frame["x_rel_quantity"], frame["y_rel_quantity"], False)
        self.frame           = frame
        self.material_colors = frame['material_colors']
        self.layers          = frame['layers']
        self.len_layers      = len(self.layers) 
        self.legend          = ['default']
        self.point_count     = {'skipped':0, 'plotted':0}     # [skipped, plotted]
        self.alpha_points    = self.layers[-1]['alpha_points']
        self.alpha_areas     = self.layers[-1]['alpha_areas' ]

    def plot(self, data):
        return self.recursive_preparation(
                            data,
                            current_layer_number = 0,
                            hirachie             = [],
                            current_color        = self.frame['material_colors']['default'],
                        )


    def recursive_preparation(self, data, current_layer_number, hirachie, current_color):
        # +       recursive repetition       +
        if current_layer_number < self.len_layers - 1:
            try:
                layer_name           = self.layers[current_layer_number]['name']
                layer_whitelist_flag = self.layers[current_layer_number]['whitelist_flag']
                layer_whitelist      = self.layers[current_layer_number]['whitelist']
                layer_alpha          = self.layers[current_layer_number]['alpha']
                combined_DATA        = np.full((1, 2), np.nan)      # & leer erstelen?
            except:
                raise KeyError(f"could not import layer {current_layer_number +1}. Check config.json!")

            for category, material_data in data.groupby(layer_name):
                if pd.isna(category): category == None            
                print("====== Layer ", current_layer_number, ": ", category, "  (", layer_name, ") ======") 

                if (category  in layer_whitelist and layer_whitelist_flag == True) or \
                (category not in layer_whitelist and layer_whitelist_flag == False):
                    if category in self.material_colors and category not in self.legend and layer_alpha:   # ° color & legend entry handling
                        current_color = self.material_colors [category]
                        self.graphics.legend.append_category(category, current_color)
                        self.legend.append(category)

                    DATA, plotted = self.recursive_preparation(
                            material_data,
                            current_layer_number + 1,
                            hirachie + [category],
                            current_color,
                        )

                    # print(DATA)
                    # print("plotted: ", plotted, "  -  keys: ", data.groupby(layer_name).groups.keys())
                    if DATA.shape[0] > 1 and layer_alpha > 0 and layer_alpha != None          \
                    and not len(data.groupby(layer_name).groups.keys()) == 1       \
                    and plotted == False: # hull not empty  &  visible  &  not identical to layer below if layer below is plotted
                        self.graphics.draw_hull(
                                DATA,
                                category,
                                hirachie,
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
            DATA = self.single_values(   # plot individual points
                    data,
                    current_color,
                    hirachie,
                )
            return DATA, False



    def single_values(self, data, current_color, hirachie):
        point_list = np.full((1, 2), np.nan)     # [x, y][low, high][datapoints]

        for data_point in range(len(data)):
            coords = np.full((2, 2), np.nan)
            for dim, dimension in enumerate(['x','y']):
                coords[dim, :] = self.point_per_axis(data, data_point, dim)

            if np.any(coords[:] == None): 
                self.point_count['skipped'] += 1
                print("⚠ skipped Point")
            else:
                self.point_count['plotted'] += 1
                self.plot_point(coords, point_list, hirachie, current_color)
                point_list = np.vstack((point_list, coords[:,0]))  # add low
                if not np.all(pd.isna(coords[:, 1])):
                    point_list = np.vstack((point_list, coords[:,1]))   # add high if not empty in both dimensions

        point_list = point_list[1: ,:] # remove placeholder on beginning
        print("x: ", np.transpose(point_list[:, 0]))
        print("y: ", np.transpose(point_list[:, 1]))
        return point_list


    def point_per_axis(self, data, data_point, dim):
        point = self.absolute.property_availability(data, data_point, dim)
        if np.all(point == None): return None
        if self.relative.columns[dim] == [None]:               # specific data  (/density)
            return point
        else:
            point_rel = self.relative.property_availability(data, data_point, dim)
            if np.all(point_rel == None): return None
            point /= point_rel
            return point




    def plot_point(self, coords, point_list, hirachie, current_color):
        point_list = np.vstack((point_list, coords[:,0]))  # add low
        if not np.all(pd.isna(coords[:, 1])):
            point_list = np.vstack((point_list, coords[:,1]))   # add high if not empty in both dimensions

        # +  plot  + 
            if self.alpha_areas != None and self.alpha_areas > 0:
                if np.isnan(coords[0,1]): coords[0,1] = coords[0,0]
                if np.isnan(coords[1,1]): coords[1,1] = coords[1,0]

                self.graphics.draw_ellipses(
                        np.transpose(coords),
                        self.legend[-1],
                        hirachie    = hirachie,
                        scale       = 1.05,
                        plot_kwargs = {
                            'color':current_color,
                            'alpha':self.alpha_areas,
                            'picker':6,
                            },
                        value_ranges = True
                    )
        elif self.alpha_points != None and self.alpha_points > 0:
            self.graphics.plot(
                    coords[0, :],
                    coords[1, :],
                    color       = current_color,
                    alpha       = self.alpha_points,
                    hirachie    = hirachie,
                    legend_item = self.legend[-1]
                )

class parse_data():
    def __init__(self, frame, x_quantity, y_quantity, absolute = True):
        self.quantities = [ None ,  None ]
        self.labels     = [ None ,  None ]
        self.columns    = [[None], [None]]
        self.modes      = [ None ,  None ]
        for i, quantity in enumerate([x_quantity, y_quantity]):
            for axe in frame['axes']:
                if axe['name'] == quantity:
                    self.quantities[i]  = axe['name']
                    self.labels[i]      = axe['labels'][frame['language']]
                    self.columns[i]     = axe['columns']
                    self.modes[i]       = axe['mode']
                    break

        if absolute and None in self.quantities:
            raise ValueError("quantity not found. please check the config.json")
        if np.any(self.columns[:] == None):
            raise KeyError("at least one axes has no column assigned to it. please check 'axes' 'x'/'y-quantity' in the config.json")

        self.len_col = [len(self.columns[:][0]), len(self.columns[:][1])]


    def property_availability(self, data, data_point, dim):
        point  = np.full((2, self.len_col[dim]), np.nan)   #[low,high][column entries]
        index  = None
        column = self.columns[dim]
        for property, property_data in enumerate(column):
            if not pd.isna(data[property_data + ' low'].iloc[data_point]):
                point[0, property] = data[property_data + ' low' ].iloc[data_point].copy()  # low
                point[1, property] = data[property_data + ' high'].iloc[data_point].copy()  # high
        
        if not np.all(np.isnan(point[0, :])):
            if   self.modes[dim] == "max":      # & ignoring high value
                index = np.nanargmax(point[0, :])
            elif self.modes[dim] == "min":
                index = np.nanargmin(point[0, :]) 
            else:
                index = np.argmax(~np.isnan(point[0, :]))

            return point[:,index]

        
        else:
            return None