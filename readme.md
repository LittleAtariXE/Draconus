# DRACONUS

### This code DOES NOT promote or encourage any illegal activities! The content in this document is provided solely for educational purposes, to create awareness and to learning Python!


###  May this be a warning to both you and your family. Don't download software that you don't trust. Only download software from reputable software developers and those you trust.

###### This is beta version and will be upgrade. So sometimes something gonna wrong. 

######  !!!!! Propably works only in a local network !!!!!!!

#### I STRONGLY RECOMMENDED USES RATs and other WORMs only in Virtual Machine. YOU CAN DAMAGE YOUR SYSTEM !!!!!

###### TESTING ON:
 - Windows 7 all service pack and updates - VICTIM
 - Linux Parrot - ATTACKER
 

------------

######  Use this to comipile RAT and WORM
 https://github.com/brentvollebregt/auto-py-to-exe

-------------------------------------------------------------------------

### HOW IT WORK:

##### TEST: TEST: 
	HOST: Parrot - Draconus
	CLIENT: Win7 - worm, rat etc.
	
- Compile rat.py and worm-win7.py. Rename "rat.exe" to "rat-win7.exe" or change value FILE_RAT in "queen.py". Move "rat-win7.exe" to hive directory.
- Run draconus.py
- Draconus is a server will handle victim and worm calls

- On Client machine run "worm-win7.exe"
- Worm will connect to Draconus, recive RAT, save RAT on disk and add to registry autostart. So after reboot client machine, The RAT will be launched and will automatically connect to Draconus. Draconus show menu option.


------------

Project use: Python3.9 , not include any external libraries.


