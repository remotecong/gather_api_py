#!/bin/bash
if [ -z "$TERR" ];
then
  export TERR=$1
fi
#python app/print_helper_worksheet.py $TERR
python app/print_new_template.py $TERR
mv "${TERR}.xlsx" ~/git/gather-py/out/
# open -a Finder ~/Desktop
