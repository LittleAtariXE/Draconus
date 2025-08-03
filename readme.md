<!DOCTYPE markdown>
<html>
<head>
</head>
<body>

<div id="Draconus">
    <h1 align="center">Draconus</h1>
    <p align="center">
        <img src="img/logo1.webp" alt="Logo Projektu" width="300">
    </p>
    <h4 align="center">Every USER should have a Cyber Weapon to defend himself.</h4>
    <p align="center">This project serves as a comprehensive toolkit designed to introduce fundamental concepts in ethical hacking and malware creation. It offers tools and functionalities for creating shellcodes, basic malware, code obfuscation, and code packing into single lines, providing an engaging way to explore malware techniques responsibly.</p>
    <h2>Features and Advantages</h2>
    <ul>
        <li><strong>Shellcode Generation</strong>: Create custom shellcodes for testing and experimentation.</li>
        <li><strong>Simple Malware Creation</strong>: Build your own malware and choose the modules yourself.</li>
        <li><strong>Various Code Obfuscation Methods</strong>: Additional modules responsible for code obfuscation.</li>
        <li><strong>Cross Compilation</strong>: Capability to build ready-to-use EXE and DLL files from a Linux environment.</li>
        <li><strong>Python Cross Compilation</strong>: Capability to create ready-to-use EXE files using Nuitka and PyInstaller from a Linux environment.</li>
        <li><strong>Built-in C2</strong>: Ability to create various server types supporting multiple simultaneous connections.</li>
        <li><strong>Special Compilation Scripts</strong>: Ability to add information to compiled files using a database.</li>
    </ul>
<div>
<div id="Disclaimer">
    <h2>Disclaimer</h2>
    <p>
    <strong>This toolkit is developed solely for ethical and educational purposes to deepen understanding of malware creation and analysis. Using this tool to target other users, conduct attacks without prior consent, or apply it in unauthorized environments is strictly forbidden. The responsibility for proper use rests entirely on the user. Caution is advised! Misuse could harm your system or other users. We highly recommend using this tool within isolated virtual machines.</strong>
    </p>
</div>
<div id="Warning">
    <h2>⚠️ Important Warning</h2>
    <p><strong>It is highly recommended to use Draconus and any worms you create in isolated virtual machines with a dedicated network.</strong></p>
    <p>Some modules, such as <code>PyVir</code> or <code>Panther</code>, can infect files or destroy a system after a single execution. The same applies to modules designed for DDOS attacks.</p>
    <p>Use this tool wisely to avoid unintentionally causing harm to yourself or others.</p>
</div>
<div id="tutorial_link">
    <h2>Draconus Tutorials</h2>
    <p>***** <a href="https://github.com/LittleAtariXE/Draconus_Tutorials">TUTORIALS</a> *****</p>
</div>
<div id="Contents">
    <h2>Contents</h2>
    <ul>
        <li><a href="#Draconus">Draconus</a></li>
        <li><a href="#Disclaimer">Disclaimer</a></li>
        <li><a href="#Warning">Important Warning</a></li>
        <li><a href="#About">About Draconus</a></li>
        <li><a href="#Install">Install</a></li>
        <li><a href="#Start">Start</a></li>
        <li><a href="#First_Step">First Step</a></li>
        <li><a href="#Hive">Hive</a></li>
        <li><a href="#">My First Rat</a>
            <ol><a href="https://github.com/LittleAtariXE/Draconus_Tutorials">Please see Tutorials</a></a></ol>
        </li>
        <li><a href="#AboutProject">About The Project</a></li>
        <li><a href="#Features">Project Features</a></li>
        <li><a href="#Changelog">Changelog</a></li>
        <li><a href="https://github.com/LittleAtariXE/Draconus_Tutorials">Tutorials</a></li>
    </ul>
</div>
<div id="About">
    <h2>About Draconus</h2>
    <p><strong>Draconus</strong> is a robust program consisting of two sub-programs designed for streamlined server management and client interaction. It offers an automated approach to managing connections, messages, and file transfers without requiring user intervention, making it a powerful tool for ethical hacking and controlled testing environments.</p>
    <h3>Program Structure</h3>
    <ul>
        <li><strong>Background Program</strong>: The first sub-program runs in the background, handling server operations and managing client connections automatically. This design allows for seamless, automated tasks, such as accepting connections, receiving messages, and file handling, all without needing manual input.</li>
        <li><strong>Control Program</strong>: The second sub-program serves as the user interface, connecting to the background program. Built with the <code>Python Click</code> interface, it provides the user with interactive control over various functions, enabling flexible and precise management.</li>
    </ul>
    <h3>Main Sections</h3>
    <ul>
        <li><strong>Main Draconus Section</strong>: Responsible for creating and managing servers, handling connections, and overseeing core operations.</li>
        <li><strong>Hive Section</strong>: Specializes in creating and compiling ready-to-use client programs, making it easy to deploy new clients as needed.</li>
    </ul>
