#!/bin/bash
if [ -z "$TERR" ];
then
  export TERR=$1
fi
python app/print_territory.py $TERR > ~/Desktop/$TERR.txt
open ~/Desktop/$TERR.txt || xed ~/Desktop/$TERR.txt

