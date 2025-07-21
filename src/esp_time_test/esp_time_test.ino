#include <ESP8266WiFi.h>
#include <ESP8266WebServer.h>
#include "time.h"


// Wi-Fi 信息
const char* ssid = "Z";//WiFi名称
const char* password = "ky123456";//WiFi密码

void setup() {
  Serial.begin(115200);
  WiFi.begin(ssid, password);
  
  Serial.print("Connecting to WiFi");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println(" connected");

  // 设置时区，秒数偏移，比如东八区是 8*3600 秒
  configTime(8 * 3600, 0, "pool.ntp.org", "time.nist.gov");

  Serial.println("Waiting for time");
  while (time(nullptr) < 100000) {  // 等待时间同步
    delay(100);
  }
  Serial.println("Time synchronized");
}

void loop() {
  time_t now = time(nullptr);   // 获取当前时间戳
  struct tm* timeinfo = localtime(&now);  // 转成本地时间

  char timeStr[64];
  strftime(timeStr, sizeof(timeStr), "%Y-%m-%d %H:%M:%S", timeinfo);

  Serial.println(timeStr);

  delay(1000);
}


