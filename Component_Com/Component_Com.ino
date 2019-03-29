#include <MFRC522.h>
#include <SPI.h>

#define RST_PIN         9          // Configurable, see typical pin layout above
#define SS_PIN          10       // Configurable, see typical pin layout above

MFRC522 mfrc522(SS_PIN, RST_PIN);  // Create MFRC522 instance

MFRC522::MIFARE_Key key;
byte valid[] = {0x14, 0x74, 0xF1, 0xD5};
bool validate = true;
bool there = false;
bool check = false;

//rfid data
byte sector         = 1;
byte blockAddr      = 4;
byte dataBlock[]    = {
    0x00, 0x00, 0x00, 0x00, //won value
    0x00, 0x00, 0x00, 0x00, 
    0x00, 0x00, 0xda, 0xdd, 
    0xee, 0x00, 0x00, 0x00  
};
byte trailerBlock   = 7;
MFRC522::StatusCode status;
byte buffer[18];
byte size = sizeof(buffer);
bool started = false;

//String to serial print for parsing
String toPrint = "Temp";
String prevPrint = "";
String rfidData = "";

//pin data
const int rotAPin = 2;
const int rotBPin = 3;
const int tempPlus5Pin = 33;
const int tempPlus1Pin = 35;
const int startPin = 23;
const int voltPins[] = {24, 26, 28, 30, 32, 34, 36, 38};

//data and debounce times
double tempData = 0;
double rotData = 0;
int voltData = 0;
int rotAState;
int lastRotAState;
long timeTempPlus5 = 0;
long timeTempPlus1 = 0;
long timeSend = 0;
long timeSerial = 0;
const int sendDebounce = 40;
const int compDebounce = 350;
float currentTime = 0;
//String buffers
byte recBuff[10];
int recBuffIndex = 0;
byte strBuff[10];

String temp;
void setup() {
  // put your setup code here, to run once:
  Serial.begin(9600);   // Initialize serial communications with the PC
  pinMode(tempPlus5Pin, INPUT_PULLUP);
  pinMode(tempPlus1Pin, INPUT_PULLUP);
  pinMode(rotAPin, INPUT);
  lastRotAState = digitalRead(rotAPin);
  pinMode(rotBPin, INPUT);
  pinMode(startPin, INPUT_PULLUP);
  for (int i=0; i < 8; i++)
  {
    pinMode(voltPins[i], INPUT_PULLUP);
    digitalWrite(voltPins[i], LOW);
  }
  
  while (!Serial);    // Do nothing if no serial port is opened (added for Arduinos based on ATMEGA32U4)
  SPI.begin();      // Init SPI bus
  //mfrc522.PCD_Init();   // Init MFRC522
  //mfrc522.PCD_DumpVersionToSerial();  // Show details of PCD - MFRC522 Card Reader details
  Serial.println(F("Scan PICC to see UID, SAK, type, and data blocks..."));
  //for (byte i = 0; i < 6; i++) {
  //      key.keyByte[i] = 0xFF;
  //}
}

void loop() {
  // put your main code here, to run repeatedly:
  if (Serial.available())
  {
    byte resetCheck = Serial.read();
    if (resetCheck == 'R')
    {
      reset();
    }
  }
  if (!started)
  {
    if(digitalRead(startPin) == LOW)
    {
      bool received = false;
      Serial.println("S-W-True-E");
      while (received == false)
      {
        recBuffIndex = 0;
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
    /*
    else if (digitalRead(CPin) == HIGH  && millis() - timeC > debounce)
    {
      toPrint += "C ";
      timeC = millis();
      sendData = true;
    }
  
    else if (digitalRead(GPin) == HIGH  && millis() - timeG > debounce)
    {
      toPrint += "G ";
      timeG = millis();
      sendData = true;
    }
  
    else if (digitalRead(TPin) == HIGH  && millis() - timeT > debounce)
    {
      toPrint += "T ";
      timeT = millis();
      sendData = true;
    }
    
    if (digitalRead(ConPin) == HIGH  && millis() - timeCon > debounce)
    {
      toPrint += "confirm ";
      timeCon = millis();
      sendData = true;
    }
  
    if (digitalRead(BackPin) == HIGH  && millis() - timeBack > debounce)
    {
      toPrint += "back ";
      timeBack = millis();
      sendData = true;
    }
    
    rfidCheck();
    if (rfidData != "" and rfidData != prevCheck)
    {
      toPrint += rfidData;
      prevCheck = rfidData;
      sendData = true;
    }
    */
    toPrint += "-E";
    if (currentTime - timeSend > sendDebounce)
    {
      timeSend = millis();
      Serial.println(toPrint);
    }
}

void rfidCheck(){
    validate = true;
    if (!mfrc522.PICC_IsNewCardPresent()) {
      //timeRead = millis();
      if (!there){
          rfidData = "No Card ";
          return;
      }
    } 

    if ( ! mfrc522.PICC_ReadCardSerial()) 
       there = false;
    else
       there = true;

   
    // Authenticate using key A
    status = (MFRC522::StatusCode) mfrc522.PCD_Authenticate(MFRC522::PICC_CMD_MF_AUTH_KEY_A, trailerBlock, &key, &(mfrc522.uid));
    if (status != MFRC522::STATUS_OK) {
        //Serial.print(F("PCD_Authenticate() failed: "));
        //Serial.println(mfrc522.GetStatusCodeName(status));
        return;
    }
    // Authenticate using key B
    status = (MFRC522::StatusCode) mfrc522.PCD_Authenticate(MFRC522::PICC_CMD_MF_AUTH_KEY_B, trailerBlock, &key, &(mfrc522.uid));
    if (status != MFRC522::STATUS_OK) {
        //Serial.print(F("PCD_Authenticate() failed: "));
        //Serial.println(mfrc522.GetStatusCodeName(status));
        return;
    }
    for (int i=0; i < 4; i++)
    {
       if (mfrc522.uid.uidByte[i] != valid[i])
         validate = false;
    }
    
    
    if (validate)
    {
        rfidData = "Right ";
    }

    else if (!validate)
    {
        rfidData = "Wrong ";
    }
}

void printHex(byte *buffer, byte bufferSize) {
  for (byte i = 0; i < bufferSize; i++) {
    Serial.print(buffer[i] < 0x10 ? " 0" : " ");
    Serial.print(buffer[i], HEX);
  }
}
void reset()
{
  started = false;
  tempData = 0;
  rotData = 0;
  toPrint = "Temp";
  prevPrint = "";
  rfidData = "";  
  temp = "";
  Serial.println("Reset");
}
