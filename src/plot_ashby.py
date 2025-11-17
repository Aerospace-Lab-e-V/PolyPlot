import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import json

from import_data import *
from plotting import *
from eventhandling import *


if __name__ == '__main__':
    print("\n\nstarting Ashby-Plot Generator            Ⓒ afffe 2025")

    dataframes = import_json('config.json')
    for dataframe_index, dataframe in enumerate(dataframes):
        print(f"\n::::::::::::::::::::::::::::::::::::: loading dataframe {dataframe_index + 1} of {len(dataframes)} :::::::::::::::::::::::::::::::::::::")

        for frame_index, frame in enumerate(dataframe['frames']):
            if not (dataframe.get('create_all_frames', True) == True or frame_index in dataframe.get('create_all_frames', True)):
                continue

            name = frame.get('name',None)
            if name != None:
                name = f":  {name}"
            print(f"\n::::::::::::::::::::::::::::  creating frame {frame_index + 1} of {len(dataframe['frames'])}{name} :::::::::::::::::::::::::::: \n")


            # : General setup :
            if frame['export_file_name'] != None:
                font_color = 'white'
            else:
                title = frame['title']
                font_color = 'black'

            figure_size = (frame['image_width'],frame['image_height'])
            fig, ax = plt.subplots(1,1, figsize=figure_size)
            if frame['legend_flag'] == True:
                plt.subplots_adjust(left=0.09, right=0.86)
            
            ax.tick_params(colors=font_color, labelsize=15)
            ax.spines[:].set_color(font_color)

            plt.rc('font', family='sans-serif')
            plt.rcParams.update({'font.sans-serif':'Arial'})
            plt.rcParams.update({'font.size': 18})
            # plt.rc('text',usetex='False')
            # plt.rcParams['mathtext.default'] = 'regular'


            # ~ import data 
            if dataframe['teable_url'] != None:
                data = import_teable(dataframe['teable_url'], dataframe['API_Key'], columns, frame['layers'], frame['filter'])
                # & filter
            else:
                data = import_excel(dataframe['import_file_name'], dataframe['import_sheet'])
            if len(data) == 0:
                raise ValueError("No Vailid Data imported")


            # : class init :
            Graphics = plotter_graphics(ax, frame['algorithm'])       # plot_hull.py   → legend()  # § class §

            Sorted_data = data_handling(Graphics, dataframe, frame)   # plot_utilities.py # § class §

            Marker = marker(frame['annotations'], dataframe['material_colors'], Sorted_data.absolute.quantities, ax)   # plot_acessories.py # § class §

            # : Data plotting :
            DATA, _ = Sorted_data.plot(data)

            if not len(DATA):
                raise ValueError("No Data plotted. Please check the config.json and your data source (Excel/Teable)")
            # print(DATA)

            # : plot from config :
            Plot_size = plot_size(frame, DATA, Marker) # § class §
                        

            if frame['legend_flag']:
                Graphics.legend.create_legend(
                    language = frame['language'],
                    font_color = font_color,
                )

            try:
                if len(frame['colored_areas']) > 0:
                    draw_colored_areas(
                        frame['colored_areas'],
                        ax = ax
                    )
            except:
                print("❗ERROR drawing colored areas. Check config.json! continuing...")


            try:
                draw_guideline(
                        frame['guidelines'],
                        x_min = Plot_size.x.low  /2,
                        x_max = Plot_size.x.high *2,
                        y_min = Plot_size.y.low  /2,
                        y_max = Plot_size.y.high *2,
                        ax = ax,
                    )
            except:
                print("❗ERROR drawing guidelines. Check config.json! continuing...")


            Marker.create_annotations(Plot_size)
            # Graphics.legend.format_label_pos(Plot_size)

            # : Figure manipulation :
            # ~ set axes limits 
            ax.set(xlim=[Plot_size.x.low, Plot_size.x.high], ylim=[Plot_size.y.low, Plot_size.y.high])        

            # ~ toggle log in plot 
            if frame['log_x_flag']:
                ax.set_xscale('log')
            if frame['log_y_flag']:
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
            if frame['export_file_name'] == None:
                plt.title(title, loc='center', size=40, pad=15)
                fig.canvas.manager.set_window_title(figurename(frame, dataframe_index, frame_index))
                watermark(fig, alpha=0.5, pos=[0.72, 0.13], size=.13)

                # + event handling +
                handler = pick_event_handing(fig, ax, Graphics)
                # +                +

                plt.show(block=False)
                print(f"⇒ plot displayed \n")
            else:
                if frame.get('image_dpi',None) in [None, 'svg']:
                    plt.rcParams.update({"savefig.format":"svg"})
                    frame['image_dpi'] = 100
                plt.savefig(os.path.join('export', frame['export_file_name']), dpi=frame['image_dpi'], transparent=True)
                print(f"⇒ plot saved as ./export/{frame['export_file_name']} \n")
                plt.close()
            
            plt.pause(.3)
            plt.show()