import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import json

from import_data import *
from plotting import *
from eventhandling import *


if __name__ == '__main__':
    print("\n\nstarting Ashby-Plot Generator       Ⓒ afffe 2025")

    frames = import_json('config.json')

    for frame in frames:
        print(f"\n:::::::::::::::::::::::::::: creating frame {frames.index(frame) + 1} of {len(frames)} :::::::::::::::::::::::::::: \n")

        # : General setup :
        if frame["export_file_name"] != None:
            font_color = 'white'
        else:
            title = frame["title"]
            font_color = 'black'

        figure_size = (frame["image_width"],frame["image_height"])
        fig, ax = plt.subplots(1,1, figsize=figure_size)
        if frame["legend_flag"] == True:
            plt.subplots_adjust(left=0.09, right=0.86)
        
        ax.tick_params(colors=font_color, labelsize=15)
        ax.spines[:].set_color(font_color)

        plt.rc('font', family='sans-serif')
        plt.rcParams.update({'font.sans-serif':'Arial'})
        plt.rcParams.update({'font.size': 18})
        # plt.rc('text',usetex='False')
        # plt.rcParams['mathtext.default'] = 'regular'


        # ~ import data 
        if frame["teable_url"] != None:
            data = import_teable(frame["teable_url"], frame["API_Key"], columns, frame["layers"], frame["filter"])
            # & filter
        else:
            data = import_excel(frame["import_file_name"], frame["import_sheet"])
        if len(data) == 0:
            raise ValueError("No Vailid Data imported")


        # : class init :
        graphics = plotter_graphics(ax,     # plot_hull.py # § class §
                                    frame["algorithm"])

        sorted_data = data_handling(graphics = graphics, # plot_utilities.py # § class §
                                    frame    = frame)

        marker = marker(frame["annotations"],   # plot_acessories.py # § class §
                        frame["material_colors"],
                        sorted_data.absolute.quantities,
                        ax)

        # : Data plotting :
        DATA, _ = sorted_data.plot(data)

        if not len(DATA):
            raise ValueError("No Data plotted. Please check the config.json and your data source (Excel/Teable)")
        # print(DATA)
        # : plot from config :
        plot_size = plot_size(frame, DATA, marker) # § class §


        if frame["legend_flag"]:
            graphics.legend.create_legend(
                language = frame["language"],
                font_color = font_color,
            )

        try:
            if len(frame["colored_areas"]) > 0:
                draw_colored_areas(
                    frame["colored_areas"],
                    ax = ax
                )
        except:
            print("❗ERROR drawing colored areas. Check config.json! continuing...")


        try:
            draw_guideline(
                    frame["guidelines"],
                    x_min = plot_size.x.low  /2,
                    x_max = plot_size.x.high *2,
                    y_min = plot_size.y.low  /2,
                    y_max = plot_size.y.high *2,
                    ax = ax,
                )
        except:
            print("❗ERROR drawing guidelines. Check config.json! continuing...")


        marker.create_annotation(plot_size)


        # : Figure manipulation :
        # ~ set axes limits 
        ax.set(xlim=[plot_size.x.low, plot_size.x.high], ylim=[plot_size.y.low, plot_size.y.high])        

        # ~ toggle log in plot 
        if frame["log_x_flag"]:
            ax.set_xscale('log')
        if frame["log_y_flag"]:
            ax.set_yscale('log')
        
        # ~ set x- and y-labels 
        ax.set_xlabel(axe_label(sorted_data, 0), color = font_color, fontsize = 18, labelpad=10)
        ax.set_ylabel(axe_label(sorted_data, 1), color = font_color, fontsize = 18, labelpad=5 )


        # ~ add grid lines 
        ax.grid(
                which = 'major',
                axis = 'both',
                linestyle = '-.',
            )
        # .plt.tight_layout(pad=2.5)

        # ~ general info 
        print(f"skipped a total of {sorted_data.point_count['skipped']} Datapoints due to missing entries.  {sorted_data.point_count['plotted']} were plotted.")  # & low & high ≙ 2 Values

        # : export :
        if frame["export_file_name"] == None:
            plt.title(title, loc='center', size=40, pad=15)
            fig.canvas.manager.set_window_title(frame.get('name', f"Figure {frames.index(frame) + 1}"))
            watermark(fig, alpha=0.7, pos=[0.72, 0.13], size=.13)

            # + event handling +
            handler = pick_event_handing(fig, ax, graphics)
            # +                +

            plt.show(block=False)
            print(f"⇒ plot displayed \n")
        else:
            plt.savefig(os.path.join('export', frame["export_file_name"]), dpi=frame["image_dpi"], transparent=True)
            print(f"⇒ plot saved as ./export/{frame['export_file_name']} \n")
            plt.close()
        plt.pause(.3)
        plt.show()