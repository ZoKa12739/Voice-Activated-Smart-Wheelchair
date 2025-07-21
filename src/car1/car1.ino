const int trigPin = A4;      // 超声波Trig接A5
const int echoPin = A5;      // 超声波Echo接A4

int motorSpeed = 200;        // 电机运行速度（0~255

volatile int yuyin;
#include <SoftwareSerial.h>

// 串口发送消息最大长度
#define UART_SEND_MAX      32
#define UART_MSG_HEAD_LEN  2
#define UART_MSG_FOOT_LEN  2
// 串口发送消息号
#define U_MSG_bozhensgshu      1
#define U_MSG_boxiaoshu      2
#define U_MSG_bobao1      3
#define U_MSG_bobao2      4
#define U_MSG_bobao3      5
#define U_MSG_bobao4      6
#define U_MSG_bobao5      7
#define U_MSG_bobao6      8
#define U_MSG_bobao7      9
#define U_MSG_bobao8      10
#define U_MSG_bobao9      11
#define U_MSG_bobao10      12
#define U_MSG_bobao11      13
#define U_MSG_bobao12      14
#define U_MSG_bobao13      15
#define U_MSG_bobao14      16
#define U_MSG_bobao15      17
#define U_MSG_bobao16      18
#define U_MSG_bobao17      19
#define U_MSG_bobao18      20
#define U_MSG_bobao19      21
#define U_MSG_bobao20      22
#define U_MSG_bobao21      23
#define U_MSG_bobao22      24
#define U_MSG_bobao23      25
#define U_MSG_bobao24      26
#define U_MSG_bobao25      27
#define U_MSG_bobao26      28
#define U_MSG_bobao27      29
#define U_MSG_bobao28      30
#define U_MSG_bobao29      31
#define U_MSG_bobao30      32
#define U_MSG_bobao31      33
#define U_MSG_bobao32      34
#define U_MSG_bobao33      35
#define U_MSG_bobao34      36
// 串口消息参数类型
typedef union {
  double d_double;
  int d_int;
  unsigned char d_ucs[8];
  char d_char;
  unsigned char d_uchar;
  unsigned long d_long;
  short d_short;
  float d_float;}uart_param_t;

SoftwareSerial mySerial(A8,A9);
// 串口发送函数实现
void _uart_send_impl(unsigned char* buff, int len) {
  // TODO: 调用项目实际的串口发送函数
  for(int i=0;i<len;i++)
{
   mySerial.write (*buff++);
}
}

// 串口通信消息尾
const unsigned char g_uart_send_foot[] = {
  0x55, 0xaa
};

// 十六位整数转32位整数
void _int16_to_int32(uart_param_t* param) {
  if (sizeof(int) >= 4)
    return;
  unsigned long value = param->d_long;
  unsigned long sign = (value >> 15) & 1;
  unsigned long v = value;
  if (sign)
    v = 0xFFFF0000 | value;
  uart_param_t p;  p.d_long = v;
  param->d_ucs[0] = p.d_ucs[0];
  param->d_ucs[1] = p.d_ucs[1];
  param->d_ucs[2] = p.d_ucs[2];
  param->d_ucs[3] = p.d_ucs[3];
}

// 浮点数转双精度
void _float_to_double(uart_param_t* param) {
  if (sizeof(int) >= 4)
    return;
  unsigned long value = param->d_long;
  unsigned long sign = value >> 31;
  unsigned long M = value & 0x007FFFFF;
  unsigned long e =  ((value >> 23 ) & 0xFF) - 127 + 1023;
  uart_param_t p0, p1;
  p1.d_long = ((sign & 1) << 31) | ((e & 0x7FF) << 20) | (M >> 3);
  param->d_ucs[0] = p0.d_ucs[0];
  param->d_ucs[1] = p0.d_ucs[1];
  param->d_ucs[2] = p0.d_ucs[2];
  param->d_ucs[3] = p0.d_ucs[3];
  param->d_ucs[4] = p1.d_ucs[0];
  param->d_ucs[5] = p1.d_ucs[1];
  param->d_ucs[6] = p1.d_ucs[2];
  param->d_ucs[7] = p1.d_ucs[3];
}

// 串口通信消息头
const unsigned char g_uart_send_head[] = {
  0xaa, 0x55
};