</div>
<div id="Install">
    <h2>Installation</h2>
    <ol>
        <li>Ensure you have Python 3.11.2 or a newer version installed on your system.</li>
        <li>Install Docker (e.g., using the following command):
            <pre><code>sudo apt install docker.io</code></pre>
        </li>
        <li>To allow the program to interact with Docker, you need to set the appropriate permissions. Run:
            <pre><code>sudo usermod -aG docker $USER</code></pre>
            Afterward, log out and back in (or restart your system) to apply the new permissions.
        </li>
        <li>Due to the recent policy changes in Python modules on Linux, make sure you have Python’s virtual environment package, <code>venv</code>, installed. If not, install it with:
            <pre><code>sudo apt install python3.11-venv</code></pre>
        </li>
        <li>Navigate to the <code>Draconus</code> directory:
            <pre><code>cd Draconus</code></pre>
        </li>
        <li>Create a virtual environment:
            <pre><code>python3 -m venv ./venv</code></pre>
        </li>
        <li>Activate the virtual environment:
            <pre><code>source ./venv/bin/activate</code></pre>
        </li>
        <li>Install the project dependencies:
            <pre><code>pip install -r requirements.txt</code></pre>
        </li>
    </ol>
    <p>The installation is complete, and your environment is ready to use.</p>
</div>
<div id="Start">
    <h2>Getting Started</h2>
    <p>Before running the program, edit the <code>CONFIG.ini</code> file. This file contains configuration settings with explanations. The main setting to update is <code>IP</code>, where you should enter the IP address of the computer or virtual machine that will run Draconus. After saving your changes, you can proceed with launching the program.</p>
    <p><strong>Draconus</strong> consists of two main components: <code>Draconus</code> and <code>Commander</code>. Follow these steps to launch both programs correctly:</p>
    <p><strong>Note:</strong> Before launching the programs, you need to activate the virtual environment. Draconus can be run without activating the virtual environment, but Commander requires an active <code>venv</code>. To activate the <code>venv</code>, navigate to the <code>Draconus</code> directory and execute:
        <pre><code>source ./venv/bin/activate</code></pre>
    </p>
    <ol>
        <li><strong>Start Draconus</strong>: Run Draconus with the command:
            <pre><code>python3 Draconus.py</code></pre>
            Since Draconus is designed to operate in the background, you can also launch it as a background process using:
            <pre><code>nohup python3 Draconus.py &</code></pre>
        </li>
        <li><strong>Start Commander</strong>: After Draconus is running, launch Commander with:
            <pre><code>python3 Commander.py</code></pre>
            Commander will attempt to connect to Draconus upon startup. If Draconus is not running, Commander will display an error message and will not launch until it detects an active Draconus instance.
        </li>
    </ol>
