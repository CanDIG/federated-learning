#!/bin/bash 
################################################################################
# Constants                                                                    #
################################################################################
SLEEP_TIME=20
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
   echo "   bash ingest_file.sh [options] PROJECT_TITLE DATASET_TITLE TABLE_TITLE WORKFLOW_ID ABSOLUTE_DATAPATH"
   echo "Arguments:"
   echo "   SYNTHEA_PATH      The absolute path of the Synthea breast cancer dataset on your workstation."
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

python3 ./configure_docker_compose.py 5000 2

docker compose up -d


echo "Sleeping for $SLEEP_TIME seconds to let Docker containers complete initialization process."
sleep ${SLEEP_TIME}

proj0=$(bash ./ingestion_scripts/create_project.sh -t katsu-0 ${PROJECT_NAME})
dset0=$(bash ./ingestion_scripts/create_dataset.sh -t katsu-0 ${proj0} ${DATASET_NAME})
table0=$(bash ./ingestion_scripts/create_table.sh -t katsu-0 ${dset0} ${TABLE_NAME} mcodepacket)

proj1=$(bash ./ingestion_scripts/create_project.sh -t katsu-1 ${PROJECT_NAME})
dset1=$(bash ./ingestion_scripts/create_dataset.sh -t katsu-1 ${proj1} ${DATASET_NAME})
table1=$(bash ./ingestion_scripts/create_table.sh -t katsu-1 ${dset1} ${TABLE_NAME} mcodepacket)

echo "The table you should ingest data into on katsu-0 is ${table0}"
echo "The table you should ingest data into on katsu-1 is ${table1}"
echo "Would you like quickstart to attempt to ingest files in ${SYNTHEA_PATH} to katsu-0 and katsu-1? [y/N]"

read res

if [ $res == "y" ]
then
    echo "Proceeding with automatic ingest from folder ${SYNTHEA_PATH}"
    bash ./ingestion_scripts/ingest.sh -t katsu-0 -l -d ${table0} mcode_fhir_json ${SYNTHEA_PATH}
    bash ./ingestion_scripts/ingest.sh -t katsu-1 -l -d ${table1} mcode_fhir_json ${SYNTHEA_PATH}
    echo "Completed ingest attempt. Turning down docker compose services."

    docker compose down
else
    echo "Not ingesting. Turning down docker compose services."
    docker compose down
fi