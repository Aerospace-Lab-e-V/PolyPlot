import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import json

from import_data import *
from plotting import *
from eventhandling import *


if __name__ == '__main__':
    print("\n\nstarting Ashby-Plot Generator            Ⓒ afffe18 @ RPS (ASL) 2025")


# : DATAFRAME                                                                           :
    dataframes = import_json('config.json')
    for dataframe_index, dataframe in enumerate(dataframes):
        print(f"\n::::::::::::::::::::::::::::::::::::: loading dataframe {dataframe_index + 1} of {len(dataframes)} :::::::::::::::::::::::::::::::::::::")

        language = dataframe.get('language',"en")
        resolution = dataframe.get('resolution', None)
        if resolution in [None,"svg"]:
            fileformat = "svg"
            resolution = 100
        else:
            fileformat = "png"
        image_ratio    = dataframe.get('image_ratio', 16/9)
        create_frames  = dataframe.get('create_all_frames', True)


# : FRAME                                                                               :
        for frame_index, frame in enumerate(dataframe['frames']):
            if not (create_frames == True or frame_index +1 in create_frames):
                continue

            print(f"\n::::::::::::::::::::::::::::  creating frame {frame_index + 1} of {len(dataframe['frames'])} {frame.get('name',"")} :::::::::::::::::::::::::::: \n")


            # : General setup :
            if frame.get('export_file_name',None) != None:
                font_color = 'white'
            else:
                font_color = 'black'

            figure_size = (10*image_ratio ,10)
            fig, ax = plt.subplots(1,1, figsize=figure_size)
            if frame.get('legend_flag',True) == True:
                plt.subplots_adjust(left=0.09, right=0.86)
            
            ax.tick_params(colors=font_color, labelsize=15)
            ax.spines[:].set_color(font_color)

            plt.rc('font', family='sans-serif')
            plt.rcParams.update({'font.sans-serif':'Arial'})
            plt.rcParams.update({'font.size': 18})
            # plt.rc('text',usetex='False')
            # plt.rcParams['mathtext.default'] = True
            if fileformat == "svg":
                plt.rcParams.update({"savefig.format":"svg"})

            # : class init :
            Graphics = plotter_graphics(ax, frame.get('algorithm',"cubic"))       # plot_hull.py   → legend()  # § class §

            Sorted_data = data_handling(Graphics, dataframe, frame)   # plot_utilities.py # § class §

            Marker = marker(frame.get('annotations',{}), dataframe['material_colors'], Sorted_data.absolute.quantities, Sorted_data.relative.quantities, ax)   # plot_acessories.py # § class §


            # : import data :
            if dataframe.get('teable_url',None) != None:
                data = import_teable(dataframe['teable_url'], dataframe['API_Key'], Sorted_data.absolute.columns, frame['layers'], frame.get('filter', None))
            elif dataframe.get('import_file_name',None) != None:
                data = import_excel(dataframe['import_file_name'], dataframe.get('import_sheet',0))
                filter_data(data, frame.get('filter', None))
            else:
                raise FileNotFoundError("no datasource selected. set teable_url or import_file_name in config")
            if len(data) == 0:
                raise ValueError("No Vailid Data imported")


            # : Data plotting :
            DATA, _ = Sorted_data.plot(data)

            if not len(DATA):
                raise ValueError("No Data plotted. Please check the config.json and your data source (Excel/Teable)")
            # print(DATA)

            # : plot from config :
            Plot_size = plot_size(frame, DATA, Marker) # § class §
                        

            if frame.get('legend_flag',True):
                Graphics.legend.create_legend(
                    language = language,
                    font_color = font_color,
                )

            try:
                if len(frame.get('colored_areas',{})) > 0:
                    draw_colored_areas(
                        frame['colored_areas'],
                        ax = ax
                    )
            except:
                print("❗ERROR drawing colored areas. Check config.json! continuing...")


            # try:
            draw_guideline(
                    frame.get('guidelines',{}),
                    x_min = Plot_size.x.low  /2,
                    x_max = Plot_size.x.high *2,
                    y_min = Plot_size.y.low  /2,
                    y_max = Plot_size.y.high *2,
                    font_color=font_color,
                    ax = ax,
                    )
            # except:
            #     print("❗ERROR drawing guidelines. Check config.json! continuing...")


            Marker.create_annotations(Plot_size)
            # Graphics.legend.format_label_pos(Plot_size)

            # : Figure manipulation :
            # ~ set axes limits 
            ax.set(xlim=[Plot_size.x.low, Plot_size.x.high], ylim=[Plot_size.y.low, Plot_size.y.high])        

            # ~ toggle log in plot 
            if frame.get('log_x_flag',False):
                ax.set_xscale('log')
            if frame.get('log_y_flag',False):
                ax.set_yscale('log')
            
            # ~ set x- and y-labels 
            ax.set_xlabel(axe_label(Sorted_data, 0), color = font_color, fontsize = 18, labelpad=10)
            ax.set_ylabel(axe_label(Sorted_data, 1), color = font_color, fontsize = 18, labelpad=5 )


            # ~ add grid lines 
            ax.grid(
                    which = 'major',
                    axis = 'both',
                    linestyle = '-.',
                )
            # .plt.tight_layout(pad=2.5)

            # ~ general info 
            print(f"skipped a total of {Sorted_data.point_count['skipped']} Datapoints due to missing entries.  {Sorted_data.point_count['plotted']} were plotted.")  # & low & high ≙ 2 Values

            # : export :
            if frame.get('export_file_name',None) == None:
                plt.title(frame.get('title',""), loc='center', size=40, pad=15)
                fig.canvas.manager.set_window_title(figurename(frame, dataframe_index, frame_index))
                watermark(fig, alpha=0.5, pos=[0.72, 0.13], size=.13)

                # + event handling +
                handler = pick_event_handing(fig, ax, Graphics)
                # +                +

                plt.show(block=False)
                print(f"⇒ plot displayed \n")

            else:
                # os.makedirs(dir, exist_ok=True)    
                plt.savefig(os.path.join('export', frame['export_file_name']), dpi=resolution/10, transparent=True) # & create directory
                print(f"⇒ plot saved as ./export/{frame['export_file_name']} \n")
                plt.close()
            
            plt.pause(.3)
            plt.show()