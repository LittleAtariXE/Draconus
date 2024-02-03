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


<div id="Whatis" align="center">
    <h2 align="center"> What is "Draconus"? </h2>
    <h5> Draconus is a background-running program. Through another program called "Command Center," we connect to Draconus. Draconus enables the creation of various types of servers. These servers run as separate processes in the background but remain dependent on Draconus. As long as Draconus is running, all servers created by us will keep running.</h5>  
    <h5> The advantage of this setup is that you can safely disconnect from Draconus (using the Command Center), and it will continue to run alongside the servers as "Daemon Processes" in the system. </h5>  
    <h5> Draconus allows you to create an unlimited number of servers (I mean, I didn't introduce any limitations) until your CPU explodes! 😄 Each server is capable of handling connections from multiple clients simultaneously, managing those connections, receiving and sending messages or commands. Feel free to test the endurance of the servers, i.e., how many clients they can handle simultaneously and communicate with.</h5>  
    <h5> You're welcome to test and see how robust these servers are! </h5>
</div>
