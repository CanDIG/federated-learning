# federated-learning
For the development of differentially private federated machine learning on the CanDIG data services

## Dependencies
1. **Pull submodule updates.** The `federated-learning` repository relies on the `mohccn-data` submodule to provide adequate synthetic data for training purposes. Pull its most recent updates with the following command:
- Navigate to the `katsu` repo and run `git submodule update --init --recursive`

## Quick Start

1. **Configure docker-compose.** The `docker-compose.yaml` file expects a `.env` file in root folder, so that it can configure the Katsu database with some secrets such as the password. For a generic configuration, defaults are already specified in the `docker-compose.yml` file.
2. **Spin up Katsu.** Run `docker-compose up katsu`
3. **Browse Katsu.** Navigate your browser to `localhost:5002`

## Ingesting Data

The `federated-learning` repository has provided a bash script interface for you to communicate with Katsu. To ingest data, into Katsu, you must first create a project, dataset, and table in Katsu for your data to live in. The bash interface makes this a chain of straightforward commands. The bash scripts assume your Katsu container is tagged `katsu`, as is the case if you have followed the quick start thus far.

We have [walkthrough examples](#examples) to ingest files from our `mohccn-data` repository and the CodeX/Synthea breast cancer dataset.
### Creating a Project
To create a project, run
```bash
bash ingestion_scripts/create_project.sh -t <DOCKER_TAG> <PROJECT_TITLE>
```
This should return a uuid that you should save to use in the next command to create a dataset. See `bash ingestion_scripts/create_project.sh -h` for details.

### Creating a Dataset
To create a dataset, run
```bash
bash ingestion_scripts/create_dataset.sh -t <DOCKER_TAG> <PROJECT_UUID> <DATASET_NAME>
```
This should return a uuid that you should save to use in the next command to create a table. See `bash ingestion_scripts/create_dataset.sh -h` for details.

### Creating a Table
To create a table, run
```bash
bash ingestion_scripts/create_table.sh -t <DOCKER_TAG> <DATASET_UUID> <TABLE_NAME> <TABLE_TYPE>
```
where `<TABLE_TYPE>` is one of "mcodepacket" or "phenopacket", depending on the type of data you expect to ingest into the table.
This should return a uuid that you should save to use in the next command to ingest data. See `bash ingestion_scripts/create_table.sh -h` for details.

### Ingesting Data
To ingest data, use the `ingest.sh` script. Roughly speaking, the script runs as follows
```bash
bash ingestion_scripts/ingest.sh -t <DOCKER_TAG> <TABLE_UUID> <WORKFLOW_ID> <ABSOLUTE_PATH>
```
Valid data ingestion workflows are: "mcode_json", "mcode_fhir_json", or "phenopackets_json".
Ingested data may be stored locally (specify this with the -l flag) or on the Katsu's Docker container (by default). 
The data path may specify a single file (by default), or a directory of JSON files to ingest (specify the -d) flag.
See `bash ingestion_scripts/ingest.sh -h` for more details.

 After ingesting, you should see a message resembling the following
 ```
 mcodepacket Data have been ingested from source at /app/chord_metadata_service/scripts/mCode_ingest_scripts.json
 ```

We have walkthrough examples of using the `ingest.sh` script to ingest both single files and directories in our examples section below.

## Examples

### Ingesting Single Files
The `federated-learning` repository provides sample MCODE data in the `mohccn-data` submodule to ingest onto a local Katsu instance. To ingest this data, we first create a project by running
```bash
bash ingestion_scripts/create_project.sh -t <DOCKER_TAG> mohccn-test
```
This should return a uuid that you should save to use in the next command to create a dataset. We create this dataset by running
```bash
bash ingestion_scripts/create_dataset.sh -t <DOCKER_TAG> <PROJECT_UUID> dataset-test
```
This should return a uuid that you should save to use in the next command to create a table. We create this table by running
```bash
bash ingestion_scripts/create_table.sh -t <DOCKER_TAG> <DATASET_UUID> table-test mcodepacket
```
This should return a uuid that you should save to use in the next command to ingest data. Notice that we specify our table type as mcodepacket since the `mohccn-data` repository supplies MCODE data. Finally, we ingest our data from our local filesystem by running our ingest script with the `-l` flag specified.
```bash
bash ingestion_scripts/ingest.sh -t <DOCKER_TAG> -l <TABLE_UUID> mcode_json <PATH_TO_FEDERATED_LEARNING_REPOSITORY>/mohccn-data/mCode_ingest_scripts.json
```
After ingesting, you should see a message resembling the following
```
mcodepacket Data have been ingested from source at /app/chord_metadata_service/scripts/mCode_ingest_scripts.json
```

### Ingesting Directories
The `federated-learning` repository uses the [CodeX/Synthea-1 2000 Female Breast Cancer Synthetic MCODE Dataset](https://confluence.hl7.org/display/COD/mCODE+Test+Data). Since this is currently a dead link as of writing, we provide a small sample of this data to ingest in the `synthea-examples` directory. To ingest this data, we first create a project by running
```bash
bash ingestion_scripts/create_project.sh -t <DOCKER_TAG> synthea-test
```
This should return a uuid that you should save to use in the next command to create a dataset. We create this dataset by running
```bash
bash ingestion_scripts/create_dataset.sh -t <DOCKER_TAG> <PROJECT_UUID> dataset-test-synthea
```
This should return a uuid that you should save to use in the next command to create a table. We create this table by running
```bash
bash ingestion_scripts/create_table.sh -t <DOCKER_TAG> <DATASET_UUID> table-test-synthea mcodepacket
```
This should return a uuid that you should save to use in the next command to ingest data. Notice that we specify our table type as mcodepacket since the breast cancer dataset is of MCODE data. Finally, we ingest our data from our local filesystem by running our ingest script with the `-l` flag specified. We also specify the `-d` flag since we are ingesting a directory
```bash
bash ingestion_scripts/ingest.sh -t <DOCKER_TAG> -l -d <TABLE_UUID> mcode_fhir_json <PATH_TO_SYNTHEA_EXAMPLES>
```
This should successfully ingest our data.

### Analyzing Data

We have examples in our `examples/` directory. Please see each example's directory for detailed reproduction instructions.
## Development

To run more existing services alongside Katsu, add the services to the `docker-compose.yaml` file and add their default configuration variables to `.default.env`.

You can also contribute code pertaining to federated learning to this repository. Please organize new files into subdirectories. The root folder should only contain the README, configuration files, and subdirectories.
