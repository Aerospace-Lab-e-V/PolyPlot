
import sklearn.preprocessing
import sklearn.pipeline
import scipy.spatial

from scipy.spatial import ConvexHull
from scipy.interpolate import splprep, splev
import alphashape
from shapely.geometry import Point


import numpy as np
import matplotlib.pyplot as plt
from matplotlib import patches
import matplotlib.colors as colors



def draw_ellipses(
        x,
        y,
        ax,
        data_type = 'ranges',
        scale = 1.02,
        plot_kwargs = None):


    center_x = (min(x) + max(x))/2
    center_y = (min(y) + max(y))/2

    r_x = (max(x) - min(x)) * scale
    r_y = (max(y) - min(y)) * scale

        #FIXME add log flag
        # ell_offset = ScaledTranslation(center_x, center_y,ax.transScale)
        # ell_tform = ell_offset + ax.transLimits + ax.transAxes
        # ell_scaling = ax.transScale.transform((r_x, r_y))


    if data_type == 'values':      
        plot_kwargs['facecolor'] = colors.to_rgba(  # & Übergeabeparameter
                plot_kwargs['color'],
                alpha=0.25
            )
        plot_kwargs['edgecolor'] = plot_kwargs['color']
        del plot_kwargs['color']
        del plot_kwargs['alpha']
        
        if r_x > r_y:
            angle = np.rad2deg(np.arctan((r_y)/(r_x)))
        else:
            angle = np.rad2deg(np.arctan((r_x)/(r_y)))
    else: # datatype == 'ranges'
        angle = 0

    if r_x == 0 or r_y == 0:
        plot_kwargs['linewidth'] = 5


    ellipse = patches.Ellipse(
            xy = (center_x,center_y),
            width = r_x,
            height = r_y,
            angle = angle,
            **plot_kwargs,
        )
    ax.add_patch(ellipse)


def calculate_hull(
        X, 
        scale=1.1, 
        n_interpolate=100, 
        interpolation="quadratic"):
    """
        Calculates a "smooth" hull around given points in `X`.
        The different settings have different drawbacks but the given defaults work reasonably well.
        Parameters
        ----------
        X : np.ndarray
            2d-array with 2 columns and `n` rows
        scale : float, optional
            padding strength, by default 1.1
        padding : str, optional
            padding mode, by default "scale"
        n_interpolate : int, optional
            number of interpolation points, by default 100
        interpolation : str or callable(ix,iy,x), optional
            interpolation mode, by default "quadratic_periodic"

        Inspired by: https://stackoverflow.com/a/17557853/991496
    """
    
    scaler = sklearn.pipeline.make_pipeline(
        # sklearn.preprocessing.MaxAbsScaler()
        # sklearn.preprocessing.RobustScaler(quantile_range = (25,75))
        # sklearn.preprocessing.PowerTransformer(method='box-cox'),
        # TODO: make a flag based on log-log scaling?
        sklearn.preprocessing.FunctionTransformer(np.log),
        sklearn.preprocessing.MinMaxScaler(feature_range = (0,1)),
        sklearn.preprocessing.StandardScaler(with_std=False),
        )
    points_scaled = scaler.fit_transform(X) * scale
    
    points_scaled = points_scaled[~np.isnan(points_scaled[:, 0])]
    points_scaled = points_scaled[~np.isnan(points_scaled[:, 1])]

    hull_scaled = scipy.spatial.ConvexHull(points_scaled, incremental=True)
    hull_points_scaled = points_scaled[hull_scaled.vertices]
    
    # old code (modified for log scaling)
    hull_points= np.concatenate([hull_points_scaled,hull_points_scaled[:1]])
    
    #stackoverflow code
    # hull_points = scaler.inverse_transform(hull_points_scaled)
    # hull_points = np.concatenate([hull_points, hull_points[:1]])
    
    # number of interpolated points
    nt = np.linspace(0, 1, n_interpolate)
    
    x, y = hull_points[:,0], hull_points[:,1]
    

    if interpolation == 'alpha':
        hashape.alphashape(hull_points, .02)
        coords = np.column_stack(hull_poly.exterior.xy)
        t = np.linspace(0, 1, len(x))
        tck, _ = splprep([coords[:,0], coords[:,1]], s=0.001, per=True)
        u_fine = np.linspace(0, 1, 500)
        x2, y2 = splev(u_fine, tck)
    elif interpolation == 'cubic':
        t = np.zeros(x.shape)
        t[1:] = np.sqrt((x[1:] - x[:-1])**2 + (y[1:] - y[:-1])**2)
        t = np.cumsum(t)
        t /= t[-1]
        x2 = scipy.interpolate.CubicSpline(t, x, bc_type="periodic")(nt)
        y2 = scipy.interpolate.CubicSpline(t, y, bc_type="periodic")(nt)


    X_hull = np.concatenate([x2.reshape(-1,1), y2.reshape(-1,1)], axis=1)
    
    X_hull = scaler.inverse_transform(X_hull)
    X_hull = np.exp(X_hull)
    X_hull = X_hull[~np.isnan(X_hull).any(axis=1)]
        

    return X_hull


