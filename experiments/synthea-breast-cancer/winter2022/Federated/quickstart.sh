#! /usr/bin/env bash

# Modified from Rishabh's quickstart.sh file present in the experiments/synthea-breast-cancer/fall2021/Federated directory

################################################################################
# Constants                                                                    #
################################################################################
SLEEP_TIME=40
PROJECT_NAME="synthea-project"
DATASET_NAME="synthea-dataset"
TABLE_NAME="synthea-table"

################################################################################
# Help                                                                         #
################################################################################
help ()
{
   # Display Help
   echo
   echo "NOTE: OPTIONS MUST PRECEDE ALL ARGUMENTS"
   echo "Starts an instance of the federated-learning environment with sample data stored locally"
   echo "Start this program from the root directory of the federated-learning repo"
   echo
   echo "Usage:"
   echo "   ./quickstart.sh [options] DATA_PATH NUM_SITES BASE_PORT"
   echo "Arguments:"
   echo "   DATA_PATH      The absolute path of the Synthea breast cancer dataset on your workstation."
   echo "   NUM_SITES      The number of federated learning sites/clients to generate"
   echo "   BASE_PORT      The base port number for the federated-learning docker services"
   echo "Options:"
   echo "   -h      help: Display this help text"
   echo "   -i      ingest: Ingest Data into Katsu"
   echo "   -s      same: Keep all of the data in one dataset"
}

################################################################################
# Errors                                                                       #
################################################################################
error () 
{
    echo "$1" 1>&2
    exit 1
}

################################################################################
# Script                                                                       #
################################################################################

# TODO: Change Synthea Path to be an Option (-d) instead of Argument
# TODO: Change Base Port to be an Option (-p) instead of Argument
# TODO: Create Option (-r) to reset katsu DB before ingestion 

# Read in the script options
while getopts ":his" opt; do
  case $opt in
    h)  help
        exit 0
        ;;
    i)  to_ingest=1
        ;;
    s)  same_data=1
        ;;
    \?) echo "Invalid option -$OPTARG" >&2
        exit 0
        ;;
  esac
done
shift "$((OPTIND - 1))"

if [ $# -lt 2 ]; 
   then 
   printf "Not enough arguments - entered %d argument(s). Call the script with the -h flag for details.\n" $# 
   exit 0 
fi

# Get Arguments & Set Default Values
SYNTHEA_PATH=$1
NUM_SITES=$2
BASE_PORT=$3

if [ -z to_ingest ]; then
    to_ingest=0
fi

if [ -z same_data ]; then
    same_data=0
fi

if [ -z ${BASE_PORT} ]; then
    BASE_PORT=5000
fi

# Validate Arguments
ls ${SYNTHEA_PATH} 2>/dev/null 1>/dev/null  
SYNTHEA_PATH_CODE=$?

if [ ${SYNTHEA_PATH_CODE} -ne 0 ]; then
    error "There was an error in finding the SYNTHEA_PATH: Error Code ${SYNTHEA_PATH_CODE}"
fi

if ! [[ ${SYNTHEA_PATH} =~ .*/$ ]]; then
    SYNTHEA_PATH="${SYNTHEA_PATH}/"
fi

if ! [[ "${NUM_SITES}" =~ ^[0-9]+$ ]]; then
    error "The argument NUM_SITES must be a non-negative integer. You entered: ${NUM_SITES}"
elif ! [[ ${NUM_SITES} -ge 2 ]]; then
    error "2 or more clients are required to set up the federated-learning service. You entered: ${NUM_SITES}"
fi

if ! [[ "${BASE_PORT}" =~ ^[0-9]*$ ]]; then
    error "The argument BASE_PORT must be a positive integer. You entered ${BASE_PORT}"
elif ! [[ ${BASE_PORT} -ge 1 ]]; then
    error "The argument BASE_PORT must be a greater than 0. You entered ${BASE_PORT}"
fi

# Display Arguments
echo "The following arguments have been provided:"
echo "      SYNTHEA_PATH: ${SYNTHEA_PATH}"
echo "      NUM_SITES: ${NUM_SITES}"
echo "      BASE_PORT: ${BASE_PORT}"
echo

# Create Docker-Compose File
$PWD/orchestration-scripts/configure_docker_compose.py ${BASE_PORT} ${NUM_SITES}

# Start Katsu & GraphQL-interface
echo
docker-compose up -d katsu gql-interface
echo
echo "Sleeping for $SLEEP_TIME seconds to let Docker containers complete initialization process."

sleep ${SLEEP_TIME}

client_path="${PWD}/services/fl-client/"
server_path="${PWD}/services/fl-server/"

# Ingest Data, if necessary
if [ ${to_ingest} -eq 1 ]; then
    # Check to see if Table Files Exist
    if [[ -e "${client_path}tables.txt" ]]; then
        rm "${client_path}tables.txt"
    fi

    # Ingest Data into one Table
    if [[ ${same_data} -eq 1 ]]; then
        echo
        ingestion=$(bash $PWD/ingestion-scripts/init.sh -l -d ${SYNTHEA_PATH} ${PROJECT_NAME} ${DATASET_NAME} ${TABLE_NAME} mcodepacket | tee /dev/tty)

        echo "$ingestion" | grep "TABLE_UUID" >> "${client_path}tables.txt"
        echo "$ingestion" | grep "TABLE_UUID" >> "${server_path}tables.txt"
    else
        # Ingest Data into multiple Tables
        SITE_DIRS=()
        folder_len=$(($(ls -l ${SYNTHEA_PATH} | wc -l) - 1))

        if [ ${folder_len} -ge ${NUM_SITES} ]; then
            split_size=$((${folder_len} / ${NUM_SITES}))

            for ((i=1 ; i <= ${NUM_SITES} ; i++)); do
                SITE_DIRS+=($(mktemp -d))
            done

            counter=0
            for i in ${SYNTHEA_PATH}*; do
                cp "${i}" "${SITE_DIRS[counter]}"
                counter=$((${counter} + 1))

                if [[ counter -ge NUM_SITES ]]; then
                    counter=0
                fi
            done
        fi

        counter=1
        for i in "${SITE_DIRS[@]}"; do
            echo "Folder Name: ${i}"

            ingestion=$(bash $PWD/ingestion-scripts/init.sh -l -d "${i}" "${PROJECT_NAME}-${counter}" "${DATASET_NAME}-${counter}" "${TABLE_NAME}-${counter}" mcodepacket | tee /dev/tty)

            echo "$ingestion" | grep "TABLE_UUID" >> "${client_path}tables.txt"
            echo "$ingestion" | grep "TABLE_UUID" >> "${server_path}tables.txt"

            rm -rf "${i}"

            counter=$((${counter} + 1))
        done
    fi
fi

echo
echo "Sleeping for $SLEEP_TIME seconds to let Docker containers complete the ingestion process."

sleep ${SLEEP_TIME}

echo
docker-compose up -d