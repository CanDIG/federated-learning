import sys
import argparse
import requests

"""
An ingest script that automates the initial data ingest for katsu service.

Note that you should run this script with Katsu's virtualenv activated.
"""

def create_table(katsu_server_url: str, dataset_uuid: str, table_name: str, data_type: str) -> str:
    """
    Create a new katsu table.

    Return the uuid of the newly-created table.
    """

    table_request = {
        "name": table_name,
        "data_type": data_type,
        "dataset": dataset_uuid
    }

    r3 = requests.post(katsu_server_url + "/tables", json=table_request)

    if r3.status_code == 200 or r3.status_code == 201:
        table_id = r3.json()["id"]
        return table_id
    else:
        print("Something else went wrong. It might be that your a table with the same name already exists or that your table name is too short.")
        sys.exit()

def main():
  """
  Driver function for script.
  """
  parser = argparse.ArgumentParser(description="A script that creates a new table and returns its uuid.")

  parser.add_argument("dataset_uuid", help="Dataset name.")
  parser.add_argument("table", help="Table name.")
  parser.add_argument("data_type", help="The type of data. Only phenopacket and mcodepacket are supported.")
  parser.add_argument("server_url", help="The URL of Katsu Instance.")

  args = parser.parse_args()
  dataset_uuid = str.strip(args.dataset_uuid)
  table_name = str.strip(args.table)
  katsu_server_url = str.strip(args.server_url)
  data_type = str.strip(args.data_type)

  if data_type not in ['phenopacket', 'mcodepacket']:
      print("Table data type must be either phenopacket or mcodepacket.")
      sys.exit()

  table_uuid = create_table(katsu_server_url, dataset_uuid, table_name, data_type)
  print(table_uuid)

if __name__ == "__main__":
    main()
