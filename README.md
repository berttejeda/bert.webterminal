# Overview

This is the Webterminal agent to be used with various projects I've developed, e.g.

- [bert.dashboard](https://github.com/berttejeda/bert.dashboard)
- [bert.bill](https://github.com/berttejeda/bert.bill) (superceded by above)
- [bert.slidev - webterminal addon](https://github.com/berttejeda/bert.slidev)

This agent allows the app's [xtermjs]((https://github.com/xtermjs/xterm.js/)) Webterminal React component to connect \
to a local bash process on your computer.

You can get this Webterminal agent running either by:

- Running the pre-built docker image:
  ```shell
  docker run -it --name webterminal --rm -p 10001:10001 berttejeda/bill-webterminal
  ```
- Running `docker-compose up -d` from this project
- Install btdashboard with `pip install btdashboard` and running `btdashboard`, OR \
  Cloning the [berttejeda/bert.dashboard](https://github.com/berttejeda/bert.dashboard) project, installing all requirements, and \
  running `python btdashboard/app.py -aio` \
  Doing so will launch a local websocket that forwards keystrokes to a bash process on your system
- Install bertdotbill with `pip install bertdotbill` and running `bill -aio`, OR \
  Cloning the [bert.bill](https://github.com/berttejeda/bert.bill) project, installing all requirements, and \
  running `python bertdotbill/app.py -aio` \
  Doing so will launch a local websocket that forwards keystrokes to a bash process on your system

Either of the commands above will start the websocket and bash process on localhost:10001, \
but you can change the port if you like.

You can then connect to the agent through the Web UI.

# Architecture

- Utilizes [spyder-terminal](https://github.com/spyder-ide/spyder-terminal) component

# Features

- You can practice the lesson material with your own OS/system
- Simply **click** on a command, and it will be sent and executed on the underlying shell via web terminal!
- Default shell is bash (for now)