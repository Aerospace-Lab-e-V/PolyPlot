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
        draw_plot,
        plotting_presets,
    )

from src.plot_acessories import (
        draw_guideline,
        draw_colored_areas,
        create_marker,
        create_annotation,
    )
from src.formating import(
        create_legend,
        watermark

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
    file_name = 'MatWeb_materials_export_tom_finaleDaten.xlsx'
    sheet = 0

    figure_type = 'presentation' #options are 'publication' or 'presentation'
    figure_size = (16,9) #width, height, in inches

    # & Titel

    # quantities you would like to plot
    x_axes_quantities = ['Deflection Temperature at 1.8 MPa 264 psi']
    x_label = x_axes_quantities[0]
    y_axes_quantities = ["Tensile Strength Yield", "Tensile Strength Ultimate", "Tensile Strength at Break", "Tensile Strength"]
    y_label = y_axes_quantities[0]
    legend_flag = True

    # ~ layer                                                   
    layers = {           # different hirachie layers the Materials are stored in the excel  # & still very buggy (3. & 2.if!1.)
            'name': 'Gruppe',
            'visible': True,
            'whitelist_flag': True,    # False ≙ blacklist 
            'whitelist': ['PA'],
            'alpha': 0.4
        },{
            'name': 'Material',
            'visible': True,
            'whitelist_flag': False,    # False ≙ blacklist 
            'whitelist': [None],
            'alpha': 0.4
        },{
            'name': 'Hersteller',
            'visible': False,
            'whitelist_flag': False,    # False ≙ blacklist 
            'whitelist': [None],
            'alpha': 0.4,
        },{
            'name': None,       # individual Datapoints
            'visible': True,
            'whitelist_flag': False,    # ignore
            'whitelist': [None],        # ignore
            'alpha': 0.3, 
        }

    # ~ filter                                                  
    # & filter_flag
    filter_flag = False
    if filter_flag:
        filter = {     # & little groups aren't plotted correctly
            "name": "available",
            "states": [True, False, None]
        },
    else:
        filter = None       # & performance skip filtercheck when getting data if flag == False

    filter_keys = {
        "state":   True,
        "entries": ["y","Y","✔","true", "True" ]
    },{
        "state":   False,
        "entries": ["n","N","✘","false","False"]
    },{
        "state":   None,
        "entries": ["", " ","-","none", "None" ]
    }

    # ~ log-Space                                               
    log_x_flag = False                          # & incompatible with: guideline, areas(?)
    log_y_flag = False                          # & other gridlines

    # ~ x- and y-axes limits                                    
    automatic_Display_Area_flag   = True
    automatic_Display_Area_margin = .1
    x_lim = [20, 250]
    y_lim = [20, 150]


    # ~ insert Guideline (linear)                               
    guideline_flag = False
    if guideline_flag:
        guidelines = [{
                'x': 100,       # % Point x-coordinate | vertical   if m = True  
                'y': 80,        # % Point y-coordinate | horizontal if m = False 
                'm': .4,        # % incline                                      
                'linestyle': '--',
                'color':'green',
                'linewidth': 4,
                'fontsize': 22,
                'string':r"$\frac{Latex}{Test} = ✔$",        # bottom left corner in (x,y) + padding
                'string_above': True,   # text above ore below line
                'string_padding': 4     # distance form line
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
                'arrow':0           # None ≙ no arrow
            },
        ]
        arrows = [{
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
                'x': [0, 300, 300, 80,  80, 0  ],
                'y': [0,   0,  50, 50, 200, 200],
                'color': "r",
                'alpha': 0.2        # ∈[0;1]
            # },{
            #     'x': [0, 100,  100, 0],
            #     'y': [1,   100, 50, 5],
            #     'color': "g",
            #     'alpha': 0.2        # ∈[0;1]
            },
        ]
    # ~ units (LaTeX)                                                
    units = {
        'Density': 'kg/m$^3$',
        "Tensile Strength Yield": 'MPa',
        "Young Modulus": 'GPa',
        "Fracture Toughness": r"MPa$\sqrt{\text{m}}$",
        "Thermal Conductivity": r"W/m$\cdot$K",
        "Thermal expansion": "1$^-6$/m",
        "Resistivity": r"$\Omega \cdot$m",
        "Poisson": "-",
        "Poisson difference": "-",
        "Melting Point": "°C",
        "Deflection Temperature at 1.8 MPa 264 psi": "°C",
        }
    # ~ colors                                                      
    material_colors = {
        'ABS': '#219DD3',	
        'PA12':'#7BBFD9', 	
        'PEEK':'#D69D20',	
        'PLA': '#E3B768',	
        'PET': '#3BD420',	
        'PETG':'#85E064',	
        'PPSU':'#B52ED6',	
        'PPS': '#CE82E0',

        'PA11':'#219DD3',	
        'POM': '#7BBFD9',	
        'PP':  '#D69D20',	
        'PVDF':'#E3B768',	
        'PC':  '#3BD420',	
        'PEI': '#85E064',	
        'PA6': '#B52ED6',	
        'PPA': '#CE82E0',

        'PA': "red",
        'PET':"black",
        'default':"white",
        }
# ~ export                                                          
    export_transparent_flag = False
    if export_transparent_flag:
        export_file_name = "Ashbyplot_transparent"
        font_color = 'white'
    else:
        font_color = 'black'
# ❗ end of USER INPUT                                                                                                                                      

    # : General setup :
    # Set up baseline plot formatting
    plotting_presets(figure_type)

    #load data
    data = pd.read_excel(
        os.path.join(
            os.getcwd(),
            # 'ashby-diagramme-1',
            'material_properties',
            file_name,
            ),
        sheet_name = sheet
        )

    #Create figure
    fig, ax = plt.subplots(1,1, figsize=figure_size)
    # & other formats: title , legend at side


# : Data plotting :
    DATA, legend_items, _ = draw_plot(
            0,      # current_layer_number
            None,   # current_master_layer_name
            layers,
            filter,
            filter_keys,
            data,
            x_axes_quantities,
            y_axes_quantities,
            [],     # legend_items
            ax,
            0,      # current_color
            material_colors
        )

    if len(DATA):

        if legend_flag:
            create_legend(
                legend_items,
                material_colors = material_colors,
                font_color = font_color
            )


        if colored_area_flag:
            draw_colored_areas(
                colored_areas,
                ax = ax
            )

        if guideline_flag:
            if automatic_Display_Area_flag:
                draw_guideline(
                        guidelines,
                        x_min = np.nanmin(DATA[:,0])/2,
                        x_max = np.nanmax(DATA[:,0])*2,
                        y_min = np.nanmin(DATA[:,1])/2, # for vertical lines
                        y_max = np.nanmax(DATA[:,1])*2,
                        ax = ax,
                    )
            else:
                draw_guideline(
                        guidelines,
                        x_min = x_lim[0],
                        x_max = x_lim[1],
                        y_min = y_lim[0],
                        y_max = y_lim[1],
                        ax = ax,
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



    # : Figure manipulation :
        #set axes limits
        if automatic_Display_Area_flag:
            # ax.margins(x=automatic_Display_Area_margin, y=automatic_Display_Area_margin)
            x_low  = float(np.nanmin(DATA[:,0]))
            x_high = float(np.nanmax(DATA[:,0]))
            y_low  = float(np.nanmin(DATA[:,1]))
            y_high = float(np.nanmax(DATA[:,1]))
            x_lim[0] = x_low  - (x_high - x_low) * automatic_Display_Area_margin    # & edit for log
            x_lim[1] = x_high + (x_high - x_low) * automatic_Display_Area_margin
            y_lim[0] = y_low  - (y_high - y_low) * automatic_Display_Area_margin
            y_lim[1] = y_high + (y_high - y_low) * automatic_Display_Area_margin
        ax.set(xlim=x_lim, ylim=y_lim)
        

         #toggle log in plot
        if log_x_flag:
            ax.set_xscale('log')
        if log_y_flag:
            ax.set_yscale('log')

        #add grid lines
        ax.grid(
                which = 'major',
                axis = 'both',
                linestyle = '-.',
                zorder = 0.5,
            )

        # set x- and y-labels
        try:
            x_label = x_label + '  [' + units[x_label]  + ']'
            y_label = y_label + '  [' + units[y_label]  + ']'

            ax.set_xlabel(x_label, color = font_color)
            ax.set_ylabel(y_label, color = font_color)
        except:
            raise ValueError("Could not set correct x- and y-labels. Make sure your x_axis_quantity and y_axis_quantity have equivalent key-value pairs in the units dictionary (common_definitions function).")
    else:
        raise ValueError("No Data plotet. Are the filters named correctly?")

# : export :
    if export_transparent_flag:
        watermark(fig, alpha=0.7)
        
        ax.tick_params(colors=font_color)     # Achsenbeschriftungen
        ax.spines[:].set_color(font_color)

        plt.savefig(os.path.join('export', export_file_name), dpi=300, transparent=True)

    plt.show()

