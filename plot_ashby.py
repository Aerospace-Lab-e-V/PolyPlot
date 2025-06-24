'''
    This script will plot various material properties in an 'Ashby-type' way (
    i.e., convex hulls surrounding points of certain classes).

    Input file format: one excel file, with either material property ranges or
    single values defined.

    Dependencies:
        files: plot_convex_hull.py
            rotation_aware_annotation.py
            plot_utilities.py
            math_utilities.py
        python modules:
            os (pre-installed)
            pandas
            numpy
            matplotlib
            scipy
            sklearn
'''
import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import json

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
        plotting_presets,
    )


if __name__ == '__main__':
    with open('config.json', 'r', encoding="utf-8") as file:
        config = json.load(file)
        for frame in config["frames"]:
            # : General setup :

            if frame["export_file_name"] != None:
                font_color = 'white'
            else:
                title = "Ashbyplot"
                font_color = 'black'

            plotting_presets(figure_type = 'presentation')
            figure_size = (frame["plot_width"],frame["plot_height"])

            #load data
            data = pd.read_excel(
                os.path.join(
                    os.getcwd(),
                    'material_properties',
                    frame["file_name"],
                    ),
                sheet_name = frame["sheet"]
                )

            #Create figure
            fig, ax = plt.subplots(1,1, figsize=figure_size)
            plt.subplots_adjust(left=0.09, right=0.86)

            # fig = plt.figure(figsize=figure_size)                      # hulls in right plot ??
            # ax  = plt.subplot2grid((1,11), (0,0), colspan=10)
            # legend_sp = plt.subplot2grid((1,11), (0,10), colspan=1)    # hide spines, ticks, 
            # & other formats: title , legend at side


        # : Data plotting :
            DATA, legend_items, _ = draw_plot(
                    0,      # current_layer_number
                    None,   # current_master_layer_name
                    frame["layers"],
                    frame["filter"],
                    frame["filter_keys"],
                    data,
                    frame["x_axes_quantities"],
                    frame["y_axes_quantities"],
                    [],     # legend_items
                    ax,
                    0,      # current_color
                    frame["material_colors"]
                )

            if len(DATA):

                if frame["legend_flag"]:
                    create_legend(
                        legend_items,
                        material_colors = frame["material_colors"],
                        font_color = font_color
                    )


                if frame["colored_areas_flag"]:
                    draw_colored_areas(
                        frame["colored_areas"],
                        ax = ax
                    )

                if frame["guideline_flag"]:
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
                        draw_guideline(
                                frame["guidelines"],
                                x_min = x_lim[0],
                                x_max = x_lim[1],
                                y_min = y_lim[0],
                                y_max = y_lim[1],
                                ax = ax,
                            )


                if frame["marker_flag"]:
                    create_marker(
                        frame["markers"],
                        frame["x_axes_quantities"],
                        frame["y_axes_quantities"],
                        frame["marker_size"],
                        ax = ax
                    )

                if frame["annotation_flag"]:
                    create_annotation(
                        frame["annotations"],
                        frame["arrows"],
                        ax = ax
                    )



            # : Figure manipulation :
                #set axes limits
                if frame["automatic_Display_Area_flag"]:
                    x_lim = frame["x_lim"]
                    y_lim = frame["y_lim"]
                    # .ax.margins(x=automatic_Display_Area_margin, y=automatic_Display_Area_margin)
                    x_low  = float(np.nanmin(DATA[:,0]))
                    x_high = float(np.nanmax(DATA[:,0]))
                    y_low  = float(np.nanmin(DATA[:,1]))
                    y_high = float(np.nanmax(DATA[:,1]))
                    x_lim[0] = x_low  - (x_high - x_low) * frame["automatic_Display_Area_margin"]    # & edit for log
                    x_lim[1] = x_high + (x_high - x_low) * frame["automatic_Display_Area_margin"]
                    y_lim[0] = y_low  - (y_high - y_low) * frame["automatic_Display_Area_margin"]
                    y_lim[1] = y_high + (y_high - y_low) * frame["automatic_Display_Area_margin"]
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

                # set x- and y-labels
                try:
                    # .x_label = x_label + '  [' + units[x_label]  + ']'
                    # .y_label = y_label + '  [' + units[y_label]  + ']'

                    ax.set_xlabel(frame["x_label"], color = font_color)
                    ax.set_ylabel(frame["y_label"], color = font_color)
                except:
                    raise ValueError("Could not set correct x- and y-labels. Make sure your x_axis_quantity and y_axis_quantity have equivalent key-value pairs in the units dictionary (common_definitions function).")
            else:
                raise ValueError("No Data plotet. Are the filters named correctly?")

            # : export :
            if frame["export_file_name"] != None:
                
                ax.tick_params(colors=font_color)     # Achsenbeschriftungen
                ax.spines[:].set_color(font_color)

                plt.savefig(os.path.join('export', frame["export_file_name"]), dpi=300, transparent=True)
            else:
                plt.title(title, loc='left', size=40)
                watermark(fig, alpha=0.7, pos=[0.72, 0.13], size=.13)

            plt.show()

