import sys
import argparse
import requests

"""
An ingest script that automates the initial data ingest for katsu service.

Note that you should run this script with Katsu's virtualenv activated.
"""

def create_dataset(katsu_server_url: str, project_uuid: str, dataset_title: str) -> str:
    """
    Create a new dataset.

    Return the uuid of newly-created dataset.
    """
    dataset_request = {
        "project": project_uuid,
        "title": dataset_title,
        "data_use": {
            "consent_code": {
                "primary_category": {"code": "GRU"},
                "secondary_categories": [{"code": "GSO"}],
            },
            "data_use_requirements": [{"code": "COL"}, {"code": "PUB"}],
        },
    }

    r2 = requests.post(katsu_server_url + "/api/datasets", json=dataset_request)

    if r2.status_code == 201:
        dataset_uuid = r2.json()["identifier"]
        return dataset_uuid
    elif r2.status_code == 400:
        print(
            "A dataset of title '{}' exists, please choose a different title, or delete this dataset.".format(
                dataset_title
            )
        )
        sys.exit()
    else:
        print(r2.json())
        sys.exit()

def main():
  """
  Driver function for script.
  """

  parser = argparse.ArgumentParser(description="A script that facilitates initial data ingestion of Katsu service.")

  parser.add_argument("project_uuid", help="Project uuid.")
  parser.add_argument("dataset_name", help="Dataset name.")
  parser.add_argument("server_url", help="The URL of Katsu Instance.")

  args = parser.parse_args()
  project_uuid = args.project_uuid
  dataset_name = args.dataset_name
  katsu_server_url = args.server_url

  dataset_uuid = create_dataset(katsu_server_url, project_uuid, dataset_name)
  print(dataset_uuid)

if __name__ == "__main__":
    main()
