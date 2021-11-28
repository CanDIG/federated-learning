# Synthea MCODE Breast Cancer Analyses

Here we have some sample workflows using the Synthea MCODE Breast Cancer synthetic dataset. This dataset is downloadable from [here](https://confluence.hl7.org/display/COD/mCODE+Test+Data). Occasionally the dataset links on this page become dead.

To run these notebooks requires a primary dependency in the [CanDIG GraphQL Interface](https://github.com/CanDIG/GraphQL-interface). Follow the setup instructions in that repository (which includes setting up the `rego_development_playground`).

## Ingesting the dataset
Ingesting data into the rego development playground's Katsu requires a few special considerations. We outline the full process here.

First, edit the `rego_development_playground/docker-compose.yml` file to mount the `federated-learning/ingestion_scripts/internal` directory to `katsu`. Assuming the `federated-learning` repository is in the same parent directory as `rego_development_playground` this involves appending the following line under katsu's volumes,
```
      - ../federated-learning/ingestion_scripts/internal:/app/chord_metadata_service/
```
although this may be different depending on where your repositories are located. Now we can start the rego development playground by running `docker-compose up -d`. Assuming that the above line is read correctly by Docker, the `federated-learning` ingestion scripts should now be mounted onto the `rego_development_playground`'s version of Katsu.

Next, we create the project and dataset for our data using the ingestion scripts. From the `federated-learning/ingestion_scripts` directory,
```
bash create_project.sh synthea_proj
```
This gives us a uuid that we pass to the next script, creating our dataset.
```
bash create_dataset.sh <PROJ_UUID> synthea_dset
```
Now we choose to make the `synthea_dset` dataset open/public for OPA. This involves editing `rego_development_playground/permissions_engine/permissions.rego` so that `synthea_dset` is contained in the `open_datasets` list. Assuming a fresh install of the `rego_development_playground`, your `open_datasets` line would look like this
```
open_datasets = ["open1", "open2", "synthea_dset"]
```
Now we can restart the services by calling `docker-compose down` and then `docker-compose up -d` in the `rego_development_playground` directory. We are ready to create our table and ingest our data.
```
bash create_table.sh <DATASET_UUID> synthea_table mcodepacket
```
Finally, call the ingest function on your extracted synthea dataset folder.
```
bash ingest.sh -l -d <TABLE_UUID> mcode_fhir_json <PATH_TO_SYNTHEA_DIRECTORY>
```
Ingesting can take anywhere between 30 seconds and 5 minutes depending on your hardware.

Now you can start the GraphQL server with
```
uvicorn app:app --reload --port 7999
```
from the `GraphQL-interface` directory. Assuming the ingest occurred successfully, `EDA.ipynb` and `Non-FederatedClassification.ipynb` should execute without error.
