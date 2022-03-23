#!/bin/bash 
################################################################################
# Constants                                                                    #
################################################################################
SERVER_URL="http://localhost:8000"
KATSU_TAG="katsu"
KATSU_INGESTION_DIR="/app/chord_metadata_service/ingestion_dirs/"
DIRECTORY=false
LOCAL=false

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
   echo "   TABLE_UUID      The uuid of the table to add the data to. To generate a table use the \"create_table.sh\" script."
   echo "   WORKFLOW_ID     The id of the ingest workflow to occur."
   echo "                   Options are [\"phenopackets_json\", \"mcode_json\", \"mcode_fhir_json\"]."
   echo "                   The workflow must be compatible with the table being ingested into."
   echo "                   \"mcode_json\" and \"fhir_mcode_json\" can be ingested into \"mcodepacket\" tables."
   echo "                   \"phenopackets_json\" can be ingested into \"phenopacket\" tables."
   echo "   ABSOLUTE_PATH   The absolute path of the file to ingest on Katsu's Docker container." 
   echo "                   This can be a local path if the '-l' flag is specified."
   echo "Options:"
   echo "   -h      Display this help text"
   echo "   -d      Use this flag if the path being provided specifies a directory of JSON files to ingest."
   echo "   -l      Use this flag if the path being provided is on the local machine rather than the Katsu Docker container."
   echo "   -s      Use this flag if you have a custom server url (default is http://localhost:8000)"
   echo "   -t      Use this flag if you have a custom katsu container tag (default is 'katsu')"
   echo "Returns:"
   echo "   _"
}
################################################################################
################################################################################
# Main program                                                                 #
################################################################################
################################################################################

# Read in the script options
while getopts ":hlds:t:" opt; do
  case $opt in
    h)  help
        exit
        ;;
    l)  LOCAL=true
        ;;
    d)  DIRECTORY=true
        ;;
    s)  SERVER_URL=$OPTARG
        ;;
    t)  KATSU_TAG=$OPTARG
        ;;
    \?) echo "Invalid option -$OPTARG" >&2
        ;;
  esac
done
shift $((OPTIND - 1))

if [ $# -lt 3 ]; 
   then 
   printf "Not enough arguments - %d. Call the script with the -h flag for details.\n" $# 
   exit 0 
fi 
docker exec -it $KATSU_TAG test -d "$KATSU_INGESTION_DIR" # if the ingestion_dirs directory doesn't exist, create it.
success=$?
if [ $success -eq 1 ] ; then
  echo "$KATSU_INGESTION_DIR does not exist, creating now."
  docker exec -it $KATSU_TAG mkdir $KATSU_INGESTION_DIR
fi

# Read in the script arguments
table_uuid="$1"
workflow_id="$2"
absolute_path="$3"

if [ "$LOCAL" = true ] ; then
  echo "local flag specified. Copying path into Docker container."
  basename="$(basename $absolute_path)"
  docker cp $absolute_path $KATSU_TAG:$KATSU_INGESTION_DIR
  absolute_path="$KATSU_INGESTION_DIR$basename" # now absolute_path must be either the user provided Docker path or the script created one.
  echo $absolute_path
fi

if [ "$DIRECTORY" = true ]
then
  echo "directory flag specified."

  for file in $(docker exec -it $KATSU_TAG \ls $absolute_path) ; do # here we loop through all files in the directory path.
    datapath="$absolute_path/$file"
    docker exec -it $KATSU_TAG python /app/chord_metadata_service/ingestion-scripts/ingest_file.py $table_uuid $datapath $SERVER_URL $workflow_id
  done
else
  echo "no directory flag specified."
  docker exec -it $KATSU_TAG python /app/chord_metadata_service/ingestion-scripts/ingest_file.py $table_uuid $absolute_path $SERVER_URL $workflow_id
fi