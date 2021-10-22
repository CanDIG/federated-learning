project_title=$1
dataset_title=$2
table_title=$3
server_url=$4
data_type=$5
mcode_ingestion_type=$6
data_dir=$7

# table_uuid=`docker exec -it katsu python /app/chord_metadata_service/scripts/create_table.py $1 $2 $3 $4 $5`
uuid_cr=$(docker exec -it katsu python /app/chord_metadata_service/ingestion_scripts/create_table.py $1 $2 $3 $4 $5 | tail -1)
uuid=$(echo $uuid_cr | tr -d '\r')
docker exec -it katsu python /app/chord_metadata_service/ingestion_scripts/ingest_dir.py $uuid $data_dir $server_url $data_type $mcode_ingestion_type
