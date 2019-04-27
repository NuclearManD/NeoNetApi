#define GPRS Serial1

//#define GPRS_DEBUG

void gprsCleanLine();

#define INBUF_SIZE 256

boolean connected = false;
int inlen = 0;
int inpos = 0;
byte tcp_buffer[INBUF_SIZE];

int tcp_available(){
  return inlen-inpos;
}

byte tcp_read(){
  inpos++;
  if(inpos>=INBUF_SIZE)inpos=inpos%INBUF_SIZE;
  return tcp_buffer[(inpos-1)%INBUF_SIZE];
}

String readGprs(boolean doRet=true){
  String result = "";
  boolean is_reading_yet = false;
  while(true){
    if(!GPRS.available()){
      long timer = millis()+1200;
      while(!GPRS.available()){
        if(timer<millis())return result;
      }
    }
    char c = GPRS.read();
    //Serial.write(c);
    if(c=='\r' || c=='\n' || (c==':'&&result.startsWith("+IPD"))){
      if(is_reading_yet){
        result.trim();
        break;
      }
    }else{
      result += (char)c;
      is_reading_yet = true;
    }
  }
  delay(5);
  if(result.indexOf("CLOSED")!=-1){
    connected=false;
    Serial.println("[disconnect]");
    if(doRet)return readGprs();
  }
  if(result.startsWith("+IPD")){
    int len = result.substring(5).toInt();
    #ifdef GPRS_DEBUG
    Serial.print("Reading TCP input, ");
    Serial.print(len);
    Serial.print(" bytes:");
    #endif
    for(int i=0;i<len;i++){
      while(!GPRS.available());
      byte data=GPRS.read();
      tcp_buffer[inlen]=data;
      #ifdef GPRS_DEBUG
      Serial.print(data, HEX);
      Serial.write(' ');
      #endif//*/
      inlen++;
    }
    if(inlen>=INBUF_SIZE)inlen=inlen%INBUF_SIZE;
    #ifdef GPRS_DEBUG
    Serial.print("\nBytes in TCP buffer:");
    Serial.println(tcp_available());
    #endif
    if(doRet)return readGprs();
  }
  #ifdef GPRS_DEBUG
  if(doRet)Serial.println("Got: "+result);
  #endif
  return result;
}

void gprsClean(){
  if(!GPRS.available())return;
  #ifdef GPRS_DEBUG
  Serial.println("[cleaning buffer]");
  #endif
  while(GPRS.available()){
    #ifdef GPRS_DEBUG
    Serial.print(GPRS.available());
    Serial.println(" bytes left to clear...");
    #endif
    readGprs(false);
  }
  #ifdef GPRS_DEBUG
  Serial.println("[done cleaning buffer]");
  #endif
}

void sys_yield(){
  gprsClean();
}

long tx_timer = 0;

void gprsWaitTx(){
  while(tx_timer>millis())gprsWaitTx();
  tx_timer = millis()+60;
}

String execGprsCommand(String command){
  //gprsClean();
  
  //gprsWaitTx();
  GPRS.println(command);
  #ifdef GPRS_DEBUG
  Serial.println("Sending: "+command);
  long timer = millis();
  #endif
  delay(5);
  String res = readGprs();
  String res2;
  //Serial.println(res);
  if(res==command){
    res2 = readGprs();
    if(res2!="")res=res2;
  }
  if((res=="OK" && command!="AT")||res==""){
    long timer = millis()+500;
    while(!GPRS.available()){
      if(timer<millis())goto ret;
      //delay(5);
    }
    res2 = readGprs();
    if(res2!="")res=res2;
  }
  ret:
  #ifdef GPRS_DEBUG
  Serial.println("Returned: '"+res+"' in "+(millis()-timer)+"ms.");
  #endif
  //gprsWaitTx();
  return res;
}

String my_ip = "UNKNOWN";

boolean setup_gprs() {
  GPRS.begin(19200);
  delay(100);
  // clear buffer of junk data
  while(GPRS.available())GPRS.read();
  for(int i=0;i<10;i++){
    if(execGprsCommand("AT")=="OK"){
      break;
    }
    if(i==9)return false;
    delay(200);
  }
  execGprsCommand("ATE0");
  int cnt = 0;
  while(execGprsCommand("AT+CIPSHUT")!="SHUT OK"){
    if(cnt==3) return false;
    cnt++;
  }
  cnt = 0;
  execGprsCommand("AT+CIPMUX=0");
  while(execGprsCommand("AT+CIPSTATUS").indexOf("IP INITIAL")==-1){
    delay(200);
    if(cnt==15)return false;
    cnt++;
  }
  cnt = 0;
  if(execGprsCommand("AT+CSTT= \"hologram\", \"\", \"\"")!="OK")return false;
  while(execGprsCommand("AT+CIPSTATUS").indexOf("IP START")==-1){
    delay(200);
    if(cnt==15)return false;
    cnt++;
  }
  cnt = 0;
  execGprsCommand("AT+CIICR");
  while(execGprsCommand("AT+CIPSTATUS").indexOf("GPRSACT")==-1){
    delay(200);
    if(cnt==15)return false;
    cnt++;
  }
  cnt = 0;
  //execGprsCommand("AT+CIPSHUT");
  my_ip = execGprsCommand("AT+CIFSR");

  // set communication parameters
  execGprsCommand("AT+CIPHEAD=1");
  gprsClean();
  #ifdef GPRS_DEBUG
  Serial.println("GPRS Connected!\n\n");
  #endif
  return true;
}
#define CONNECT_ERR_GPRS -1
#define CONNECT_ERR_TCP -2
int connect_tcp(String ip, int port){
  String result = execGprsCommand("AT+CIPSTART=\"TCP\",\""+ip+"\",\""+String(port)+"\"");
  while(result=="" or result=="OK")result = readGprs();
  if(result.indexOf("ERROR")!=-1){
    Serial.println("ERROR = "+execGprsCommand("AT+CEER"));
    return CONNECT_ERR_GPRS;
  }
  if(result.indexOf("FAIL")!=-1)return CONNECT_ERR_TCP;
  if(result.indexOf("CONNECT OK")!=-1){
    connected=true;
    return 0;
  }
}

int tcp_send(byte* data, int len){
  String res = execGprsCommand("AT+CIPSEND="+String(len));
  //delay(20);
  if(res.indexOf(">")==-1){
    connected = false;
    return -1;
  }
  GPRS.write(data,len);
  //GPRS.write(0x1a);
  long timeout = millis()+5000;
  res = readGprs();
  while(res==""&&timeout>millis())res = readGprs();
  /*if(res.indexOf("ERROR")!=-1){
    Serial.println("ERROR = "+execGprsCommand("AT+CEER"));
  }else if(res.indexOf("SEND OK")==-1){
    Serial.println("TCP?e='"+res+"'");
  }*/
  #ifdef GPRS_DEBUG
  /*Serial.print("TCPOUT: ");
  for(int i=0;i<len;i++){
    Serial.print(data[i],HEX);
    Serial.write(' ');
  }
  Serial.println('\n'+res);//*/
  #endif
  return res.indexOf("SEND OK")==-1 ? -2 : 0;
}
int tcp_send(String s){
  tcp_send((byte*)s.c_str(),s.length());
}
int tcp_close(){
  return execGprsCommand("AT+CIPCLOSE")=="SHUT OK" ? 0 : -1;
}
