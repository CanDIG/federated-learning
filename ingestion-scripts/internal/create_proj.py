import sys
import argparse
import requests

"""
An ingest script that automates the initial data ingest for katsu service.

Note that you should run this script with Katsu's virtualenv activated.
"""

def create_project(katsu_server_url: str, project_title: str) -> str:
    """
    Create a new Katsu project.

    Return the uuid of the newly-created project.
    """

    project_request = {
        "title": project_title,
        "description": "A new project."
    }

    try:
        r = requests.post(katsu_server_url + "/api/projects", json=project_request)
    except requests.exceptions.ConnectionError:
        print(
            "Connection to the API server {} cannot be established.".format(
                katsu_server_url
            )
        )
        sys.exit()

    if r.status_code == 201:
        project_uuid = r.json()["identifier"]
        return project_uuid
    elif r.status_code == 400:
        print(
            "Something else went wrong. It might be that your a table with the same name already exists or that your table name is too short."
        )
        sys.exit()
    else:
        print(r.json())
        sys.exit()

def main():
  """
  Driver function for script.
  """
  parser = argparse.ArgumentParser(description="A script that facilitates initial data ingestion of Katsu service.")

  parser.add_argument("project_name", help="Project name.")
  parser.add_argument("server_url", help="The URL of Katsu Instance.")

  args = parser.parse_args()
  project_name = str.strip(args.project_name)
  katsu_server_url = str.strip(args.server_url)

  project_uuid = create_project(katsu_server_url, project_name)
  print(project_uuid)

if __name__ == "__main__":
    main()