</div>
<div id="First_Step">
    <h2>First Steps</h2>
    <p>Once Commander has connected to Draconus, you will have access to a console menu resembling a Linux terminal. This interface allows you to manage connections, create servers, and establish direct connections with clients. The <code>help</code> menu is always available, and many commands can be run with the <code>--help</code> parameter for additional assistance.</p>
    <h3>Server Types</h3>
    <p>You can create four main types of servers:</p>
    <ul>
        <li><strong>Default</strong>: Communicates via TCP socket, with data formatted in JSON and encoded in base64. This server type is recommended for advanced communication, background file transfers, and automated tasks with clients that require no user intervention.</li>
        <li><strong>Raw</strong>: Uses TCP socket but sends raw bytes, allowing for simple message reading and file reception (one at a time) without metadata such as name or type. Ideal for lightweight client programs that don't require complex communication.</li>
        <li><strong>Down</strong>: Designed solely for receiving files, without support for messages, commands, or other functionalities.</li>
        <li><strong>Send</strong>: A server designed only to send files to the client. It does not support messages or commands. When a connection is established, it automatically sends the set files.</li>
        <li><strong>b64</strong>: TCP server. Receives and sends base64 encoded messages.</li>
    </ul>
    <h3>Make Servers:</h3>
    <p>Servers can be created using the following format:</p>
    <pre>
    server [name] [port]
    </pre>
    <p>or:</p>
    <pre>
    server [name] [port] -t [type]
    </pre>
    <p>For example:</p>
    <pre>
    server my_server 4444 -t raw
    </pre>
    <p>If you don't specify a server type, the default type will be selected automatically.</p>
    <p>Servers start automatically after creation and wait for incoming connections from clients. Each server can handle multiple connections simultaneously, so you are not limited to a single connection. Draconus provides access to manage all connected clients, assigning a unique global ID to each client. Servers also automatically detect when a client disconnects and clean up its connection from the program.</p>
    <h3>Exiting the Program</h3>
    <p>The program can be terminated using two commands: <code>exit</code> or <code>quit</code>.</p>
    <ul>
    <li>
        <strong>exit</strong> - Stops the Commander program. The program closes, but Draconus continues to run in the background. 
        It can still accept connections, send and receive files from clients. 
        When you restart Commander, it will reconnect to the running Draconus, and any pending actions or messages will be displayed on the screen.
    </li>
    <li>
        <strong>quit</strong> - Stops both Commander and Draconus. It sends a termination signal to Draconus, 
        shutting down both programs completely.
    </li>
    </ul>
    <h3>Additional Commands</h3>
    <ul>
    <li>
        <strong>close</strong> - Shuts down the specified server and disconnects all connected clients. 
        For example: <code>close my_server</code>.
    </li>
    <li>
        <strong>task</strong> - Displays all tasks currently being performed by Draconus. 
        These include threads actively running within the program.
    </li>
     <li>
        <strong>conn</strong> - Enters interaction mode with a connected client. 
        This allows you to send commands, files, and more. Each connected client is assigned a unique ID by Draconus, which is used for identification. 
        To initiate communication with a client, use the command <code>conn [ID]</code>, for example: <code>conn 3</code>.
    </li>
    <li>
        <strong>show</strong> - Displays a list of created servers and connected clients.
        <ul>
        <li><strong>-s</strong> - Shows a list of created servers.</li>
        <li><strong>-c</strong> - Displays a list of all connected clients across all servers.</li>
        </ul>
    </li>
    <li>
        <strong>hive</strong> - Accesses a new section of the program with additional commands, menus, and options. 
        This is where you can create worms.
    </li>
    </ul>
    <h3>First Run</h3>
    <p>When you start Draconus, a directory named <code>OUTPUT</code> will appear in its main directory. This is a critical folder where Draconus stores its logs, downloaded files, created worms, and more. Do not delete this directory while the program is running. You can safely delete it only when both Draconus and Commander are stopped.</p>
    <h4>Contents of the <code>OUTPUT</code> Directory:</h4>
    <ul>
    <li>
        <strong>Logs</strong> - This folder contains log files. Every message displayed by Draconus is saved here, along with a timestamp. 
        Similarly, any message received from clients is also logged.
    </li>
    <li>
        <strong>LOOT</strong> - This folder stores files downloaded from or sent by clients. It will contain subdirectories named after the IP addresses of clients, which will hold the files sent by them. 
        Additionally, a <code>dump</code> subdirectory will store files that could not be identified during download. For example, if a client sends a file without headers or metadata (e.g., name, type), it will end up here. 
        Think of the <code>LOOT</code> folder as the treasure chest for files received from clients.
    </li>
    <li>
    <strong>Hive</strong> - This folder contains files related to worms, source code, shellcodes, and ready-to-use executables. 
    If you create a worm, it will be stored here.
  </li>
  <li>
        <strong>Shortcuts</strong> - This folder provides shortcuts to various useful resources in the project, so you don't have to search for them manually. 
        It includes:
        <ul>
        <li>A folder with icons where you can add your own icons and use them when creating worms.</li>
        <li>A shortcut to files where you can add custom code, for example, to payloads.</li>
        </ul>
  </li>
    </ul>
    <p>Additional directories may also appear in the <code>OUTPUT</code> folder, depending on the tools you use in Draconus. 
