import geopandas as gpd
import numpy as np
import os
import matplotlib.pyplot as plt


os.environ["SHAPE_RESTORE_SHX"] = "YES"


def line_visualize(shp_file_path):
    gdf = gpd.read_file(shp_file_path)

    linestring = gdf['geometry'][0]
    data = np.array(linestring.coords)

    fig = plt.figure()
    ax = fig.add_subplot(projection='3d')

    ax.scatter(data[:,0], data[:,1], data[:,2], marker='o')

    ax.set_xlabel('X Label')
    ax.set_ylabel('Y Label')
    ax.set_zlabel('Z Label')

    plt.show()