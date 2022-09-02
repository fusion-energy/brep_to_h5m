
FROM mcr.microsoft.com/vscode/devcontainers/miniconda:0-3 as dependencies

RUN apt-get --allow-releaseinfo-change update
RUN apt-get update -y && \
    apt-get upgrade -y

RUN apt-get install -y libgl1-mesa-glx libgl1-mesa-dev libglu1-mesa-dev freeglut3-dev libosmesa6 libosmesa6-dev libgles2-mesa-dev curl imagemagick

RUN conda install -c conda-forge mamba

RUN mamba install -c conda-forge -y "openmc=0.13.0=*nompi*"

RUN mamba install -c fusion-energy -c cadquery -c conda-forge -y paramak=0.8.3

