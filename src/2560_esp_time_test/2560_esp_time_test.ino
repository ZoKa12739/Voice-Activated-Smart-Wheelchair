unsigned long lastReceiveTime = 0; // 上次收到数据的时间
unsigned long timeoutInterval = 3000; // 超时时间，单位毫秒

void setup() {
  Serial.begin(9600);    // 用于电脑串口监视器输出
  Serial1.begin(115200); // 接收来自NodeMCU的数据
  Serial.println("等待ESP8266发送时间...");
}

void loop() {
  // 如果收到串口数据
  if (Serial1.available()) {
    String receivedTime = Serial1.readStringUntil('\n');
    Serial.print("收到时间: ");
    Serial.println(receivedTime);

    lastReceiveTime = millis(); // 记录最近一次收到的时间
  }

  // 检查是否超时
  if (millis() - lastReceiveTime > timeoutInterval) {
    Serial.println("⚠ 未收到ESP8266发送的数据！");
    lastReceiveTime = millis(); // 重置计时，避免一直重复提示
  }
}
