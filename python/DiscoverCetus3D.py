# DiscoverCetus3D - Discovers cetus3D printers on the local network 
import socket  
import sys


print("DiscoverCetus3D")
print("  Discovers cetus3D printers on the local network")
print("  2018 mar 3 Maarten Pennings")
# Output should be something like this
# DiscoverCetus3D
#   Discovers cetus3D printers on the local network
#   2018 mar 3 Maarten Pennings
# Receiver
#   IP: 192.168.178.20
#   rxport: 41121
#   sent: WhoIsPresent to *:31246
# Waiting for ImPresent
#   ... received from 192.168.178.10:31246
#   Serial num: 12345678
#   Name: 'MyCetus3D'
# Done


# "ImPresent" (137 bytes) UDP printer->host
# 0 0 0 0 0 0 0 0 0  0 1 1 1  1 1 1 1 1 1 1 2 2 2 2 2 2 2 2 2 2 3 3 3 3 3 3 3 3 3 3 4 4 4 4 4 4 4 4 4 4 5 5 5 5 5 5 5 5 5 5 6 6 6 6 6 6 6 6 6 6 7 7 7  7 7 7 7 7 7 7 8 8 8 8 8 8 8 8 8 8 9 9 9 9 9 9 9 9 9 9 1010101010 101010101011111111111111111111121212121212121212121313131313131313
# 0 1 2 3 4 5 6 7 8  9 0 1 2  3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2  3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4  5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7  
#                    prsernum                                                                                                                          M---y---C---e---t---u---s---3---D---<00>                         C-e-t-u-s- -S-7-(-N-L-)-
# f0f000014080000000 a233d15f 000000007f27000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000 4d00790043006500740075007300330044000000000000000000000000000000 4365747573205337284e4c290000000000000000000000000000000000000000
def parse_ImPresent(data):
  prsnum= int.from_bytes(data[9:13], 'little')
  prname= data[73:105].decode("utf_16")
  prtype= data[105:137].decode("utf_8")
  return (prsnum,prname,prtype)

  
# This port is hardwired inside the Cetus3D; the Cetus listens to "WhoIsPresent" messages here.
CETUS3D_PORT=31246


# Create local socket so that the Cetus3D can send "ImPresent" back to us
print( "Receiver")
# Get own IP
ip= list(map(int,socket.gethostbyname(socket.gethostname()).split(".")))
print( "  hostip  : {}".format( ".".join(str(i) for i in ip) ))
# Create the rx socket
rxsock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM) # UDP
rxsock.bind(("0.0.0.0", 0))
rxsock.settimeout(5) # seconds
rxport= rxsock.getsockname()[1] # Which local port was picked by the OS?
print( "  hostport: {}".format(rxport))


# Send "WhoIsPresent"
# Create the tx socket
tmpsock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
tmpsock.setsockopt(socket.SOL_SOCKET,socket.SO_BROADCAST, 1)
# Compose message (content unknown except for two fields: the IP and port number - the Cetus should send ImPresent to this)
MSG_WHOISPRESENT = b"\xf0\xf0\x00\x01\x10\x12\x00\x00\x00\x02\x00\xc5\x63"+bytearray(ip)+b"\x2f\x78\xa6\x62\xf6\x7f\x00\x00"+bytes([rxport//256,rxport%256])    
# Send
tmpsock.sendto(MSG_WHOISPRESENT, ("255.255.255.255", CETUS3D_PORT)) # broadcast message to all Cetus3Ds
print( "  sending : WhoIsPresent to *.*.*.*:31246")
# Close
tmpsock.close()


# Waiting for (a single) "ImPresent"
print("Waiting for ImPresent")
print('  ... ', end='',flush=True)
try:
  data, addr = rxsock.recvfrom(1024) # buffer size is 1024 bytes
  print("received")
  print("  prip    : {}\n  prport  : {}".format(addr[0],addr[1]))
  (prsnum,prname,prtype)= parse_ImPresent(data)
  print("  prsnum  : {}\n  prname  : {}\n  prtype  : {}".format(prsnum,prname,prtype))
except:
  print("no answer")


# Close  
rxsock.close()
print("Done")
