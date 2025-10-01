import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import json

from src.import_data import(
        import_teable,
        import_excel
    )

from src.plot_utilities import (
        draw_plot,
    )

from src.plot_acessories import (
        draw_guideline,
        draw_colored_areas,
        create_marker,
        create_annotation,
    )
from src.formatting import(
        create_legend,
        watermark,
        plot_padding
    )



if __name__ == '__main__':
    with open('config.json', 'r', encoding="utf-8") as file:
        config = json.load(file)

        for frame in config["frames"]:
            print(f":::::::::::::::::::::: creating frame {config['frames'].index(frame) + 1} / {len(config['frames'])} ::::::::::::::::::::::")

            # : axes :
            quantities = [None, None]
            labels     = [None, None]
            columns    = [None, None]
            modes      = [None, None]
            for i, quantity in enumerate([frame["x_quantity"], frame["y_quantity"]]):
                for axe in frame['axes']:
                    if axe['name'] == quantity:
                        quantities[i] = axe['name']
                        labels[i]     = axe['labels'][frame['language']]
                        columns[i]    = axe['columns']
                        modes[i]      = axe['mode']
                        break
            if None in quantities:
                raise ValueError("quantity not found. please check the config.json")
            x_quantity, y_quantity = quantities
            x_label,    y_label    = labels
            x_column,   y_column   = columns
            x_mode,     y_mode     = modes

            if x_column == None or y_column == None:
                raise KeyError("at least one axes has no column assigned to it. please check 'axes' 'x'/'y-quntity' in the config.json")


            # : General setup :

            if frame["export_file_name"] != None:
                font_color = 'white'
            else:
                title = frame["title"]
                font_color = 'black'


            # Create figure & plotting presets
            figure_size = (frame["image_width"],frame["image_height"])
            fig, ax = plt.subplots(1,1, figsize=figure_size)
            if frame["legend_flag"] == True:
                plt.subplots_adjust(left=0.09, right=0.86)

            plt.rc('font', family='sans-serif')
            plt.rcParams.update({'font.sans-serif':'Arial'})
            plt.rcParams.update({'font.size': 18})
            plt.rc('text',usetex='False')


            if frame["teable_url"] != None:
                data = import_teable(frame["teable_url"], frame["API_Key"], columns, frame["layers"], frame["filter"])
            else:
                data = import_excel(frame["import_file_name"], frame["import_sheet"])
            if len(data) == 0:
                raise ValueError("No Vailid Data imported")


            # : Data plotting :
            DATA, legend_items, _ = draw_plot(
                    0,      # current_layer_number
                    None,   # current_master_layer_name
                    frame["layers"],
                    data,
                    columns,
                    modes,
                    [],     # legend_items
                    ax,
                    0,      # current_color
                    frame["material_colors"]
                )

            if not len(DATA) or not np.all(np.sum(~np.isnan(DATA), axis=0) >= 2):
                raise ValueError("No Data plotted. Please check the config.json. and your data source (Excel/Teable)")


            if frame["legend_flag"]:
                create_legend(
                    legend_items,
                    language = frame["language"],
                    material_colors = frame["material_colors"],
                    font_color = font_color
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
                if frame["automatic_Display_Area_flag"]:
                    draw_guideline(
                            frame["guidelines"],
                            x_min = np.nanmin(DATA[:,0])/2,
                            x_max = np.nanmax(DATA[:,0])*2,
                            y_min = np.nanmin(DATA[:,1])/2, # for vertical lines
                            y_max = np.nanmax(DATA[:,1])*2,
                            ax = ax,
                        )
                else:
                    if len(frame["guidelines"]) > 0:
                        draw_guideline(
                                frame["guidelines"],
                                x_min = x_lim[0],
                                x_max = x_lim[1],
                                y_min = y_lim[0],
                                y_max = y_lim[1],
                                ax = ax,
                            )
            except:
                print("❗ERROR drawing guidelines. Check config.json! continuing...")

            try:
                if len(frame["markers"]) > 0:
                    create_marker(
                        frame["markers"],
                        x_column,
                        y_column,
                        frame["marker_size"],
                        ax = ax
                    )
            except:
                print("❗ERROR plotting markers. Check config.json! continuing...")

            try:
                if len(frame["annotations"]) > 0:
                    create_annotation(
                        frame["annotations"],
                        frame["arrows"],
                        ax = ax
                    )
            except:
                print("❗ERROR printing annotations. Check config.json! continuing...")


            # : Figure manipulation :
            #set axes limits
            if frame["automatic_Display_Area_flag"]:
                # .ax.margins(x=automatic_Display_Area_margin, y=automatic_Display_Area_margin)
                x_lim = plot_padding(float(np.nanmin(DATA[:,0])), float(np.nanmax(DATA[:,0])), frame["log_x_flag"], frame["automatic_Display_Area_margin"])
                y_lim = plot_padding(float(np.nanmin(DATA[:,1])), float(np.nanmax(DATA[:,1])), frame["log_y_flag"], frame["automatic_Display_Area_margin"])
            else:
                x_lim = frame["x_lim"]
                y_lim = frame["y_lim"]
            ax.set(xlim=x_lim, ylim=y_lim)

            

            #toggle log in plot
            if frame["log_x_flag"]:
                ax.set_xscale('log')
            if frame["log_y_flag"]:
                ax.set_yscale('log')

            #add grid lines
            ax.grid(
                    which = 'major',
                    axis = 'both',
                    linestyle = '-.',
                    zorder = 0.5,
                )
            # .plt.tight_layout(pad=2.5)
            
            try: # set x- and y-labels
                ax.set_xlabel(x_label, color = font_color, fontsize = 18, labelpad=10)
                ax.set_ylabel(y_label, color = font_color, fontsize = 18, labelpad=5 )
            except:
                print("❗ERROR: Could not set correct x- and y-labels. continung...")

        # : export :
        ax.tick_params(colors=font_color, labelsize=15)
        ax.spines[:].set_color(font_color)
        if frame["export_file_name"] == None:
            plt.title(title, loc='center', size=40, pad=15)
            watermark(fig, alpha=0.7, pos=[0.72, 0.13], size=.13)
            
            plt.show()
        else:
            plt.savefig(os.path.join('export', frame["export_file_name"]), dpi=frame["image_dpi"], transparent=True)
            print(f"⇒ plot saved as ./export/{frame['export_file_name']}")