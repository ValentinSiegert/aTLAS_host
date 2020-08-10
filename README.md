# <img src="../aTLAS/logos/atlas_orange.svg" alt="aTLAS orange" width="3%" height="3%"> TrustLab Host

This is the host library of the TrustLab aTLAS and thus a submodule of aTLAS' main repository.
(https://github.com/N0omB/aTLAS)

## Setup

1. Ensure Setup of aTLAS. (https://github.com/N0omB/aTLAS)

2. Clone submodule to host where required if not on same machine as aTLAS.

3. Setup pipenv in submodule root:
    ```bash
    pipenv install
    ```
   **OR** install all requirements in your virtual environment for this submodule with:
   ```bash
    pip install -r requirements.pip --exists-action w
    ```

## Run

1. Ensure Running of aTLAS. (https://github.com/N0omB/aTLAS)

2. Start supervisor, e.g. with a maximum capacity of 10 agents:
    ```bash
    python3 supervisors.py 10
    ```
   For more specific preferences conduct the help of `supervisors.py`:
   ```bash
    python3 supervisors.py -h
    ```

## Links To Know

* aTLAS Project page \
https://vsr.informatik.tu-chemnitz.de/projects/2020/atlas/

* Latest online prototype \
https://vsr.informatik.tu-chemnitz.de/projects/2020/atlas/demo/

* aTLAS main repository \
https://github.com/N0omB/aTLAS