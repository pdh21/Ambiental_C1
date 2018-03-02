FROM continuumio/miniconda3

LABEL maintainer "peter@datajavelin.com"

# Set the working directory to /app
WORKDIR /app

RUN git clone https://github.com/pdh21/Ambiental_C1.git && cd Ambiental_C1 && pip install -e './'

EXPOSE 90


CMD["python", find_errors"]