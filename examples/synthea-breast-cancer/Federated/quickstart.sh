#!/bin/bash 
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
   echo "Ingests a file or directory into an existing, compatible table in Katsu's data service."
   echo
   echo "Usage:"
   echo "   bash ingest_file.sh [options] PROJECT_TITLE DATASET_TITLE TABLE_TITLE WORKFLOW_ID SYNTHEA_PATH NUM_SITES"
   echo "Arguments:"
   echo "   SYNTHEA_PATH      The absolute path of the Synthea breast cancer dataset on your workstation."
   echo "   NUM_SITES         The number of federated learning sites/clients to generate"
   echo "Options:"
   echo "   -h      Display this help text"
}
################################################################################
################################################################################
# Main program                                                                 #
################################################################################
################################################################################

# Read in the script options
while getopts ":h" opt; do
  case $opt in
    h)  help
        exit
        ;;
    \?) echo "Invalid option -$OPTARG" >&2
        ;;
  esac
done
shift $((OPTIND - 1))

if [ $# -lt 1 ]; 
   then 
   printf "Not enough arguments - %d. Call the script with the -h flag for details.\n" $# 
   exit 0 
fi

SYNTHEA_PATH=$1
NUM_SITES=$2
echo "The following arguments have been provided:"
echo "      SYNTHEA_PATH: ${SYNTHEA_PATH}"
echo "      NUM_SITES: ${NUM_SITES}"

python3 ./configure_docker_compose.py 5000 ${NUM_SITES}

docker-compose up -d


echo "Sleeping for $SLEEP_TIME seconds to let Docker containers complete initialization process."
sleep ${SLEEP_TIME}

# Create arrays to contain the uuids of the new projects, datasets, and tables
# The contents of these arrays will be indexed by the numbered site that the uuid pertains to
# ie. a project injested into katsu-1 will have it's uuid stored in ${proj_uuids[1]}
proj_uuids=()
dset_uuids=()
table_uuids=()

echo "Generating a project, dataset, and table into each katsu instance. The following names will be used:"
echo "      PROJECT_NAME: ${PROJECT_NAME}"
echo "      DATASET_NAME: ${DATASET_NAME}"
echo "      TABLE_NAME: ${TABLE_NAME}"
for ((s=0; s<$NUM_SITES; s++))
do
    proj_uuids+=($(bash ./ingestion_scripts/create_project.sh -t katsu-${s} ${PROJECT_NAME}))
    dset_uuids+=($(bash ./ingestion_scripts/create_dataset.sh -t katsu-${s} ${proj_uuids[${s}]} ${DATASET_NAME}))
    table_uuids+=($(bash ./ingestion_scripts/create_table.sh -t katsu-${s} ${dset_uuids[${s}]} ${TABLE_NAME} mcodepacket))

    echo "The table you should ingest data into on katsu-${s} is ${table_uuids[${s}]}"
done

echo "Would you like quickstart to attempt to ingest files in ${SYNTHEA_PATH} into all katsu instances? [y/N]"

read res

if [ $res == "y" ]
then
    echo "Proceeding with automatic ingest from folder ${SYNTHEA_PATH}"
    for ((s=0; s<$NUM_SITES; s++))
    do
        bash ./ingestion_scripts/ingest.sh -t katsu-${s} -l -d ${table_uuids[${s}]} mcode_fhir_json ${SYNTHEA_PATH}
        echo "Completed attempt to ingest into katsu-${s}. Migrating its database..."
        docker-compose up -d katsu-${s}
    done
    echo "Sleeping for $SLEEP_TIME seconds to let katsu instances complete migration."
    sleep ${SLEEP_TIME}
    echo "Completed all ingest and migration attempts. Turning down docker compose services."

    docker-compose down
else
    echo "Not ingesting. Turning down docker compose services."
    docker-compose down
fi