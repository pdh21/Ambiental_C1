import domains
import argparse
import sys
import gdal
import shapefile
from osgeo import osr
import glob
from scipy import interpolate
from shapely.geometry import Point
import pandas as pd
import geopandas as gpd
from geopandas import GeoSeries, GeoDataFrame
import numpy as np
from sklearn.cluster import DBSCAN
import warnings
warnings.simplefilter(action = "ignore", category = RuntimeWarning)




if __name__ == '__main__':
   parser = argparse.ArgumentParser()
   parser.add_argument('--map')
   parser.add_argument('--domains')
   parser.add_argument('--dist')
   parser.add_argument('--ngroup')
   parser.add_argument('--output')
   args = parser.parse_args()
   mapfile=args.map
   domain_direc=args.domains
   eps=args.dist
   ngroup=args.ngroup
   output=args.output

   print('floodmap set as: ',mapfile)
   print('directory containing domains: ',domain_direc)


floodmap=gdal.Open(mapfile)

arr = floodmap.ReadAsArray()
geo_transform = floodmap.GetGeoTransform()
origin_x = geo_transform[0]
origin_y = geo_transform[3]
pixel_width = geo_transform[1]
pixel_height = geo_transform[5]
n_cols = floodmap.RasterXSize
n_rows = floodmap.RasterYSize

band = floodmap.GetRasterBand(1)

extent_lonlat = (
    origin_x,
    origin_x + (pixel_width * floodmap.RasterXSize),
    origin_y + (pixel_height * floodmap.RasterYSize),
    origin_y
)

sfiles=glob.glob(domain_direc+'/*.shp')


if ngroup ==None:
   ngroup=10
   print('Using default min group no. of ',ngroup)
if eps==None:
   eps=pixel_width * 3
   print('Using default distance of ',eps,' for grouping')
ngroup=np.float(ngroup)
eps=np.float(eps)

df = []
for ii, s in enumerate(sfiles):
   sf = shapefile.Reader(s)
   sh_points = np.array(sf.shapes()[0].points)
   xpix = np.arange(extent_lonlat[0], extent_lonlat[1], pixel_width)
   ypix = np.arange(extent_lonlat[3], extent_lonlat[2], pixel_height)

   # loop over shape points
   points = np.ones((5000, 3))
   c = 0
   pix_dist = np.array([1, 5])

   for i in range(0, sh_points.shape[0] - 1):
      # need to interpolate between points in shapefile
      fx = interpolate.interp1d(sh_points[i:i + 2, 0], sh_points[i:i + 2, 1], kind='slinear', fill_value='extrapolate')
      if sh_points[i, 0] < sh_points[i + 1, 0]:
         xnew = np.arange(sh_points[i, 0], sh_points[i + 1, 0], pixel_width)
      else:
         xnew = np.arange(sh_points[i, 0], sh_points[i + 1, 0], -pixel_width)
      ynew = fx(xnew)
      fy = interpolate.interp1d(sh_points[i:i + 2, 1], sh_points[i:i + 2, 0], kind='slinear', fill_value='extrapolate')
      if sh_points[i, 1] > sh_points[i + 1, 1]:
         ynew_2 = np.arange(sh_points[i, 1], sh_points[i + 1, 1], pixel_height)
      else:
         ynew_2 = np.arange(sh_points[i, 1], sh_points[i + 1, 1], -pixel_height)
      xnew_2 = fy(ynew_2)

      for j in range(xnew.shape[0] - 1):
         # calculate difference in x and y for tangent
         dy = ynew[j + 1] - ynew[j]
         dx = xnew[j + 1] - xnew[j]
         angle = 0.5 * np.pi - np.arctan(dy / dx)
         t_x = pix_dist * pixel_width * np.cos(angle)  # ideally should be 0.5*pixel but more stable if 1.1
         t_y = pix_dist * pixel_height * np.sin(angle)
         # inner value
         x_in = domains.find_nearest(xpix, xnew[j] + t_x)
         y_in = domains.find_nearest(ypix, ynew[j] + t_y)
         # outer value
         x_out = domains.find_nearest(xpix, xnew[j] - t_x)
         y_out = domains.find_nearest(ypix, ynew[j] - t_y)

         points[c, :] = [(np.max(arr[y_out, x_out]) - np.max(arr[y_in, x_in])) / dx, xnew[j], ynew[j]]
         c += 1
      for j in range(xnew_2.shape[0] - 1):
         # calculate difference in x and y for tangent
         dy = ynew_2[j + 1] - ynew_2[j]
         dx = xnew_2[j + 1] - xnew_2[j]
         angle = 0.5 * np.pi - np.arctan(dy / dx)
         t_x = pix_dist * pixel_width * np.cos(angle)  # ideally should be 0.5*pixel but more stable if 1.1
         t_y = pix_dist * pixel_height * np.sin(angle)
         # inner value
         x_in = domains.find_nearest(xpix, xnew_2[j] + t_x)
         y_in = domains.find_nearest(ypix, ynew_2[j] + t_y)

         # outer value
         x_out = domains.find_nearest(xpix, xnew_2[j] - t_x)
         y_out = domains.find_nearest(ypix, ynew_2[j] - t_y)
         points[c, :] = [(np.max(arr[y_out, x_out]) - np.max(arr[y_in, x_in])) / dx, xnew_2[j], ynew_2[j]]
         c += 1
   ind = points[:, 0] < -100.0
   if ind.sum() > 0:
      db = DBSCAN(eps=eps * 5, min_samples=ngroup).fit(points[ind, 1:3])
      labels = db.labels_
      ind_keep = labels >= 0
      data = {'Domain': s.split('/')[-1],
              'lat': points[ind, 2][ind_keep],
              'lon': points[ind, 1][ind_keep], 'group': labels[ind_keep]}

      df.append(pd.DataFrame(data))
   if ((ii % 100) == 0):
      print('Completed ', ii,' / ', len(sfiles))
alldf = pd.concat(df)
geometry = [Point(xy) for xy in zip(alldf['lon'], alldf['lat'])]
gdf = GeoDataFrame(alldf, geometry=geometry)
gdf.to_file(filename=output)