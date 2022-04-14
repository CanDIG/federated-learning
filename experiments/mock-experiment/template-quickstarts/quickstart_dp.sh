#! /usr/bin/env bash

# Modified from Rishabh's quickstart.sh file present in the experiments/synthea-breast-cancer/fall2021/Federated directory

################################################################################
# Constants                                                                    #
################################################################################
SLEEP_TIME=40
PROJECT_NAME="experiment-project"	
DATASET_NAME="experiment-dataset"	
TABLE_NAME="experiment-table"
# Script Kill Constants
export TOP_PID=$$
trap "exit 1" TERM

################################################################################
# Help                                                                         #
################################################################################

# Output Help menu to the screen
help ()
{
   # Display Help
   echo
   echo "NOTE: OPTIONS MUST PRECEDE ALL ARGUMENTS"
   echo "Starts an instance of the differentially-private federated-learning environment with sample data stored locally"
   echo "Start this program from the root directory of the federated-learning repo"
   echo
   echo "Usage:"
   echo "   ./quickstart.sh [options]"
   echo "Options:"
   echo "   -i <INGEST_PATH>               Ingest Data present at Path into Katsu"
   echo "   -p <PORT>                      Specify Port Number to expose. Defaults to 5000"
   echo "   -n <SITES>                     Number of Sites to federate. Defaults to 2"
   echo "   -r <ROUNDS>                    Number of rounds of trials to conduct. Defaults to 100."
   echo "   -e <EXPERIMENT_PATH>           Pass in the path to the experiment folder. Defaults to ./experiment in the root folder. Ensure this path is either an absolute path, or that it starts with './'"
   echo "   -f <FEDERATED_EXPERIMENT_PATH> Pass in the path to the experiment folder of the federated trial. Defaults to ./experiment in the root folder. Ensure this path is either an absolute path, or that it starts with './'"
   echo "   -s                             Keep all of the data in one dataset - Useful only if -i specified"
   echo "   -h                             Display this help text"
}

################################################################################
# Errors                                                                       #
################################################################################

# Output Error Message and exit
error () 
{
    echo "$1" 1>&2
    kill -s TERM $TOP_PID
}

################################################################################
# Helper Functions                                                             #
################################################################################

# Check to see if the ingestion path is valid
check_path()
{
    DATASET_PATH=${1}
    
    if [[ ${DATASET_PATH} =~ ^-.* ]]; then
        error "The path '${DATASET_PATH}' cannot be an option"
    fi

    ls ${DATASET_PATH} 2>/dev/null 1>/dev/null  
    DATASET_PATH_CODE=$?

    if [[ ${DATASET_PATH_CODE} -ne 0 ]]; then
        error "There was an error in finding the path '${DATASET_PATH}': Error Code ${DATASET_PATH_CODE}"
    fi

    if ! [[ ${DATASET_PATH} =~ .*/$ ]]; then
        DATASET_PATH="${DATASET_PATH}/"
    fi

    echo ${DATASET_PATH}
}

# Check to see if number entered is positive integer
check_positive()
{
    NUM=${1}
    ARG_NAME=${2}

    if ! [[ "${NUM}" =~ ^[0-9]*$ ]]; then
        error "The option ${ARG_NAME} must be a positive integer. You entered ${NUM}"
    elif ! [[ ${NUM} -ge 1 ]]; then
        error "The option ${ARG_NAME} must be greater than 0. You entered ${NUM}"
    fi

    echo ${NUM}
}

# Check to see if the passed in port is valid
check_port()
{
    BASE_PORT=${1}
    echo $(check_positive ${BASE_PORT} -p)
}

# Check to see if the number of rounds is valid
check_rounds()
{
    ROUNDS=${1}
    echo $(check_positive ${ROUNDS} -r)
}

# Check to see if the number of sites is valid
check_sites()
{
    NUM_SITES=${1}

    if ! [[ "${NUM_SITES}" =~ ^[0-9]+$ ]]; then
        error "The option -n must be a non-negative integer. You entered: ${NUM_SITES}"
    elif ! [[ ${NUM_SITES} -ge 2 ]]; then
        error "2 or more clients are required to set up the federated-learning service. You entered: ${NUM_SITES}"
    fi

    echo ${NUM_SITES}
}

# Check to see if value is empty, and if so, replace it with a passed in default
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
while getopts ":i:p:n:r:e:f:sh" opt; do
  case $opt in
    i)  DATASET_PATH=$(check_path ${OPTARG})
        TO_INGEST=1
        ;;
    p)  BASE_PORT=$(check_port ${OPTARG})
        ;;
    n)  NUM_SITES=$(check_sites ${OPTARG})
        ;;
    r)  ROUNDS=$(check_rounds ${OPTARG})
        ;;
    e)  EXPERIMENT_PATH=$(check_path ${OPTARG})
        ;;
    f)  FEDERATED_EXPERIMENT_PATH=$(check_path ${OPTARG})
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
DATASET_PATH=$(check_value ${DATASET_PATH} "NOT INGESTING DATA")
SAME_DATA=$(check_value ${SAME_DATA} 0)
BASE_PORT=$(check_value ${BASE_PORT} 5000)
NUM_SITES=$(check_value ${NUM_SITES} 2)
TO_INGEST=$(check_value ${TO_INGEST} 0)
ROUNDS=$(check_value ${ROUNDS} 100)
EXPERIMENT_PATH=$(check_path $(check_value ${EXPERIMENT_PATH} ./experiment))
FEDERATED_EXPERIMENT_PATH=$(check_path $(check_value ${FEDERATED_EXPERIMENT_PATH} ./experiment))

