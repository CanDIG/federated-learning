# Orchestration
The federated-learning setup is very dependent on the docker configuration created. To aid in this process, orchestration script(s) have been added to the [`orchestration-scripts`](../orchestration-scripts) folder to aid in tasks like generating a `docker-compose.yml` file. Any scripts created that work with the configuration of the entire federated-learning repo, should be placed in this folder. The documentation for said scripts should be placed in this file, under the [Scripts Subheading](#Scripts)

## Orchestration File Tree
```bash
orchestration-scripts
|  configure_docker_compose.py
|  additional-scripts-here (add any new orchestration scripts here)
```
## Scripts

### configure_docker_compose.py
This script generates a `docker-compose.yml` file, and saves it in the current working directory. To call it from the root federated-learning directory, use the following form:
```bash
./orchestration-scripts/configure_docker_compose.py PORT SCALE ROUNDS EXPERIMENT_PATH
```

Arguments:
```
PORT := The port at which to expose the fl-services
SCALE := The number of clients that will be used in the federated experiment
ROUNDS := The number of global rounds to train the models for
EXPERIMENT_PATH := The path of the 'experiment' folder
```

Additional help is visible using `./orchestration-scripts/configure_docker_compose.py -h`