# StatusCetus3D - Gets status messages from a cetus3D printer and prints them continuously
import time
import socket
import sys
import datetime


print("StatusCetus3D")
print("  Gets status messages from a cetus3D printer and prints them continuously")
print("  2018 mar 4 Maarten Pennings")
# Output should be something like this (example is initialization after power up)
# StatusCetus3D
#   Gets status messages from a cetus3D printer and prints them continuously
#   2018 mar 4 Maarten Pennings
# Server
#   hostip  : 192.168.178.64
#   hostport: 49862
#   sending : CallMeHere to 192.168.178.10:31246
# Waiting for connect
#   ... connect from 192.168.178.10:2755
#   press ^C to stop
#   ----- --------------- ----- ------- ---- -------- ------- ------- --------------------------------------------------------------------------------------------------------------------------------
#   msgix          status layer  height prgs     time noztemp bedtemp binary-message-data
#   ----- --------------- ----- ------- ---- -------- ------- ------- --------------------------------------------------------------------------------------------------------------------------------
#   00001 non-initialized L#0     0.0mm   0% 0:00:00s  29.46C  17.32C 03000000000000000000c105ae3062030e1700000000380000000000000000000000000000000000440100bf1e00000000000000000000ffffffffffffffff06
#   00002 non-initialized L#0     0.0mm   0% 0:00:00s  29.46C  17.32C 03000000000000000000c105ae3062030e1700000000380000000000000000000000000000000000440100bf1e00000000000000000000ffffffffffffffff06
#   00003 non-initialized L#0     0.0mm   0% 0:00:00s  29.40C  17.32C 03000000000000000000be05ae3062030f1700000000380000000000000000000000000000000000440100bf1e00000000000000000000ffffffffffffffff06
#   00004 non-initialized L#0     0.0mm   0% 0:00:00s  29.40C  17.32C 03000000000000000000be05ae3062030f1700000000380000000000000000000000000000000000440100af1e00000000000000000000ffffffffffffffff06
#   00005 non-initialized L#0     0.0mm   0% 0:00:00s  29.36C  17.32C 03000000000000000000bc05ae3062030f1700000000380000000000000000000000000000000000440100af1e00000000000000000000ffffffffffffffff06
#   00006    initializing L#0     0.0mm   0% 0:00:00s  29.36C  17.32C 02000000000000000000bc05ae3062030f1700000000380000000000000000000000000000000010440100bf1e00000000000000000000ffffffffffffffff06
#   00007    initializing L#0     0.0mm   0% 0:00:00s  29.30C  17.32C 02000000000000000000b905ae3062030f1700000000380000000000000000000000000000000000440100bf1e00000000000000000000ffffffffffffffff06
#   00008    initializing L#0     0.0mm   0% 0:00:00s  29.30C  17.32C 02000000000000000000b905ae3062030f1700000000280000000000000000000000000000000001440100bf1e00000000000000000000ffffffffffffffff06
#   00009    initializing L#0     0.0mm   0% 0:00:00s  29.20C  17.32C 02000000000000000000b405432f62030f1700000000280000000000000000000000000000000001440100bf1e00000000000000000000ffffffffffffffff06
#   00010    initializing L#0     0.0mm   0% 0:00:00s  29.20C  17.32C 02000000000000000000b405432f62030f1700000002380000000000000000cbcc4ccb0000000001440100bf1e00000000000000000000ffffffffffffffff06
#   00011    initializing L#0     0.0mm   0% 0:00:00s  29.10C  17.32C 02000000000000000000af05442f6203111700000002280000000000000000c5cc4ccb0000000001440100bf1e00000000000000000000ffffffffffffffff06
#   00012    initializing L#0     0.0mm   0% 0:00:00s  29.10C  17.32C 02000000000000000000af05442f6203111700000002380000000000000000bfcc4ccb0000000001440100bf1e00000000000000000000ffffffffffffffff06
#   00013    initializing L#0     0.0mm   0% 0:00:00s  29.04C  17.32C 02000000000000000000ac05432f6203101700000002280000000000000000b9cc4ccb0000000001440100bf1e00000000000000000000ffffffffffffffff06
#   00014    initializing L#0     0.0mm   0% 0:00:00s  29.04C  17.32C 02000000000000000000ac05432f6203101700000002280000000000000000b3cc4ccb0000000001440100bf1e00000000000000000000ffffffffffffffff06
#   00015    initializing L#0     0.0mm   0% 0:00:00s  28.98C  17.32C 02000000000000000000a905432f6203101700000002280000000000000000adcc4ccb0000000001440100bf1e00000000000000000000ffffffffffffffff06
#   00016    initializing L#0     0.0mm   0% 0:00:00s  28.98C  17.32C 02000000000000000000a905432f6203101700000002280000000000000000a7cc4ccb0000000001440100bf1e00000000000000000000ffffffffffffffff06
#   00017    initializing L#0     0.0mm   0% 0:00:00s  28.92C  17.32C 02000000000000000000a605432f6203101700000002280000000000000000a1cc4ccb0000000001440100bf1e00000000000000000000ffffffffffffffff06
#   00018    initializing L#0     0.0mm   0% 0:00:00s  28.92C  17.32C 02000000000000000000a605432f62031017000000023800000000000000009bcc4ccb0000000001440100bf1e00000000000000000000ffffffffffffffff06
#   00019    initializing L#0     0.0mm   0% 0:00:00s  28.88C  17.32C 02000000000000000000a405432f620310170000000228000000000000000095cc4ccb0000000001440100bf1e00000000000000000000ffffffffffffffff06
#   00020    initializing L#0     0.0mm   0% 0:00:00s  28.88C  17.32C 02000000000000000000a405432f62031017000000023800000000000000008fcc4ccb0000000001440100bf1e00000000000000000000ffffffffffffffff06
#   00021    initializing L#0     0.0mm   0% 0:00:00s  28.80C  17.32C 02000000000000000000a005432f620310170000000228000000000000000089cc4ccb0000000001440100bf1e00000000000000000000ffffffffffffffff06
#   00022    initializing L#0     0.0mm   0% 0:00:00s  28.80C  17.32C 02000000000000000000a005432f620310170000000238000000000000000083cc4ccb0000000001440100bf1e00000000000000000000ffffffffffffffff06
#   00023    initializing L#0     0.0mm   0% 0:00:00s  28.74C  17.32C 020000000000000000009d05432f62031017000000022800000000000000007dcc4ccb0000000001440100bf1e00000000000000000000ffffffffffffffff06
#   00024    initializing L#0     0.0mm   0% 0:00:00s  28.74C  17.32C 020000000000000000009d05432f620310170000000228000000000000000077cc4ccb0000000001440100bf1e00000000000000000000ffffffffffffffff06
#   00025    initializing L#0     0.0mm   0% 0:00:00s  28.70C  17.32C 020000000000000000009b05432f620310170000000238000000000000000071cc4ccb0000000001440100bf1e00000000000000000000ffffffffffffffff06
#   00026    initializing L#0     0.0mm   0% 0:00:00s  28.70C  17.32C 020000000000000000009b05432f62031017000000022800000000000000006bcc4ccb0000000001440100bf1e00000000000000000000ffffffffffffffff06
#   00027    initializing L#0     0.0mm   0% 0:00:00s  28.64C  17.32C 020000000000000000009805432f620310170000000228000000000000000065cc4ccb0000000001440100bf1e00000000000000000000ffffffffffffffff06
#   00028    initializing L#0     0.0mm   0% 0:00:00s  28.64C  17.32C 020000000000000000009805432f62031017000000022800000000000000005fcc4ccb0000000001440100bf1e00000000000000000000ffffffffffffffff06
#   00029    initializing L#0     0.0mm   0% 0:00:00s  28.60C  17.32C 020000000000000000009605432f620310170000000228000000000000000059cc4ccb0000000001440100bf1e00000000000000000000ffffffffffffffff06
#   00030    initializing L#0     0.0mm   0% 0:00:00s  28.60C  17.32C 020000000000000000009605432f620310170000000228000000000000000053cc4ccb0000000001440100bf1e00000000000000000000ffffffffffffffff06
#   00031    initializing L#0     0.0mm   0% 0:00:00s  28.60C  17.32C 020000000000000000009605432f62031017000000023800000000000000004dcc4ccb0000000001440100bf1e00000000000000000000ffffffffffffffff06
#   00032    initializing L#0     0.0mm   0% 0:00:00s  28.52C  17.32C 020000000000000000009205432f620310170000000238000000000000000047cc4ccb0000000001440100bf1e00000000000000000000ffffffffffffffff06
#   00033    initializing L#0     0.0mm   0% 0:00:00s  28.52C  17.32C 020000000000000000009205432f620310170000000228000000000000000041cc4ccb0000000001440100bf1e00000000000000000000ffffffffffffffff06
#   00034    initializing L#0     0.0mm   0% 0:00:00s  28.50C  17.32C 020000000000000000009105432f62031017000000023800000000000000003bcc4ccb0000000001440100bf1e00000000000000000000ffffffffffffffff06
#   00035    initializing L#0     0.0mm   0% 0:00:00s  28.50C  17.32C 020000000000000000009105432f620310170000000228000000000000000035cc4ccb0000000001440100bf1e00000000000000000000ffffffffffffffff06
#   00036    initializing L#0     0.0mm   0% 0:00:00s  28.44C  17.32C 020000000000000000008e05432f62031017000000023800000000000000002fcc4ccb0000000001440100bf1e00000000000000000000ffffffffffffffff06
#   00037    initializing L#0     0.0mm   0% 0:00:00s  28.44C  17.32C 020000000000000000008e05432f620310170002000038c2cc4ccb00000000000000000000000001440100bf1e00000000000000000000ffffffffffffffff06
#   00038    initializing L#0     0.0mm   0% 0:00:00s  28.40C  17.32C 020000000000000000008c05432f620310170002000028a4cc4ccb00000000000000000000000001440100bf1e00000000000000000000ffffffffffffffff06
#   00039    initializing L#0     0.0mm   0% 0:00:00s  28.40C  17.32C 020000000000000000008c05432f62031017000200002886cc4ccb00000000000000000000000001440100bf1e00000000000000000000ffffffffffffffff06
#   00040    initializing L#0     0.0mm   0% 0:00:00s  28.34C  17.32C 020000000000000000008905432f62031017000002003800000000bbcc4c4b000000000000000001440100bf1e00000000000000000000ffffffffffffffff06
#   00041    initializing L#0     0.0mm   0% 0:00:00s  28.34C  17.32C 020000000000000000008905432f620310170000020028000000009dcc4c4b000000000000000001440100bf1e00000000000000000000ffffffffffffffff06
#   00042    initializing L#0     0.0mm   0% 0:00:00s  28.30C  17.32C 020000000000000000008705432f620310170000020028000000007fcc4c4b000000000000000001440100bf1e00000000000000000000ffffffffffffffff06
#   00043    initializing L#0     0.0mm   0% 0:00:00s  28.30C  17.32C 020000000000000000008705432f6203101700000200380000000061cc4c4b000000000000000001440100bf1e00000000000000000000ffffffffffffffff06
#   00044    initializing L#0     0.0mm   0% 0:00:00s  28.24C  17.32C 020000000000000000008405432f6203101700000200380000000043cc4c4b000000000000000001440100bf1e00000000000000000000ffffffffffffffff06
#   00045    initializing L#0     0.0mm   0% 0:00:00s  28.24C  17.32C 020000000000000000008405432f6203101700000000380000000000000000000000000000000001440100bf1e00000000000000000000ffffffffffffffff06
#   00046    initializing L#0     0.0mm   0% 0:00:00s  28.20C  17.32C 020000000000000000008205432f6203101700020000289ab91ac20000f041000000000000000001440100bf1e00000000000000000000ffffffffffffffff06
#   00047    initializing L#0     0.0mm   0% 0:00:00s  28.20C  17.32C 020000000000000000008205432f6203101700020000389ae9b0c20000f041000000000000000001440100bf1e00000000000000000000ffffffffffffffff06
#   00048    initializing L#0     0.0mm   0% 0:00:00s  28.14C  17.32C 020000000000000000007f05432f62031017000200002833630ac30000f041000000000000000001440100bf1e00000000000000000000ffffffffffffffff06
#   00049           ready L#0     0.0mm   0% 0:00:00s  28.14C  17.32C 030100000000000000007f05432f62031017000000002800000cc30000f041000000000000000081440100bf1e00000000000000000000ffffffffffffffff06
#   00050           ready L#0     0.0mm   0% 0:00:00s  28.10C  17.32C 030100000000000000007d05432f62031017000000002800000cc30000f041000000000000000081440100bf1e00000000000000000000ffffffffffffffff06
#   00051           ready L#0     0.0mm   0% 0:00:00s  28.10C  17.32C 030100000000000000007d05432f62031017000000002800000cc30000f041000000000000000081440100bf1e00000000000000000000ffffffffffffffff06
#   00052           ready L#0     0.0mm   0% 0:00:00s  28.04C  17.32C 030100000000000000007a05432f62031017000000002800000cc30000f041000000000000000081440100bf1e00000000000000000000ffffffffffffffff06
#   00053           ready L#0     0.0mm   0% 0:00:00s  28.04C  17.32C 030100000000000000007a05432f62031017000000002800000cc30000f041000000000000000081440100bf1e00000000000000000000ffffffffffffffff06
#   aborted by user
# Done


