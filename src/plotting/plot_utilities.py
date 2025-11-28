import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import colors
from types import SimpleNamespace
from termcolor import (colored, cprint)


from .plot_hull import plotter_graphics

class data_handling(): 
    def __init__(self, graphics:type, dataframe:pd.DataFrame, frame:dict):
        self.graphics        = graphics
        self.absolute        = parse_data(dataframe, frame, frame["x_quantity"], frame["y_quantity"])
        self.relative        = parse_data(dataframe, frame, frame.get("x_rel_quantity",None), frame.get("y_rel_quantity",None))
        self.frame           = frame
        self.material_colors = dataframe['material_colors']
        self.layers          = frame['layers']
        self.layer_names     = []
        self.len_layers      = len(self.layers) 
        self.point_count     = {'skipped':0, 'plotted':0}     # [skipped, plotted]
        self.alpha_points    = self.layers[-1].get('alpha_points', None)
        self.alpha_areas     = self.layers[-1].get('alpha_areas',  None)

        self.material_colors['default'] = self.material_colors.get('default', '#000000')


    def plot(self, data:pd.DataFrame) -> np.ndarray:
        self.absolute.clear_unused_columns(data)
        self.relative.clear_unused_columns(data)

        return self.recursive_preparation(
                            data,
                            current_layer_number = 0,
                            hirachie             = [],
                            legend_item          = "default",
                            current_color        = self.material_colors['default'],
                        )

    def recursive_preparation(self, data:pd.DataFrame, current_layer_number:int, hirachie:list, legend_item:str, current_color:str) -> np.ndarray:
        # +       recursive repetition       +
        if current_layer_number < self.len_layers - 1:
            try:
                layer_name           = self.layers[current_layer_number]['name']
                self.layer_names.append(layer_name)
                layer_whitelist_flag = self.layers[current_layer_number].get('whitelist_flag',False)
                layer_whitelist      = self.layers[current_layer_number].get('whitelist',[])
                layer_alpha          = self.layers[current_layer_number].get('alpha',None)
                combined_DATA        = np.full((1, 2), np.nan)      # & leer erstelen?
            except:
                raise KeyError(f"could not import layer {current_layer_number +1}. Check config.json!")

            for category, material_data in data.groupby(layer_name):
                if pd.isna(category): category == None
                plotted = False            
                # print("====== Layer ", current_layer_number, ": ", category, "  (", layer_name, ") ======") 

                if (category  in layer_whitelist and layer_whitelist_flag == True) or \
                (category not in layer_whitelist and layer_whitelist_flag == False):
                    if category in self.material_colors and category != legend_item and layer_alpha:   # ° color & legend entry handling
                        current_color = self.material_colors [category]
                        legend_item = category
                        if current_color != None: 
                            self.graphics.legend.append_category(category, current_color)

                    DATA, plotted = self.recursive_preparation(
                            material_data,
                            current_layer_number + 1,
                            hirachie + [category],
                            legend_item,
                            current_color,
                        )

                    # print(DATA)
                    # print("plotted: ", plotted, "  -  keys: ", data.groupby(layer_name).groups.keys())
                    if DATA.shape[0] > 1 and layer_alpha != None and 0 < layer_alpha <= 1          \
                    and current_color != None and plotted == False: # hull not empty  &  visible  &  not identical to layer below if layer below is plotted
                        self.graphics.draw_hull(
                                DATA,
                                hirachie,
                                legend_item,
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
                    hirachie,
                    legend_item,
                    current_color,
                )
            return DATA, False



    def single_values(self, data:pd.DataFrame, hirachie:list, legend_item:str, current_color:str) -> pd.DataFrame:
        point_list = np.full((1, 2), np.nan)     # [x, y][low, high][datapoints]

        for data_point in range(len(data)):
            coords = np.full((2, 2), np.nan)
            for dim, dimension in enumerate(['x','y']):
                coords[dim, :] = self.point_per_axis(data, data_point, dim)

            if np.any(np.isnan(coords[:,0])): 
                self.point_count['skipped'] += 1
                # print("⚠ skipped Point")
            else:
                self.point_count['plotted'] += 1
                self.plot_point(coords, point_list, hirachie, legend_item, current_color)
                point_list = np.vstack((point_list, coords[:,0]))  # add low
                if not np.all(pd.isna(coords[:, 1])):
                    point_list = np.vstack((point_list, coords[:,1]))   # add high if not empty in both dimensions

        point_list = point_list[1: ,:] # remove placeholder on beginning
        # print("x: ", np.transpose(point_list[:, 0]))
        # print("y: ", np.transpose(point_list[:, 1]))
        return point_list


    def point_per_axis(self, data:pd.DataFrame, data_point:pd.DataFrame, dim:int) -> pd.DataFrame:
        point = self.absolute.property_availability(data, data_point, dim)
        if np.all(point == None): return None

        if self.relative.columns[dim] != [None]:               # specific data  (/density)
            point_rel = self.relative.property_availability(data, data_point, dim)
            if np.all(point_rel == None): return None
            point /= point_rel

        return point



    def plot_point(self, coords:list, point_list:list, hirachie:list, legend_item:str, current_color:str) -> None:
        point_list = np.vstack((point_list, coords[:,0]))  # add low
        if not np.all(pd.isna(coords[:, 1])):
            point_list = np.vstack((point_list, coords[:,1]))   # add high if not empty in both dimensions

        # +  plot  + 
            if self.alpha_areas != None and 0 < self.alpha_areas <= 1 and current_color != None:
                if np.isnan(coords[0,1]): coords[0,1] = coords[0,0]
                if np.isnan(coords[1,1]): coords[1,1] = coords[1,0]

                self.graphics.draw_ellipses(
                        np.transpose(coords),
                        hirachie    = hirachie,
                        legend_item = legend_item,
                        scale       = 1.05,
                        plot_kwargs = {
                            'color':current_color,
                            'alpha':self.alpha_areas,
                            'picker':6,
                            },
                        value_ranges = True
                    )
        elif self.alpha_points != None and 0 < self.alpha_points <= 1 and current_color != None:
            self.graphics.plot(
                    coords[0, :],
                    coords[1, :],
                    color       = current_color,
                    alpha       = self.alpha_points,
                    hirachie    = hirachie,
                    legend_item = legend_item,
                )




