#include <ESP8266WiFi.h>
#include <ESP8266WebServer.h>
#include <WiFi.h>
#include "time.h"

// Wi-Fi 信息
const char* ssid = "Z";//WiFi名称
const char* password = "ky123456";//WiFi密码

// 创建 Web 服务器对象，监听 80 端口（HTTP 默认端口）
ESP8266WebServer server(80);

void setup() {
  Serial.begin(115200);
  WiFi.begin(ssid, password);
  Serial.print("正在连接Wi-Fi");

  // 等待连接成功
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println("");
  Serial.println("Wi-Fi 已连接！");
  Serial.print("IP 地址：");
  Serial.println(WiFi.localIP()); // 记住这个 IP，浏览器用！

  // 设置网页响应内容
  server.on("/", []() {
    server.send(200, "text/html", "<h1>Hello from ESP8266!</h1>");
  });

  // 启动服务器
  server.begin();
  Serial.println("网页服务器已启动");
}

void loop() {
  server.handleClient(); // 必须持续调用，用于处理请求
}
