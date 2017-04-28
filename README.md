# Worm
It scans IP addresses for open ssh ports. Once found it will try to crack the password then upload a python file called `happy.py` to the victim's machine. The python file will then encrypt all the documents in the victim's documents folder and cause a fork-bomb which will slow down their system until it crashes.