# CurrentStatus (64 bytes) TCP printer->host
# 0 0  0 0   0 0    0   0 0  0  1 1  1 1  1 1  1 1 1 1 2 2 2 2 2 2 2 2 2 2 3 3 3 3 3 3 3 3 3 3 4 4 4 4 4 4 4 4 4 4 5 5 5 5 5 5 5 5 5 5 6 6 6 6 6
# 0 1  2 3   4 5    6   7 8  9  0 1  2 3  4 5  6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4
# stat layer height pr  time ?? ntmp ???? btmp ?????
# (?)  (#)   (.1mm) (%) (s)
# 0202 1600  1c00   3f  d519 00 3200 3400 1100 3800070202023a9a7974c29ad9514266962fc35d268a482b450100bf1e00000000000000000000ffffffffffffffff06
# 0301 0000  0000   00  0000 00 4705 442f 6203 1117000000003800000cc30000f041000000000000000081440100bf1e00000000000000000000ffffffffffffffff06
def parse_CurrentStatus(data):
  jobstatcode= int.from_bytes(data[0:2], 'little')
  if  ( jobstatcode == 0x0003 ): jobstatname= "non-initialized"
  elif( jobstatcode == 0x0002 ): jobstatname= "initializing"
  elif( jobstatcode == 0x0103 ): jobstatname= "ready"
  elif( jobstatcode == 0x0202 ): jobstatname= "printing"
  elif( jobstatcode == 0x0303 ): jobstatname= "pausing"
  elif( jobstatcode == 0x0102 ): jobstatname= "stopping"
  else                         : jobstatname= "$"+jobstatcode
  joblayer= int.from_bytes(data[2:4], 'little')
  jobheight= int.from_bytes(data[4:6], 'little')
  jobprogress= int.from_bytes(data[6:7], 'little')
  jobtime= int.from_bytes(data[7:9], 'little')
  jobnoztemp= int.from_bytes(data[10:12], 'little')
  jobbedtemp= int.from_bytes(data[14:16], 'little')
  return (jobstatcode, jobstatname, joblayer, jobheight, jobprogress, jobtime, jobnoztemp, jobbedtemp)


