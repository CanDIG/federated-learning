#!/bin/bash 
################################################################################
# Constants                                                                    #
################################################################################
SERVER_URL="http://localhost:8000"
KATSU_TAG="katsu"
################################################################################
# Help                                                                         #
################################################################################
help ()
{
   # Display Help
   echo
   echo "NOTE: OPTIONS MUST PRECEDE ALL ARGUMENTS"
   echo "Creates a project in Katsu."
   echo
   echo "Usage:"
   echo "   bash create_project.sh [options] PROJECT_TITLE"
   echo "Arguments:"
   echo "   PROJECT_TITLE     The title of the newly created project."
   echo "Options:"
   echo "   -h      Display this help text"
   echo "   -s      Use this flag if you have a custom server url (default is http://localhost:8000). This is the url on the katsu Docker container, not the local machine."
   echo "   -t      Use this flag if you are ingesting into a container not tagged 'katsu' and provide said tag."
   echo "Returns:"
   echo "   _"
}
################################################################################
################################################################################
# Main program                                                                 #
################################################################################
################################################################################

# Read in the script options
while getopts "hs:t:" opt; do
  case $opt in
    h)  help
        exit
        ;;
    s) SERVER_URL=$OPTARG
        ;;
    t) KATSU_TAG=$OPTARG
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

# Read in the script arguments
proj_title="$1"

docker exec -it $KATSU_TAG python /app/chord_metadata_service/ingestion-scripts/create_proj.py $proj_title $SERVER_URL