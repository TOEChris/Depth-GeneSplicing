#include <MFRC522.h>
#include <SPI.h>

#define DEBUG

const byte numReaders = 3;
//47: Human DNA | 45: Cephalopod DNA | 43: Catalyst
const byte ssPins[numReaders] = {47, 45, 43};
const byte resetPin = 5;

MFRC522 mfrc522[numReaders];

String currentIDs[numReaders];

String correctIDs[numReaders] = {"ba9d18d3", "1474f1d5", "ecdcd183"}; //ala3d083
String idStatus[numReaders] = {"N", "N", "N"};

MFRC522::MIFARE_Key key;

//rfid data
byte sector         = 1;
byte blockAddr      = 4;
byte dataBlock[]    = {
    0xda, 0xdd, 0xee   //correct values for keg
    //0x11, 0x11, 0x11     //test values
};
byte trailerBlock   = 7;
MFRC522::StatusCode status;
byte buffer[18];
byte size = sizeof(buffer);
boolean started = false;

//String to serial print for parsing
String toPrint = "Temp";
String prevPrint = "";
String rfidData = "";

//pin data
const int rotAPin = 2;
const int rotBPin = 3;
const int tempPlus10Pin = 31;
const int tempPlus5Pin = 33;
const int tempPlus1Pin = 35;
const int tempMinus1Pin = 37;
const int tempMinus5Pin = 39;
const int tempMinus10Pin = 41;
const int startPin = 23;
const int voltPins[] = {24, 26, 28, 30, 32, 34, 36, 38};
const int lockPin = 10;

//data and debounce times
double tempData = 0;
double rotData = 0;
int voltData = 0;
int rotAState;
int lastRotAState;
long timeTempPlus10 = 0;
long timeTempPlus5 = 0;
long timeTempPlus1 = 0;
long timeTempMinus1 = 0;
long timeTempMinus5 = 0;
long timeTempMinus10 = 0;
long timeSend = 0;
long timeSerial = 0;
const int sendDebounce = 40;
const int compDebounce = 400;
float currentTime = 0;
boolean changedValue = false;
boolean rfidCorrect = false;
boolean kegComplete = false;

//String buffers
byte recBuff[10];
byte strBuff[10];

String temp;
void setup() {
  // put your setup code here, to run once:
  Serial.begin(9600);   // Initialize serial communications with the PC
  pinMode(tempPlus10Pin, INPUT_PULLUP);
  pinMode(tempPlus5Pin, INPUT_PULLUP);
  pinMode(tempPlus1Pin, INPUT_PULLUP);
  pinMode(tempMinus1Pin, INPUT_PULLUP);
  pinMode(tempMinus5Pin, INPUT_PULLUP);
  pinMode(tempMinus10Pin, INPUT_PULLUP);
  pinMode(rotAPin, INPUT);
  lastRotAState = digitalRead(rotAPin);
  pinMode(rotBPin, INPUT);
  pinMode(startPin, INPUT_PULLUP);
  pinMode(lockPin, LOW);
  for (int i=0; i < 8; i++)
  {
    pinMode(voltPins[i], INPUT_PULLUP);
    digitalWrite(voltPins[i], LOW);
  }
  
  while (!Serial);    // Do nothing if no serial port is opened (added for Arduinos based on ATMEGA32U4)
  SPI.begin();      // Init SPI bus
  
  for (byte i = 0; i < 6; i++) {
        key.keyByte[i] = 0xFF;
  }
  
  for (uint8_t i = 0; i < numReaders; i++) {
    mfrc522[i].PCD_Init(ssPins[i], resetPin);
    
    #ifdef DEBUG
    Serial.print(F("Reader #"));
    Serial.print(i);
    Serial.print(F(" initialised on pin "));
    Serial.print(String(ssPins[i]));
    Serial.print(F(". Antenna strength: "));
    Serial.print(mfrc522[i].PCD_GetAntennaGain());
    Serial.print(F(". Version : "));
    mfrc522[i].PCD_DumpVersionToSerial();
    #endif
    
    delay(100);
  }
}

void loop() {
  // put your main code here, to run repeatedly:
  if (Serial.available())
  {
    byte check = Serial.read();
    if (check == 'R')
    {
      fullReset();
    }
    if (check == 'S')
    {
      stageReset(); 
    }
    if (check == 'J')
    {
      rfidCorrect = true; 
    }
    if (check == 'W')
    {
      digitalWrite(lockPin, HIGH);
      delay(10);
      digitalWrite(lockPin, LOW);
      Serial.println("Lock triggered");
    }
  }
  if (!rfidCorrect)
  {
    String currentRFID = rfidCheck();
    Serial.println(currentRFID);
  }
  else
  {
    geneScreen();
  }
}


String rfidCheck() {
  for (int i = 0; i < numReaders; i++) {
    mfrc522[i].PCD_Init();
    String readRFID = "";

    if (mfrc522[i].PICC_IsNewCardPresent() && mfrc522[i].PICC_ReadCardSerial())
      readRFID = dump_byte_array(mfrc522[i].uid.uidByte, mfrc522[i].uid.size);
    else
      idStatus[i] = "N";
    // If the current reading is different from the last known reading
    if (readRFID != currentIDs[i])
      changedValue = true;

    currentIDs[i] = readRFID;
    if (currentIDs[i] == correctIDs[i]){
      if (i == 1 && !kegComplete) //special validation for keg, need to read rfid data
        kegComplete = validate(mfrc522[i]);
      else
        idStatus[i] = "Y"; //yes
    }
    else
    {
      if (i == 1)
        kegComplete = false;
      idStatus[i] = "N"; //no
    }
    mfrc522[i].PCD_AntennaOff();
  }
  
  String rfidData = "S-C-";
  for(int i = 0; i < numReaders; i++){
    if(i == 1)
    {
      if(kegComplete)
        idStatus[i] = "Y";
      else if (currentIDs[i] == correctIDs[i])
        idStatus[i] = "I";
      else
        idStatus[i] = "N";
    }
    rfidData += idStatus[i];
  }
  rfidData += "-E";
  return rfidData;
}

