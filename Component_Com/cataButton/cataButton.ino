const int cataButtonPin = 7;

void setup() {
  // put your setup code here, to run once:
  Serial.begin(19200);
  pinMode(cataButtonPin, INPUT_PULLUP);
}

void loop() {
  // put your main code here, to run repeatedly:
  if (digitalRead(cataButtonPin) == HIGH)
  {
    Serial.println(String(millis()));
    
  }
  while(digitalRead(cataButtonPin) == HIGH)
  {
      
  }
  delay(10);
}
