/*
  Cetus3Dbasic.ino - Application that prints Cetus3D status information on Serial
  Created by Maarten Pennings 2018 dec 4
*/


#include <ESP8266WiFi.h>
#include "cetus3d.h"


#if 0
  // Fill out the credentials of your local WiFi Access Point
  const char *  wifiSsid              = "xxxxx"; // Your WiFi network SSID name
  const char *  wifiPassword          = "xxxxx"; // Your WiFi network password
#else
  // File that contains (my secret) credentials for WiFi and ThingSpeak
  #include "credentials.h"
#endif


// Print the status in `ps` nicely on Serial. 
// If `rawtoo` holds, also the raw status bytes are printed.
// If `ps` is 0, prints a header only.
void status_print(cetus3d_status_t *ps, int rawtoo=1) {
  if( ps==0 ) {
    // Print header only
    Serial.printf("stat: %5s %6s : %4s/%15s %5s %7s %4s %8s %7s %7s ",
     "seq#", "clock", "stat", "statusname     ", "layer", "height", "done", "remain", "nozzle", "hotbed" );
    if( rawtoo ) Serial.printf("Rawdata"); 
    Serial.printf("\n");
    return;
  }
  // Split remaining time in hours/minutes/seconds
  int sec= ps->remain_s;
  int min=sec/60; sec%=60;
  int hr=min/60; min%=60;
  // Print fields
  Serial.printf("stat: %05u %05lus : %04x/%-15s L%04u %3u.%01umm %3u%% %2u:%02u:%02u %3u.%02u%c %3u.%02u%c ",
    ps->seqnum,(millis()+500)/1000,
    ps->status, cetus3d_status_str15(ps->status),
    ps->layer,
    ps->height/10,ps->height%10,
    ps->progress,
    hr,min,sec,
    ps->noztemp/50,(ps->noztemp%50)*2,ps->noztemp>100?'C':'x',
    ps->bedtemp/50,(ps->bedtemp%50)*2,ps->bedtemp>100?'C':'x');
  // Print raw
  if( rawtoo ) {
    for( int i=0; i<64; i++ ) Serial.printf("%02x",ps->raw[i]); 
  }
  Serial.printf("\n");
}


// Application mode variables
cetus3d_info_t    printer_info;
cetus3d_status_t  printer_status;


void setup() {
  // Enable Serial (for tracing prints)
  Serial.begin(115200);
  Serial.printf("\nWelcome to Cetus3Dbasic\n");

  // Enable WiFi
  Serial.print("setup: WiFi '");
  Serial.print(wifiSsid);
  Serial.print("' ..");
  WiFi.mode(WIFI_STA);
  WiFi.begin(wifiSsid, wifiPassword);
  while( WiFi.status()!=WL_CONNECTED ) {
    delay(250);
    Serial.printf(".");
  }
  Serial.printf(" ESP8266 at %s\n",WiFi.localIP().toString().c_str());

  // Try to find a Cetus3D printer
  Serial.print("setup: Finding Cetus3D ..");
  int numfound= 0;
  while( numfound==0 ) {
    numfound= cetus3d_discover(&printer_info,1);
    Serial.printf(".");
    if( numfound==0 ) delay(5000);
  }
  Serial.printf(" found '%s' at %s\n", printer_info.name, printer_info.ip.toString().c_str());

  // Print header
  status_print(0,0);
}


void loop() {
  // Try to get status report from the Cetus3D printer
  cetus3d_getstatus(printer_info.ip, &printer_status,0);
  if( printer_status.comm==CETUS3D_COMM_SUCCESS ) {
    // Get status successful
    status_print(&printer_status,0);
  } else { 
    Serial.printf("loop: Get status failed\n");
  }
  // Wait a bit; as long as this sketch is contacting the Cetus3D no other host
  // (e.g. PC or iPAD with UP software) can contact the Cetus3D. So take long intervals.
  delay(10000);
}
