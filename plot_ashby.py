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

from src.plot_utilities import (
    create_legend,
    draw_plot,
    plotting_presets,
    draw_guideline,
    draw_parallel_lines,
    draw_colored_areas,
    common_definitions,
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
    file_name = 'common_material_properties.xlsx'

    figure_type = 'presentation' #options are 'publication' or 'presentation'
    figure_size = (16,9) #width, height, in inches

    # quantities you would like to plot
    x_axis_quantity = 'Density'
    y_axis_quantity = "Young Modulus"

    # ~ Flag to plot in log-log space                           
    log_flag = True
    # log_y_flag = True     # ToDo

    # ~ x- and y-axes limits                                    
    automatic_Display_Area = False      # & not working yet
    x_lim = [10, 50000]
    y_lim = [1E-4,9E2]


    # ~ insert Guideline (linear)                               
    guideline_flag = True
    if guideline_flag:
        guideline = {
            'power':2,              # % Steigung          
            'y_intercept': 1E-4,    # % y-Achsenabschnitt 
            'x_lim':[1E-1, 1E8],    # x-limits of the guideline (not necessarily the figure x limits)
            'string':r"$\frac{E^{1/2}}{\rho} \equiv k$", # % Beschriftung 
            # 'string':r"$\frac{1}{(1+\nu)\rho} \equiv k$",
            # location of the annotation, (300,0.51) for poisson, (65, 2E-4) for stiffness
            'string_position': (65, 3) ,
            'linetype': 'k--'
            }
    
    # ~ insert horizontal & vertical lines                      
    parallel_lines_flag = True
    if parallel_lines_flag:
            parallel_lines = [{
                'direction' : 'x',
                'position' : 100,
                'color':'green',
                'linestyle':'--',
                'linewidth': 4
            },{
                'direction' : 'y',
                'position' : 1000,
                'color':'red',
                'linestyle':':',
                'linewidth': 4
            }]

    # ~ insert Marker                                           
    individual_material_flag = True
    if individual_material_flag:
        individual_materials = [{
            'Young Modulus':0.124E-2,
            'Poisson':0.45,
            'Density':400,
            'name':'Foam',
            'color':'b',
            'marker': '*'
            },{
            'Young Modulus':2.009,
            'Poisson':0.3,
            'Density':1300,
            'name':'PLA',
            'color':'r',
            'marker':'.'
            }
        ]
        marker_size = 400

    # ~ insert colored area                                           
    colored_area_flag = True
    if colored_area_flag:
        colored_areas = [{
            'x': [1, 100, 1000, 1   ],
            'y': [1, 1   , 1000, 1000],
            'color': "g",
            'alpha': 0.5        # ∈[0;1]
            },{
            'x': [1000, 100000, 100000, 1000],
            'y': [1,    1,      1000,   1000],
            'color': "r",
            'alpha': 0.2        # ∈[0;1]
            }
        ]

    # $ to edit hull colors & units go to:  plot_utilities.py line 303  
    # $ to edit legend go to:               plot_utilities.py line 203  
    # $ to edit grid go to:                 line 203                    
# ❗ end of USER INPUT                                                                                                                                      

    #%% General setup
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


    # Error handling about the colors dictionary
    if set(data.groupby('Category').groups) > set(material_colors):
        raise ValueError('You have material categories that have not been assigned a color. Please add a color to the material_colors dictionary (common_definitions function).')

    #%% Figure manipulation

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


        ax.set_xlabel(x_label)
        ax.set_ylabel(y_label)
    except:
        raise ValueError("Could not set correct x- and y-labels. \
            Make sure your x_axis_quantity and y_axis_quantity \
            have equivalent key-value pairs in the units dictionary (common_definitions function).")

    #set axes limits
    if automatic_Display_Area:
        if log_flag:
            ax.set(xlim=[   min(data[x_axis_quantity]) - abs(min(data[x_axis_quantity]))**0.2, 
                            max(data[x_axis_quantity]) + abs(max(data[x_axis_quantity]))**0.2], 
                   ylim=[   min(data[y_axis_quantity]) - abs(min(data[y_axis_quantity]))**0.2,
                            max(data[y_axis_quantity]) + abs(max(data[y_axis_quantity]))**0.2])
        else:
            ax.set(xlim=[   min(data[x_axis_quantity]) - abs(min(data[x_axis_quantity]))*0.2, 
                            max(data[x_axis_quantity]) + abs(max(data[x_axis_quantity]))*0.2], 
                   ylim=[   min(data[y_axis_quantity]) - abs(min(data[y_axis_quantity]))*0.2,
                            max(data[y_axis_quantity]) + abs(max(data[y_axis_quantity]))*0.2])
    else:
        ax.set(xlim=x_lim, ylim= y_lim)

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
        zorder = 0.5)

    #%% Data plotting

    # draw background colored areas

    if colored_area_flag:
        draw_colored_areas(
            colored_areas,
            ax = ax
        )

    #draw guideline
    if guideline_flag:
        draw_guideline(
                guideline,
                ax = ax,
                log_flag = log_flag,
                )


    if parallel_lines_flag:
        draw_parallel_lines(
                parallel_lines,
                ax = ax,
                )


    if (x_axis_quantity == 'Poisson difference') or (y_axis_quantity == 'Poisson difference'):

        data['Poisson difference high'] = 1/(1+data['Poisson low'])
        data['Poisson difference low'] = 1/(1+data['Poisson high'])

    draw_plot(
            data,
            x_axis_quantity,
            y_axis_quantity,
            ax,
            material_colors,
            )

    create_legend(
            material_classes = data.groupby('Category').groups.keys(),
            material_colors = material_colors,
            )

    # plot discrete materials
    if individual_material_flag:
        for individual_material in individual_materials:

            ax.scatter(
                individual_material[x_axis_quantity],
                individual_material[y_axis_quantity],
                c = individual_material['color'],
                edgecolors ='k',
                marker = individual_material['marker'],
                s = marker_size,
                )

plt.show()