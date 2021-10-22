# federated-learning
For the development of differentially private federated machine learning on the CanDIG data services

## Quick Start

0. **Pull submodule updates.** The `federated-learning` repository relies on the `mohccn-data` submodule to provide adequate synthetic data for training purposes. Pull its most recent updates with `git submodule update --init`.
1. **Configure docker-compose.** The `docker-compose.yaml` file expects a `.env` file in root folder, so that it can configure the Katsu database with some secrets such as the password. For a generic configuration, you can run the following to copy and use the default configuration: `cp .default.env .env`
2. **Clone CanDIG/Katsu and build a local Docker image** The current release of CanDIG/Katsu does not support MCODE data, so you will have to build a Docker image of CanDIG/Katsu locally by first cloning the [Katsu repository](https://github.com/CanDIG/katsu) and then running ``docker build -t katsu .`` in the root folder (or see below to automate this in `docker-compose.yaml`). Also, make sure to run `git submodule update --init` in the Katsu repository as our demo relies on Katsu submodules to be fully updated. **Our Compose file expects a local image tagged `katsu`.**
4. **Spin up Katsu.** Run `docker-compose up katsu`
5. **Browse Katsu.** Navigate your browser to `localhost:8000`

## Avoiding Manually Running ``docker build -t katsu .``
To avoid manually building Katsu with `docker build -t katsu .` you could add something like the following block to the `katsu` service in `docker-compose.yaml`:
```
services:
  katsu:
    build:
      context: ${KATSU_DIR}
```
And then configure `KATSU_DIR` in the `.env/.default.env` file to be a relative path pointing to the cloned Katsu repo on your machine.
## Ingesting Data

### Ingesting Single Files

The `federated-learning` repository provides sample MCODE data in the `mohccn-data` submodule to ingest onto a local Katsu instance. To ingest this data, you should run
 ```python
 python mohccn-data/ingest.py testproj testdset testtable http://localhost:8000 /app/chord_metadata_service/scripts/mCode_ingest_scripts.json mcodepacket
 ```

 In general, you can run 
 ```bash
  python mohccn-data/ingest.py <PROJ_NAME> <DSET_NAME> <TABLE_NAME> <SERVER_URL> <DATA_PATH> <DATA_TYPE> <MCODE_INGEST_TYPE>
 ```
 where MCODE_INGEST_TYPE is `fhir` if the data you are ingesting is `fhir_mcode_json` as per the [katsu documentation](https://metadata-service.readthedocs.io/en/develop/modules/introduction.html) (see #3 on FHIR MCODE data ingest). However, keep in mind that `<DATA_PATH>` is the absolute path of your data _on Katsu's docker container_. If you plan on supplying your own data, please edit `docker-compose.yaml` to provide the data as a volume to Katsu's container. As an example, to supply our sample data, we include
 ```
- ./mohccn-data/mCode_ingest_scripts.json:/app/chord_metadata_service/scripts/mCode_ingest_scripts.json
 ```
 underneath the `volumes` header for `katsu` in `docker-compose.yaml`. For more information about formatting `docker-compose.yaml` to include volumes like this, see the [short syntax for volumes in the Compose file](https://docs.docker.com/compose/compose-file/compose-file-v3/#volumes).

 After ingesting, you should see a message resembling the following
 ```
 mcodepacket Data have been ingested from source at /app/chord_metadata_service/scripts/mCode_ingest_scripts.json
 ```

 ### Ingesting a Directory

 Since `<DATA_PATH>` is the absolute path of data on the katsu Docker container, ingesting a directory can be a bit more involved. We provide a bash script `./ingestion-scripts/ingest_dir.sh` to perform this workflow. From our root directory,
 ```bash
 bash ./ingestion-scripts/ingest_dir.sh <PROJ_TITLE> <DSET_TITLE> <TABLE_TITLE> <SERVER_URL> <DIR_PATH> <DATA_TYPE> <MCODE_INGEST_TYPE>
 ```
 where MCODE_INGEST_TYPE is `fhir` if the data you are ingesting is `fhir_mcode_json` as per the [katsu documentation](https://metadata-service.readthedocs.io/en/develop/modules/introduction.html) or anything else otherwise (see #3 on FHIR MCODE data ingest). Remember again that the `<DIR_PATH>` is the absolute directory path of the data you are ingesting on katsu's Docker container.

## Development

To run more existing services alongside Katsu, add the services to the `docker-compose.yaml` file and add their default configuration variables to `.default.env`.

You can also contribute code pertaining to federated learning to this repository. Please organize new files into subdirectories. The root folder should only contain the README, configuration files, and subdirectories.
