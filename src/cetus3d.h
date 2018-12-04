/*
  cetus3d.h - Library to discover Cetus3d printers and get status information on a print
  2018 dec 04  v2  Maarten Pennings  Small textual changes
  2018 mar 03  v1  Maarten Pennings  Created
*/
#ifndef _CETUS3D_H_
#define _CETSU3D_H_


#include <stdint.h>
#include <ESP8266WiFi.h>


// A Cetus3D printer has a network stack to communicate with a host (typically a Windows PC, or an iPad)
// but now we add an ESP8266. There are two phases, discovery and control.
//
// Communication starts with discovery; the goal of discovery is to find the IP address of the printer.
// If the IP address is already known, the discovery phase can be skipped. Discovery starts with a 
// "WhoIsPresent" broadcast message from the host, and each Cetus3D replies to the host with an 
// "ImPresent" message, passing the printer's IP address, serial number, printer name and type. 
// The host then knows the IP address of the printer (assuming there is only one, or the printer 
// name is known).
//
// In the second phase of communication the host asks for status. The host opens a control server
// (i.e. opens a TCP port and listens) and sends a "CallMeHere" message to the printer (IP address). 
// The printer then establishes a connection with that control server. When the host is connected 
// to the printer, it can send commands. Note that there are several commands, e.g. for calibration, 
// initialization, uploading the print job and for getting status. This library only support the 
// "GiveStatus" command. The printer replies with "CurrentStatus", which includes remaining print
// time, nozzle temperature, print job height.
//
// When the host no longer needs to send commands, it closes the control connection. This is important,
// because a Cetus3D can only be connected to one control server (one host) at a time. This library only
// sends "get status". Therefore, it establishes a control connection, gets status once, and then closes.
// If the application using this library only makes infrequent "get status" requests, more important 
// control hosts, like a PC with Cetus3D software can still connect and give e.g. a stop command.


// Port 31246 is the port used by Cetus3D printers.
#define CETUS3D_PORT 31246


// ===== DISCOVERY ===== ===== ===== ===== ===== ===== ===== ===== ===== ===== ===== ===== 


// This structure contains the information published by a Cetus3D printer during discovery.
// Note that the printer name is published with 2-byte characters, this library assumes the second byte is always 0 (ASCII)

#define CETUS3D_NAME_MAXLEN     16
#define CETUS3D_TYPE_MAXLEN     32
#define CETUS3D_IMPRESENT_SIZE 137

typedef struct cetus3d_info_s {
  IPAddress ip;                          // IP number of the Cetus3D printer
  uint32    serial;                      // The serial number of the Cetus3D printer
  char      name[CETUS3D_NAME_MAXLEN+1]; // The name (as configured by the end-user) of the Cetus3D printer (+1 for terminating zero)
  char      type[CETUS3D_TYPE_MAXLEN+1]; // The type (as configured by the manufacturer (?)) of the Cetus3D printer (+1 for terminating zero)
  uint8_t   raw[CETUS3D_IMPRESENT_SIZE]; // The info bytes reported by the Cetus3D printer.
} cetus3d_info_t;

// This function will search the local network for Cetus3D printers.
// The number of printers found is returned, and the printer information is available in `printers`.
// Caller must allocate a the `printers` array, and pass the size (num of elements) in `num`.
// Note: seems only to work with num==1.
// Note: pass 1 for `verbose` to get progress prints on Serial.
// Note: discovery is done by broadcasting messages to `cetus3dport`.
int cetus3d_discover( cetus3d_info_t * printers, int num, int verbose=0, int cetus3dport=CETUS3D_PORT);


// ===== STATUS ===== ===== ===== ===== ===== ===== ===== ===== ===== ===== ===== ===== 


// This structure contains the information published by a Cetus3D printer when asked for status.
// Other fields are also published, but not yet understood.

#define CETUS3D_STATUS_SIZE 64

typedef struct cetus3d_status_s {
  int seqnum;                       // Sequence number
  int comm;                         // Communication code, see CETUS3D_COMM_XXX macros.
  int status;                       // Status code, see CETUS3D_STATUS_XXX macros for the known ones.
  int layer;                        // Layer number, counting from 0 up. Note that layers counts all layers, including an optional raft (e.g. 8 layer).
  int height;                       // Height in 1/10mm of the print job. This is excluding the raft (so the first 8 layers this stays zero). Steps with the "Layer Thickness" in "Print Settings".
  int progress;                     // Progress from 0 to 100 (%). It typically changes when the layer number increases.
  int remain_s;                     // Remaining print time in seconds. It typically changes when the layer number increases.
  int noztemp;                      // The nozzle temperature. When printing, noztemp/50 reports closeness to the temperature set point (actual-temp/set-point). When not printing, noztemp/50 is the temperature in C.
  int bedtemp;                      // The print bed temperature. When printing, bedtemp/50 reports closeness to the temperature set point (actual-temp/set-point). When not printing, bedtemp/50 is the temperature in C.
  uint8_t raw[CETUS3D_STATUS_SIZE]; // The status bytes reported by the Cetus3D printer.
} cetus3d_status_t;

// Communication codes as reported by cetus3d_getstatus().
#define CETUS3D_COMM_SUCCESS        0
#define CETUS3D_COMM_FAIL           1 // Any failure, not further detailed

// Known status codes as reported by the Cetus3D printer (in status_t.status).
#define CETUS3D_STATUS_NONINIT      0x0003 // Printer switched on, but not yet initialized.
#define CETUS3D_STATUS_INITIALIZING 0x0002 // Printer is initializing.
#define CETUS3D_STATUS_READY        0x0103 // Printer is initialized, but not yet or no longer printing.
#define CETUS3D_STATUS_PRINTING     0x0202 // Printer is printing (), this includes the heat-up phase.
#define CETUS3D_STATUS_PAUSING      0x0303 // Printer is pausing
#define CETUS3D_STATUS_STOPPING     0x0102 // Printer is stopping 
// Converts a CETUS3D_STATUS_XXX to a string
const char * cetus3d_status_str15( int status ); // max 15 chars
const char * cetus3d_status_str8 ( int status ); // max 8 chars

// This function will query the Cetus3D printer at ip address `ip` for status and return the result in `status`.
// If the communication with the printer fails, status->comm is CETUS3D_COMM_FAIL and all other fields in status are untouched.
// Note: If the printer is already connected to a PC or iPad this function will fail.
// Note: pass 1 for `verbose` to get progress prints on Serial.
// Note: status getting starts by sending a message to `cetus3dport`.
void cetus3d_getstatus(IPAddress ip, cetus3d_status_t * status, int verbose=0, int cetus3dport=CETUS3D_PORT);


#endif

