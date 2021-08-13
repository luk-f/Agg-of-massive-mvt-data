import pandas as pd
import numpy as np
from pandas.core.arrays.sparse import dtype

from scipy.spatial import  voronoi_plot_2d
import matplotlib.pyplot as plt
import datetime

import os
import settings
import logging
import sys

from utils import str_to_bool, random_color, gap_arrow

from part3_voronoi_and_addpoints import voronoi_map

""""""
PLOT_SHOW = True
PLOT_STOPS = False
""""""


if __name__ == "__main__":

    print(f"Numbers of arg: {len(sys.argv)}")
          
    # parameters
    ## by default
    maxRadius = 0.2
    region = "liege"
    without_interchange = True # choose if consider interchanges or not
    apply_algo_3 = True # choose between "algo 2" and "algo 2 & 3"
    
    try:
        if len(sys.argv) > 2:
            maxRadius = float(sys.argv[1])
            region = sys.argv[2]
        if len(sys.argv) > 3:
            without_interchange = str_to_bool(sys.argv[3])
        if len(sys.argv) > 4:
            apply_algo_3 = str_to_bool(sys.argv[4])
    except:
        print("Arg error")
            
    print(f"{maxRadius}, {region}, {without_interchange}, {apply_algo_3}")

    # define input folder (for stops, centroids and segments)
    number_dec = str(maxRadius-int(maxRadius))[2:]
    input_folder_name = f"{region}_0{number_dec}"
    if apply_algo_3:
        input_folder_name += "_algo_3"
    start_date = datetime.datetime(2021, 1, 4, 0 ,0, 0)
    end_date = datetime.datetime(2021, 1, 15, 0 ,0, 0)
    path_data = os.path.join(settings.LOCAL_DATA_CLUSTER_ANDRIENKO, input_folder_name)
    logging.info(f'Path data to collect stop and centroids: {path_data}')

    # define name file input for segments
    prefix_input_seg = "agg_mvt_"
    if apply_algo_3:
        prefix_input_seg += "algo_3_"
    ## if True, ignore interchange
    if without_interchange:
        prefix_input_seg += "without_interchange_"
    path_filename_seg_values = os.path.join(path_data, prefix_input_seg+\
        f'{start_date.strftime("%Y_%m_%d_%H_%M_%S")}__{end_date.strftime("%Y_%m_%d_%H_%M_%S")}.csv')
    logging.info(f'Path data to collect segments values: {path_filename_seg_values}')
    
    # define datetime interval for input data
    date_str_for_csv_input = f'{start_date.strftime("%Y_%m_%d_%H_%M_%S")}__{end_date.strftime("%Y_%m_%d_%H_%M_%S")}.csv'
    
    # load stops and centroids data
    df_stops = pd.read_csv(os.path.join(path_data, date_str_for_csv_input), index_col=0)
    df_centroids = pd.read_csv(os.path.join(path_data, f"centroids_{date_str_for_csv_input}"), index_col=0)
    # load segments data
    segments_values = pd.read_csv(path_filename_seg_values, index_col=0, dtype=np.uint64)

    # compute border limit
    lat_min = df_stops.LATITUDE.min()
    lat_max = df_stops.LATITUDE.max()
    lon_min = df_stops.LONGITUDE.min()
    lon_max = df_stops.LONGITUDE.max()

    points = df_centroids.to_numpy()

    voronoi = voronoi_map(points, maxRadius, lat_min, lat_max, lon_min, lon_max)

    fig = plt.figure(figsize=(10, 10))
    ax = fig.add_subplot(111)

    if PLOT_STOPS:
        for centroid_number in df_stops['CENTROID_NUMBER'].unique():
            # print(group_points)
            df_tmp = df_stops[df_stops['CENTROID_NUMBER'] == centroid_number]
            ax.scatter(df_tmp['LATITUDE'], df_tmp['LONGITUDE'], 
                       # cmap=plt.cm.nipy_spectral,
                       color=random_color(as_str=False, alpha=1), marker='.',
                       alpha=0.5)

    fig = voronoi_plot_2d(voronoi, ax=ax, line_alpha=0.5)

    max_width_arrow = 0.05
    # max_width_arrow = 0.01
    ratio_width_arrow = segments_values.to_numpy().max() / max_width_arrow
    radius_centroid = maxRadius*0.2

    for start, row in enumerate(segments_values.to_numpy()):
        start_lat = df_centroids.loc[start].LATITUDE
        start_long = df_centroids.loc[start].LONGITUDE
        for end, val in enumerate(row):
            end_lat = df_centroids.loc[end].LATITUDE
            end_long = df_centroids.loc[end].LONGITUDE
            if val > 0:
                if start != end:
                    dlat = end_lat - start_lat
                    dlong = end_long - start_long
                    gap_lat, gap_long = gap_arrow(dlat, dlong, radius_centroid)
                    plt.arrow(start_lat+gap_lat, start_long+gap_long, 
                              dlat-2*gap_lat, dlong-2*gap_long,
                              length_includes_head=True, 
                              width=(val/ratio_width_arrow),
                              shape='right',
                              head_width=0.005,
                              head_length=0.01)

    # save directory and file name
    day_now = datetime.datetime.now().strftime("%Y_%m")
    res_path_name = os.path.join(os.path.join(settings.ONE_DRIVE_FOLDER, day_now), "results")
    if not os.path.exists(res_path_name):
        os.makedirs(res_path_name)
        logging.info(f"Directory {res_path_name} Created ")
    else:    
        logging.info(f"Directory {res_path_name} already exists")
    
    plt.title(region+'_'+prefix_input_seg+f'0.{number_dec}')
    fig = plt.gcf()
    
    path_savefig = os.path.join(res_path_name, region+'_'+prefix_input_seg+f'0{number_dec}.pdf')
    fig.savefig(path_savefig)
    logging.info(f'Fig {path_savefig} saved!')
    
    if PLOT_SHOW:
        plt.show()
