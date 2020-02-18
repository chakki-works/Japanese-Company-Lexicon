### Parameters ###
DATA="data"
HOJIN="data/hojin"
HOJIN_CSV="data/hojin/csv"
HOJIN_ZIP="data/hojin/zip"
HOJIN_OUTPUT="data/hojin/output"

green=`tput setaf 2`
reset=`tput sgr0`

echo ${green}=== Hojin Data Preparation ===${reset}

### Create directories ###

# corpora, dictionaries
mkdir -p data/corpora/{bccwj,mainichi,output}
mkdir -p data/dictionaries/{ipadic,ipadic-neologd,juman,output}

# model
mkdir ckpts

# hojin data
echo Create Directories...
mkdir -p data/hojin/{csv,zip,output}
echo "  $HOJIN_ZIP, $HOJIN_CSV, $HOJIN_OUTPUT"

echo "Make sure you have downloaded ZIP files to data/hojin/zip"
### Extract Hojin CSV file ###
if [ -z "$(ls -A -- "$HOJIN_ZIP")" ]
then
  echo "$HOJIN_ZIP is empty, make sure the ZIP files are downloaded."
  exit 1
else
  echo "Begin extracting ZIP to CSV files..."
  cd $HOJIN_ZIP 
  unzip "*.zip"
  cd -
  mv $HOJIN_ZIP/*.csv $HOJIN_CSV/ 
  rm $HOJIN_ZIP/*.asc
fi

echo ${green}=== Hojin Data Preparation Done===${reset}