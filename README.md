# Ambiental_C1
First Contract with Ambiental. Our priority is:

1. Identification of ‘domain errors’ (model domains cutting off the floodplain) on composite flood maps.
2. Identification of unstable simulations (on individual sims);
3. Identification of likely flow obstructions in LiDAR DTM;
4. Work on the Flowroute-hydro calibration/sensitivity challenges. 

## Identification of ‘domain errors’
Initial data analysis is in notebook [Data_analysis.ipynb](./Data_analysis.ipynb) and prototyping of solution in
 [Domain_error_example.ipynb](Domain_error_example.ipynb).
 
### Solution
The solution works by scanning around each domain, and looking at gradient across it. When that gradient is below an 
unphysical threshold, the corresponding pixel is flagged. Once scanning for each domain is complete, we look at how 
close together those pixels are. Only if the number of pixels is above a predefined level (see `ngroup` below) do 
those pixels remain flagged. This clustering requirement helps removes the false positives.

We provide two ways to run solution, a python package (which requires installation of required modules), or a docker 
image which has all the python modules pre-installed and will run on any OS as long as docker is installed.

----------
#### Python Package
 Code is packaged up as a python installation (python 3). Install with the command:
 
`pip install -e './' `


This should install all required modules

To find the errors, you can run `find_errors.py`.This requires three arguments, and one optional argument:

##### Arguments:

`--map`: the flood simulation file (a tif file)

`--domains`:the directory containing the domain shape files

`--output`: the filename you want for output. The output is a `.shp` file, containing a list of pixels, their positions 
(in co-ordinate system of domain files), the domain they correspond to, and what group number the pixels belong to.

##### Optional argument:
`--ngroup`: the minimum number of points in group. The higher the number, the less likely to pick up false positives.
 Needs testing
 
#### Example:

`python find_errors.py --map './data/NOR_Fluvial_100yr.tif'  --domains './data/Domains/' --output 'bad_points' --ngroup 10` 

-----------
#### Docker Image

To install docker [see here for information](https://docs.docker.com/install/). To run the docker image, run the 
following command:

`docker run -v /absolute/path/to/folder/with/map/:/map \
    -v /absolute/path/to/folder/with/domains/:/domains \
    -v /absolute/path/to/output/folder/:/output \
    datajavelin/ambiental_c1:v0.1 
    --map='/map/map_file.tif' 
    --domains '/domains/' 
    --output '/output/problem_domains'
    --ngroup '20'
`
The `-v` commands attaches the local folders to the docker container.

For example:
`docker run -v /Users/pdh21/Ambiental_DataJavelin_FloodMap_QA/Domain_Errors/Examples/CombinedOutput_FloodMap/:/map \
 -v /Users/pdh21/Ambiental_DataJavelin_FloodMap_QA/Domain_Errors/Examples/Problematic_Domains/:/domains \
 -v /Users/pdh21/output/:/output \
 datajavelin/ambiental_c1:v0.1 --map '/map/SEV_Fluvial_100yr.tif' \
 --domains '/domains/' \
 --output '/output/test' \
 --ngroup '10'
 `
> Note: The default memory allocation for docker containers may not be enough. Ideally set to 6GB or above
------


## Identification of unstable simulations
Initial data analysis is in [Instabilities.ipynb](Instabilities.ipynb)
