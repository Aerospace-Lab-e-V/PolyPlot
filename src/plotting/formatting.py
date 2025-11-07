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

def axe_label(sorted_data, axe):
    if sorted_data.relative.labels[axe] == None:
        label = f"{sorted_data.absolute.labels[axe]}"
    else:
        label = f"{sorted_data.absolute.labels[axe]}  / {sorted_data.relative.labels[axe]}"
    return label


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


class plot_size():
    def __init__(self, frame, DATA, marker):
        self.automatic_Display_Area_flag = frame["automatic_Display_Area_flag"]
        self.margin         = frame["automatic_Display_Area_margin"]
        self.DATA           = DATA
        self.x = dimension(self, 0, marker, frame["log_x_flag"], frame["x_lim"]) # § class §
        self.y = dimension(self, 1, marker, frame["log_y_flag"], frame["y_lim"]) # § class §

class dimension():
    def __init__(self, head, dim, marker, log_flag, limit):
        self.log_flag = log_flag
        self.space = 1
        if head.automatic_Display_Area_flag:
            # .ax.margins(x=automatic_Display_Area_margin, y=automatic_Display_Area_margin)
            self.plot_padding(float(np.nanmin(head.DATA[:,dim])), float(np.nanmax(head.DATA[:,dim])), head.margin, marker.limits(dim))
        else:
            self.low  = limit[dim][0]
            self.high = limit[dim][1]
        

    def plot_padding(self, min, max, margin, marker):
        low  = np.nanmin([marker[0], min])
        high = np.nanmax([marker[1], max])

        if self.log_flag:
            low_log  = np.log10(low )
            high_log = np.log10(high)
            diff = (high_log - low_log) * margin
            self.low  = 10 ** (low_log  - diff)
            self.high = 10 ** (high_log + diff)
            self.space = (np.log10(self.high) - np.log10(self.low)) / 100
        else:
            self.low  = low  - (high - low) * margin
            self.high = high + (high - low) * margin
            self.space = (self.high - self.low) /100
    
    def offset(self, pos, diff):
        if self.log_flag:
            return 10**(np.log10(pos) + self.space * diff)
        else:
            return pos + self.space * diff

        