class parse_data():
    def __init__(self, dataframe:pd.DataFrame, frame:dict, x_quantity:str, y_quantity:str) -> None:
        import_quantities = [x_quantity, y_quantity]
        self.quantities = [ None ,  None ]
        self.labels     = [ None ,  None ]
        self.columns    = [[None], [None]]
        self.modes      = [ None ,  None ]

        for dim, quantity in enumerate(import_quantities):
            for axe in dataframe['axes']:
                if axe['name'] == quantity:
                    self.quantities[dim]  = axe['name']
                    self.labels[dim]      = axe['labels'][dataframe['language']]
                    self.columns[dim]     = axe['columns']
                    self.modes[dim]       = axe.get('mode',"default")
                    break
            
            if self.quantities[dim] != import_quantities[dim]:
                raise KeyError(f"{["x","y"][dim]}-quantity '{import_quantities[dim]}' not found. please check the config.json and datasource")

    def clear_unused_columns(self, data:pd.DataFrame) -> None:
        for dim in [0,1]:
            for column in self.columns[dim][:]:
                if column != None and f"{column} low" not in data.columns:
                    self.columns[dim].remove(column)
                    cprint(f"❗'{column}' does not exist in your dataset but is set in '{self.quantities[dim]}'","yellow")
        self.len_col = [len(self.columns[:][0]), len(self.columns[:][1])]


    def property_availability(self, data:dict, data_point:pd.DataFrame, dim:int) -> pd.DataFrame | None:
        point  = np.full((2, self.len_col[dim]), np.nan)   #[low,high][column entries]
        index  = None
        column = self.columns[dim]
        for property, property_data in enumerate(column):
            if not pd.isna(data[property_data + ' low'].iloc[data_point]):
                point[0, property] = data[property_data + ' low' ].iloc[data_point].copy()  # low
                point[1, property] = data.get(property_data + ' high', np.nan).iloc[data_point].copy()  # high
        
        if not np.all(np.isnan(point[0, :])):
            if   self.modes[dim] == "max":
                # index = np.nanargmax(np.nanmax(point, axis=0))    # & RuntimeWarning: All-NaN slice encountered
                index = np.nanargmax(np.hstack([point[0,:],point[1,:]]))
                print(index, point,  np.hstack([point[0,:],point[1,:]]), np.size(point, axis=1))
                index = index-np.size(point, axis=1) if index >= np.size(point, axis=1) else index
                print(index)
            elif self.modes[dim] == "min":
                index = np.nanargmin(          point[0, :]) 
            else:
                index = np.argmax(~np.isnan(   point[0, :]))

            return point[:,index]

        else:
            return None