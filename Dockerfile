FROM continuumio/miniconda3

LABEL maintainer "peter@datajavelin.com"

RUN conda update conda && git clone https://github.com/pdh21/Ambiental_C1.git

WORKDIR Ambiental_C1
RUN conda install -c conda-forge gdal && conda install -c conda-forge geopandas
RUN conda install scikit-image && pip install -e './'

ENTRYPOINT ["python","find_instabilities.py"]