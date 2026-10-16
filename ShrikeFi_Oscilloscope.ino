// Shrike-Fi (ESP32-S3) educational USB oscilloscope, version 1.
//
// Signal: exposed ESP_GPIO1 header. Reference: GND header.
// CAUTION: NO 5V, negative voltages, or unknown/external high voltages on GPIO1.
// Start with 0 to 2.5 V signals for useful ADC accuracy.

#include <Arduino.h>

constexpr uint8_t  ADC_PIN             = 1;      // Shrike-Fi header: ESP_GPIO1
constexpr uint32_t BAUD_RATE           = 115200;
constexpr uint32_t SAMPLE_INTERVAL_US  = 2000;   // 500 samples/second
constexpr uint8_t  TEST_PIN            = 4;      // Shrike-Fi header: ESP_GPIO4
constexpr bool     ENABLE_TEST_WAVE    = true;   // 10 Hz square wave on GPIO4
constexpr uint32_t TEST_HALF_PERIOD_US = 50000;

uint32_t lastSampleUs = 0;
uint32_t lastToggleUs = 0;
bool     testHigh     = false;

void setup() {
  Serial.begin(BAUD_RATE);
  pinMode(ADC_PIN, INPUT);

  if (ENABLE_TEST_WAVE) {
    pinMode(TEST_PIN, OUTPUT);
    digitalWrite(TEST_PIN, LOW);
  }

  analogReadResolution(12);                       // 12-bit ADC
  analogSetPinAttenuation(ADC_PIN, ADC_11db);     // ESP32-S3 nominal ~0.15-3.1 V calibrated range

  delay(500);
  lastSampleUs = micros();
  lastToggleUs = lastSampleUs;
}

void loop() {
  const uint32_t now = micros();

  // Toggle test square wave every half-period.
  if (ENABLE_TEST_WAVE &&
      (uint32_t)(now - lastToggleUs) >= TEST_HALF_PERIOD_US) {
    lastToggleUs = now;
    testHigh     = !testHigh;
    digitalWrite(TEST_PIN, testHigh ? HIGH : LOW);
  }

  // Sample ADC at the target interval.
  if ((uint32_t)(now - lastSampleUs) >= SAMPLE_INTERVAL_US) {
    lastSampleUs = now;

    // Espressif Arduino core returns a calibrated millivolt estimate.
    const uint32_t mV = analogReadMilliVolts(ADC_PIN);

    // CSV output: time_in_microseconds,voltage_in_millivolts
    Serial.print(now);
    Serial.print(',');
    Serial.println(mV);
  }
}