# This port is hardwired inside the Cetus3D
CETUS3D_PORT= 31246
# The IP address is typically found by "discovery" (run ScanCetus3D.py)
CETUS3D_IP= "192.168.178.10" ### TODO: fill out correct IP num of your Cetus3D printer


# Create a local socket for the control server
print( "Server")
# Get own IP
ip= list(map(int,socket.gethostbyname(socket.gethostname()).split(".")))
print( "  hostip  : {}".format( ".".join(str(i) for i in ip) ))
# Create a TCP/IP socket
cssock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# Then bind() is used to associate the socket with the server address.
#cssock.bind( ('192.168.178.64', 0) )
cssock.bind( ("0.0.0.0", 0) )
csport= cssock.getsockname()[1] # Which local port was picked by the OS?
print("  hostport: {}".format(csport))
cssock.settimeout(5)
print("  timeout:  {}s".format(cssock.gettimeout()))
# Listen for incoming connections
cssock.listen(1)


# Send "CallMeHere"
MSG_CALLMEHERE= b"\xf0\xf0\x00\x02\x10\x4c\x00\x00\x00\x02\x00" + bytes([csport//256,csport%256]) + bytearray(ip) + b"\x2f\x78\x8d\x80\xf7\x7f\x00\x00\xc9\x1e\x6e\x25\xe8\x78\x6c\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x4d\x79\x50\x43\x00\x02\x00\x00\x02\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
#MSG_CALLMEHERE= b"\xf0\xf0\x00\x02\x10\x4c\x00\x00\x00\x02\x00" + bytes([csport//256,csport%256]) + bytearray(ip) + b"\x2f\x78\x47\xbe\xf7\x7f\x00\x00\xd1\x01\x6e\x25\xe8\x78\x08\x00\x00\x00\x00\x00\x9e\xda\x4c\x01\x00\x00\x4d\x61\x61\x72\x74\x65\x6e\x4c\x61\x70\x74\x6f\x70\x00\x00\x00\x96\x9d\x5f\xcd\xfd\x7f\x00\x00\xe3\x20\x03\xa8\x93\x0f\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
tmpsock= socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
tmpsock.sendto(MSG_CALLMEHERE, (CETUS3D_IP, CETUS3D_PORT))
print( "  sending : CallMeHere to {}:{}".format(CETUS3D_IP, CETUS3D_PORT))
# Close
tmpsock.close()


# Wait for a connection
print("Waiting for connect")
print('  ... ', end='',flush=True)
MSG_GIVESTATUS= b"\xf0\xf0\x00\x0e\x20\x40\x00\x00\x00\x72\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
try:
  connection, printer = cssock.accept()
except timeout:
  print("  timeout")
  sys.exit(2)
except KeyboardInterrupt:
  print("  aborted by user")
  sys.exit(1)

# accept() returns an open connection between the server and client, along with the address of the client.
# The connection is actually a different socket on another port (assigned by the kernel).
# Data is read from the connection with recv() and transmitted with sendall().
try:
  data= b""
  print("connect from {}:{}".format(printer[0],printer[1]))
  print("  press ^C to stop")
  msgix= 0
  print("  ----- --------------- ----- ------- ---- -------- ------- ------- --------------------------------------------------------------------------------------------------------------------------------")
  print("  {:>5} {:>15} {:>5} {:>7} {:>4} {:>8} {:7s} {:7s} {}".format("msgix","status","layer","height","prgs","time","noztemp","bedtemp","binary-message-data"))
  print("  ----- --------------- ----- ------- ---- -------- ------- ------- --------------------------------------------------------------------------------------------------------------------------------")
  while True:
    if( len(data)==0 ):
      connection.sendall(MSG_GIVESTATUS)
    # Receive the data in small chunks
    while True:
      data += connection.recv(16)
      if( len(data)==64 ):
        msgix+= 1
        (jobstatcode ,jobstatname, joblayer, jobheight, jobprogress, jobtime,jobnoztemp,jobbedtemp) = parse_CurrentStatus(data)
        nozunit= 'C' if jobnoztemp/50>2 else 'x'
        bedunit= 'C' if jobbedtemp/50>2 else 'x'
        print("  {:05} {:>15} L#{:<3d} {:5.1f}mm {:3}% {}s {:6.2f}{} {:6.2f}{} {}".format(msgix, jobstatname, joblayer, jobheight/10, jobprogress, str(datetime.timedelta(jobtime/24/60/60)), jobnoztemp/50, nozunit, jobbedtemp/50, bedunit, data.hex()))
        data= b""
        break
    time.sleep(1)
except KeyboardInterrupt:
  print("  aborted by user")
  pass
finally:
  # Clean up the connection
  connection.close()

# Close
cssock.close()
print("Done")

