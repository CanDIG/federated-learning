# Synthea Breast Cancer EDA

This directory contains the Jupyter Notebooks related to the Synthea Data 
EDA for Ali Raza Zaidi and Laiba Zaman.

## Quickstart
**Katsu Setup** (Borrowed from README for federated-learning Repo):
- Clone Federated-Learning Repo
- Install Dependencies: 
    - **Clone CanDIG/Katsu** The current release of CanDIG/Katsu does not support MCODE data, so you will have to supply a locally built Docker image of CanDIG/Katsu. Clone the [Katsu repository](https://github.com/CanDIG/katsu) to prepare the build context. Configure `KATSU_DIR` in your .env file to point to the `katsu` repo on your machine.
    - **Pull submodule updates.** 
        - The `katsu` repository relies on `DATS JSON` schemas. Pull this dependency by navigating to the `katsu` repo and run `git submodule update --init`
        - The `federated-learning` repository relies on the `mohccn-data` submodule to provide adequate synthetic data for training purposes. Pull this dependency by navigating to the `federated-learning` repo and run `git submodule update --init`
- Start Katsu:
    - **Configure docker-compose.** The `docker-compose.yaml` file expects a `.env` file in root folder, so that it can configure the Katsu database with some secrets such as the password. For a generic configuration, you can run the following to copy and use the default configuration: `cp .default.env .env`
    - **Spin up Katsu.** Run `docker-compose up katsu`
    - **Browse Katsu.** Navigate your browser to `localhost:8000`
    - **Query Katsu** by GETting from `localhost:8000/api/mcodepackets`. There will be zero results (`"count": 0`) prior to ingest, and a number of results equal to the dataset size following ingest. 
- Ingesting Synthea Data:
    - The dataset currently being used for training can be browsed [here](https://confluence.hl7.org/display/COD/mCODE+Test+Data) under `Approx. 2,000 Patient Records with 10 Years of Medical History`. Or, just clicl this direct download [link](http://hdx.mitre.org/downloads/mcode/mcode1_0_10yrs.zip).
    - Once downloaded, unzip the folder and move the `10yrs` subdirectory into the `federated-learning` project root, or wherever you prefer.
    - The following command ingests all files in the local `10yrs/female` directory as `mcodepackets` into the `test_` project/dataset/table. ```bash ./ingestion_scripts/init.sh -l -d 10yrs/female test_proj test_dataset test_table mcodepacket ```
___
**GraphQL Setup** (Borrowed from README for GraphQL-interface repo):
- Clone GraphQL-interface Repo
- Setup Local Environment:
    - In the root GraphQL-interface directory, run: `export KATSU_API=http://localhost:8000/api`
    - Build a virtualenv for the repo: `python3 -m venv venv`
    - Activate Virtual Environment: `source venv/bin/activate`
    - Install the requirements.txt: ``` pip install -r requirements.txt ```
    - Run the GraphQL interface: ``` uvicorn app:app --reload --port 7999 ```
___
**EDA Dependencies**:
- Ensure you have the following installed: 
    - Use `pip install` to do so if they aren't there already: `typing, requests, pandas, seaborn, matplotlib, sklearn`
    - `sudo apt install graphviz`: `Graphviz`
___
**Running the EDAs**:
- First, use a Jupyter Notebook instance to run the [Synthea EDA File](https://github.com/CanDIG/federated-learning/blob/AliRZ-02/DIG-757-SyntheaEDA/examples/synthea-breast-cancer/Ali_Laiba_syntheaEDA/SyntheaEDA.ipynb). Ensure that it has downloaded a local CSV file called `SyntheaEDA.csv`
- One can now run the [SyntheaClassifiers](SyntheaClassifiers.ipynb) file. It can be run on a Jupyter Notebook instance. This file will use the `SyntheaEDA.csv` file to collect the processed data, and will then train several classifiers with the collected data, outputting the results of evaluation metrics performed on each of the datasets. The file will also export a file called `cancer_model.dot` that has a representation of the Decision Tree in the form of a `DOT` file. It will also export a visual representation of the tree in a file called `cancer_model.png`.
   - If you are having trouble converting from the `cancer_model.dot` file to the `cancer_model.png` file through python, try navigating to the repository where the `cancer_model.dot` file is located, and execute the following command in your terminal: `dot -Tpng cancer_model.dot -o cancer_model.png`.

# Resources
The Confluence Pages Associated with the Jupyter Notebooks Can be found as 
Sub-Pages within the Federated-Learning Confluence Page.
