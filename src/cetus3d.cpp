/*
  cetus3d.c - Library to discover Cetus3d printers and get status information on a print
  2018 dec 04  v2  Maarten Pennings  Small textual changes
  2018 mar 03  v1  Maarten Pennings  Created
*/


#include "cetus3d.h"
#include <WiFiUdp.h>


// ===== DISCOVERY ===== ===== ===== ===== ===== ===== ===== ===== ===== ===== ===== ===== 


// The port used by the host during discovery (arbitrary number).
#define HOST_DISCOVERY_PORT  41414
// Time out for waiting on ImPresent messages
#define IMPRESENT_TIMEOUT_MS 2000
// IP address for broadcast
static const IPAddress IP_BROADCAST(255, 255, 255, 255);
// The WhoIsPresent message (the FFs need to be filled out still)
static uint8_t WhoIsPresent[] = "\xf0\xf0\x00\x01\x10\x12\x00\x00\x00\x02\x00\xc5\x63\xFF\xFF\xFF\xFF\x2f\x78\xa6\x62\xf6\x7f\x00\x00\xFF\xFF";    


// This function will search the local network for Cetus3D printers.
int cetus3d_discover( cetus3d_info_t * printers, int num, int verbose, int cetus3dport) {
  // Input validation
  if( num<1 || printers==0 ) return 0;
  
  // UDP socket to send (broadcast) the WhoIsPresent message and to receive the ImPresent messages.
  WiFiUDP  Udp;

  // Gather local ("host") IP data 
  IPAddress hostip= WiFi.localIP();
  if( verbose ) Serial.printf("cts3:Host\n");
  if( verbose ) Serial.printf("cts3:  hostip  : %s\n",hostip.toString().c_str());
  Udp.begin(HOST_DISCOVERY_PORT);
  if( verbose ) Serial.printf("cts3:  hostport: %d\n", HOST_DISCOVERY_PORT);

  // Fill out host IP in broadcast message
  WhoIsPresent[13]= hostip[0];
  WhoIsPresent[14]= hostip[1];
  WhoIsPresent[15]= hostip[2];
  WhoIsPresent[16]= hostip[3];
  // Fill out host port  in broadcast message
  WhoIsPresent[25]= HOST_DISCOVERY_PORT / 256;
  WhoIsPresent[26]= HOST_DISCOVERY_PORT % 256;

  // Broadcast WhoIsPresent
  Udp.beginPacket(IP_BROADCAST, CETUS3D_PORT);
  Udp.write(WhoIsPresent, sizeof WhoIsPresent -1 ); // not the terminating \0
  Udp.endPacket();
  if( verbose ) Serial.printf( "  sending : WhoIsPresent to *.*.*.*:%d\n",cetus3dport);

  // Wait for answers
  if( verbose ) Serial.printf("cts3:Waiting for ImPresent\n");
  int prix= 0; // printer index into printers[]
  int timeout_ms= IMPRESENT_TIMEOUT_MS; // when to stop waiting for answers
  memset(printers[prix].raw,0xA5,CETUS3D_IMPRESENT_SIZE); // Clear buffer (for debugging)
  while( prix<num && timeout_ms>0 ) {
    if( verbose ) Serial.printf("cts3:  waiting for printer %d ",prix);
    Udp.parsePacket();
    int rawix= 0; // byte index into printers[prix].raw[];
    while( rawix<CETUS3D_IMPRESENT_SIZE && timeout_ms>0 ) {
      rawix+= Udp.read(&printers[prix].raw[rawix], CETUS3D_IMPRESENT_SIZE-rawix);
      if( rawix<CETUS3D_IMPRESENT_SIZE) { 
        if( verbose ) printf(".");
        delay(50);
        timeout_ms-= 50;
      }
    }
    if( verbose ) printf("\n");
    if( rawix!=CETUS3D_IMPRESENT_SIZE ) return prix; // last wait failed
    // Extract printer ip
    printers[prix].ip= Udp.remoteIP();
    if( verbose ) Serial.printf("cts3:    ip  : %s\n", printers[prix].ip.toString().c_str());
    // Extract printer serial number
    printers[prix].serial= printers[prix].raw[9] + printers[prix].raw[10]*256U + printers[prix].raw[11]*256U*256U + printers[prix].raw[12]*256U*256U*256U;
    if( verbose ) Serial.printf("cts3:    snum: %u\n", printers[prix].serial);
    // Extract printer name
    for(int i=0; i<CETUS3D_NAME_MAXLEN; i++ ) printers[prix].name[i]= printers[prix].raw[i*2+73]; // Two byte chars, but we assume next byte is 0x00
    if( verbose ) Serial.printf("cts3:    name: %s\n", printers[prix].name);
    // Extract printer type
    for(int i=0; i<CETUS3D_TYPE_MAXLEN; i++ ) printers[prix].type[i]= printers[prix].raw[i+105]; // ASCII
    if( verbose ) Serial.printf("cts3:    type: %s\n", printers[prix].type);
    // Next printer
    prix++;    
  }

  // Done (Udp goes out of scope) 
  return prix;
}


// ===== STATUS ===== ===== ===== ===== ===== ===== ===== ===== ===== ===== ===== ===== 


// Time out for waiting on CallMeHere connect
#define CALLMEHERE_TIMEOUT_MS 2000
#define GIVESTATUS_TIMEOUT_MS 3000
// The port used by the host for the control server (arbitrary number).
#define HOST_CONTROL_PORT  52525
// The control server
WiFiServer controlserver(HOST_CONTROL_PORT);

