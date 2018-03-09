import argparse
import numpy as np
import gdal
from shapely.geometry import Point
import pandas as pd
from geopandas import GeoSeries, GeoDataFrame

def fft_map(arr):
    from scipy import fftpack
    # Take the fourier transform of the image.
    F1 = fftpack.fft2(arr)

    # Now shift the quadrants around so that low spatial frequencies are in
    # the center of the 2D fourier transformed image.
    F2 = fftpack.fftshift(F1)
    return F2


def filter_fft(im_fft2):
    from scipy import fftpack

    # Set r and c to be the number of rows and columns of the array.
    r, c = im_fft2.shape

    # Define the fraction of coefficients (in each direction) we keep
    keep_fraction = 0.3  # Set to zero all rows with indices between r*keep_fraction and
    # r*(1-keep_fraction):
    im_fft2[int(r * keep_fraction):int(r * (1 - keep_fraction))] = 0

    # Similarly with the columns:
    im_fft2[:, int(c * keep_fraction):int(c * (1 - keep_fraction))] = 0
    return np.abs(fftpack.ifft2(fftpack.fftshift(im_fft2)))


def peak_finder(filt_im, dist, threshold):
    """Find peak in filtered image"""
    from skimage.feature import peak_local_max
    coordinates = peak_local_max(filt_im, min_distance=dist, threshold_abs=threshold)
    return coordinates


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--map')
    parser.add_argument('--output')
    args = parser.parse_args()

    mapfile=args.map
    output=args.output

    print('floodmap set as: ',mapfile)
floodmap=gdal.Open(mapfile)
arr = floodmap.ReadAsArray()
arr[arr < 0] = 0.0

F2=fft_map(arr)
filt_im=filter_fft(F2)
coords=peak_finder(filt_im,3,1.25)

geo_transform = floodmap.GetGeoTransform()
origin_x = geo_transform[0]
origin_y = geo_transform[3]
pixel_width = geo_transform[1]
pixel_height = geo_transform[5]
n_cols = floodmap.RasterXSize
n_rows = floodmap.RasterYSize

extent_lonlat = (
    origin_x,
    origin_x + (pixel_width * floodmap.RasterXSize),
    origin_y + (pixel_height * floodmap.RasterYSize),
    origin_y
)
xpix = np.arange(extent_lonlat[0], extent_lonlat[1], pixel_width)
ypix = np.arange(extent_lonlat[3], extent_lonlat[2], pixel_height)

data = {'Domain': mapfile.split('/')[-1] * coords.shape[0],
              'lat':ypix[coords[:,0]] ,
              'lon': xpix[coords[:,1]]}
df=pd.DataFrame(data)

geometry = [Point(xy) for xy in zip(df['lon'], df['lat'])]
gdf = GeoDataFrame(df, geometry=geometry)
gdf.to_file(filename=output)