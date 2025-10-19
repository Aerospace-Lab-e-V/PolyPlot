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


class plotter_graphics():
    def __init__(self, ax):
        self.point_count    = [0,0]        # [skipped, plotted]
        self.hulls          = []
        self.splines        = []
        self.ellipses       = []
        self.points         = []
        self.ax = ax
    
    def __str__(self):
        print(f"Hulls:    {self.hulls   }")
        print(f"Splines:  {self.splines }")
        print(f"Ellipses: {self.ellipses}")
        print(f"Points:   {self.points  }")
        return ""


    def add_point_skipped(self):
        self.point_count[0] +=1
    def add_point_plotted(self):
        self.point_count[1] +=1
    
    def get_point_count(self):
        return self.point_count
    



    

    # : plot content :
    def plot(self, x, y, color, marker, alpha, picker=8):
        points = self.ax.plot(
                        x,
                        y,
                        color  = color,
                        marker = 'o',
                        alpha  = alpha,
                        picker = picker,
                        zorder = 5,
                    )
        self.points.append(points)


    def draw_hull(
            self,
            X,      # [:,x/y]
            scale=1.1, 
            n_interpolate=100, 
            interpolation="quadratic_periodic",  # & remoove
            plot_kwargs={}, 
        ):
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

        for pos, entry in enumerate(X):     # replace nan with value incase of range in onlY one dimension
            if np.isnan(entry[0]):          
                entry[0] = X[pos-1,0]
            elif np.isnan(entry[1]):
                entry[1] = X[pos-1,1]
        
        # print(np.transpose(X))

        line = True
        angle = np.atan2(X[0,1]-X[1,1], X[0,0]-X[1,0])
        for pos, entry in enumerate(X):          # checks if all entries are in one line which makes calculating a hull impossible
            if abs(angle - np.atan2(X[0,1]-X[pos,1], X[0,0]-X[pos,0])) > 0.01 and np.all(X[0,:] != X[pos,:]):  # not same angle and not identical
                line = False
                break

        if line == True:
            self.draw_ellipses(
                    X,
                    scale = scale,
                    plot_kwargs = plot_kwargs
                )
        else:
            X_hull = self.calculate_hull(
                    X,
                    scale=scale,
                    n_interpolate=n_interpolate,
                    interpolation=interpolation
                )
            # ell_tform = ax.transScale + ax.transLimits + ax.transAxes
            # new_hull = ell_tform.transform(X_hull)
            
                
            patch = plt.fill(
                X_hull[:,0],
                X_hull[:,1],
                **plot_kwargs,
                )
                        
            try: 
                del plot_kwargs['hatch']
            except:
                pass
            
            spline = plt.plot(
                X_hull[:,0],
                X_hull[:,1],
                **plot_kwargs
                )
            
            self.hulls.append(patch)
            self.splines.append(spline)




    def draw_ellipses(
            self,
            X,      # [:,x/y]
            scale = 1.02,
            value_ranges=False,
            plot_kwargs = None
        ):

        angle = np.rad2deg(np.arctan2(X[1,1]-X[0,1], X[1,0]-X[0,0]))

        center_x = (np.max(X[0,0]) + np.min(X[1,0])) / 2
        center_y = (np.max(X[0,1]) + np.min(X[1,1])) / 2
        center = [center_x, center_y]

        r_x = (np.max(X[:,0]) - np.min(X[:,0]))
        r_y = (np.max(X[:,1]) - np.min(X[:,1]))

        r_1 = np.sqrt(r_x**2 + r_y**2) * scale

        if not value_ranges:
            r_2 = r_1 / 8
            ellipse = patches.Ellipse(
                xy = center,
                width = r_1,
                height = r_2,
                angle = angle,
                **plot_kwargs,
            )
            ax.add_patch(ellipse)

        else:
            ellipse = self.ax.plot(X[:,0], X[:,1], linewidth=5, **plot_kwargs)
        
        self.ellipses.append(ellipse)
        # print(f"angle: {angle} - center: ({center_x}|{center_y}) - r_x/y: {r_x}, {r_y}  - r_1/2: {r_1}, {r_2}  | {X[0,1],X[1,1], X[0,0],X[1,0]}")

            

    def calculate_hull(
            self,
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