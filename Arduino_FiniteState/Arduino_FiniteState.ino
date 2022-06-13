const int digital1 = 48;
const int digital2 = 49;
const int digital3 = 50;
const int digital4 = 51;
const int digital5 = 52;
const int digital6 = 53;
const int digitalOuts[] = {digital1, digital2, digital3, digital4, digital5, digital6};

#define Start 0
#define S1 1
#define S2 2
#define End 3

char StartSym = '-';
char EndSym = '\n';

int state = End; //start in the end state
int channel = -1;
int activation = -1;

void setup() {
    for(int i=0; i<6; i++){
        pinMode(digitalOuts[i], OUTPUT);
        digitalWrite(digitalOuts[i], LOW);
    }
	Serial.begin(9600); // use the same baud-rate as the python side
}


void loop(){
    while (Serial.available()){
        int newByte = Serial.read();
        switch (state){
            case Start:
//                 Serial.println("Start");
                if ((char) newByte == StartSym || (char) newByte == EndSym){
                    state = Start;
                } else {
                    channel = (int) newByte;
                    state = S1;
                }
                break;
            case S1:
//                 Serial.println("S1");
                if ((char) newByte == StartSym || (char) newByte == EndSym){
                    state = Start;
                } else {
                    activation = (int) newByte;
                    state = S2;
                }
                break;
            case S2:
//                 Serial.println("S2");
                if ((char) newByte == EndSym){
                    setActivation(channel, activation);
                    Serial.print(channel);
                    Serial.println(activation);
                    state = End;
                }
                break;
            case End:
//                 Serial.println("End");
                if ((char) newByte == StartSym){
                    channel = -1;
                    activation = -1;
                    state = Start;
                }
                break;
        }
    }
}

void setActivation(int deviceIndex, int activation){
    if (deviceIndex < 0 || activation < 0){return;}
    
    int a = activation > 0 ? HIGH : LOW;
    digitalWrite(digitalOuts[deviceIndex], a);
}