Instructions for new directories will be displayed within the program. Similarly, subdirectories may contain additional files as you use the program. 
For example, many shortcuts in the <code>Shortcuts</code> folder are only created after you access the "hive" section in Draconus.</p>
</div>
<div id="Hive">
    <h2>Hive</h2>
    <p>The <strong>Hive</strong> section is where you create worms. Worms are generated by selecting a main template from the <code>worm</code> section. Depending on the type of worm, some allow the addition of extra modules, payloads, and even code obfuscation, while others only support adding payloads.</p>
    <p>After selecting the appropriate modules, the process moves to filling out the so-called variables, such as IP address, connection port, and more. Many modules are configurable, and everything is clearly described with example values provided to make configuration straightforward.</p>
    <h3>Main Modules for Building Worms</h3>
    <ul>
    <li>
        <strong>worm</strong> - The main template. This is the first module that must be added. 
        It determines the type of worm you are creating and which additional modules can be used. 
        There are versions that support every type of module, but there are also smaller worms written in assembler, 
        allowing for the addition of simple scripts, and so on. 
        In general, you can create an executable file that weighs over 10 MB or a mini worm with a file size of around 3 KB.
    </li>
    <li>
        <strong>module</strong> - A variety of modules that add different functionalities to your worms. 
        These can include selecting a TCP connection method, connecting via Discord webhook, network scanning, launching a shell, and more. 
        Each module comes with a detailed description of its purpose and functionality.
    </li>
     <li>
        <strong>payload</strong> - Various types of payloads written in Python, PowerShell, or as executable files for testing. 
        Some modules and worms allow embedding a binary (executable) file within the worm itself, which can then be executed later.
    </li>
    <li>
        <strong>shadow</strong> - Code obfuscation options. The final code undergoes various processes to make analysis more difficult. 
        You can use multiple obfuscation modules to make the code even harder to analyze.
    </li>
    <li>
        <strong>starter</strong> - The final method of embedding code into the program. 
        For example, you can choose to place the entire code at the very end, encoded in Base64, and run it as a one-liner.
    </li>
    <li>
        <strong>wrapper</strong> - An additional option that allows embedding the entire worm code into another program. 
        For example, the worm is built using Python modules, but instead of being compiled directly, 
        it is embedded into assembler code. The assembler code is then compiled, and it executes the Python worm code.
    </li>
    <li>
        <strong>process</strong> - Defines the steps the worm will go through until it is fully created. 
        These steps include code generation, obfuscation, adding imports, compilation, and shellcode creation. 
        The processes vary depending on the main worm template. For example, a worm designed for shellcodes 
        will have different steps compared to one created in Python.
        <p>It is not recommended to modify the default processes unless you are already familiar with the program and understand what you are doing.</p>
    </li>
    <li>
        <strong>cscript</strong> - Special scripts used during compilation. They add information to EXE and DLL files, such as version numbers, company names, etc. You can create your own custom entries or use entries from a predefined database.
    </li>
    <li>
        <strong>food</strong> - You could say it's food for the worm. These are special variables that contain pre-defined values. When building a worm, it may need things like text to hide shellcode, base URLs, or other resources — these are fetched from the Food section.
        Food values can be assigned to variables, making it a convenient tool when you want to store a collection of paths, text, shellcode, scripts, etc.
        In the shortcuts directory, you'll find references to some Food variables that you can modify — and those changes will be reflected in the worms you create.
    </li>
    <li>
        <strong>scode</strong> - Templates used to generate shellcode.
    </li>
    </ul>
    <h3>Hive Commands</h3>
    <ul>
    <li>
        <strong>show</strong> - Displays a list with descriptions of available modules. 
        <br>Usage: <code>show [module_type]</code>, e.g., <code>show worm</code>. 
        <br>You must specify the module type, such as <code>worm</code>, <code>module</code>, <code>payload</code>, etc.
    </li>
    <li>
        <strong>add</strong> - Adds a module to your template. 
        <br>Usage: <code>add [module_type] [name]</code>, e.g., <code>add module Binky</code>. 
        <br>The first module to be added must always be one of the main modules, such as <code>worm</code>.
    </li>
    <li>
        <strong>remove</strong> - Removes a specified module from your worm. 
        <br>Usage: <code>remove [module_type] [name]</code>, e.g., <code>remove payload MicroRat</code>.
    </li>
    <li>
        <strong>name</strong> - Sets the name of the worm being created. 
        <br>Usage: <code>name [worm_name]</code>, e.g., <code>name MyFirstWorm</code>. 
        <br>A directory with the worm's name will appear in the <code>Hive</code> folder, where its final files will be stored.
    </li>
     <li>
        <strong>icon</strong> - Sets an icon for the executable file. 
        <br>Usage: <code>icon [file_name]</code>, e.g., <code>icon bee1.ico</code>. 
        <br>You can add additional icons to the folder whose shortcut is located in the <code>Shortcuts</code> directory. 
        Draconus includes several default icons that you can use.
    </li>
    <li>
        <strong>worm</strong> - Displays the entire configuration of the worm being created. 
        <br>Usage: <code>worm</code>.
        <br>It shows added modules, descriptions, required variables to fill in, and more. This is the main command for overseeing the building process.
    </li>
    <li>
        <strong>var</strong> - Sets variables for the worm being created. 
        <br>Usage: <code>var [name] '[value]'</code>, e.g., <code>var ip_addr "192.168.1.1"</code>. 
        <br>Variables depend on the type of worm being created and the modules added. Some modules require additional variables. 
        You can modify all variables listed in the <code>required variables</code> and <code>set variables</code> sections.
    </li>
    <li>
        <strong>rebuild</strong> - Clears all modules and resets the entire worm. 
        <br>Usage: <code>rebuild</code>. 
        <br>This allows you to start a new project from scratch.
    </li>
    <li>
        <strong>comp</strong> - Displays a list of available compilers. 
        <br>Usage: <code>comp</code>. 
        <br>Not all worms can use all compilers. This command lets you view the name and description of each compiler so you can choose the appropriate one for your worm. 
        Worms have default compilers set, such as <code>PyInstaller</code> for Python worms, but you can switch to others, like <code>Nuitka</code>.
    </li>
    <li>
        <strong>install</strong> - Installs the required compilers. 
        <br>Usage: <code>install</code> or <code>install -i [master_compiler_name]</code>. 
        <br>Draconus is installed without compilers by default. You need to install compilers as you use the program. 
        You don't have to install all compilers, especially if you don't plan to create files for certain systems. 
        However, some functionalities, such as building shellcode, are not possible without specific compilers.
        <p><strong>Note:</strong> Installing additional compilers involves downloading special Docker images, which can take up extra disk space. 
        For example, the compiler for creating Windows EXE files from Python takes approximately 3.5 GB.</p>
    </li>
    <li>
        <strong>dlc</strong> - Installs additional modules. 
        <br>Usage: <code>dlc -s</code> or <code>dlc -i [dlc_name]</code>, e.g., <code>dlc -i "DLC_1"</code>. 
        <br>Draconus allows adding extra modules over time without requiring you to download or install a new version of the program. 
        To install a DLC, place the package in the <code>IN</code> folder that appears in Draconus's main directory.
    </li>
    <li>
        <strong>sheme</strong> - Displays a list of processes and steps available for worms. 
        <br>Usage: <code>sheme</code>. 
        <br>This is primarily for informational purposes to help you understand the worm-building process if you want to customize it.
    </li>
    <li>
        <strong>gvar</strong> - Displays a list of global options. 
        <br>Usage: <code>gvar</code>. 
        <br>These are special options you can configure, such as changing the default compiler for worms or applying additional compilation options.
    </li>
    <li>
        <strong>setgvar</strong> - Sets a global option. 
        <br>Usage: <code>setgvar [name] [value]</code>, e.g., <code>setgvar COMPILER_NAME WinePyNuitka</code>.
    </li>
    <li>
        <strong>exit</strong> - Exits the Hive console and returns to the Draconus console. 
        <br>Usage: <code>exit</code>.
    </li>
    <li>
        <strong>build</strong> - Starts building the worm into an executable file. 
        <br>Usage: <code>build</code> or <code>build --options</code>, e.g., <code>build --no_compile</code>. 
        <br>If the <code>--no_compile</code> option is used, the executable file will not be created; instead, you will receive a file with the raw code.
    </li>
    </ul>
    <p>Many commands offer additional help, accessible with the <code>--help</code> option, e.g., <code>build --help</code>.</p>
