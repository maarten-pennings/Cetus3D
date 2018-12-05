Python scripts for Cetus3D
==========================
2018 Mar 23 Maarten Pennings


(1) You need to have python on your PC.

(2) Then run the DiscoverCetus3D.py script.
    It outputs something like this.
    Note the prip (IP number of the printer)
    
      DiscoverCetus3D
        Discovers cetus3D printers on the local network
        2018 mar 3 Maarten Pennings
      Receiver
        hostip  : 192.168.178.64
        hostport: 55125
        sending : WhoIsPresent to *.*.*.*:31246
      Waiting for ImPresent
        ... received
        prip    : 192.168.178.10
        prport  : 31246
        prsnum  : 70172384
        prname  : MaartensCetus3D
        prtype  : Cetus S7(NL)
      Done

(3) Then edit StatusCetus3D.py and change line 
      CETUS3D_IP= "192.168.178.10" ### TODO: fill out correct IP num of your Cetus3D printer
    to have the printer IP just found
    
(4) Run StatusCetus3D.py
    It outputs something like this.

      StatusCetus3D
        Gets status messages from a cetus3D printer and prints them continuously
        2018 mar 4 Maarten Pennings
      Server
        hostip  : 192.168.178.64
        hostport: 54919
        timeout:  5.0s
        sending : CallMeHere to 192.168.178.10:31246
      Waiting for connect
        ... connect from 192.168.178.10:24032
        press ^C to stop
        ----- --------------- ----- ------- ---- -------- ------- ------- --------------------------------------------------------------------------------------------------------------------------------
        msgix          status layer  height prgs     time noztemp bedtemp binary-message-data
        ----- --------------- ----- ------- ---- -------- ------- ------- --------------------------------------------------------------------------------------------------------------------------------
        00001 non-initialized L#0     0.0mm   0% 0:00:00s  22.94C  17.32C 030000000000000000007b04ad306203111700000000380000000000000000000000000000000000440100bf1e00000000000000000000ffffffffffffffff06
        00002 non-initialized L#0     0.0mm   0% 0:00:00s  22.94C  17.32C 030000000000000000007b04ad306203111700000000380000000000000000000000000000000000440100bf1e00000000000000000000ffffffffffffffff06
        00003 non-initialized L#0     0.0mm   0% 0:00:00s  22.92C  17.32C 030000000000000000007a04ad306203111700000000380000000000000000000000000000000000440100bf1e00000000000000000000ffffffffffffffff06
        aborted by user
      Done

(end)
