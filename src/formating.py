import os
import matplotlib.pyplot as plt
from matplotlib import patches
from PIL import Image
import numpy as np


def create_legend(
        legend_items,
        material_colors,
        font_color
        ):
    '''
        Creates a legend located outside the plot bounding box. Currently
        set to the top of the plot.

        Important references:
            Extracting an iterable from a pandas groupby:
                https://stackoverflow.com/questions/28844535/python-pandas-groupby-get-list-of-groups
            Manual legend creation:
                https://stackoverflow.com/questions/39500265/how-to-manually-create-a-legend
            Plotting legends outside the bounding box:
                https://stackoverflow.com/questions/4700614/how-to-put-the-legend-outside-the-plot

        Parameters
        ----------
        material_classes : Iterable list or dict_keys object
            The list of different material classes you wish to display in the
            legend. Commonly found via data.groupby("Category").groups.keys()
        material_colors : DICT
            Dictionary that references the material class to the color you
            wish to display it as.
        Returns
        -------
        None.
    '''
    handles = []

    for item in legend_items:
        patch = patches.Patch(
            color = material_colors[item],
            label = item
            )
        handles.append(patch)
    
    plt.legend(
            handles=handles,
            bbox_to_anchor = (1, 0, 1, 1),
            title="Materialien:",
            loc  = 'center left',
            labelspacing = 1.05,
            mode = 'expand',
            borderaxespad = 0,
            fontsize = 15,
            labelcolor = font_color,
            facecolor = 'none',
            edgecolor = 'none',
            ncol = 1,
            # draggable = True
        )
    # plt.legend(        # ° legend above
    #     handles=handles,
    #     bbox_to_anchor = (0, 1.02, 1, 0.2),
    #     loc  = 'lower left',        # & put Legend right of the plot
    #     mode = 'expand',
    #     borderaxespad = 0,
    #     fontsize = 15,
    #     labelcolor = font_color,
    #     facecolor = 'none',
    #     edgecolor = 'none',
    #     ncol = 5)


def watermark(fig, alpha, pos, size):
    logo =  os.path.join(
            os.getcwd(),
            'media',
            'watermark.png'
        )

    # change alpha value
    img = Image.open(logo).convert("RGBA")
    r, g, b, a = img.split()
    a = a.point(lambda x: int(x * alpha))
    img = Image.merge("RGBA", (r, g, b, a))
    img_array = np.array(img)

    logo_ax = fig.add_axes([pos[0], pos[1], size, size], anchor='SE', zorder=101, )
    logo_ax.imshow(img_array)
    logo_ax.axis('off')


def plotting_presets(figure_type:str = 'publication'):
    '''
        Creates plotting presets for font size, marker size,
        and other quality of life presets.


        Parameters
        ----------
        figure_type : str
            Type of figure you would like to create.
            Options are 'publication' or 'presentation'
            Toggles different presets like font family, font size, etc.

        Returns
        -------
        None.
    '''
    #Graphs in a separate window (run in Spyder)
    if 'SPY_PYTHONPATH' in os.environ:
        # see https://stackoverflow.com/questions/32538758/nameerror-name-get-ipython-is-not-defined
        # running inside spyder!
        #Graphs in a separate window
        from IPython import get_ipython
        get_ipython().run_line_magic('matplotlib', 'qt')
        #Graphs inline (ala Jupyter notebook)
        #get_ipython().run_line_magic('matplotlib', 'inline')
    if figure_type.lower() == 'publication':
        # Plot with serif, Times New Roman Font
        plt.rc('font', family='serif')
        plt.rc('font', serif='Times New Roman')
        plt.rcParams.update({'font.size': 10})
        plt.rc('text', usetex='True')
    elif figure_type.lower() == 'presentation':
        #Plot with sans serif, Arial font
        plt.rc('font', family='sans-serif')
        plt.rcParams.update({'font.sans-serif':'Arial'})
        plt.rcParams.update({'font.size': 18})
        plt.rc('text',usetex='False')
    else:
        raise(ValueError,'Options for plotting_presets are publication or presentation')

    # Use Latex to render all fonts (this may interfere with the svg font encoding)
    # plt.rc('text', usetex='True')
    #Use no svg font encoding such that they can be imported as text into inkscape
    # FIXME grab the stack overflow link for this.
    plt.rcParams['svg.fonttype'] = 'none'
    #Modify marker size to make them readable
    plt.rcParams['lines.markersize'] = 10