</div>
<div id="AboutProject">
    <h3>About the Project</h3>
    <p>I understand and acknowledge that the techniques presented in this project are amateur and, for some, may seem primitive. However, I developed this project while teaching myself how all of this is actually created.</p>
    <p>I do not work in IT and have never worked in the field. I’m not a professional programmer—just a hobbyist. I’m aware that the entire project could probably be done much better: the code could be written more efficiently, better libraries could be used, and so on. But for me, what matters most is that it works.</p>
    <p>The project will continue to evolve, and over time I plan to add new tools and modules.</p>
</div>
<div id="Features">
    <h2>🚀 Planned Features</h2>
    <p>In version 1.0, I focused primarily on building and testing Draconus. Less attention was given to creating various modules.</p>
    <p>In future versions, I plan to add the following:</p>
    <ul>
    <li>More payloads written in PowerShell.</li>
    <li>More Python-based worms with different functionalities.</li>
    <li>Additional types of DDOS attacks.</li>
    <li>Support for building Windows shellcode.</li>
    <li>Ability to create DLL files. - DONE</li>
    <li>More DLL files.</li>
    </ul>
</div>
<div id="Changelog">
    <h2>Changelog</h2>
    <ul>
        <li>
            <h3>Draconus 1.0</h3>
            <p>Start Project</p>
        </li>
        <li>
            <h3>Draconus 1.0.1</h3>
            <p>Improved reading of 'RAW' messages from network sockets.</p>
            <p>Added payload 'reverse shell' module in python for linux and windows.</p>
        </li>
    </ul>
    <h3>🛠️ Draconus 1.1</h3>
    <ul>
        <li><strong>New payload building system:</strong> Now it's time to come up with something... :)</li>
        <li><strong>Added payload module:</strong> <code>PS_DeliverObf</code> - An obfuscated PowerShell payload with configurable options.</li>
        <li><strong>Added payload module:</strong> <code>PyReverse</code> - A reverse shell written in Python for both Windows and Linux.</li>
        <li><strong>Added main template:</strong> <code>Worm Arkanoid</code> - Enables the creation of DLL files with PowerShell payloads. Additionally, an EXE file is generated to call the payload function. The DLL libraries can be used in any other code.</li>
        <li><strong>Improved raw message handling from sockets:</strong> A message buffer was introduced to prevent the screen from being flooded with hundreds of single-character messages. See <code>CONFIG.INI</code> for more details.</li>
        <li><strong>New functionality:</strong> Automatically prepares a directory with only the necessary files for the worm to operate. If the worm requires several files, a folder with the worm's name is created, containing only the essential files.</li>
        <li><strong>Bug fixes:</strong> Addressed numerous small and significant issues.</li>
    </ul>
    <h2>🛠️ Changelog for Version 1.1.1</h2>
    <ul>
        <li><strong>Added support for special "food" variables:</strong> These contain predefined data such as shellcodes and various worm-related data.</li>
        <li><strong>New worm: <code>WinShell</code> (x86)</strong> - A Windows 32-bit worm designed for testing shellcodes.</li>
        <li><strong>New worm: <code>WinShell64</code> (x64)</strong> - A Windows 64-bit worm designed for testing shellcodes.</li>
        <li><strong>New worm: <code>RiverRaid</code> (x86)</strong> - Hides shellcode among multiple text variables. 
            Generates both an EXE file and a separate DLL with injection functions, making detection more difficult.</li>
        <li><strong>New worm: <code>BrutePID</code> (x86)</strong> - Scans every process PID within a given range and attempts to inject shellcode into one of the processes.</li>
        <li><strong>New cross-compiler: <code>MC_win64</code></strong> - A 64-bit cross-compiler supporting C, C++, and assembler.</li>
        <li><strong>Added text display customization:</strong> In <code>CONFIG.ini</code>, a new option allows adjusting text display for different screen sizes.</li>
        <li><strong>More information added to the "Queen" console commands.</strong></li>
        <li><strong>New DLL building system.</strong></li>
        <li><strong>New wrapper: <code>DropZone</code> (not fully functional)</strong> - An experimental "worm-in-a-worm" system. 
            It embeds a compiled worm inside a "wrapper worm" and attempts to execute it as a separate process. 
            However, it struggles to handle large binary files (several MB). Work is ongoing to resolve this issue.</li>
        <li><strong>Added several new tools</strong> to assist in building different types of worms.</li>
        <li><strong>Bug fixes:</strong> Many small fixes, and probably some new bugs as well! 😄</li>
    </ul>
    <h2>🛠️ Changelog for Version 1.2</h2>
    <ul>
        <li><strong>New Worm Constructor</strong> Completely redesigned the process of building custom worms, improving the creation of new EXE and DLL combinations.</li>
        <li><strong>New Single Image CrossComp Compiler</strong>A single compiler image containing multiple compilers (mingw-x64, mingw-x32, PyInstaller, Nuitka). Older images can be deleted as they will no longer be used.</li>
        <li><strong>New Cscript Module Type</strong>New scripts for the compilation phase, allowing various descriptions to be added to DLL and EXE files.</li>
        <li><strong>New Worm: <code>BrutePID64</code> (x64)</strong> - A test program that attempts to open processes within a specified PID range, inject, and execute shellcode.</li>
        <li><strong>New Payload: <code>PyDllInject</code></strong> - A payload written in Python for DLL injection.</li>
        <li><strong>New Payload: <code>PyExeShell</code></strong> - A payload written in Python for shellcode injection.</li>
        <li><strong>New Module: <code>LodeRunner</code></strong> - A DLL library. Upon import, it starts a thread establishing a TCP connection, downloading a file, and executing it. See the program description for more details.</li>
        <li><strong>New Worm: <code>BruteDLL</code></strong> - Written in assembly. Checks each process within the specified range and attempts to inject a DLL using dynamic function import.</li>
    </ul>
    <h2>🛠️ Changelog for Version 1.2.1</h2>
    <ul>
        <li><strong>Build Worm as Payload</strong> — A new option allows building a Python-based worm and converting it into a payload instead of compiling it. The payload will appear automatically in the <code>payload</code> section of the library. Currently works only with raw Python code (support for compiled payloads is in progress).<br>
        Usage: <code>build --payload</code> or <code>build -p</code>.</li>
        <li><strong>New Module: <code>Smuggler_DLL</code></strong> — A special library that dynamically imports functions from <code>kernel32</code> and other DLLs. It locates the Export Table address in memory, allowing the hiding of imports and dynamic linking without recompilation.</li>
        <li><strong>New Module: <code>Smuggler_Lib</code></strong> — Same functionality as <code>Smuggler_DLL</code>, but in the form of a static <code>lib</code> library instead of a <code>dll</code>. Designed for manual linking during compilation.</li>
        <li><strong>New Worm: <code>Pong</code></strong> — A reverse TCP worm that launches <code>cmd</code> by default. All function names are dynamically generated and hidden, making detection very difficult. Compiled as a single-file executable using additional libraries.<br>
        ✅ <em>Tested on updated Windows 10 (April 2025). Not detected by Windows Defender.</em></li>
        <li><strong>New Worm: <code>Pong2</code></strong> — Same as <code>Pong</code>, but split into two files: an <code>exe</code> and a <code>dll</code> containing the worm logic. This separation allows for alternative execution methods.<br>
        ✅ <em>Tested on updated Windows 10 (April 2025). Not detected by Windows Defender.</em></li>
        <li><strong>New Module: <code>PayloadStorage</code></strong> — A 64-bit Assembly module for embedding large payloads. Accepts any type of binary data and supports basic obfuscation by altering the hex values of each byte. Payload capacity can be adjusted via a variable.</li>
        <li><strong>New Module: <code>UnLoader</code></strong> — A stealth module that writes files to disk using imports loaded directly from memory, avoiding static references to common APIs.</li>
        <li><strong>New Worm: <code>Falcon</code></strong> — A minimalistic worm written entirely in Assembly. It decodes a payload, writes it to disk, and launches it via <code>WinExec</code> or <code>OpenProcessA</code>. The execution command can be customized using a special variable. Uses memory-only dynamic imports for stealth.<br>
        ✅ <em>Tested on updated Windows 10 (April 2025). Not detected by Windows Defender.</em></li>
    </ul>
    <h2>🛠️ Changelog for Version 1.2.2</h2>
    <ul>
        <li><strong>Removed Worm: <code>LittleMolly</code></strong> — The <code>LittleMolly</code> worm has been removed and replaced by a new, more advanced version.</li>
        <li><strong>New Worm: <code>Montezuma</code></strong> — A Python-based worm that can be customized by adding various modules, including code obfuscators and more. Perfect for building your own payload or compiling into a standalone executable.</li>
        <li><strong>Improved Compatibility</strong> — Many Python modules have been updated to ensure full compatibility with the new <code>Montezuma</code> worm template.</li>
        <li><strong>TCP Module Update</strong> — The basic TCP communication module can now receive and interpret commands directly within the worm.</li>
        <li><strong>Updated Module: <code>Panther</code> (Ransomware)</strong> — Improved with support for fast or slow encryption modes and extended file search across the disk. Now more effective and configurable.</li>
        <li><strong>Improved Module Display</strong> — The module lists, worm configurations, and variable tables are now displayed using the Python <code>tabulate</code> library for better formatting and readability.  
        ⚠️ Please re-run: <code>pip install -r requirements.txt</code> to update your environment.</li>
    </ul>
    <h2>🛠️ Changelog for Version 1.2.3</h2>
