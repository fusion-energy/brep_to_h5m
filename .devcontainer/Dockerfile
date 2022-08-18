
FROM mcr.microsoft.com/vscode/devcontainers/miniconda:0-3 as dependencies

RUN conda install -c conda-forge mamba

RUN mamba install -c conda-forge -y "openmc=0.13.0=*nompi*"

RUN mamba install -c fusion-energy -c cadquery -c conda-forge paramak=0.8.3

