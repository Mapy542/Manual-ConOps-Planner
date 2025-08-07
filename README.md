# Manual-ConOps-Planner
Quick and easy python script to layout a route within a fixed size arena. Calculate times and distance overall and per route segment.

Designed with the NASA Lunabotics compeition in mind.

## Install

You need Tkinter to run this application.

- Windows:
  - Select to install tkinter during python installation wizard.
- Linux:
  - `sudo apt-get install python3-tk`


## Getting Started

1. Enter the size of your arena and expected traversal speed.
2. Active multiplier refers to a change in traversal speed when doing something, ie a robot digging while travering. A multiplier > 1 slows down active segments, while < 1 speeds up during active segments. An active segment is red, and is enabled by right clicking the two nodes it connects.
3. Press `h` for the help menu to see all options, and to modify traversal speed settings.

## Features

- Normal Traversal Segments
- Active Traversal Segments
- Circular Landmarks
- Rectangular Landmarks
- Import/Export of json data