<ul>
    <li><strong>New Commander Launch Option</strong> — You can now run the control interface directly with the command: <code>python3 c2.py</code>.  
    This new loader will automatically activate the virtual environment, create one if missing, install all required dependencies, and then launch Commander.  
    Both the old and new launch methods are supported and can be used interchangeably.</li>
    <li><strong>New Server Type: <code>b64</code></strong> — A new server type that uses TCP sockets with Base64-encoded communication.  
    Commands are sent using the standard <code>msg</code> instruction. This server type is required for communication with the new <code>Zaxxon</code> worm.</li>
    <li><strong>New Worm: <code>Zaxxon</code></strong> — A fully assembly-written worm and the author's first large-scale project in pure ASM.  
    <ul>
        <li>Polymorphic design: every build produces a different binary with randomized code and values.</li>
        <li>Uses hidden imports and passes Defender analysis tests.</li>
        <li>Communicates over Base64-encoded TCP socket (requires server type <code>b64</code>).</li>
        <li>Executes commands in new threads, allowing continuous communication during task execution.</li>
        <li>Supports creation of a secondary socket for file transfer (ideal for <code>send</code> server).</li>
        <li>Can search directories and steal files matching patterns like <code>*.jpg</code> or <code>aa??.bmp</code>.</li>
        <li>Contains space for two separate shellcodes, hidden within large blocks of random text.</li>
        <li>Includes special feature for injecting shellcode in fragments, decoded gradually from hidden text blocks (tested with MSF calc shellcode — undetected and successfully injected).</li>
        <li>Scans process ranges to find candidates for injection.</li>
        <li>Includes a fun feature to spam the screen with <code>MessageBox</code> windows.</li>
        <li>All commands are available after connecting to Draconus. Use the command <code>msg help</code> to view supported options.</li>
        <li>Zaxxon includes customizable parameters: hex names, random text pools for function obfuscation, and more.</li>
        <li>Has the ability to clone itself and add entries to Windows autostart. Be cautious when testing!  
            Check the Windows registry to find where Zaxxon has created its autostart entry.</li>
    </ul>
    </li>
