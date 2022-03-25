#! /usr/bin/env bash

# Modified from Rishabh's quickstart.sh file present in the experiments/synthea-breast-cancer/fall2021/Federated directory

################################################################################
# Constants                                                                    #
################################################################################
SLEEP_TIME=40
PROJECT_NAME="synthea-project"
DATASET_NAME="synthea-dataset"
TABLE_NAME="synthea-table"

# Script Kill Constants
export TOP_PID=$$
trap "exit 1" TERM

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
   echo "   ./quickstart.sh [options]"
   echo "Options:"
   echo "   -i <PATH>     Ingest Data present at Path into Katsu"
   echo "   -p <PORT>     Specify Port Number to expose. Defaults to 5000"
   echo "   -n <SITES>    Number of Sites to federate. Defaults to 2"
   echo "   -s            Keep all of the data in one dataset - Useful only if -i specified"
   echo "   -h            Display this help text"
}

################################################################################
# Errors                                                                       #
################################################################################
error () 
{
    echo "$1" 1>&2
    kill -s TERM $TOP_PID
}

################################################################################
# Helper Functions                                                             #
################################################################################
check_path()
{
    SYNTHEA_PATH=${1}
    
    if [[ ${SYNTHEA_PATH} =~ ^-.* ]]; then
        error "The ingestion PATH '${SYNTHEA_PATH}' cannot be an option"
    fi

    ls ${SYNTHEA_PATH} 2>/dev/null 1>/dev/null  
    SYNTHEA_PATH_CODE=$?

    if [[ ${SYNTHEA_PATH_CODE} -ne 0 ]]; then
        error "There was an error in finding the ingestion PATH '${SYNTHEA_PATH}': Error Code ${SYNTHEA_PATH_CODE}"
    fi

    if ! [[ ${SYNTHEA_PATH} =~ .*/$ ]]; then
        SYNTHEA_PATH="${SYNTHEA_PATH}/"
    fi

    echo ${SYNTHEA_PATH}
}

check_port()
{
    BASE_PORT=${1}

    if ! [[ "${BASE_PORT}" =~ ^[0-9]*$ ]]; then
        error "The argument PORT must be a positive integer. You entered ${BASE_PORT}"
    elif ! [[ ${BASE_PORT} -ge 1 ]]; then
        error "The argument PORT must be greater than 0. You entered ${BASE_PORT}"
    fi

    echo ${BASE_PORT}
}

check_sites()
{
    NUM_SITES=${1}

    if ! [[ "${NUM_SITES}" =~ ^[0-9]+$ ]]; then
        error "The option SITES must be a non-negative integer. You entered: ${NUM_SITES}"
    elif ! [[ ${NUM_SITES} -ge 2 ]]; then
        error "2 or more clients are required to set up the federated-learning service. You entered: ${NUM_SITES}"
    fi

    echo ${NUM_SITES}
}

check_value()
{
    value=${1}
    default=${2}

    if [[ -z ${value} ]]; then
        value=${default}
    fi

    echo ${value}
}

################################################################################
# Script                                                                       #
################################################################################

# Read in the script options
while getopts ":i:p:n:sh" opt; do
  case $opt in
    i)  SYNTHEA_PATH=$(check_path ${OPTARG})
        to_ingest=1
        ;;
    p)  BASE_PORT=$(check_port ${OPTARG})
        ;;
    n)  NUM_SITES=$(check_sites ${OPTARG})
        ;;
    s)  SAME_DATA=1
        ;;
    h)  help
        exit 0
        ;;
    \?) echo "Invalid option -$OPTARG" >&2
        exit 0
        ;;
  esac
done
shift "$((OPTIND - 1))"

# Get Argument Values & Set Defaults
SYNTHEA_PATH=$(check_value ${SYNTHEA_PATH} "NOT INGESTING DATA")
SAME_DATA=$(check_value ${SAME_DATA} 0)
BASE_PORT=$(check_value ${BASE_PORT} 5000)
NUM_SITES=$(check_value ${NUM_SITES} 2)

# Display Arguments
echo "The following arguments have been provided:"
echo "      SYNTHEA_PATH: ${SYNTHEA_PATH}"
echo "      NUM_SITES: ${NUM_SITES}"
echo "      BASE_PORT: ${BASE_PORT}"

# Create Docker-Compose File
echo
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
if [[ ${to_ingest} -eq 1 ]]; then
    # Check to see if Table Files Exist
    if [[ -e "${client_path}tables.txt" ]]; then
        rm "${client_path}tables.txt"
    fi

    # Ingest Data into one Table
    if [[ ${SAME_DATA} -eq 1 ]]; then
        echo
        ingestion=$(bash $PWD/ingestion-scripts/init.sh -l -d ${SYNTHEA_PATH} ${PROJECT_NAME} ${DATASET_NAME} ${TABLE_NAME} mcodepacket | tee /dev/tty)

        echo "$ingestion" | grep "TABLE_UUID" >> "${client_path}tables.txt"
        echo "$ingestion" | grep "TABLE_UUID" >> "${server_path}tables.txt"
    else
        # Ingest Data into multiple Tables
        SITE_DIRS=()
        folder_len=$(($(ls -l ${SYNTHEA_PATH} | wc -l) - 1))

        if [[ ${folder_len} -ge ${NUM_SITES} ]]; then
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

    echo
    echo "Sleeping for $SLEEP_TIME seconds to let Docker containers complete the ingestion process."

    sleep ${SLEEP_TIME}
fi

echo
docker-compose up -d