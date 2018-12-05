# Cetus3D
Library for getting the status of the Cetus3D printer.


## Introduction
Using the standard Cetus3D PC software (now [UP Studio](https://www.tiertime.com/up-studio/) from Tier Time) 
and [WireShark](https://www.wireshark.org/) and a lot of experiments, I was able to reverse engineer the
communication between UP Studio and my [Cetus3D](https://www.cetus3d.com/).

When I shared a short [video](https://photos.app.goo.gl/89zFwejhkBJ2FMWw6) with Cetus3D support,
I got an OK to publish this, and even a bit of support. 
Find my logs and a support mail from Cetus3D in the [docs](docs) directory.

Next step was to replay the logged communication. I focused on "getting status" 
(on my todo list is the reverse engineering of the "extrude" and "withdraw" commands, and maybe "initialize").
For this I wrote a [Python](python) script.

Third step, was to create a Arduino library. Find it in the [src](src) directory.
A simple example is [Cetus3Dbasic](examples/Cetus3Dbasic) in the [examples](examples) directory.

As you can see on the video, I made a complete "product" out of it, with two OLED displays 
and two temperature sensors. At this moment, that project is not ready to be shared.
It is too specific with all the hardware requirements.


## Example output
This is the output of the [Cetus3Dbasic](examples/Cetus3Dbasic) example.

```
Welcome to Cetus3Dbasic
setup: WiFi 'MaartensWiFi' ... ESP8266 at 192.168.178.63
setup: Finding Cetus3D ... found 'MaartensCetus3D' at 192.168.178.10
stat:  seq#  clock : stat/statusname      layer  height done   remain  nozzle  hotbed 
stat: 00000 00008s : 0003/non-initialized L0000   0.0mm   0%  0:00:00  23.58C  17.32C 
stat: 00001 00013s : 0003/non-initialized L0000   0.0mm   0%  0:00:00  23.60C  17.32C 
stat: 00002 00018s : 0003/non-initialized L0000   0.0mm   0%  0:00:00  23.60C  17.32C 
stat: 00003 00024s : 0003/non-initialized L0000   0.0mm   0%  0:00:00  23.60C  17.32C 
stat: 00004 00030s : 0003/non-initialized L0000   0.0mm   0%  0:00:00  23.60C  17.32C 
stat: 00005 00038s : 0003/non-initialized L0000   0.0mm   0%  0:00:00  23.60C  17.32C 
stat: 00006 00043s : 0003/non-initialized L0000   0.0mm   0%  0:00:00  23.60C  17.32C 
loop: Get status failed
stat: 00007 00055s : 0003/non-initialized L0000   0.0mm   0%  0:00:00  23.64C  17.32C 
stat: 00008 00061s : 0003/non-initialized L0000   0.0mm   0%  0:00:00  23.64C  17.32C 
```


## Complete log
I have printed an axis of about 35mm, using the 0.2 nozzle, and a layer height of 0.05mm.
I have captured the complete [output](docs/capture.log) of [Cetus3Dbasic](examples/Cetus3Dbasic).
Note
 - First few lines (1..4) is the output of setup: connecting to WiFi and finding the Cetus3D
 - Next we see a couple of `Get status failed` lines (5..10). 
   The reason for this is that I was using the PC application to upload a print. 
   The PC is then the controlling host, and the ESP8266 can not connect.
 - Next we see the printer heating up the nozzle (lines 11..25), from 38.32C to 188.64C 
   (and actually to 210C but that was not captured in the log)
 - Once the nozzle temperature set-point is reached (line 26), the temperature reporting changes.
   No longer is 210C reported, but a factor, where 1.0 means exact on the set-point (of 210).
 - We see the layer counter increment, but not the height (lines 26..98).
   The reason is that a raft counts in the layers, but not in the objects height.
 - Finally, we get to printing the object. Since I used a 0.05 layer height, and the 
   status reports in 0.1mm, we see the layer jump twice as fast as the height.
 - At line 1104, the printer reports 100% complete (from the 0% at line 11).
 - The remaining lines reports `ready`, and we see the temperature of the nozzle
   going down again.
 - Also note that my printbed is not heated, it always reports 17.32C
 - One interesting column remain: the estimated run time (from 1:39:17 down to 0:00:00)
 - Also note that there is an incidental `Get status failed` (lines 280, 288, 654, 795, 1105 and 1109).
   I can not explain these.
 
(end of doc)