void setup(){
  Serial.begin(9600);
  //Serial2.begin(38400);
  pinMode(7, OUTPUT);
  pinMode(6, OUTPUT);
  pinMode(5, OUTPUT);
  pinMode(4, OUTPUT);
  analogWrite(5,0);
  analogWrite(6,0);
  digitalWrite(7,LOW);
  digitalWrite(4,LOW);
  mySerial.begin(9600);
  yuyin = 0;

   pinMode(trigPin, OUTPUT);
  pinMode(echoPin, INPUT);
  pinMode(motorPin1, OUTPUT);
  pinMode(motorPin2, OUTPUT);
}

long readUltrasonicDistance() {
  digitalWrite(trigPin, LOW);
  delayMicroseconds(2);
  
  digitalWrite(trigPin, HIGH);
  delayMicroseconds(10);
  digitalWrite(trigPin, LOW);
  
  long duration = pulseIn(echoPin, HIGH);
  long distance = duration * 0.0343 / 2;
  return distance;
}

void loop(){

//GPS模块
/*while(Serial2.available() >0){
  char c =Serial2.read();
  Serial.write(c);
}*/

//超声波测距
 /*long distance = readUltrasonicDistance();
  Serial.print("Distance: ");
  Serial.print(distance);
  Serial.println(" cm");
  
  if (distance < 30&&distance >0) {
    analogWrite(motorPin1, 100);
    analogWrite(motorPin2, 100);
    digitalWrite(7,HIGH);
    digitalWrite(4,HIGH);
    delay(200);
  } */
  
  //你好小爱唤醒语音识别模块
  //语音识别模块RX引脚接uno开发12引脚，TX引脚接uno开发8引脚

  if (mySerial.available() > 0) {
  yuyin = mySerial.read();
   Serial.println(yuyin,HEX);
  }
  if (yuyin == 1) {
    yuyin = 0;
    Serial.println("前进");
    goahead();
  }
  else if (yuyin == 2) {
    yuyin = 0;
    Serial.println("后退 ");
    goback();
  }
  else if (yuyin == 3) {
    yuyin = 0;
    Serial.println("左转 ");
    turnleft();
}
else if (yuyin == 4) {
    yuyin = 0;
    Serial.println("右转");
    turnright();
}
else if (yuyin == 5) {
    yuyin = 0;
    Serial.println("刹车");
    brake();
}
}
//前进控制
void goahead(){
  analogWrite(11,150);
  analogWrite(10,150);
  analogWrite(9,150);
  analogWrite(8,150);
  digitalWrite(34,HIGH);
  digitalWrite(35,LOW);
  digitalWrite(36,HIGH);
  digitalWrite(37,LOW);
  digitalWrite(38,HIGH);
  digitalWrite(39,LOW);
  digitalWrite(40,HIGH);
  digitalWrite(41,LOW);
}

//后退控制
void goback(){
  analogWrite(11,150);
  analogWrite(10,150);
  analogWrite(9,150);
  analogWrite(8,150);
  digitalWrite(34,LOW);
  digitalWrite(35,HIGH);
  digitalWrite(36,LOW);
  digitalWrite(37,HIGH);
  digitalWrite(38,LOW);
  digitalWrite(39,HIGH);
  digitalWrite(40,LOW);
  digitalWrite(41,HIGH);
}

//左转控制
void turnleft(){
  analogWrite(11,150);
  analogWrite(10,150);
  analogWrite(9,150);
  analogWrite(8,150);
  digitalWrite(34,LOW);
  digitalWrite(35,HIGH);
  digitalWrite(36,LOW);
  digitalWrite(37,HIGH);
  digitalWrite(38,HIGH);
  digitalWrite(39,LOW);
  digitalWrite(40,HIGH);
  digitalWrite(41,LOW);
}

//右转控制
void turnright(){
  analogWrite(11,150);
  analogWrite(10,150);
  analogWrite(9,150);
  analogWrite(8,150);
  digitalWrite(34,HIGH);
  digitalWrite(35,LOW);
  digitalWrite(36,HIGH);
  digitalWrite(37,LOW);
  digitalWrite(38,LOW);
  digitalWrite(39,HIGH);
  digitalWrite(40,LOW);
  digitalWrite(41,HIGH);
}

//刹车控制
void brake(){
  analogWrite(11,0);
  analogWrite(10,0);
  analogWrite(9,0);
  analogWrite(8,0);
  digitalWrite(34,LOW);
  digitalWrite(35,LOW);
  digitalWrite(36,LOW);
  digitalWrite(37,LOW);
  digitalWrite(38,LOW);
  digitalWrite(39,LOW);
  digitalWrite(40,LOW);
  digitalWrite(41,LOW);
}
