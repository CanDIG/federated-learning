#!/bin/bash 

################################################################################
# Help                                                                         #
################################################################################
help ()
{
   # Display Help
   echo
   echo "NOTE: OPTIONS MUST PRECEDE ALL ARGUMENTS"
   echo "Creates a project, dataset, and table in Katsu for ingesting into."
   echo "Optionally runs ingest.sh on a specified file or directory."
   echo
   echo "Usage:"
   echo "   ./ingestion-scripts/init.sh [options] PROJECT_TITLE DATASET_TITLE TABLE_TITLE TABLE_TYPE"
   echo "Arguments:"
   echo "   PROJECT_TITLE   The title of the newly created project."
   echo "   DATASET_TITLE   The title of the newly created dataset."
   echo "   TABLE_TITLE     The title of the newly created table."
   echo "   TABLE_TYPE      The type of the newly created table."
   echo "                   Options are [\"phenopacket\" or \"mcodepacket\"]."
   echo "Options:"
   echo "   -h      Display this help text"
   echo "   -d      Run ingest.sh on the specified directory after initialization"
   echo "   -f      Run ingest.sh on the specified file after intitialization"
   echo "   -l      Path to ingestable file/dir is local, ie. located on host filepath rather than in Docker container."
   echo "   -s      Use this flag if you have a custom Katsu server url. Default http://localhost:8000"
   echo "   -t      Specify the ingestion strategy. Currently supports {mcode_json, mcode_fhir_json}. Default: mcode_fhir_json"
}
################################################################################
################################################################################
# Main program                                                                 #
################################################################################
################################################################################

# Creates a project in Katsu
# Outputs the UUID of the created project
_create_project () {
    docker exec -it katsu python /app/chord_metadata_service/ingestion-scripts/create_proj.py $proj_title $server_url
}

# Creates a dataset in Katsu
# Outputs the UUID of the created dataset
_create_dset () {
    docker exec -it katsu python /app/chord_metadata_service/ingestion-scripts/create_dset.py $PROJ_UUID $dset_title $server_url
}
# Creates a dataset in Katsu
# Outputs the UUID of the created table
_create_table () {
    docker exec -it katsu python /app/chord_metadata_service/ingestion-scripts/create_table.py $DSET_UUID $table_title $table_type $server_url
}

################################# Variable default values

server_url="http://localhost:8000"
ingest_strategy="mcode_fhir_json"

################################# Script start

# Read in the script options
while getopts ":hld:f:s:t:" opt; do
  case $opt in
    h)  help
        exit
        ;;
    l)  local=1
        ;;
    d)  ingest_dirpath=$OPTARG
        ;;
    f)  ingest_filepath=$OPTARG
        ;;
    s)  server_url=$OPTARG
        ;;
    t)  ingest_strategy=$OPTARG
        ;;
    \?) echo "Invalid option -$OPTARG" >&2
        ;;
  esac
done
shift $((OPTIND - 1))

if [ $# -lt 4 ]; 
   then 
   printf "Not enough arguments - %d. Call the script with the -h flag for details.\n" $# 
   exit 0 
fi 

# Read in the script arguments
proj_title="$1"
dset_title="$2"
table_title="$3"
table_type="$4"

# TODO remove
echo "The following arguments have been provided:"
echo "proj_title: " $proj_title
echo "dset_title: "$dset_title
echo "table_title: "$table_title
echo "table_type: "$table_type

# Run the initializing script
echo "Creating the project..."
export PROJ_UUID=$(_create_project)
echo
echo "PROJ_UUID: " $PROJ_UUID
echo

echo "Creating the dataset..."
export DSET_UUID=$(_create_dset)
echo
echo "DSET_UUID: " $DSET_UUID
echo

echo "Creating the table..."
export TABLE_UUID=$(_create_table)
echo
echo "TABLE_UUID: " $TABLE_UUID
echo

# If script was run with either of the ingest options, run ingest.sh on the specified file(s)
if [ ! -z "${ingest_filepath}" ]; then
    if (( $local > 0 )); then
        echo "Ingesting local file " $ingest_filepath
        bash ingestion-scripts/ingest.sh -l $TABLE_UUID $ingest_strategy $ingest_filepath
    else
        echo "Ingesting containerized file " $ingest_filepath
        bash ingestion-scripts/ingest.sh $TABLE_UUID $ingest_strategy $ingest_filepath
    fi
elif [ ! -z "${ingest_dirpath}" ]; then
    if (( $local > 0 )); then
        echo "Ingesting local dir " $ingest_dirpath
        bash ingestion-scripts/ingest.sh -l -d $TABLE_UUID $ingest_strategy $ingest_dirpath
    else
        echo "Ingesting containerized dir " $ingest_dirpath
        bash ingestion-scripts/ingest.sh -d $TABLE_UUID $ingest_strategy $ingest_dirpath
    fi
fi

echo
