import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import json

from import_data import(
        import_teable,
        import_excel,
        fill_config_with_default,
    )
from plotting import *
from eventhandling import *


if __name__ == '__main__':
    with open('config.json', 'r', encoding="utf-8") as file:
        config = json.load(file)

        for frame in config["frames"]:
            print(f"\n\n:::::::::::::::::::::::::::: creating frame {config['frames'].index(frame) + 1} of {len(config['frames'])} :::::::::::::::::::::::::::: \n")

            fill_config_with_default(frame)


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
            plt.rc('text',usetex='False')

            # ~ import data 
            if frame["teable_url"] != None:
                data = import_teable(frame["teable_url"], frame["API_Key"], columns, frame["layers"], frame["filter"])
            else:
                data = import_excel(frame["import_file_name"], frame["import_sheet"])
            if len(data) == 0:
                raise ValueError("No Vailid Data imported")


            # : class init :
            graphics = plotter_graphics(ax, 
                                        frame["algorithm"])
            sorted_data = data_handling(graphics= graphics, 
                                        frame   = frame,
                                        )
            # : Data plotting :
            DATA, _ = sorted_data.plot(data)

            if not len(DATA):
                raise ValueError("No Data plotted. Please check the config.json and your data source (Excel/Teable)")
            print(DATA)


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

            # & fkt to get x/y, min/max and check if empty → guideline & automatic display area
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
            # ~ set axes limits 
            if frame["automatic_Display_Area_flag"]:
                # .ax.margins(x=automatic_Display_Area_margin, y=automatic_Display_Area_margin)
                x_lim = plot_padding(float(np.nanmin(DATA[:,0])), float(np.nanmax(DATA[:,0])), frame["log_x_flag"], frame["automatic_Display_Area_margin"])
                y_lim = plot_padding(float(np.nanmin(DATA[:,1])), float(np.nanmax(DATA[:,1])), frame["log_y_flag"], frame["automatic_Display_Area_margin"])
            else:
                x_lim = frame["x_lim"]
                y_lim = frame["y_lim"]
            ax.set(xlim=x_lim, ylim=y_lim)
            

            # ~ toggle log in plot 
            if frame["log_x_flag"]:
                ax.set_xscale('log')
            if frame["log_y_flag"]:
                ax.set_yscale('log')

            # ~ add grid lines 
            ax.grid(
                    which = 'major',
                    axis = 'both',
                    linestyle = '-.',
                )
            # .plt.tight_layout(pad=2.5)
            
            try: # ~ set x- and y-labels 
                ax.set_xlabel(x_label, color = font_color, fontsize = 18, labelpad=10)
                ax.set_ylabel(y_label, color = font_color, fontsize = 18, labelpad=5 )
            except:
                print("❗ERROR: Could not set correct x- and y-labels. continung...")

            # ~ general info 
            skipped_points, plotted_points = sorted_data.point_count
            print(f"skipped a total of {skipped_points} Datapoints due to missing entries.  {plotted_points} were plotted.")  # & low & high ≙ 2 Values

            # : export :
            if frame["export_file_name"] == None:
                plt.title(title, loc='center', size=40, pad=15)
                fig.canvas.manager.set_window_title(frame.get('# name', f"Figure {config['frames'].index(frame) + 1}"))
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