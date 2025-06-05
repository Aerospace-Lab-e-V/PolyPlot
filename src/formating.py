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
        bbox_to_anchor = (0, 1.02, 1, 0.2),
        loc  = 'lower left',        # & put Legend right of the plot
        mode = 'expand',
        borderaxespad = 0,
        fontsize = 15,
        labelcolor = font_color,
        facecolor = 'none',
        edgecolor = 'none',
        ncol = 5)


def watermark(fig, alpha):
    logo =  os.path.join(
            os.getcwd(),
            'media',
            'watermark.png'
        )

    img = Image.open(logo).convert("RGBA")
    r, g, b, a = img.split()
    a = a.point(lambda x: int(x * alpha))  # z.B. 40% Sichtbarkeit
    img = Image.merge("RGBA", (r, g, b, a))
    img_array = np.array(img)

    logo_ax = fig.add_axes([0.75, 0.11, 0.15, 0.15], anchor='SE', zorder=101)
    logo_ax.imshow(img_array)
    logo_ax.axis('off') 
