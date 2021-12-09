# Synthea MCODE Breast Cancer Analyses

Here we have some sample workflows using the Synthea MCODE Breast Cancer synthetic dataset. This dataset is downloadable from [here](https://confluence.hl7.org/display/COD/mCODE+Test+Data). Occasionally the dataset links on this page become dead.

To run these notebooks requires a primary dependency in the [CanDIG GraphQL Interface](https://github.com/CanDIG/GraphQL-interface). Follow the setup instructions in that repository.

## Ingesting the dataset
Ingesting data into the rego development playground's Katsu requires a few special considerations. We outline the full process here.

First, pull the katsu submodule updates by running `git submodule update --init` in the `rego_development_playground` root.

Next, we create the project and dataset for our data using the ingestion scripts. From the `federated-learning/ingestion_scripts` directory,
```
bash create_project.sh synthea_proj
```
This gives us a uuid that we pass to the next script, creating our dataset. We will pass the dataset UUID returned to the following command.
```
bash create_dataset.sh <PROJ_UUID> synthea_dset
```
We are ready to create our table and ingest our data. We will pass the table UUID returned to the following command.
```
bash create_table.sh <DATASET_UUID> synthea_table mcodepacket
```
Finally, call the ingest function on your extracted synthea dataset folder, or to `../synthea-examples`
```
bash ingest.sh -l -d <TABLE_UUID> mcode_fhir_json <PATH_TO_SYNTHEA_DIRECTORY>
```
Ingesting can take anywhere between 30 seconds and 5 minutes depending on your hardware.

Now you can start the GraphQL server by navigating to `../GraphQL-interface` and running
```
export KATSU_API=http://localhost:8000/api &&\
uvicorn app:app --reload --port 7999
```
Assuming the ingest occurred successfully, `EDA.ipynb` and `Non-FederatedClassification.ipynb` should execute without error.
