# Ingestion

The `federated-learning` repository has provided a bash script interface for you to communicate with Katsu. To ingest data, into Katsu, you must first create a project, dataset, and table in Katsu for your data to live in. The bash interface makes this a chain of straightforward commands. The bash scripts assume your Katsu container is tagged `katsu`.

See [Quick Ingest](#quick-ingest) below to quickly initialize the database for testing.

We also provide [walkthrough examples](#examples) to manually ingest files from our `mohccn-data` repository and the CodeX/Synthea breast cancer dataset.

## Ingestion File Tree
```bash
ingestion-scripts
|  create_dataset.sh
|  create_project.sh
|  create_table.sh
|  ingest.sh
|  init.sh
|__internal
   |  create_dset.py
   |  create_proj.py
   |  create_table.py
   |  ingest_file.py
|__additional-scripts-here (add additional folders with scripts, if needed)
  |  ...
```
___
## Quick Ingest

`ingestion_scripts/init.sh` is provided to help you quickly initialize the Katsu database for ingestion, and optionally ingest straight into it.

To create a Project, Dataset, and Table, and ingest a locally-stored directory straight into the generated table, run:
```bash
./ingestion_scripts/init.sh -l -d <PATH_TO_LOCAL_INGESTABLE_DIR> <PROJECT_TITLE> <DATASET_TITLE> <TABLE_TITLE> <TABLE_TYPE>
```

Note that you can exclude the `-d`/`-f` options to simply intialize the database without actually running the ingestion, then run `./ingestion_scripts/ingest.sh` to do the ingest in a later step.

### Synthea/CodeX Synthetic Breast Cancer MCODE dataset

The dataset currently being used for training can be browsed [here](https://confluence.hl7.org/display/COD/mCODE+Test+Data) under `Approx. 2,000 Patient Records with 10 Years of Medical History`. Or, just click this direct download [link](http://hdx.mitre.org/downloads/mcode/mcode1_0_10yrs.zip).

Once downloaded, unzip the folder and move the `10yrs` subdirectory into the `federated-learning` project root, or wherever you prefer.

The following command ingests all files in the local `10yrs/female` directory as `mcodepackets` into the `synthea_` project/dataset/table.
```bash
./ingestion_scripts/init.sh -l -d 10yrs/female synthea_proj synthea_dataset synthea_table mcodepacket
```

The EDA and model training files in this repository were done using only the data in the `female` subdirectory. If you wish to ingest all of the `female`, `male`, and `assorted` data together (thereby increasing the corpus size) simply move all of the files together into a single folder and ingest that folder:
```bash
cp 10yrs/female/* 10yrs/male/* 10yrs/assorted/* 10yrs
rm -rf 10yrs/female 10yrs/male 10yrs/assorted
./ingestion_scripts/init.sh -l -d 10yrs synthea_proj synthea_dataset synthea_table mcodepacket
```

___
## Manual Ingest

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

#### Examples

##### Ingesting Single Files
The `CanDIG/mohccn-data` repository provides sample MCODE data to ingest onto a local Katsu instance. To ingest this data, we first create a project by running
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
bash ingestion_scripts/ingest.sh -t <DOCKER_TAG> -l <TABLE_UUID> mcode_json <PATH_TO_MOHCCN_DATA_REPO>/mCode_ingest_scripts.json
```
After ingesting, you should see a message resembling the following
```
mcodepacket Data have been ingested from source at /app/chord_metadata_service/scripts/mCode_ingest_scripts.json
```

##### Ingesting Directories
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

___
## Analyzing Data

We have examples in our `experiments/` directory. Please see each example's directory for detailed reproduction instructions. Older experiments may need tweaking of the configuration to work properly, if you want to run them live instead of reading through the old experimental results in the Jupyter notebook.
