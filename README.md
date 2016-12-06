# Basic_Bash_Script_Repository
## A simple botnet made for a capture the flag game based on Mafia-2007
Servers run Unbuntu 7.10

The ctf_sploiting.py script utilizes two code execution vulnerabilities to download the exp.sh script
After executing the exp.sh it uses a privaledge exploit to obtain root and re-download itself and all tools as root
All tools and activities are done in /dev/shm/.tools/
When cmnd.sh is executed (from the first run of exp.sh) the 'cmnd.sh -c' command is inserted into /etc/crontab directly and ran every minute
'cmnd.sh -c' grabs a file from the server called: file_[last 3 digits of IP]; and then executes every line/command of that file as root

### List of exploits used
Local Privaledge Escalation: https://www.exploit-db.com/exploits/9545/
Remote Code Execution:	https://www.exploit-db.com/exploits/34900/
Remote Code Execution: https://www.exploit-db.com/exploits/29290/
