# Synthea Breast Cancer Experiment
The team at [The MITRE Corporation](https://mitre.org) have created a population simulation tool called `Synthea`, which was leveraged by the [HL7](https://hl7.org) organization to create [synthetic patient mCODE datasets](https://confluence.hl7.org/display/COD/mCODE+Test+Data).

We are using the `Approx. 2,000 Patient Records with 10 Years of Medical History` breast cancer dataset, downloadable [here](http://hdx.mitre.org/downloads/mcode/mcode1_0_10yrs.zip). This synthetic dataset mostly contains patients with breast cancer, though some other cancers are also present. We have created multiple experimental setups to use this data to create and train models for use in federated, and non-federated contexts.

We made extensive use of Docker Volumes in this experiment so that if we needed to modify any parameters, we wouldn't need to rebuild the docker image & container, and instead could simply restart the container. It is encouraged to make use of docker volumes (bind mounts) for this experiment.

## External Resources
In addition to the documentation present within the folders of each experimental setup, the following external resources also contain useful documentation for this experiment.

- [Rishabh EDA & Classifier Selection](https://candig.atlassian.net/wiki/spaces/CA/pages/607059969/Federated+Learning)
- [Ali & Laiba EDA - Inputs & Outputs](https://candig.atlassian.net/wiki/spaces/CA/pages/624427043/Synthea+Breast+Cancer+Dataset+-+Inputs+and+Outputs)
- [Ali & Laiba EDA - Classifier Training](https://candig.atlassian.net/wiki/spaces/CA/pages/624623655/Synthea+Breast+Cancer+Dataset+-+Classifier+Training)
- [Ali & Laiba EDA - Federation](https://candig.atlassian.net/wiki/spaces/CA/pages/632389635/Synthea+Breast+Cancer+Dataset+-+Federation)
- [Ali & Laiba EDA - Differentially Private Federation](https://candig.atlassian.net/wiki/spaces/CA/pages/634224664/Synthea+Breast+Cancer+-+Choice+of+Differential+Privacy+Algorithm)

## Useful Commands

When testing or experimenting, the following commands will allow you to restart the experiment with ease (assuming your root repo is called `federated-learning`):

### Starting the experiment:
- `./experiments/synthea-breast-cancer/winter2022/{{EXPERIMENT_TYPE_FOLDER}}/quickstart.sh [OPTIONS]`
- `EXPERIMENT_TYPE_FOLDER` can be either `Federated` or `Differentially-Private`

### Deleting All fl-server/fl-client Docker Containers
- `docker rm $(docker ps -a | grep fl- | awk '{print $1;}')`

### Deleting All fl-server/fl-client Docker Images
- `docker rmi -f $(docker images | grep federated-learning_fl- | awk '{print $3;}')`

### Example
- Run experiment with ingest
```bash
./experiments/synthea-breast-cancer/winter2022/{{EXPERIMENT_TYPE_FOLDER}}/quickstart.sh -i 10yrs/female -e ./experiments/synthea-breast-cancer/winter2022/{{EXPERIMENT_TYPE_FOLDER}}/experiment
```

- See results, make changes, etc.

- Restart experiment (without ingestion)
```bash
docker rm $(docker ps -a | grep fl- | awk '{print $1;}')
docker rmi -f $(docker images | grep federated-learning_fl- | awk '{print $3;}')
./experiments/synthea-breast-cancer/winter2022/{{EXPERIMENT_TYPE_FOLDER}}/quickstart.sh -e ./experiments/synthea-breast-cancer/winter2022/{{EXPERIMENT_TYPE_FOLDER}}/experiment
```