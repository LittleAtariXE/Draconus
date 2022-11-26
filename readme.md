
This code DOES NOT promote or encourage any illegal activities! The content in this document is provided solely for educational purposes, to create awareness and to learning Python!


 May this be a warning to both you and your family. Don't download software that you don't trust. Only download software from reputable software developers and those you trust.

 This is beta version and will be upgrade. So sometimes something gonna wrong. 

I STRONGLY RECOMMENDED USES RATs and other WORMs only in Virtual Machine. YOU CAN DAMAGE YOUR SYSTEM !!!!!


 TESTING ON:
 - Windows 7 all service pack and updates - WORK !

 Use this to comipile RAT and WORM
 https://github.com/brentvollebregt/auto-py-to-exe

 Use two VM. Host (tested on Linux Parrot) and Client (Windows 7)
 HOW IT WORK:
    Compile both rat.py and worm-win7.py
    "rat.exe" put in hive directory

    Run draconus.py
    Draconus is a server will handle victim and worm calls

    On Client machine run "worm-win7.exe"
    Worm will connect to Draconus, recive RAT, save RAT on disk and add to registry autostart. So after reboot client machine RAT will be start and will automatically connect to Draconus. After connect Draconus show menu option.
    
    NOW only work:
    - Reverse Shell (CMD) TCP   ("cd" change directory command is simple making by me. Work only "cd <path>" !!! "cd .." etc. Not Working !!!)


Project and description will be upgrade