// The CallMeHere message (the FFs need to be filled out still) 
static uint8_t CallMeHere[] = "\xf0\xf0\x00\x02\x10\x4c\x00\x00\x00\x02\x00\xFF\xFF\xFF\xFF\xFF\xFF\x2f\x78\x8d\x80\xf7\x7f\x00\x00\xc9\x1e\x6e\x25\xe8\x78\x6c\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x4d\x79\x50\x43\x00\x02\x00\x00\x02\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00";
// The GiveStatus message
static uint8_t GiveStatus[]= "\xf0\xf0\x00\x0e\x20\x40\x00\x00\x00\x72\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00";

const char * cetus3d_status_str15( int status ) {
  if     ( status == CETUS3D_STATUS_NONINIT      ) return "non-initialized";
  else if( status == CETUS3D_STATUS_INITIALIZING ) return "initializing";
  else if( status == CETUS3D_STATUS_READY        ) return "ready";
  else if( status == CETUS3D_STATUS_PRINTING     ) return "printing";
  else if( status == CETUS3D_STATUS_PAUSING      ) return "pausing";
  else if( status == CETUS3D_STATUS_STOPPING     ) return "stopping";
  else                                             return "<error>";
}

const char * cetus3d_status_str8( int status ) {
  if     ( status == CETUS3D_STATUS_NONINIT      ) return "non-init";
  else if( status == CETUS3D_STATUS_INITIALIZING ) return "initing";
  else if( status == CETUS3D_STATUS_READY        ) return "ready";
  else if( status == CETUS3D_STATUS_PRINTING     ) return "printing";
  else if( status == CETUS3D_STATUS_PAUSING      ) return "pausing";
  else if( status == CETUS3D_STATUS_STOPPING     ) return "stopping";
  else                                             return "<error>";
}

// This function will query the Cetus3D printer at ip address `ip` for status and return the result in `status`.
void cetus3d_getstatus(IPAddress ip, cetus3d_status_t * status, int verbose, int cetus3dport) {
  status->comm= CETUS3D_COMM_FAIL;
  if( status==0 ) { if( verbose ) Serial.printf("cts3: WARN: no arg\n"); return; }

  if( verbose ) Serial.printf("cts3:Host control server\n");
  IPAddress hostip= WiFi.localIP();
  if( verbose ) Serial.printf("cts3:  hostip  : %s\n",hostip.toString().c_str());
  if( verbose ) Serial.printf("cts3:  hostport: %d\n",HOST_CONTROL_PORT);
  controlserver.begin();

  // Fill out host port
  CallMeHere[11]= HOST_CONTROL_PORT / 256;
  CallMeHere[12]= HOST_CONTROL_PORT % 256;
  // Fill out host IP
  CallMeHere[13]= hostip[0];
  CallMeHere[14]= hostip[1];
  CallMeHere[15]= hostip[2];
  CallMeHere[16]= hostip[3];

  // UDP socket to send CallMeHere
  WiFiUDP  Udp;
  // Send CallMeHere
  Udp.beginPacket(ip, cetus3dport);
  Udp.write(CallMeHere, sizeof CallMeHere -1 ); // not the terminating \0
  Udp.endPacket();
  if( verbose ) Serial.printf("cts3:  sending : CallMeHere to %s:%d\n",ip.toString().c_str(),cetus3dport);

  // Wait for answer
  if( verbose ) Serial.printf("cts3:  waiting for printer ");
  WiFiClient client;
  int timeout_ms = CALLMEHERE_TIMEOUT_MS;
  while( client==0 && timeout_ms>0 ) {
    if( verbose ) Serial.printf(".");
    client= controlserver.available(); 
    delay(100);
    timeout_ms-= 100;
  }
  if( verbose ) Serial.printf("!\n");
  if( !client ) { if( verbose ) Serial.printf("cts3: WARN: no client\n"); return; }

  // Client (printer) connected, send GiveStatus
  if( verbose ) Serial.printf("cts3:  connected\n");
  client.write(GiveStatus, sizeof GiveStatus -1 ); // not the terminating \0
  
  // Wait for CurrentStatus
  if( verbose ) Serial.printf("cts3:  data: ");
  timeout_ms = GIVESTATUS_TIMEOUT_MS;
  int rawix=0;
  memset(status->raw,0x5A,CETUS3D_STATUS_SIZE); // Clear buffer (for debugging)
  while( client.connected() && rawix<CETUS3D_STATUS_SIZE && timeout_ms>0 ) {
    rawix+= client.read(&status->raw[rawix], CETUS3D_STATUS_SIZE-rawix);
    if( client.connected() && !client.available() && rawix<CETUS3D_STATUS_SIZE ) {
      if( verbose ) printf(".");
      delay(100);
      timeout_ms-= 100;
    }
  }
  if( verbose ) Serial.printf("\n");
  if( rawix==CETUS3D_STATUS_SIZE ) { 
    static int seqnum;
    status->seqnum= seqnum++;
    status->comm= CETUS3D_COMM_SUCCESS;
    status->status= status->raw[0]+status->raw[1]*256;
    status->layer= status->raw[2]+status->raw[3]*256;
    status->height= status->raw[4]+status->raw[5]*256;
    status->progress= status->raw[6];
    status->remain_s= status->raw[7]+status->raw[8]*256;
    status->noztemp= status->raw[10]+status->raw[11]*256;
    status->bedtemp= status->raw[14]+status->raw[15]*256;
  } else {
    if( verbose ) Serial.printf("cts3: WARN: %s\n", timeout_ms>0 ? "client disconnected": "data timeout"); 
  }
  
  // Disconnect from printer
  client.stop();
  if( verbose ) Serial.printf("cts3:  disconnected (payload=%d bytes)\n", rawix);
}
