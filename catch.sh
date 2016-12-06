#!/bin/bash

PORT=1234
FILE=catcher_save.txt

echo "PORT: $PORT"

function save_output {
echo "SAVING: $FILE"
while true; do
		nc -k -lvp $PORT >> $FILE 2>&1
done

}

function no_save_output {
while true; do
		nc -k -lvp $PORT
done
}

no_save_output

exit 0
