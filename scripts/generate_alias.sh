#!/bin/bash

green=`tput setaf 2`
reset=`tput sgr0`

echo ${green}=== Company Alias Generation ===${reset}

echo "Convert CSV to JSONL..."
python tools/convert_csv2jsonl.py

echo "Generate alias..."
python tools/alias_generation.py

echo "Filter alias..."
python tools/jcl_filter.py

echo ${green}=== Company Alias Generation Done ===${reset}
