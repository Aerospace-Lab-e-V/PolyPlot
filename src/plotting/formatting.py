import os
import matplotlib.pyplot as plt
from matplotlib import patches
from PIL import Image
import numpy as np


class legend():
    def __init__(self):       
        self.handles = []
        self.map = {}

    def append_category(self, item, color):
        patch = patches.Patch(
                color   = color,
                label   = item,
            )
        self.handles.append(patch)
        self.map[item] = [patch]

    def append_content(self, category, item):
        self.map[category].append(item)


    def create_legend(self, language, font_color):
        match language:
            case "de":
                title = "Materialien:"
            case _:
                title = "materials:"

        self.legend = plt.legend(
                handles=self.handles,
                bbox_to_anchor = (1, 0, 1, 1),
                title= title,
                loc  = 'center left',
                labelspacing = 1.05,
                mode = 'expand',
                fontsize = 15,
                alignment = 'left',
                labelcolor = font_color,
                facecolor = 'none',
                edgecolor = 'none',
                ncol = 1,
                # draggable = True
            )

        for entry in self.legend.legend_handles: # edit copy
            entry.set_picker(True)

        plt.setp(self.legend.get_title(), color=font_color)  # legend title color

        # ° legend above
            # plt.legend(        
            #     handles=handles,
            #     bbox_to_anchor = (0, 1.02, 1, 0.2),
            #     loc  = 'lower left',
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


def plot_padding(low, high, log_flag, margin):
    if log_flag:
        low_log  = np.log10(low )
        high_log = np.log10(high)
        diff = (high_log - low_log) * margin
        lower_limit = 10 ** (low_log  - diff)
        upper_limit = 10 ** (high_log + diff)
    else:
        lower_limit = low  - (high - low) * margin
        upper_limit = high + (high - low) * margin
    return [lower_limit, upper_limit]