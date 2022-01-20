# Synthea Breast Cancer EDA

This directory contains the Jupyter Notebooks related to the Synthea Data 
EDA for Ali Raza Zaidi and Laiba Zaman.

## Procedure
1. Ensure you have the required dependencies installed. They can be 
   installed via the package manager of you choosing (e.g. `pip`).
   - These include `typing, requests, pandas, seaborn, matplotlib, sklearn`
   - Ensure to have `graphviz` already installed on your system: `sudo apt 
     install graphviz`.
2. One will need to set up a local instance of their katsu server as well 
   as a GraphQL endpoint. The instructions for both of these lie in the 
   READMEs of the 
   [Federated-Learning Repository](https://github.com/CanDIG/federated-learning) and the [GraphQL-interface Repository](https://github.com/CanDIG/GraphQL-interface).
3. One may also need to download and ingest the Synthea MCode Dataset onto 
   their local katsu instance, the process for which is detailed on the 
   [Federated-Learning Repository](https://github.com/CanDIG/federated-learning).
4. Once all dependencies have been installed and all services are up and 
   running, [SyntheaEDA](SyntheaEDA.ipynb) should be the first file you 
   run. Execute it with a Jupyter Notebook Instance, and then it will save 
   its processed data into a csv file called `SyntheaEDA.csv`. 
5. One can now run the [SyntheaClassifiers](SyntheaClassifiers.ipynb) file 
   can be run on a Jupyter Notebook instance. This file will use the 
   `SyntheaEDA.csv` file to collect the processed data, and will then train 
   several classifiers with the collected data, outputting the results of 
   evaluation metrics performed on each of the datasets. The file will also 
   export a file called `cancer_model.dot` that has a representation of the 
   Decision Tree in the form of a `DOT` file. It will also export a 
   visual representation of the tree in a file called `cancer_model.png`.
   - If you are having trouble converting from the `cancer_model.dot` file 
     to the `cancer_model.png` file through python, try navigating to the 
     repository where the `cancer_model.dot` file is located, and execute 
     the following command in your terminal: `dot -Tpng cancer_model.dot -o 
     cancer_model.png`.

# Resources
The Confluence Pages Associated with the Jupyter Notebooks Can be found as 
Sub-Pages within the Federated-Learning Confluence Page.