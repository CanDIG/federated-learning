#!/bin/bash 
################################################################################
# Constants                                                                    #
################################################################################
SERVER_URL="http://localhost:8000"

################################################################################
# Help                                                                         #
################################################################################
help ()
{
   # Display Help
   echo
   echo "NOTE: OPTIONS MUST PRECEDE ALL ARGUMENTS"
   echo "Creates a table in Katsu given an existing dataset's uuid."
   echo
   echo "Usage:"
   echo "   bash create_table.sh [options] DATASET_UUID TABLE_TITLE TABLE_TYPE"
   echo "Arguments:"
   echo "   DATASET_UUID    The uuid of the dataset to add the table to. To generate a dataset use the \"create_dataset.sh\" script."
   echo "   TABLE_TITLE     The title of the newly created table."
   echo "   TABLE_TYPE      The type of the newly created table."
   echo "                   Options are [\"phenopacket\" or \"mcodepacket\"."
   echo "Options:"
   echo "   -h      Display this help text"
   echo "   -s      Use this flag if you have a custom server url (default is http://localhost:8000)"
   echo "Returns:"
   echo "   _"
}
################################################################################
################################################################################
# Main program                                                                 #
################################################################################
################################################################################

# Read in the script options
while getopts ":hs:" opt; do
  case $opt in
    h)  help
        exit
        ;;
    s)  echo $OPTARG
        SERVER_URL=$OPTARG
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

# Read in the script arguments
dset_uuid="$1"
table_title="$2"
table_type="$3"

docker exec -it katsu python /app/chord_metadata_service/ingestion_scripts/create_table.py $dset_uuid $table_title $table_type $SERVER_URL