import sys
import argparse
import json
import requests
import os

"""
An ingest script that automates the initial data ingest for katsu service.

Note that you should run this script with Katsu's virtualenv activated. Additionally, this script requires
that it is run from the katsu Docker container.
"""

def ingest_data(katsu_server_url, table_id, data_file, data_type, mcode_ingestion_type):
    """
    Ingest the data file.
    """

    workflow_info = {
        "phenopacket": {
            "id": "phenopackets_json",
            "params": "phenopackets_json.json_document",
        },
        "mcodepacket": {
            "id": "mcode_json",
            "params": "mcode.json_document"
        },
        "fhirmcodepacket": {
            "id": "mcode_fhir_json",
            "params": "mcode_fhir_json.json_document"
        }
    }
    
    workflow_params = {}
    if mcode_ingestion_type == 'fhir':
        data_type = "fhirmcodepacket"
    workflow_params[workflow_info[data_type]["params"]] = data_file

    private_ingest_request = {
        "table_id": table_id,
        "workflow_id": workflow_info[data_type]['id'],
        "workflow_params": workflow_params,
        "workflow_outputs": {"json_document": data_file},
    }

    print("Ingesting {} data, this may take a while...".format(data_type))

    r5 = requests.post(
        katsu_server_url + "/private/ingest", json=private_ingest_request
    )

    if r5.status_code == 200 or r5.status_code == 201 or r5.status_code == 204:
        print("{} Data have been ingested from source at {}".format(data_type, data_file))
    elif r5.status_code == 400:
        print(r5.text)
        sys.exit()
    else:
        print(
            "Something else went wrong when ingesting data, possibly due to duplications."
        )
        print(
            "Check you are using the absolute path of data_file, and make sure you aren't ingesting \
                duplicated data. Exception messages from Katsu printed below."
        )
        print(r5.text)
        sys.exit()

def main():

    parser = argparse.ArgumentParser(description="A script that facilitates initial data ingestion of Katsu service.")

    parser.add_argument("table_uuid", help="The table_uuid of the table that this data should be ingested to")
    parser.add_argument("data_dir", help="The absolute path to the local data directory.")
    parser.add_argument("server_url", help="The URL of Katsu Instance.")
    parser.add_argument("data_type", help="The type of data. Only phenopacket and mcodepacket are supported.")
    parser.add_argument("mcode_ingestion_type", help="whether ingestion should be mcode_fhir_json or just mcode_json")

    args = parser.parse_args()
    table_uuid = args.table_uuid
    katsu_server_url = args.server_url
    data_dir = args.data_dir
    data_type = args.data_type
    mcode_ingestion_type = args.mcode_ingestion_type

    if data_type not in ['phenopacket', 'mcodepacket']:
        print("Data type must be either phenopacket or mcodepacket.")
        sys.exit()

    print(table_uuid)
    for filename in os.listdir(data_dir):
      data_file = os.path.join(data_dir, filename)
      print(data_file)
      ingest_data(katsu_server_url, table_uuid, data_file, data_type, mcode_ingestion_type)

if __name__ == "__main__":
    main()
