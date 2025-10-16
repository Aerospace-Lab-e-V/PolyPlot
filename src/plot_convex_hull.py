
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
        X,
        ax,
        scale = 1.02,
        plot_kwargs = None):

    center = (X[0,:] + X[1,:]) /2

    r_x = (X[1,0] - X[0,0])
    r_y = (X[1,1] - X[0,1])

    r_1 = np.sqrt(r_x**2 + r_y**2) * scale
    r_2 = r_1 / 4
       
    angle = np.rad2deg(np.arctan2(r_y, r_x))
    print(f"angle: {angle} - r_x/y: {r_x}, {r_y}  - r_1/2: {r_1}, {r_2}")
 
    if r_x == 0 or r_y == 0:
        plot_kwargs['linewidth'] = 5

    ellipse = patches.Ellipse(
            xy = center,
            width = r_1,
            height = r_2,
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
    for pos, entry in enumerate(X):
        if np.isnan(entry[0]):
            entry[0] = X[pos-1,0]
        elif np.isnan(entry[1]):
            entry[1] = X[pos-1,1]

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
    # np.linalg.matrix_rank(points_scaled - points_scaled[0]) < 2 → check if in a line
    
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
        hull_polynome = alphashape.alphashape(hull_points, .02)
        coords = np.column_stack(hull_polynome.exterior.xy)
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

    if plot_kwargs is None: # & ?
        plot_kwargs = {}

    line = False
    for i in [0,1]:     # check if all entries a in one straight line which makes hul creation impossible # & check only horizontal / vertical
        if min(X[:,i]) == max(X[:,i]):
            line = True
            print(f"X: {X}")
        
    # if np.sum(~np.isnan(X).any(axis=1)) <= 3 or line == True: #if you have fewer than three data points, you cannot form a convex hull
    if X.shape[0] <= 2 or line == True:
        draw_ellipses(
            X,
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