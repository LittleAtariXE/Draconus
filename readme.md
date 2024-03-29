<div id="Intro">
  <h1 align="center">DRACONUS</h1>
  <p align="center">
    <img src="img/draki.png" alt="Intro">
  </p>
  <p align="center">
    <h3> This code does NOT promote or encourage any illegal activities! The content of this document is for educational purposes only, intended to raise awareness and learn the Python language and in particular the socket module </h3>
    <h3> May this be a warning to both you and your family. Don't download software that you don't trust. Only download software from reputable software developers and those you trust.</h3>
  </p>

</div>

<br/>
<br/>

<div id="toc">
  <h2 align="center">Contents</h2>
  <div align="center">
    <a href="#Intro">Intro</a> &nbsp;|&nbsp;
    <a href="#About">About</a> &nbsp;|&nbsp;
    <a href="#Whatis">What is Draconus</a>  &nbsp;|&nbsp;
    <a href="#How_works">How Works</a>  &nbsp;|&nbsp;
    <br/>
    <h3><a href="#LetsPlay">Let's Play</a></h3>
    <a href="#before">Before Start</a>  &nbsp;|&nbsp;
    <a href="#install">instalation</a>  &nbsp;|&nbsp;
    <a href="#firstrun">First Run</a>  &nbsp;|&nbsp;
    <br>
    <h3><a href="#firstrat">My First RAT</a></h3>
  </div>
</div>





<br/>
<br/>

<div id="About" align="center">
    <h2 allign="center"> ABOUT </h2>
    <h5> I created this project primarily to gain a better understanding of how network sockets work in Python, and also as a fun exploration of Processes and Threads. After many, many... hours of work and testing with network sockets, I can only say one thing: "You can get a serious brain workout!" 😄 </h5>
    <h5> However, it seems to me that I've managed to create servers and clients that, to some extent, can work together (recover connections, avoid hanging, etc.). Nevertheless, strange "things" can still happen, and network sockets may behave in quite peculiar ways. </h5>
    <h5> In any case, I invite you to test and improve this project, as someone else might be able to tame those "network sockets." Good luck!</h5>
    <h5> After many hours of testing, arranging logic, etc., I experienced a 'brain freeze' The problem turned out to be the 'selectors' module, which could hang the socket in a few strange cases. I removed it from the project, and now clients can disconnect, reconnect, and the chance of hanging is very slim. This also applies to servers, which can now enable 'listening', turn it off, and recover connections without any problems.
The 'selectors' module has made it onto my blacklist </h5>
  </div>

<br/>
<br/>

