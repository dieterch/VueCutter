Quart VueCutter
========
(c)2024 Dieter Chvatal

- This is a fullstack web-application with a backend in Python using the Quart framework, the backend is responsible for providing the frontend with the necessary data and for executing the cutting process. The cutting process is executed by an rq worker, which is started as a seperate process 'python worker.py'. the rq quue requires a redis server.
- The redis server is provided by a docker container (specifying 'redispw' in the docker-compose.yml file).
- The frontend consists of a vuetify-vue SPA. The compiled application is delivered by the Quart ASGI Webserver, so rest interface and frontend share one 'ip:port'. 
- A Plex Server in the local network is obviously required. python PlexAPI package is used to access the Plex Server. 

Installation
------------
To configure this application, you have to create a **config.toml** file in the same directory as this file with the following content:
:: 
  fileserver = 'xx.xx.xx.xx'
  plexurl = 'http://xx.xx.xx.xx:32400'
  plextoken = 'xxxxxxxxxxxxxxxxxx'
  redispw = 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
::

**Windows:**

Create and activate a virtual environment:
:: 
  git clone https://github.com/DieterChvatal/dstatemachine.git
  cd dstatemachine
  python -m venv venv
  .\venv\Scripts\activate.bat (windows)
  source ./venv/bin/activate (OSX, Linux)
  pip install -r requirements.txt
::

get Updates from github:
:: 
  cd "%USERPROFILE%/Documents\Scripts\dstatemachine
  .\venv\Scripts\activate.bat (windows)
  source ./venv/bin/activate (OSX, Linux)
  git stash
  git pull
  pip install -r requirements.txt
::

Start
------
>  jupyter lab
     
first run ./Tools/login.ipynb and every following 31 days, you are prompted for your myplant.
login and credentials:
::
  Please enter your myPlant login:
  User: xxxxxxx
  Password: xxxxxxxx
  TOTP Secret: xxxxxxxxx
::

go to the settings tab and update the installed fleet data

Icon on Desktop
---------------
Please create a file e.g. 'go_venv.bat' 
in your "%USERPROFILE%/Documents" Folder.
Copy the following into it:
::
  @echo off
  @echo ==============================================
  @echo Statemachine (c) Dieter.Chvatal@innio.com 2023
  @echo ==============================================
  cd "%USERPROFILE%/Documents\Scripts\dstatemachine"
  call %USERPROFILE%/Documents/Scripts/dstatemachine/venv/Scripts/jupyter lab
  REM pause
::

Create a link on the desktop. You can now start dstatemachine by
double clicking the link 

Release History
---------------

-  0.1.0
-  Work in progress

Meta
----

Your Name – dieter.chvatal@gmail.com

Distributed under the MIT license. See ``LICENSE`` for more information.

`https://github.com/DieterChvatal/dstatemachine <https://github.com/DieterChvatal/>`__


Contributing
------------

1. Fork it (https://github.com/DieterChvatal/dstatemachine)
2. Create your feature branch (``git checkout -b feature/fooBar``)
3. Commit your changes (``git commit -am 'Add some fooBar'``)
4. Push to the branch (``git push origin feature/fooBar``)
5. Create a new Pull Request

hint, if pip fails
------------------
>   pip install --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org -r requirements.txt (alternativ)
