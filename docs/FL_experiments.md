# Experiments
The heart of the Federated-Learning repository lies in the `experiments` folder. This folder stores each of the experiments we wish to conduct, along with any experimental background. For each experiment performed, we will generate a new subdirectory within the larger `experiments` folder, that deals with said experiment.

## Experiments File Tree
```bash
experiments
|  README.md
|__mock-experiment
   |__bases
      |  ...
   |__experiment
      |  ...
|__new-experiment-here (each new experiment is added like so)
   |  README.md (experimental background)
   |__experimental_setup_1
      |__experiment
         |  ...
   |__experimental_setup_2
      |__experiment
         |  ...
```

### Mock-Experiment
This subdirectory provides a base with which one can generate their own experimental setup. It also provided abstract base classes upon which the fl-* services are built. For additional documentation, visit the `experiments/mock-experiment/README.md` file.

### New Experiments
For each new experiment, we generate a new sub-folder within the `experiments` directory. We create a README.md file here to detail the experimental background. Then for each experimental setup we want to test, we create sub-folders within this new folder, and each of these experimental setup folders has a folder called `experiment`, which houses the overridden classes, model, etc. This `experiment` folder will be similar to the [`experiments/mock-experiment/experiment`](../experiments/mock-experiment/experiment) folder, whose documentation is present in [`FL_experiments_structure.md`](FL_experiments_structure.md).

You may also choose to write a quickstart script to make the testing of your experimental setup easier, in which case it is advised that you keep this quickstart script within the `experimental_setup_n` folder. If you choose to make a script, you may want to check out the existing quickstart scripts, [`experiments/synthea-breast-cancer/fall2021/Federated/quickstart.sh`](../experiments/synthea-breast-cancer/fall2021/Federated/quickstart.sh) and [`experiments/synthea-breast-cancer/winter2022/Federated/quickstart.sh`](../experiments/synthea-breast-cancer/winter2022/Federated/quickstart.sh), for inspiration. The configuration files, [`orchestration-scripts/configure_docker_compose.py`](../orchestration-scripts/configure_docker_compose.py) as well as [`ingestion-scripts/init.sh`](../ingestion-scripts/init.sh) are also useful in creating quickstart scripts.