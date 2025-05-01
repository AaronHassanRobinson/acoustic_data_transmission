#include <arduinoFFT.h>

// =============================== //
// Example: Acoustic receive data via an Analog microphone
// Made by: Aaron Hassan Robinson
// Using: FFT code written by Kosme @: https://github.com/kosme/arduinoFFT
// =============================== //


// FFT stuff
const uint16_t samples = 256;             // Must be power of 2
const double samplingFrequency = 5000.0; // Sampling frequency in Hz, follow nyquist theory which is something like double max F

double vReal[samples];
double vImag[samples];
ArduinoFFT<double> FFT = ArduinoFFT<double>(vReal, vImag, samples, samplingFrequency);
const int micPin = A0;

// protocol: Defining FSK Frequencies to use. Note: Using big upper & lower bounds as analog can be innaccurate 
// Start bit: 200hz
double startBit_upperBound = 210.0;
double startBit_lowerBound = 190.0;

// end bit: 1000Hz 
double endBit_upperBound = 1010.0;
double endBit_lowerBound = 990.0;

// 0 bit: 500Hz
double zeroBit_upperBound = 510.0;
double zeroBit_lowerBound = 490.0;

// 1 bit: 700Hz
double oneBit_upperBound = 710.0;
double oneBit_lowerBound = 690.0;


void setup() {
  Serial.begin(115200);
  while (!Serial);
  Serial.println("Ready to analyze frequency!");
}

void loop() {
  // Sample the signal
  unsigned long startMicros = micros();
  for (uint16_t i = 0; i < samples; i++) {
    while (micros() - startMicros < (i * 1000000.0 / samplingFrequency)); // precise wait
    vReal[i] = analogRead(micPin) - 552;
    vImag[i] = 0;
  }

  // FFT Processing ~ From  Kosme
  FFT.windowing(FFTWindow::Hamming, FFTDirection::Forward);
  FFT.compute(FFTDirection::Forward);
  FFT.complexToMagnitude();

  // Peak detection ~ From  Kosme
  double peak = FFT.majorPeak();
  Serial.print("Peak Frequency: ");
  Serial.print(peak, 2);
  Serial.println(" Hz");

  if (peak > startBit_lowerBound && peak < startBit_upperBound) 
  {
    Serial.println("start bit detected");
    // next we want to listen for 1 or 0:
    // Ready to receive 8 bits
    int bits[8];
    for (int i = 0; i < 8; i++)
    {
      delay(900); // wait for next bit (can tune this) ~ not the best way to do this, should set some sort of sliding window 

      // Resample
      unsigned long startMicrosBit = micros();
      for (uint16_t j = 0; j < samples; j++)
      {
        while (micros() - startMicrosBit < (j * 1000000.0 / samplingFrequency));
        vReal[j] = analogRead(micPin) - 552;
        vImag[j] = 0;
      }

      FFT.windowing(FFTWindow::Hamming, FFTDirection::Forward);
      FFT.compute(FFTDirection::Forward);
      FFT.complexToMagnitude();
      double bitPeak = FFT.majorPeak();

      // Interpret bit
      if (bitPeak > 450 && bitPeak < 550)
      {
        bits[i] = 0;
        Serial.println("Bit 0");
      } 
      else if (bitPeak > 650 && bitPeak < 750)
      {
        bits[i] = 1;
        Serial.println("Bit 1");
      } 
      else 
      {
       Serial.println("Invalid bit frequency");
      }
  }

  // Wait for stop bit
  delay(20);
  unsigned long stopMicros = micros();
  for (uint16_t j = 0; j < samples; j++) {
    while (micros() - stopMicros < (j * 1000000.0 / samplingFrequency));
    vReal[j] = analogRead(micPin) - 552;
    vImag[j] = 0;
  }
  FFT.windowing(FFTWindow::Hamming, FFTDirection::Forward);
  FFT.compute(FFTDirection::Forward);
  FFT.complexToMagnitude();
  double stopPeak = FFT.majorPeak();
  if (stopPeak > 950 && stopPeak < 1050) {
    Serial.println("Stop bit detected");

    // Reconstruct the byte,
    byte value = 0;
    for (int i = 0; i < 8; i++) {
      value = (value << 1) | bits[i];
    }

    Serial.print("Received byte: ");
    Serial.println(value);
    Serial.print("As char: ");
    Serial.println((char)value);
  }
  else 
  {
    Serial.println("Stop bit not detected");
  }

  }

  //delay(100);
}