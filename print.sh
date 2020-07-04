#!/bin/bash
TERR=$1
python app/print_territory.py $1 > ~/Desktop/$1.txt
open ~/Desktop/$1.txt

