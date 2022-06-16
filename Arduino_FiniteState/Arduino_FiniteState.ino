const int digital1 = 48;
const int digital2 = 49;
const int digital3 = 50;
const int digital4 = 51;
const int digital5 = 52;
const int digital6 = 53;
const int digital7 = 22;
const int digital8 = 23;
const int digital9 = 24;
const int digital10 = 25;


const int digitalOuts[] =   {digital1, digital2, digital3, digital4, digital5,
                            digital6, digital7, digital8, digital9, digital10, LED_BUILTIN};

#define Start 0
#define S1 1
#define S2 2

const char StartSym = '-';
const char EndSym = '^';

int state = Start; //start in the start state
int channel = -1;
int activation = -1;

void setup() {
    for(int i=0; i<11; i++){
        pinMode(digitalOuts[i], OUTPUT);
        digitalWrite(digitalOuts[i], LOW);
    }
    Serial.begin(250000); // use the same baud-rate as the python side
}


void loop(){
    switch (state){
        case Start:
            ledOn(3);
            channel = -1;
            activation = -1;
            if (Serial.available()){
                int newByte = Serial.read();
                if ((char) newByte == StartSym || (char) newByte == EndSym){
                    state = Start;
                } else {
                    channel = (int) newByte;
                    state = S1;
                }
            }
            break;
        case S1:
            ledOn(2);
            if (Serial.available()){
                int newByte = Serial.read();
                if ((char) newByte == StartSym || (char) newByte == EndSym){
                    state = Start;
                } else {
                    activation = (int) newByte;
                    state = S2;
                }
            }
            break;
        case S2:
            ledOn(1);
            if (Serial.available()){
                int newByte = Serial.read();
                if ((char) newByte == EndSym){
                    setActivation(channel, activation);
                    Serial.print(channel);
                    Serial.println(activation);
                    state = Start;
                } else {
                    state = Start;
                }
            }
            break;
    }
}

void setActivation(int channel, int activation){
    if (channel < 0 || activation < 0){return;}
    
    int a = activation > 0 ? HIGH : LOW;
    digitalWrite(digitalOuts[channel - 1], a);
}

void ledOn(int j){
    for(int i=0; i<4; i++){
        digitalWrite(digitalOuts[6 + i], LOW);
    }
    digitalWrite(digitalOuts[6 + j], HIGH);
}
