import argparse

def create_docker_compose_string(initial_port: int, scale: int):
    template_top = f"""
version: '3'
services:

    fl-server:
        build: services/fl-server
        container_name: fl-server
        ports:
        - "{initial_port}:8080"
        environment:
            GRAPHQL_INTERFACE_URL: "http://gql-interface-0:7999/graphql"
    """
    initial_port += 1
    template_middle = """
volumes:
    """
    graphql_ports = [initial_port + 3*cur_num + 2 for cur_num in range(scale)]
    katsu_ports = [initial_port + 3*cur_num + 1 for cur_num in range(scale)]
    print("Your GraphQL instances are located at: ")
    print(graphql_ports)
    print("Your Katsu instances are located at: ")
    print(katsu_ports)
    flower_server_url = "fl-server:8080"
    services_string = template_top
    volume_string = template_middle
    for cur_num in range(scale):
        cur_start = initial_port + 3*cur_num
        db_katsu_port = cur_start
        katsu_port = cur_start + 1
        graphql_port = cur_start + 2
        template_services = f"""
    db-katsu-{cur_num}:
        image: postgres:latest
        container_name: db-katsu-{cur_num}
        environment:
            POSTGRES_DB: "${{KATSU_POSTGRES_DB:-metadata}}"
            POSTGRES_USER: "${{KATSU_POSTGRES_USER:-admin}}"
            POSTGRES_PASSWORD: "${{KATSU_POSTGRES_PASSWORD:-admin}}"
        ports:
        - "{db_katsu_port}:5432"
        volumes:
        - katsu-db-data-{cur_num}:/var/lib/postgresql/data

    katsu-{cur_num}:
        build: services/katsu
        container_name: katsu-{cur_num}
        volumes:
        - ./services/katsu_entrypoint.sh:/app/katsu_entrypoint.sh
        - ../federated-learning/ingestion_scripts/internal:/app/chord_metadata_service/ingestion_scripts
        entrypoint: ["/app/katsu_entrypoint.sh"]
        ports:
        - "{katsu_port}:8000"
        depends_on:
        - db-katsu-{cur_num}
        environment:
            POSTGRES_HOST: "db-katsu-{cur_num}"
            POSTGRES_PORT: 5432
            POSTGRES_DATABASE: "${{KATSU_POSTGRES_DB:-metadata}}"
            POSTGRES_USER: "${{KATSU_POSTGRES_USER:-admin}}"
            POSTGRES_PASSWORD: "${{KATSU_POSTGRES_PASSWORD:-admin}}"

    gql-interface-{cur_num}:
        build: services/gql-interface
        container_name: gql-interface-{cur_num}
        ports:
        - "{graphql_port}:7999"
        environment:
            CANDIG_SERVER: "http://candig-dev:4000"
            KATSU_API: "http://katsu-{cur_num}:8000/api"

    fl-client-{cur_num}:
        build: services/fl-client
        container_name: fl-client-{cur_num}
        depends_on:
        - fl-server
        environment:
            FLOWER_SERVER_URL: "{flower_server_url}"
            GRAPHQL_INTERFACE_URL: "http://gql-interface-{cur_num}:7999/graphql"
        """
        template_volumes = f"""
    katsu-db-data-{cur_num}:
        """
        services_string += template_services
        volume_string += template_volumes
    return services_string + volume_string

def save_file_here(contents: str, name: str):
    file = open(name, "w")
    file.write(contents)
    print("file saved!")

def main():
    info = """
    This script creates a docker-compose.yml file for the federated-learning repository.
    It takes an intial port that all containers should start on, and the number of container
    stacks that should be created.

    Each stack's containers are abbreviated with an index from 0 to scale-1 in the docker-compose
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