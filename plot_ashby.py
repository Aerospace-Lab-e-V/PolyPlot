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

from src.plot_utilities import (
    create_legend,
    draw_plot,
    plotting_presets,
    draw_guideline,
    draw_colored_areas,
    common_definitions,
    create_marker,
    create_annotation,
    )


if __name__ == '__main__':
    #%% USER INPUTS (everything you will need to change *should* be here)
    # FIXME To-do:
        # Error handling/format checking for:
        #   file type
        # Create inputs for:
            # guideline power (figure out what to call that)
            # guideline x_limits and y_intercept
            # guideline string


# ❗ start of USER INPUT                                                                                                                                      
    # file with all of your material data (must be xlsx)
    file_name = 'MatWeb_materials_export.xlsx'

    figure_type = 'presentation' #options are 'publication' or 'presentation'
    figure_size = (16,9) #width, height, in inches

    # & Titel

    # quantities you would like to plot
    x_axis_quantity = 'Deflection Temperature at 18 MPa 264 psi'
    y_axis_quantity = 'Tensile Strength at Break'

    layers = {           # different hirachie layers the Materials are stored in the excel
            'name': 'Material',
            'visible': True,
            'alpha': 0.3
        },{
            'name': 'Hersteller',
            'visible': False,
            'alpha': 0.4
        }

    # ~ Flag to plot in log-log space                           
    log_flag = False
    # log_y_flag = True                # & Semilog

    # ~ x- and y-axes limits                                    
    automatic_Display_Area_flag = True      # & not working yet
    automatic_Display_Area_margin = .065
    x_lim = [0, 200]
    y_lim = [0, 120]


    # ~ insert Guideline (linear)                               
    guideline_flag = False
    if guideline_flag:
        guidelines = [{
                'x': 100,       # % Point x-coordinate | vertical   if y & m are none 
                'y': 20,        # % Point y-coordinate | horizontal if x & m are none 
                'm': 1,         # % incline                                           
                'linestyle': '--',
                'color':'green',
                'linewidth': 4,
                'string':r"$\frac{E^{1/2}}{\rho} \equiv k$", # % Beschriftung 
                'string_position': (300, 0.5)
            },
        ]

    # ~ insert Marker                                           
    marker_flag = False
    if marker_flag:
        markers = [{
                'Young Modulus':0.124E-2,
                'Poisson':0.45,
                'Density':400,
                'name':'Foam',
                'color':'b',
                'marker': '*',
                'size_factor':1
            },{
                'Young Modulus':2.009,
                'Poisson':0.3,
                'Density':1300,
                'name':'PLA',
                'color':'r',
                'marker':'.',
                'size_factor':1
            }
        ]
        marker_size = 400

    # ~ insert annotations                                          
    annotation_flag = False
    if annotation_flag:
        annotations = [{
                'text': 'PETG',
                'fontsize': 20,
                'txt_color': 'black',
                'tip_xy': [2000, 4],
                'txt_xy': [1700, 3],
                'arrow': 1
            },
        ]
        arrows = [{ #1
                'width': 3,
                'shrink': 0.1,     # shrink = 0: no arrow  |  ∈[0;1]
                'facecolor': 'black',
                'headlength': 10,
                'headwidth': 10,
            },
        ]

    # ~ insert colored area                                           
    colored_area_flag = False
    if colored_area_flag:
        colored_areas = [{
                'x': [1, 100, 1000, 1000, 1   ],
                'y': [1, 1  , 100,  1000, 1000],
                'color': "g",
                'alpha': 0.5        # ∈[0;1]
            },{
                'x': [1000, 100000, 100000, 1000],
                'y': [1,    1,      1000,   1000],
                'color': "r",
                'alpha': 0.2        # ∈[0;1]
            }
        ]
    # ~ export
    export_transparent_flag = True
    if export_transparent_flag:
        export_file_name = "Ashbyplot_transparent"
        font_color = 'white'
    else:
        font_color = 'black'
    # $ to edit hull colors & units go to:  plot_utilities.py line 303  
    # $ to edit legend go to:               plot_utilities.py line 203  
    # $ to edit grid go to:                 line 203                    
