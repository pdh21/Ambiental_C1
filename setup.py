from setuptools import setup

setup(name='Ambiental_C1',
      version='0.1',
      description='DataJavelin solutions for first contract',
      url='https://github.com/pdh21/Ambiental_C1',
      author='Peter Hurley',
      author_email='peter@datajavelin.com',
      packages=['domains','./'],
      license='MIT',
      install_requires=['gdal','pyshp', 'scipy', 'shapely', 'pandas', 'geopandas', 'numpy',
                        'scikit-learn', 'scikit-image'],
      zip_safe=False
      )