# Display Arguments
echo "The following values have been selected:"
echo "      INGESTION PATH: ${DATASET_PATH}"
echo "      NUMBER OF SITES: ${NUM_SITES}"
echo "      BASE PORT: ${BASE_PORT}"
echo "      NUMBER OF ROUNDS: ${ROUNDS}"
echo "      EXPERIMENT PATH: ${EXPERIMENT_PATH}"
echo "      FEDERATED EXPERIMENT PATH: ${FEDERATED_EXPERIMENT_PATH}"

# Create Docker-Compose File
echo
$PWD/orchestration-scripts/configure_docker_compose.py ${BASE_PORT} ${NUM_SITES} ${ROUNDS} ${EXPERIMENT_PATH}

# Modify Docker-Compose File to remove experiment folder bind mount
echo
$PWD/orchestration-scripts/remove_bind_mounts.py -e

# Start Katsu & GraphQL-interface
echo
docker-compose up -d katsu gql-interface
echo
echo "Sleeping for $SLEEP_TIME seconds to let Docker containers complete initialization process."

sleep ${SLEEP_TIME}

TABLE_PATH="${EXPERIMENT_PATH}helpers/"

# Ingest Data, if necessary
if [[ ${TO_INGEST} -eq 1 ]]; then
    # Check to see if Table Files Exist
    if [[ -e "${TABLE_PATH}tables.txt" ]]; then
        rm "${TABLE_PATH}tables.txt"
    fi

    # Ingest Data into one Table
    if [[ ${SAME_DATA} -eq 1 ]]; then
        echo
        ingestion=$(bash $PWD/ingestion-scripts/init.sh -l -d ${DATASET_PATH} ${PROJECT_NAME} ${DATASET_NAME} ${TABLE_NAME} mcodepacket | tee /dev/tty)

        echo "$ingestion" | grep "TABLE_UUID" >> "${TABLE_PATH}tables.txt"
    else
        # Ingest Data into multiple Tables
        SITE_DIRS=()
        DATA_LEN=$(($(ls -l ${DATASET_PATH} | wc -l) - 1))

        # Copy Data into temporary folders
        if [[ ${DATA_LEN} -ge ${NUM_SITES} ]]; then
            for ((i=1 ; i <= ${NUM_SITES} ; i++)); do
                SITE_DIRS+=($(mktemp -d))
            done

            COUNTER=0
            for i in ${DATASET_PATH}*; do
                cp "${i}" "${SITE_DIRS[COUNTER]}"
                COUNTER=$((${COUNTER} + 1))

                if [[ COUNTER -ge NUM_SITES ]]; then
                    COUNTER=0
                fi
            done
        fi

        # Ingest Data and delete temporary folders
        COUNTER=1
        for i in "${SITE_DIRS[@]}"; do
            echo "Folder Name: ${i}"

            ingestion=$(bash $PWD/ingestion-scripts/init.sh -l -d "${i}" "${PROJECT_NAME}-${COUNTER}" "${DATASET_NAME}-${COUNTER}" "${TABLE_NAME}-${COUNTER}" mcodepacket | tee /dev/tty)

            echo "$ingestion" | grep "TABLE_UUID" >> "${TABLE_PATH}tables.txt"

            rm -rf "${i}"

            COUNTER=$((${COUNTER} + 1))
        done
    fi

    echo
    echo "Sleeping for ${SLEEP_TIME} seconds to let Docker containers complete the ingestion process."

    sleep ${SLEEP_TIME}
fi

# Add Experiment to Containers
echo
docker-compose up -d

## Kill All Running FL-* containers
all_containers="$(docker ps -a | grep fl- | awk '{print $1;}')"
docker kill ${all_containers} 1>/dev/null

## Create Temp Directory
temp_folder="$(mktemp -d)"

## Transfer Files from Federated Experiment to Temp Folder
for file in ${FEDERATED_EXPERIMENT_PATH}*; do
    cp -r "${file}" "${temp_folder}"
done

## Transfer Files from Diff-Priv Experiment to Temp Folder
for file in ${EXPERIMENT_PATH}*; do
    cp -r "${file}" "${temp_folder}"
done

## Transfer Temp Folder to all fl-* Containers
for container in ${all_containers}; do
    docker cp "${temp_folder}" "${container}:/src/experiment"
done

## Delete Temp Folder
rm -rf "${temp_folder}"

# Start all services
echo
docker-compose up -d