<div id="Whatis" align="center">
    <h2 align="center"> What is "Draconus"? </h2>
    <h5> Draconus is a background-running program. Through another program called "Command Center," we connect to Draconus. Draconus enables the creation of various types of servers. These servers run as separate processes in the background but remain dependent on Draconus. As long as Draconus is running, all servers created by us will keep running.</h5>  
    <h5> The advantage of this setup is that you can safely disconnect from Draconus (using the Command Center), and it will continue to run alongside the servers as "Daemon Processes" in the system. </h5>  
    <h5> Draconus allows you to create an unlimited number of servers (I mean, I didn't introduce any limitations) until your CPU explodes! 😄 Each server is capable of handling connections from multiple clients simultaneously, managing those connections, receiving and sending messages or commands. Feel free to test the endurance of the servers, i.e., how many clients they can handle simultaneously and communicate with.</h5>  
    <h5> You're welcome to test and see how robust these servers are! </h5>
</div>

<div id="How_works">
  <br/>
  <h2 align="center"> How Draco Works </h2>
  <p>Due to its nature, Draconus operates exclusively on the Linux operating system. Because of its use of the Python `multiprocessing` module, this program may not function properly on Windows. However, client-type programmes are mainly designed for Windows. Some simple version (like EchoClient, BasicRat, BasicBot) should work on any platform that has python.<p>
  <p>You can easily compile 'client' type programs (Worms) into EXE format using 'auto-py-to-exe'. Many of them only use standard Python libraries. If the client requires additional libraries for installation, a file with the necessary requirements will be included.</p>

  <p>To run Draconus, you execute it as a background process (e.g., by using the "nohup" command). Draconus and every server it creates run continuously in the background as separate processes, each having its own log file.</p>


<p> **Each server has its own separate log file** and features a "Messenger" responsible for communication with users and logging server events. When working with Draconus, you can see its messages and those of the servers in real-time (courtesy of Messenger). When you disconnect from Draconus, Messenger continues to log messages to the file while buffering them. Upon reconnecting to Draconus, you'll receive all the pending messages that have accumulated since your last connection.</p>
<p>Therefore, even when you're not currently connected to Draconus, you can review messages and events by examining the continuously updated log file.</p>
<p>With Draconus, you connect using the Command Center. Command Center makes use of the "click" and "click-shell" libraries, providing you with a command-line interface with commands, parameters, and help. The console has two levels. The first level is where you interact with Draconus, creating servers, starting, closing, exporting, and performing other actions. The second console level operates after connecting to a previously created server. Each server may have slightly different commands, depending on its specifications (a "help" command is always available with a list of commands). From this level, you can also send messages and commands to connected clients on the server.</p>
<p>Draconus generates ready-to-use clients for each server; all you need to do is start them. Messages sent between clients and the server are not yet fully encrypted (I'm working on it), and they currently undergo a simple message format transformation to "Base64." Special messages are additionally padded with randomly generated character strings (similar to headers) to confuse potential eavesdroppers. Of course, everything is configurable, but if you don't want to delve into the details, you don't have to. Draconus is designed to work very well with default settings. The only thing you need to set in the configuration is your IP address, which can be found in the "CONFIG.ini" file.</p>
<p>Draconus can also be started as a regular program using the command "python3 Draconus.py." In this case, you'll need to open a second terminal to run the "Command Center."</p>

</div>

<div id="LetsPlay">
  <h2 align="center"> Let's Play</h2>
  <p align="center">
    <img src="img/d3.jpg" alt="Draconus">
  </p>
</div>

<div id="before" align="center">
  <h2>Before Start</h2>
  <p><b>I STRONGLY RECOMMENDED: Uses Draconus and clients only in Virtual Machine. You can serious DAMAGE your System</b></p>
  <p>Some Clients can perform unauthorized port scan, "http_flood" and other attack. YOU ARE RESPONSIBLE FOR USING THIS TOOL CORRECTLY !!!</p>
  <p>Don't attack other users' sites or infect their systems !!!!</p>
</div>

<br/>

<div id="install">
  <h2 align="center">Installation</h2>

  **Basic Requirements:**

- Linux Operating System (tested on Parrot and Kali)
- Python 3.11.2

1. Clone the repo
   ```sh
   git clone https://github.com/LittleAtariXE/Draconus
   ```
2. Change directory
   ```sh
   cd Draconus
   ```
3. Install requirements
   ```sh
   pip install -r requirements.txt
   ```
</div>
<br/>


<div id="firstrun">
  <h2 align="center">First Run</h2>

   **First steps:**
   
1. Navigate to the "Draconus" directory using the command:
  ```sh
  cd Draconus
  ```

2. If you wish to change the default IP address of the servers you create, you must edit the CONFIG.ini file.
   <br/>
   In the CONFIG.py file, you will find numerous parameters such as code formatting, length of received packets, etc. If you wish, you can experiment with different settings. If something doesn't work as expected, you can adjust them. However, the only parameter you really need to concern yourself with is "DEFAULT_IP."
   <p></p>
   The second important parameter in the configuration file is MSG_NO_IMPORTANT, which is responsible for displaying additional messages from servers and clients. If you set this parameter to 'yes', you will not receive many messages such as connection termination, disconnection, start of each downloaded file, etc. At the beginning of your adventure, I recommend setting this parameter to 'no' to know exactly what is happening in the program. When you operate on many servers with many connected parameters, work can be complicated by an excessive amount of information.
    You don't need to worry about the rest.


  ```sh
  nano app/CONFIG.ini
  ```
<p align="center">
    <img src="img/nconf.png" alt="Config_File">
  </p>
  
3. Use the `nohup` command to run programs in the background. Execute the command:
  ```sh
  nohup python3 Draconus.py &
  ```

<p>When you launch Draconus, a directory named 'DRACO_FILES' will be created in the main directory. It contains the following directories:
  <br>
<b>_sockets</b> - Draconus and Servers keep their files here (it's better not to touch anything here)<br>
<b>OUTPUT</b> - This is where the log files of Draconus and the Servers are located. It is also the place for files downloaded from clients.<br>
<b>HIVE</b> - Clients created to work with the server will appear here. As the 'Queen' hatches 'Worms', they will be placed here.<br>
<b>EXTRAS</b> - a place where saved servers are located<br>
<b>PAYLOAD</b> - we place files, scripts, etc. here that we will want to send to clients.</p><br>
<p>When you run the command `ps aux | grep python3`, you should see the "Draconus" process in the list of active processes, indicating that it is running in the background. If you wish, you can explore the "DRACO_FILES/OUTPUT" directory where log files are located, allowing you to review them in real-time.</p>
<br>
<p align="center">
    <img src="img/dracoPS.png" alt="Draco_Process">
  </p>
4. So, Draconus operates in the background until you kill the process or send a command to shut it down. To connect to Draconus, we'll be using the so-called "Command Center." This program is written using the "Click" library, so it mimics a console. The HELP command is always available, and many commands have additional help accessible via "--help." The operation principles resemble a system console: there are commands and parameters, and by using the "UP" and "DOWN" keys, you can access the command history.
<br>
5. When you exit the "Command Center," Draconus and all the created servers will continue running in the background. Therefore, you can easily run Draconus even on a VPS and connect via SSH, launching the Command Center.
  To start the Command Center, use the command:
  <br>
   
  ```sh
  python3 CC_Start.py
  ```

<br>
<p align="center">
    <img src="img/cc_start.png" alt="CC_Start">
  </p>
<p> Put 'help' for command list</p>
<p align="center">
    <img src="img/draco_help.png" alt="Help Function">
  </p>
</div>

<div id="firstrat">
  <h2 align="center">My First RAT</h2>
  <p>We will create a simple server to operate and create "RATs"</p>
<p>Servers are created according to the scheme: "make NAME SERVER_TYPE PORT_NUMBER"</p>

<p><b>NAME</b> - Invent a name for the server. Do not use spaces.</p>
<p><b>SERVER_TYPE</b> - Here, we need to choose the type of server we will be creating. To get a list of available types, type the command "show -t".</p>
<p><b>PORT_NUMBER</b> - The port on which the server will listen. The recommended choice of ports is: 1000 - 9999.</p>
<p>To the "make" command, you can also add various parameters, their list can be obtained with the command "make --help".</p>
<br>
<p align="center">
    <img src="img/frat.png" alt="make Server">
  </p>

<p>When the server is created, we will see the appropriate messages. If the server has the "http" option enabled, you can view its brief description through a web browser, such as configuration, number of connected clients, etc.
The "http" option can be set in the CONFIG.ini file.</p>
<p>The next step will be to call the "hive" command, which will create a ready-to-use client for us. Each server creates clients ready to operate and configured for a specific server. You just need to run or compile it.</p>
<br>
<p align="center">
    <img src="img/queen.png" alt="make client">
  </p>
<p>Run the ready client on a different system (preferably Windows), if you want, some of the "clients" can be run on the same machine.
After launching, the client will not connect but will continuously attempt to establish a connection.
To start accepting connections on the server, you need to set it to "listen" mode. This can be done in two ways: by issuing a command from the "draconus" console, this command is "<b>start</b>". The second method is to connect directly to the server console through the "<b>conn</b>" command. In our example, it would be "<b>conn myServ</b>". You will gain access to the server console, issue the "<b>start</b>" command there, which will put the server in listen mode and start accepting connections.
If you want to stop listening, issue the "<b>stop</b>" command. The server will disconnect the clients and rebuild the "socket". You can repeatedly turn "listen" mode on and off. Clients and Servers are designed to re-establish connection.</p>
<br>
<p align="center">
    <img src="img/rcmd.png" alt="execute command">
  </p>
<p>When we receive a connection from a client, we can see their ID number by issuing the "show" command. Through the ID number, we will identify the clients. In this case, commands are issued according to the scheme: "msg CLIENT_ID COMMAND"</p>

<p><b>CLIENT_ID</b> - the number of the connected client</p>
<p><b>COMMAND</b> - the console command, depending on whether it is Windows or Linux</p>
<p>If you are sending a command that contains spaces, place it in quotation marks "".</p>
</div>


