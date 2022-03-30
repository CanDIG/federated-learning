#!/usr/bin/env python3

import argparse
import os

def print_ports(initial_port: int) -> None:
    """
    Function to print the external ports used by each service
    """

    print(f"Your Flower Server port is {initial_port}")
    print(f"Your Katsu DB port is {initial_port + 1}")
    print(f"Your Katsu port is {initial_port + 2}")
    print(f"Your GraphQL port is {initial_port + 3}\n")

def get_template_top(initial_port: int) -> str:
    """
    Function to create the main body of the docker-compose file, using the initial port given by the user
    """

    db_katsu_port = initial_port + 1
    katsu_port = initial_port + 2
    graphql_port = initial_port + 3

    return f"""
version: '3'
services:

    fl-server:
        build: services/fl-server
        container_name: fl-server
        ports:
        - "{initial_port}:8080"
        environment:
            GRAPHQL_INTERFACE_URL: "http://gql-interface:7999/"
    
    db-katsu:
        image: postgres:latest
        container_name: db-katsu
        environment:
            POSTGRES_DB: "${{KATSU_POSTGRES_DB:-metadata}}"
            POSTGRES_USER: "${{KATSU_POSTGRES_USER:-admin}}"
            POSTGRES_PASSWORD: "${{KATSU_POSTGRES_PASSWORD:-admin}}"
        ports:
        - "{db_katsu_port}:5432"
        volumes:
        - db-katsu-data:/var/lib/postgresql/data

    katsu:
        build:
            context: services/katsu
            args:
                - venv_python=3.7
                - alpine_version=3.13
        container_name: katsu
        volumes:
        - ./services/katsu_entrypoint.sh:/app/katsu_entrypoint.sh
        - ../federated-learning/ingestion-scripts/internal:/app/chord_metadata_service/ingestion-scripts
        entrypoint: ["/app/katsu_entrypoint.sh"]
        ports:
        - "{katsu_port}:8000"
        depends_on:
        - db-katsu
        environment:
            POSTGRES_HOST: "db-katsu"
            POSTGRES_PORT: 5432
            POSTGRES_DATABASE: "${{KATSU_POSTGRES_DB:-metadata}}"
            POSTGRES_USER: "${{KATSU_POSTGRES_USER:-admin}}"
            POSTGRES_PASSWORD: "${{KATSU_POSTGRES_PASSWORD:-admin}}"

    gql-interface:
        build: services/gql-interface
        container_name: gql-interface
        ports:
        - "{graphql_port}:7999"
        environment:
            GRAPHQL_CANDIG_SERVER: "http://candig-dev:4000"
            GRAPHQL_KATSU_API: "http://katsu:8000/api"
"""

def get_template_bottom() -> str:
    """
    Function to get the volumes used by the docker containers
    """
    
    return """
volumes:
    db-katsu-data:
    """

def get_current_client(cur_num: int) -> str:
    """
    Function to generate a docker-compose container for an fl-client, given the container id
    """
    
    return f"""
    fl-client-{cur_num}:
        build: services/fl-client
        container_name: fl-client-{cur_num}
        depends_on:
        - fl-server
        environment:
            FLOWER_SERVER_URL: "fl-server:8080"
            GRAPHQL_INTERFACE_URL: "http://gql-interface:7999/"
            FLOWER_CLIENT_NUMBER: "{cur_num}"
"""

def create_docker_compose_string(initial_port: int, scale: int) -> str:
    """
    Function to generate a full docker-compose file, as a string literal, given the number of requested clients and the starting port
    """
    
    template_top = get_template_top(initial_port)
    template_bottom = get_template_bottom()
    print_ports(initial_port)

    services_string = template_top
    for cur_num in range(1, scale + 1):
        template_services = get_current_client(cur_num)
        services_string += template_services
    
    return services_string + template_bottom

def save_file_here(contents: str, name: str) -> None:
    """
    Function to save a file called `name` in the `pwd` with the given `contents`
    """
    
    file = open(name, "w")
    file.write(contents)
    print(f"Docker-Compose File saved at {os.getcwd()}/{name}!")

def main() -> None:
    """
    Function to configure and save a docker-compose file, given command-line arguments for the starting port as well as the number of clients requested
    """
    
    info = """
    This script creates a docker-compose.yml file for the federated-learning repository.
    It takes an intial port that all containers should start on, and the number of container
    stacks that should be created.

    Each stack's containers are abbreviated with an index from 1 to scale in the docker-compose
    file. THIS SCRIPT WILL OVERWRITE AN EXISTING DOCKER-COMPOSE.YML FILE.
    """

    parser = argparse.ArgumentParser(description=info)

    parser.add_argument("starting_port", help="The start port at which any localhost ports will be assigned. We recommend 5001.")
    parser.add_argument("scale", help="How many client instances that should be created. Each instance contains 4 docker containers. We recommend 2.")
    
    args = parser.parse_args()
    starting_port = int(args.starting_port)
    scale = int(args.scale)

    docker_compose_string = create_docker_compose_string(starting_port, scale)
    save_file_here(docker_compose_string, "docker-compose.yml")

if __name__ == "__main__":
    main()