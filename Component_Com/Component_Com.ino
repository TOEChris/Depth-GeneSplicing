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

bool sendData = false;

//String to serial print for parsing
String toPrint = "";
String prevPrint = "";
String rfidData = "";

//pin data
const int tempPlus5Pin = 33;
const int tempPlus1Pin = 35;

//data and debounce times
float pressureData = 23.3;
long timeTempPlus5 = 0;
long timeTempPlus1 = 0;
long timeSend = 0;
const int sendDebounce = 200;
const int compDebounce = 200;
float currentTime = 0;

void setup() {
  // put your setup code here, to run once:
  Serial.begin(9600);   // Initialize serial communications with the PC
  pinMode(tempPlus5Pin, INPUT_PULLUP);
  pinMode(tempPlus1Pin, INPUT_PULLUP);
  
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
  if (!sendData)
  {
    byte temp = Serial.read();
    if(temp == 'Z')
    {
      sendData = true;
    }
  }
  else
  {
    prevPrint = toPrint;
    toPrint = "";
    currentTime = millis();
    if (digitalRead(tempPlus5Pin) == LOW && currentTime - timeTempPlus5 > compDebounce)
    {
      pressureData += 5;
      timeTempPlus5 = millis();
    }

    if (digitalRead(tempPlus1Pin) == LOW && currentTime - timeTempPlus1 > compDebounce)
    {
      pressureData += 1;
      timeTempPlus1 = millis();
    }
    toPrint += "P-" + (String)pressureData;
    
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
    
    if (currentTime - timeSend > sendDebounce && toPrint != prevPrint)
    {
      Serial.println(toPrint);
      timeSend = millis();
    }
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
  
