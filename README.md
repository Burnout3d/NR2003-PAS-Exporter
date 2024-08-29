# NR2003 PAS Exporter (WIP)
This is a Blender file export script for writing to Papyrus ASCII Scene (PAS) format. 

## Features
The ability to export to Papyrus ASCII Scene (PAS) format for use with make3do to compile the model to a 3do. 

## Notes
This is not fully functional yet. And it does require a very specific node group that I've made in Blender 4.2 for it to function. Current tuorials for modding NR2003 with 3ds Max is still very much useful. Read them. 
Currently, IK animation export is not supported yet. I do not know what exactly all works yet. I just know I can export a car to the game and get it on track. I'm making this public so I can gather feedback and see what works and what doesn't. 
I expect there to be a ton of issues. I hope someone can test double sided materials, I heard that works in 3ds Max, not sure if that works with this script. There's a lot of unknowns. 
One thing I should mention is NR2003 expects the PAS to be exported in meters. So make sure your files are scaled correctly and Blender is set up to export in meters.
And hey, it's open source, if you don't like what I'm doing, how I'm doing it, you have the code, go have fun yourself. 
