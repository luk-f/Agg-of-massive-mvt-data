import pandas as pd
import numpy as np
from scipy.spatial import voronoi_plot_2d

import sys
import os
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))

from aggofmassivemvtdata.tools_lib import tools_lib

import matplotlib.pyplot as plt

import os
import settings
from aggofmassivemvtdata.utils import random_color
from aggofmassivemvtdata.voronoi_map.part3_voronoi import build_voronoi_map_from_centroids

import datetime




if __name__ == "__main__":

    # parameters
    maxRadius = 10
    region = "liege"
    # region = "wallonie"
    apply_algo_3 = True
    number_dec = str(maxRadius-int(maxRadius))[2:]
    # TODO warning for folder_name
    if number_dec:
        folder_name = f"{region}_0{number_dec}"
    else:
        folder_name = f"{region}_{int(maxRadius)}"
    if apply_algo_3:
        folder_name += "_algo_3"
    start_date = datetime.datetime(2021, 1, 4, 0 ,0, 0)
    end_date = datetime.datetime(2021, 1, 15, 0 ,0, 0)

    # load data
    date_csv_str = f'{start_date.strftime("%Y_%m_%d_%H_%M_%S")}__{end_date.strftime("%Y_%m_%d_%H_%M_%S")}.csv'

    path_data = os.path.join(settings.LOCAL_DATA_CLUSTER_ANDRIENKO, folder_name)

    df_stops = pd.read_csv(os.path.join(path_data, date_csv_str), index_col=0)
    df_centroids = pd.read_csv(os.path.join(path_data, f"centroids_{date_csv_str}"), index_col=0)

    # compute border limit
    lat_min = df_stops.LATITUDE.min()
    lat_max = df_stops.LATITUDE.max()
    lon_min = df_stops.LONGITUDE.min()
    lon_max = df_stops.LONGITUDE.max()

    points = df_centroids.to_numpy()

    voronoi = build_voronoi_map_from_centroids(points, maxRadius, lat_min, lat_max, lon_min, lon_max)
    
    # print(voronoi.vertices)
    # print(voronoi.ridge_vertices)
    
    import matplotlib.lines as lines
    import plotly.graph_objects as go
    import folium
    
    m = folium.Map()
    
    # print(df_stops[['LATITUDE', 'LONGITUDE']].to_numpy().T)
    print(df_stops[['LATITUDE', 'LONGITUDE']].dtypes)
    for _, centroid_number in df_centroids.iterrows():
        # print(centroid_number[['LATITUDE', 'LONGITUDE']])
        folium.CircleMarker(location=(centroid_number['LATITUDE'], 
                                      centroid_number['LONGITUDE']))
        
    m
    
    exit()

    fig = plt.figure(figsize=(10, 10))
    ax = fig.add_subplot(111)

    for centroid_number in df_stops['CENTROID_NUMBER'].unique():
        # print(group_points)
        df_tmp = df_stops[df_stops['CENTROID_NUMBER'] == centroid_number]
        ax.scatter(df_tmp['LATITUDE'], df_tmp['LONGITUDE'], 
        # cmap=plt.cm.nipy_spectral,
        color=random_color(as_str=False, alpha=1), marker='.',
        alpha=0.5, s=0.1)

    fig = voronoi_plot_2d(voronoi, ax=ax, line_alpha=0.5)
    
    plt.xlim((df_stops['LATITUDE'].min(), df_stops['LATITUDE'].max()))
    plt.ylim((df_stops['LONGITUDE'].min(), df_stops['LONGITUDE'].max()))

    plt.title(folder_name)

    plt.show()