def draw_hull(
        X, 
        scale=1.1, 
        n_interpolate=100, 
        interpolation="quadratic_periodic",
        plot_kwargs=None, 
        ax=None):
    """Uses `calculate_hull` to draw a hull around given points.
        Parameters
        ----------
        X : np.ndarray
            2d-array with 2 columns and `n` rows
        scale : float, optional
            padding strength, by default 1.1
        n_interpolate : int, optional
            number of interpolation points, by default 100
        interpolation : str or callable(ix,iy,x), optional
            interpolation mode, by default "quadratic_periodic"
        plot_kwargs : dict, optional
            `matplotlib.pyplot.plot` kwargs, by default None
        ax : `matplotlib.axes.Axes`, optional
            [description], by default None
    """

    if plot_kwargs is None:
        plot_kwargs = {}

    line = False
    for i in [0,1]:
        if min(X[:,i]) == max(X[:,i]):
            line = True
            print(f"X: {X}")
        
    if np.sum(~np.isnan(X).any(axis=1)) <= 3 or line == True: #if you have fewer than three data points, you cannot form a convex hull
        draw_ellipses(
            x = X[:,0],
            y = X[:,1],
            ax = ax,
            scale = scale,
            plot_kwargs = plot_kwargs
            )
    else:
        X_hull = calculate_hull(
                X,
                scale=scale,
                n_interpolate=n_interpolate,
                interpolation=interpolation
            )
        # ell_tform = ax.transScale + ax.transLimits + ax.transAxes
        # new_hull = ell_tform.transform(X_hull)
        
        if ax is None:
            ax= plt.gca()
            
        plt.fill(
            X_hull[:,0],
            X_hull[:,1],
            **plot_kwargs,
            )
        
        try: 
            del plot_kwargs['hatch']
        except:
            pass
        
        plt.plot(
            X_hull[:,0],
            X_hull[:,1],
            **plot_kwargs
            )



def draw_rounded_hull(X, padding=0.1, line_kwargs=None, ax=None):
    """
        Plots a convex hull around points with rounded corners and a given padding.

        Parameters
        ----------
        X : np.array
            2d array with two columns and n rows
        padding : float, optional
            padding between hull and points, by default 0.1
        line_kwargs : dict, optional
            line kwargs (used for `matplotlib.pyplot.plot` and `matplotlib.patches.Arc`), by default None
        ax : matplotlib.axes.Axes, optional
            axes to plat on, by default None
    """

    default_line_kwargs = dict(
        color="black",
        linewidth=1
    )
    if line_kwargs is None:
        line_kwargs = default_line_kwargs
    else:
        line_kwargs = {**default_line_kwargs, **line_kwargs}

    if ax is None:
        ax = plt.gca()

    hull = scipy.spatial.ConvexHull(X)
    hull_points = X[hull.vertices]

    hull_points = np.concatenate([hull_points[[-1]], hull_points, hull_points[[0]]])

    diameter = padding * 2
    for i in range(1, hull_points.shape[0] - 1):

        # line
        
        # source: https://stackoverflow.com/a/1243676/991496
        
        norm_next = np.flip(hull_points[i] - hull_points[i + 1]) * [-1, 1]
        norm_next /= np.linalg.norm(norm_next)

        norm_prev = np.flip(hull_points[i - 1] - hull_points[i]) * [-1, 1]
        norm_prev /= np.linalg.norm(norm_prev)

        # plot line
        line = hull_points[i:i+2] + norm_next * diameter / 2
        ax.plot(line[:,0], line[:,1], **line_kwargs) 

        # arc
        angle_next = np.rad2deg(np.arccos(np.dot(norm_next, [1,0])))
        if norm_next[1] < 0:
            angle_next = 360 - angle_next

        angle_prev = np.rad2deg(np.arccos(np.dot(norm_prev, [1,0])))
        if norm_prev[1] < 0:
            angle_prev = 360 - angle_prev
            
            
        ell_tform = ax.transScale + ax.transLimits + ax.transAxes

        arc = patches.Arc(
            hull_points[i], 
            diameter, diameter,
            angle=0,
            fill=False,
            theta1=angle_prev,
            theta2=angle_next,
            transform = ell_tform,
            **line_kwargs)

        ax.add_patch(arc)

if __name__ == '__main__':

    import numpy as np
    import matplotlib.pyplot as plt
    from matplotlib import patches

    np.random.seed(42)
    
    
    # sample data for technical ceramics
    # X = np.zeros(shape = (10,2))
    # X[:,1] = np.array([400, 280, 300, 215, 600, 472, 310, 460, 413,720]).transpose()
    # X[:,0] = np.array([2350, 3000, 3000, 3500, 15300, 2550, 3290, 3210, 3980, 15900]).transpose()
    
    # sample data for foams 
    X = np.zeros(shape = (12,2))
    X[:,1] = np.array([0.0003,0.023,0.001,0.004,0.08,0.2,0.001,0.08,0.003,0.012,0.2,0.48]).transpose()
    X[:,0] = np.array([16,36,38,75,78,170,35,70,70,115,165,470]).transpose()
    
    
    
    fig, ax = plt.subplots(1,1, figsize=(5,5))
    ax.scatter(X[:,0], X[:,1])
    # draw_rounded_hull(X, padding=0.1, ax = ax)
    draw_hull(
        X,
        ax = ax,
        scale = 1.1,
        interpolation = 'cubic'
        )
    ax.loglog()
    # ax.set(xlim=[-1,2], ylim= [-1,2])
    # fig.savefig("_out/test.png")