boolean validate(MFRC522 reader)
{
  status = (MFRC522::StatusCode) reader.PCD_Authenticate(MFRC522::PICC_CMD_MF_AUTH_KEY_A, trailerBlock, &key, &(reader.uid));
  if (status != MFRC522::STATUS_OK) {
        Serial.print(F("PCD_Authenticate() failed: "));
        Serial.println(reader.GetStatusCodeName(status));
        status = (MFRC522::StatusCode) reader.PCD_Authenticate(MFRC522::PICC_CMD_MF_AUTH_KEY_A, trailerBlock, &key, &(reader.uid));
  }
  #ifdef DEBUG
  reader.PICC_DumpMifareClassicSectorToSerial(&(reader.uid), &key, sector);
  #endif
  status = (MFRC522::StatusCode) reader.MIFARE_Read(blockAddr, buffer, &size);
  if (status != MFRC522::STATUS_OK) {
      Serial.print(F("MIFARE_Read() failed: "));
      Serial.println(reader.GetStatusCodeName(status));
  }
  boolean result = true;
  for (byte i = 10; i < 13; i++) {
    if (buffer[i] != dataBlock[i-10])
      result = false;
    #ifdef DEBUG
    Serial.print(buffer[i], HEX); Serial.print(" "); Serial.print(dataBlock[i-10],HEX); Serial.print(" ");
    #endif
  }
  Serial.println();
  return result;
}

void geneScreen()
{
  if (!started)
  {
    if(digitalRead(startPin) == LOW)
    {
      bool received = false;
      Serial.println("S-W-True-E");
      while (received == false)
      {
        memset(recBuff, 0, sizeof(recBuff));
        recBuff[0] = Serial.read();
        
        if (recBuff[0] == 'K')
        {
          received = true;
          started = true;
        }
        else
        {
          Serial.println("S-W-True-E");
        }
      }
    }
  }
    voltData = 0;
    prevPrint = toPrint;
    toPrint = "S-";
    currentTime = millis();
    if (digitalRead(tempPlus10Pin) == LOW && currentTime - timeTempPlus10 > compDebounce)
    {
      tempData += 10;
      timeTempPlus10 = millis();
    }
    if (digitalRead(tempPlus5Pin) == LOW && currentTime - timeTempPlus5 > compDebounce)
    {
      tempData += 5;
      timeTempPlus5 = millis();
    }

    if (digitalRead(tempPlus1Pin) == LOW && currentTime - timeTempPlus1 > compDebounce)
    {
      tempData += 1;
      timeTempPlus1 = millis();
    }

    if(digitalRead(tempMinus1Pin) == LOW && currentTime - timeTempMinus1 > compDebounce)
    {
      tempData -= 1;
      timeTempMinus1 = millis();
    }
    if(digitalRead(tempMinus5Pin) == LOW && currentTime - timeTempMinus5 > compDebounce)
    {
      tempData -= 5;
      timeTempMinus5 = millis();
    }
    if(digitalRead(tempMinus10Pin) == LOW && currentTime - timeTempMinus10 > compDebounce)
    {
      tempData -= 10;
      timeTempMinus10 = millis();
    }
    if (tempData < 0)
      tempData = 0;
    dtostrf(tempData, 10, 1, strBuff);
    temp = strBuff;
    toPrint += "T-" + temp + "-";
    
    rotAState = digitalRead(rotAPin);
    if (rotAState != lastRotAState)
    {
      if (digitalRead(rotBPin) != rotAState)
      {
        rotData += 0.025;
      }
      else
      {
        rotData -= 0.025;
        if (rotData <= 0)
          rotData = 0;
      }
      lastRotAState = rotAState;  
    }
    dtostrf(rotData, 10, 3, strBuff);
    temp = strBuff;
    toPrint += "R-" + temp + "-";

    for (int i=0; i < 8; i++)
    {
      if (digitalRead(voltPins[i]) == HIGH)
        voltData += ceil(pow(2, i));
    }

    itoa(voltData, strBuff, 10);
    temp = strBuff;
    toPrint += "V-" + String(temp);
  
    toPrint += "-E";
    if (currentTime - timeSend > sendDebounce)
    {
      timeSend = millis();
      Serial.println(toPrint);
    }
}




void printHex(byte *buffer, byte bufferSize) {
  for (byte i = 0; i < bufferSize; i++) {
    Serial.print(buffer[i] < 0x10 ? " 0" : " ");
    Serial.print(buffer[i], HEX);
  }
}


String dump_byte_array(byte *buffer, byte bufferSize) {
  String read_rfid = "";
  for (byte i = 0; i < bufferSize; i++) {
    read_rfid = read_rfid + String(buffer[i], HEX);
  }
  return read_rfid;
}

void stageReset()
{
  started = false;
  tempData = 0;
  rotData = 0;
  toPrint = "Temp";
  prevPrint = "";
  rfidData = "";  
  temp = "";
}
void fullReset()
{
  started = false;
  rfidCorrect = false;
  tempData = 0;
  rotData = 0;
  toPrint = "Temp";
  prevPrint = "";
  rfidData = "";  
  temp = "";
  kegComplete = false;
  Serial.println("Full Reset");
}
