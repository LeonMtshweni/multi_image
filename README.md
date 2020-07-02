# Imaging Radio Interferometeric data via brute force (IRIvBF)

---
---
![IRIvBF](IRIvBF_logo.jpeg)
---
---
* A collection of python scripts that perform parallel Multi-Frequency Synthesis imaging jobs with various imaging and selfcal parameters.
* IRIvBF draws inspiration from [oxkat](https://github.com/IanHeywood/oxkat)
* Runs on a slurm cluter

---
# Take Note
* The pipeline makes use of the following software [CASA](https://casa.nrao.edu/docs/TaskRef/TaskRef.html), [Wsclean](https://sourceforge.net/p/wsclean/wiki/Home/), [Aimfast](https://aimfast.readthedocs.io/en/master/intro.html) and [pyBDSF](https://www.astron.nl/citt/pybdsf/). Since the pipeline works by submiting bash scripts to a slurm worker node (non-interactively) you will need to specify the path to the singularity images of the software used by the pipeline, that is, change the container path at the top of the main script (alpha_main.py)
* You will also need to change the ms_back directory. Here I'm making the assumption that you operate like I do, by keeping all the ms files in a back up directory in your scratch area

## Executing the pipeline
As per the do's and don'ts of the [ILIFU](http://docs.ilifu.ac.za/#/getting_started/submit_job_slurm?id=specifying-resources-when-running-jobs-on-slurm) clone the repo into your scratch area:

```
mkdir example dir
cd example
git clone https://github.com/LeonMtshweni/IRIvBF/
mv IRIvBF/* ./
```
Edit the config file should the defaults not be suitable for you:
```
vi config.yaml
```

Then execute the python script:

```
python alpha_main.py
```
This will take a minute. Once terminal is freed up, inspect that the bash scripts are to your satisfaction:
```
cd scripts/
```
Once you're happy with the output, you may submit the jobs:

```
source submit_jobs.sh
```
