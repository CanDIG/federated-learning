import sys
import argparse
import requests
import re

"""
An ingest script that automates the initial data ingest for katsu service.
Note that you should run this script with Katsu's virtualenv activated.
"""

def ingest_data(katsu_server_url: str, table_id: str, data_file: str, workflow: str) -> None:
    """
    Ingest the data file.
    """

    # do not yet support FHIR -> Phenopacket workflow since Katsu only has partial implementation.
    workflow_info = {
        "phenopackets_json": {
            "id": "phenopackets_json",
            "params": "phenopackets_json.json_document",
        },
        "mcode_json": {
            "id": "mcode_json",
            "params": "mcode.json_document"
        },
        "mcode_fhir_json": {
            "id":"mcode_fhir_json",
            "params": "mcode.json_document"
        }
    }
    
    workflow_params = {}
    workflow_params[workflow_info[workflow]["params"]] = data_file

    private_ingest_request = {
        "table_id": table_id,
        "workflow_id": workflow_info[workflow]['id'],
        "workflow_params": workflow_params,
        "workflow_outputs": {"json_document": data_file},
    }

    print("Ingesting {} data, this may take a while...".format(workflow))

    r5 = requests.post(
        katsu_server_url + "/private/ingest", json=private_ingest_request
    )

    if r5.status_code == 200 or r5.status_code == 201 or r5.status_code == 204:
        print("{} Data have been ingested from source at {}".format(workflow, data_file))
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
  """
  Driver function for script.
  """

  parser = argparse.ArgumentParser(description="A script that facilitates initial data ingestion of Katsu service.")

  parser.add_argument("table_uuid", help="The table_uuid of the table that this data should be ingested to")
  parser.add_argument("data_path", help="The absolute path to the data file on the Katsu Docker container.")
  parser.add_argument("server_url", help="The URL of Katsu Instance.")
  parser.add_argument("workflow", help="The ingest workflow. Only phenopackets_json, mcode_json, and mcode_fhir_json are supported.")
  
  args = parser.parse_args()
  table_uuid = str.strip(args.table_uuid)
  katsu_server_url = str.strip(args.server_url)
  data_file = str.strip(args.data_path)
  workflow = str.strip(args.workflow)

  # Piping from 'ls' in the bash script creates ANSI escape sequences that need to be filtered
  ansi_escape = re.compile(r'''
      \x1B  # ESC
      (?:   # 7-bit C1 Fe (except CSI)
          [@-Z\\-_]
      |     # or [ for CSI, followed by a control sequence
          \[
          [0-?]*  # Parameter bytes
          [ -/]*  # Intermediate bytes
          [@-~]   # Final byte
      )
  ''', re.VERBOSE)
  result = ansi_escape.sub('', str.strip(data_file))

  if workflow not in ['phenopackets_json', 'mcode_json', 'mcode_fhir_json']:
      print("Data type must be either phenopackets_json, mcode_json or mcode_fhir_json.")
      sys.exit()
  ingest_data(katsu_server_url, table_uuid, result, workflow)


if __name__ == "__main__":
    main()
