#define message_length 2

const int digital1 = 48;
const int digital2 = 49;
const int digital3 = 50;
const int digital4 = 51;
const int digital5 = 52;
const int digital6 = 53;

const int digitalOuts[] = {digital1, digital2, digital3, digital4, digital5, digital6};

void setup() {
    for(int i=0; i<6; i++){
        pinMode(digitalOuts[i], OUTPUT);
        digitalWrite(digitalOuts[i], LOW);
    }
	Serial.begin(9600); // use the same baud-rate as the python side
}

int message[message_length];
int i = 0;
void loop() {
    while (Serial.available()) {
//         Serial.print(Serial.available());
        message[i++] = Serial.read();
    }
    if (i == message_length) {
        printMessage(i);
        setActivation(message[0], message[1]);
        i = 0;
        resetMessage(i);
    }
}

void setActivation(int deviceIndex, int activation){
  int a = activation > 0 ? HIGH : LOW;
//   Serial.print("setting activation ");
//   Serial.print(deviceIndex);
//   Serial.print(" ");
//   Serial.println(activation);
  digitalWrite(digitalOuts[deviceIndex], a);
}

void printMessage(int numBytes){
  for(int i=0; i<numBytes-1; i++){
    Serial.print(message[i]);
  }
  Serial.println(message[numBytes-1]);
}

void resetMessage(int numBytes){
  for(int i=0; i<numBytes; i++){
    message[i] = 0;
  }
}
