#include <TinyGPS++.h>
#include <SoftwareSerial.h>

TinyGPSPlus gps;

// Mega 2560的Serial2端口直接用于GPS通信
#define GPS_SERIAL Serial2

// 时区偏移（例如东八区为+8小时）
const int TIME_ZONE_OFFSET = 8; 

void setup() {
  Serial.begin(9600);     // 调试输出到串口监视器
  GPS_SERIAL.begin(38400); // GPS模块默认波特率通常为9600
  Serial.println("等待GPS信号...");
}

void loop() {
  // 持续读取GPS数据
  while (GPS_SERIAL.available() > 0) {
    char c = GPS_SERIAL.read();
    if (gps.encode(c)) {  // 解析GPS数据
      printTime();        // 输出时间
    }
  }

  // 如果GPS信号无效，提示检查
  if (millis() > 5000 && gps.charsProcessed() < 10) {
    Serial.println("未检测到GPS模块，请检查接线！");
    while(true); // 停止运行
  }
}

void printTime() {
  if (gps.time.isValid() && gps.date.isValid()) {
    // 提取UTC时间
    int utcHour = gps.time.hour();
    int utcMin = gps.time.minute();
    int utcSec = gps.time.second();
    
    // 时区调整（例如东八区）
    int localHour = utcHour + TIME_ZONE_OFFSET;
    if (localHour >= 24) localHour -= 24;
    else if (localHour < 0) localHour += 24;

    // 提取日期
    int year = gps.date.year();
    int month = gps.date.month();
    int day = gps.date.day();

    // 串口输出格式化时间
    Serial.print("日期: ");
    Serial.print(year);
    Serial.print("-");
    Serial.print(month < 10 ? "0" : "");
    Serial.print(month);
    Serial.print("-");
    Serial.print(day < 10 ? "0" : "");
    Serial.println(day);

    Serial.print("时间: ");
    Serial.print(localHour < 10 ? "0" : "");
    Serial.print(localHour);
    Serial.print(":");
    Serial.print(utcMin < 10 ? "0" : "");
    Serial.print(utcMin);
    Serial.print(":");
    Serial.print(utcSec < 10 ? "0" : "");
    Serial.println(utcSec);
    Serial.println("------------------");
  } else {
    Serial.println("等待GPS时间同步...");
    delay(1000);
  }
}