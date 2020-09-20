#!/bin/bash
if [ -z "$TERR" ];
then
  export TERR=$1
fi
python app/print_worksheet.py $TERR
sleep 1
mv "${TERR}.xlsx" ~/Desktop
open -a Finder ~/Desktop
