
#include <WiFi.h>
#include <AsyncTCP.h>
#include <ESPAsyncWebServer.h>

// first ssid and password
const char* hsssid = "<<ENTER YOUR SSID>>";
const char* hspassword = "<<ENTER YOUR PASSWORD>>";

// second ssid and password in case first one fails
const char* ssid = "<<ENTER YOUR SSID>>";
const char* password = "<<ENTER YOUR PASSWORD>>";

float mul = 1;

const int trigPin = 33;
const int echoPin = 32;

#define EN_A 5
#define IN1 18
#define IN2 19

#define EN_B 15
#define IN3 4
#define IN4 2

#define SOUND_SPEED 0.034
#define CM_TO_INCH 0.393701

long duration;
float distanceCm;
float distanceInch;


// Create AsyncWebServer object on port 80
AsyncWebServer server(80);
AsyncWebSocket ws("/ws");

const char index_html[] PROGMEM = R"rawliteral(
<!DOCTYPE HTML><html>
<head>
  <title>ESP Web Server</title>
</head>
<body>
</body>
</html>
)rawliteral";

// defining the function to be called when the url is requested

void backward(){

  analogWrite(EN_A, int(mul*255));
  analogWrite(EN_B, int(mul*255));
  
  digitalWrite(IN1, HIGH);
  digitalWrite(IN2, LOW);
  
  digitalWrite(IN3, HIGH);
  digitalWrite(IN4, LOW);
}

void forward(){

  analogWrite(EN_A, int(mul*255));
  analogWrite(EN_B, int(mul*255));
    
  digitalWrite(IN1, LOW);
  digitalWrite(IN2, HIGH);

  digitalWrite(IN3, LOW);
  digitalWrite(IN4, HIGH);
}


void parked(){
  analogWrite(EN_A, 0);
  analogWrite(EN_B, 0);
  digitalWrite(IN1, LOW);
  digitalWrite(IN2, LOW);
  digitalWrite(IN3, LOW);
  digitalWrite(IN4, LOW);
}

void left(int speed = 100){
  analogWrite(EN_A, int(mul*255));
  digitalWrite(IN1, HIGH);
  digitalWrite(IN2, LOW);

  analogWrite(EN_B, int(mul*255));
  digitalWrite(IN3, LOW);
  digitalWrite(IN4, HIGH);
}

void right(int speed = 100){
  analogWrite(EN_A, int(mul*255));
  digitalWrite(IN1, LOW);
  digitalWrite(IN2, HIGH);

  analogWrite(EN_B, int(mul*255));
  digitalWrite(IN3, HIGH);
  digitalWrite(IN4, LOW);
}


// notifing the client about the distance

void notifyClients() {
  ws.textAll(String(distanceCm));
}

void handleWebSocketMessage(void *arg, uint8_t *data, size_t len) {
  AwsFrameInfo *info = (AwsFrameInfo*)arg;
  if (info->final && info->index == 0 && info->len == len && info->opcode == WS_TEXT) {
    data[len] = 0;
    if (strcmp((char*)data, "forward") == 0) {
      forward();
    }
    if (strcmp((char*)data, "backward") == 0) {
      backward();
    }
    if (strcmp((char*)data, "parked") == 0) {
      parked();
    }
    if (strcmp((char*)data, "right") == 0) {
      right();
    }
    if (strcmp((char*)data, "left") == 0) {
      left();
    }
    String st = (char*)data;
    if (st.substring(0,6) == "speed:") {
      mul = st.substring(6).toInt()/100.0;
      Serial.println(mul);
      Serial.println(int(255*mul));
      
    }
  }
}

void onEvent(AsyncWebSocket *server, AsyncWebSocketClient *client, AwsEventType type,
             void *arg, uint8_t *data, size_t len) {
  switch (type) {
    case WS_EVT_CONNECT:
      Serial.printf("WebSocket client #%u connected from %s\n", client->id(), client->remoteIP().toString().c_str());
      break;
    case WS_EVT_DISCONNECT:
      Serial.printf("WebSocket client #%u disconnected\n", client->id());
      break;
    case WS_EVT_DATA:
      handleWebSocketMessage(arg, data, len);
      break;
    case WS_EVT_PONG:
    case WS_EVT_ERROR:
      break;
  }
}

void initWebSocket() {
  ws.onEvent(onEvent);
  server.addHandler(&ws);
}



void setup(){

  Serial.begin(115200);
  Serial.println(mul);
  Serial.println(int(255*mul));

  pinMode(trigPin, OUTPUT); 
  pinMode(echoPin, INPUT); 

  pinMode(EN_A, OUTPUT);
  pinMode(IN1, OUTPUT);
  pinMode(IN2, OUTPUT);
  pinMode(EN_B, OUTPUT);
  pinMode(IN3, OUTPUT);
  pinMode(IN4, OUTPUT);

  // Connect to Wi-Fi
  WiFi.begin(hsssid, hspassword);
  delay(3000);
  if (WiFi.status() != WL_CONNECTED) {
    WiFi.begin(ssid, password);
    while (WiFi.status() != WL_CONNECTED) {
      delay(1000);
      Serial.println("Connecting to WiFi..");
    }  
  }

  Serial.println(WiFi.SSID());
  Serial.println(WiFi.localIP());

  initWebSocket();

  server.on("/", HTTP_GET, [](AsyncWebServerRequest *request){
    request->send_P(200, "text/html", index_html);
  });

  // Start server
  server.begin();
}


void loop() {

  // gettin the distance
  digitalWrite(trigPin, LOW);
  delayMicroseconds(2);
  digitalWrite(trigPin, HIGH);
  delayMicroseconds(10);
  digitalWrite(trigPin, LOW);
  
  duration = pulseIn(echoPin, HIGH);
  
  distanceCm = duration * SOUND_SPEED/2;
  distanceInch = distanceCm * CM_TO_INCH;

  // stop the car if the distance is less than 10 cm
  if (distanceCm < 10){
    parked();
  }

  ws.cleanupClients();
  delay(100);
}