</ul>
<h2>🛠️ Changelog for Version 1.2.4</h2>
    <ul>
    <li><strong>Update readme</strong></li>
    </ul>
<h2>🛠️ Changelog for Version 1.2.42</h2>
    <ul>
    <li><strong>Fixing bugs</strong></li>
    </ul>
<h2>🛠️ Changelog for Version 1.3</h2>
<ul>
    <li><strong>New Worm: <code>WShellcode</code></strong> — A new template for generating Windows x64 shellcode.  
    This main worm type allows you to create shellcode from predefined templates.  
    To begin shellcode generation, add <code>WShellcode</code> as your base worm with the command:  
    <code>add worm WShellcode</code>.  
    Templates are available as a new type of module called <code>scode</code>.  
    To list all available shellcode templates, run: <code>show scode</code>.</li>
    <li><strong>New Module Type: <code>scode</code></strong> — Shellcode templates used to generate working shellcode.  
    These modules provide different payload behaviors in low-level binary form.</li>
    <li><strong>New Shellcode Module: <code>WinExec</code></strong> — A simple test shellcode that uses the <code>WinExec</code> function to launch a program (default: <code>calc.exe</code>, can be changed).  
    Mainly for testing — unless someone gets creative with the commands 😄</li>
    <li><strong>New Shellcode Module: <code>WEPy</code></strong> — A shellcode that uses <code>OpenProcessA</code> to spawn Python via <code>cmd</code> and inject a script directly.  
    It includes a slot for a Python-based payload that you can insert manually.</li>
    <li><strong>New Compiler Option: <code>build --spayload</code></strong> — Builds a shellcode and places it into the payload library.  
    The generated shellcode can then be used like any other ready-to-use payload in other worms.</li>
    <li><strong>New Compiler Option: <code>build --food</code></strong> — Builds a shellcode and stores it as a <code>FOOD</code>-type variable.  
    These shellcodes can later be inserted into other worms or modules that accept shellcode as input.</li>
    <li><strong>Bug Fixes</strong> — Several minor bugs were fixed and improvements made for better overall stability.</li>
</ul>
<h2>📦 Version 1.3.1 – Update Summary</h2>
<h3>🆕 New Modules:</h3>
<ul>
  <li><strong>New Shellcode module: <code>MsgBoxA</code></strong> – New shellcode module. Generates MessageBoxA shellcode with custom text (default: <code>"Hello World"</code>). The message box appears as an error-type window.</li>
  <li><strong>New Worm: <code>JackRoad</code></strong> – New main worm module written in C++. Designed for shellcode testing. It scans processes within a given PID range, locates a vulnerable process, injects, and executes the shellcode.<br />
    Does not use <code>windows.h</code>; instead, it dynamically imports all functions through a custom library. Displays detailed information about the target process, memory allocation, and more.<br />
    Successfully tested with shellcode generated via Draconus on Windows 10. Injection and execution worked without detection by Windows Defender.<br />
    <em>Note: Not tested with signed shellcode generated via MSFramework.</em>
  </li>
</ul>
<h3>🔧 Other Changes:</h3>
<ul>
  <li>Removed the outdated <strong>example RAT creation</strong> section from the README.</li>
  <li>Added a link to the new <strong>tutorial section</strong>, which now includes both written guides and video walkthroughs.</li>
</ul>
</div>
</body>
</html>
