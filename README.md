# Basic_Bash_Script_Botnet
## A simple (very detectable) botnet made for a capture the flag game based on Mafia-2007
Servers are running Unbuntu 7.10

- The ctf_sploiting.py script utilizes two code execution vulnerabilities to download the exp.sh script
- After executing the exp.sh it uses a privaledge exploit to obtain root and re-download itself and all tools as root
  - All tools and activities are done in /dev/shm/.tools/
- When cmnd.sh is executed (from the first run of exp.sh) the 'cmnd.sh -c' command is inserted into /etc/crontab directly and ran every minute
- 'cmnd.sh -c' grabs a file from the server called: file_[last 3 digits of IP]; and then executes every line/command of that file as root
  - Probably overkill to send commands through the priv-esc, since crontab runs as root, but that's what happens coding in the 'am
- 'dump.sh' calls all the locations of the flags and dumps them to a file

### List of exploits used
- Local Privilege Escalation: Linux Kernel 2.4.x / 2.6.x - 'sock_sendpage()' https://www.exploit-db.com/exploits/9545/
- Remote Code Execution:	Apache mod_cgi - Remote Exploit (Shellshock) https://www.exploit-db.com/exploits/34900/
- Remote Code Execution: Apache + PHP < 5.3.12 / < 5.4.2 - cgi-bin https://www.exploit-db.com/exploits/29290/