# ❗ end of USER INPUT                                                                                                                                      

    # : General setup :
    # Create dictionaries with common units bases etc.
    units, material_colors = common_definitions()

    # Set up baseline plot formatting
    plotting_presets(figure_type)

    #load data
    file_path = os.path.join(
        os.getcwd(),
        'material_properties',
        file_name,
        )

    data = pd.read_excel(
        file_path
        )

    # : Figure manipulation :

    #Create figure
    fig, ax = plt.subplots(1,1, figsize=figure_size)

    # set x- and y-labels
    try:
        if y_axis_quantity == 'Poisson difference':
            y_label = r'Hyperbolic Poisson Ratio $\frac{1}{1+\nu}$, '+ units[y_axis_quantity]
        else:
            y_label = y_axis_quantity + '  [' + units[y_axis_quantity] + ']'

        if x_axis_quantity == 'Poisson difference':
            x_label = r'Hyperbolic Poisson Ratio $\frac{1}{1+\nu}$, '+ units[x_axis_quantity]
        else:
            x_label = x_axis_quantity + '  [' + units[x_axis_quantity]  + ']'


        ax.set_xlabel(x_label, color = font_color)
        ax.set_ylabel(y_label, color = font_color)
    except:
        raise ValueError("Could not set correct x- and y-labels. Make sure your x_axis_quantity and y_axis_quantity have equivalent key-value pairs in the units dictionary (common_definitions function).")


    #toggle log in plot     # & fix log parameter for semilog 
    if log_flag:
        ax.loglog()
    # if log_x_flag:
    #     ax.set_xscale('log')
    # if log_y_flag:
    #     ax.set_yscale('log')

    #add grid lines
    # https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.grid.htmls
    ax.grid(
            which = 'major',
            axis = 'both',
            linestyle = '-.',
            zorder = 0.5,
        )


    #set axes limits
    if automatic_Display_Area_flag:
        ax.margins(x=automatic_Display_Area_margin, y=automatic_Display_Area_margin)
    else:
        ax.set(xlim=x_lim, ylim=y_lim)
    
    
    # : Data plotting :
    current_layer = 0
    current_color = 0
    draw_plot(
            0,      # current_layer_number
            None,   # current_master_layer_name
            layers,
            data,
            x_axis_quantity,
            y_axis_quantity,
            ax,
            0,      # current_color
            material_colors
            )
    # draw background colored areas
    if colored_area_flag:
        draw_colored_areas(
            colored_areas,
            ax = ax
        )

    #draw guideline
    if guideline_flag:
        if automatic_Display_Area_flag:
            # draw_guideline(
            #         guidelines,
            #         x_min = data[x_axis_quantity + ' low' ].min(skipna=True)/2,
            #         x_max = data[x_axis_quantity + ' high'].max(skipna=True)*2,
            #         y_min = data[y_axis_quantity + ' low' ].min(skipna=True)/2,
            #         y_max = data[y_axis_quantity + ' high'].max(skipna=True)*2,
            #         ax = ax,
            #     )
            draw_guideline(guidelines, 0, 500, 0, 500, ax)
        else:
            draw_guideline(
                    guidelines,
                    x_min = x_lim[0],
                    x_max = x_lim[1],
                    y_min = y_lim[0],
                    y_max = y_lim[1],
                    ax = ax,
                )

    if (x_axis_quantity == 'Poisson difference') or (y_axis_quantity == 'Poisson difference'):
        data['Poisson difference high'] = 1/(1+data['Poisson low' ])
        data['Poisson difference low' ] = 1/(1+data['Poisson high'])


    create_legend(
            material_classes = data.groupby('Material').groups.keys(),
            material_colors = material_colors,
            font_color = font_color
            )

    if marker_flag:
        create_marker(
            markers,
            x_axis_quantity,
            y_axis_quantity,
            marker_size,
            ax = ax
        )

    if annotation_flag:
        create_annotation(
            annotations,
            arrows,
            ax = ax
        )

    if export_transparent_flag:
        ax.tick_params(colors=font_color)     # Achsenbeschriftungen
        ax.spines['bottom'].set_color(font_color)
        ax.spines['left'].set_color(font_color)
        ax.spines['top'].set_color(font_color)
        ax.spines['right'].set_color(font_color)
        ax.title.set_color(font_color)

        plt.savefig(export_file_name, dpi=300, transparent=True) # & add number of datapoints to title
        
    plt.show()

