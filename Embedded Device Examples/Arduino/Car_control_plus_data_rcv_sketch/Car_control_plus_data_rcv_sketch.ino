#include <arduinoFFT.h>

// =============================== //
// Example: Acoustic receive data & control a vehicle remotely using FSK acoustically 
// Made by: Aaron Hassan Robinson: https://github.com/AaronHassanRobinson/acoustic_data_transmission
// Using: FFT code written by Kosme @: https://github.com/kosme/arduinoFFT
// =============================== //
// microphone used: KY-037 analog microphone
// results: https://youtube.com/shorts/RTgkPt1IsJs?feature=share 

const uint16_t samples = 512;            
const double samplingFrequency = 10000.0; 
double vReal[samples];
double vImag[samples];
ArduinoFFT<double> FFT = ArduinoFFT<double>(vReal, vImag, samples, samplingFrequency);
const int micPin = 33;

// protocol:
// ----------- For sending data! --------------- // FSK binary implementation 
// 50hz guards inbetween each freq
// Start bit: 
double data_startBit_upperBound = 210.0;
double data_startBit_lowerBound = 190.0;

// end bit: 
double data_endBit_upperBound = 280.0;
double data_endBit_lowerBound = 260.0;

// 0 bit: 
double data_zeroBit_upperBound = 350.0;
double data_zeroBit_lowerBound = 330.0;

// 1 bit: 
double oneBit_upperBound = 420.0;
double oneBit_lowerBound = 400.0;


// ----------- For sending Remote control instructions! --------------- //  FSK M-ary implementation 

// Start bit: 200hz
double mvCtrl_forward_upperBound = 490.0;
double mvCtrl_forward_lowerBound = 470.0;

// Turn left bit: 
double mvCtrl_left_upperBound = 560.0;
double mvCtrl_left_lowerBound = 540.0;

// Turn Right bit: 
double mvCtrl_right_upperBound = 610.0;
double mvCtrl_right_lowerBound = 630.0;

// 1 bit: 
double mvCtrl_backwards_upperBound = 680.0;
double mvCtrl_backwards_lowerBound = 700.0;

// function used to calibrate Analog Microphone for FFT calculations
// acoustic mics generally sit at some offset value from zero, to do FFT we need to zero out this val
int dcOffset = 0;
int calculateDCOffset(int pin, int sampleCount = (samplingFrequency)) 
{
  long sum = 0;
  for (int i = 0; i < sampleCount; i++) {
    sum += analogRead(pin);
    delayMicroseconds(10); 
  }
  return sum / sampleCount;
}

void setup() {
  analogReadResolution(12);
  Serial.begin(115200);
  while (!Serial);
  dcOffset = calculateDCOffset(micPin);
  Serial.print("Calibrated DC Offset: ");
  Serial.println(dcOffset);
  Serial.println("Ready to analyze frequency!");
  delay(5000);
}
double get_fft_major_peak()
{
    unsigned long startMicros = micros();
  for (uint16_t i = 0; i < samples; i++) {
    while (micros() - startMicros < (i * 1000000.0 / samplingFrequency)); // precise wait
    vReal[i] = analogRead(micPin) - dcOffset;
    vImag[i] = 0;
  }

  // FFT Processing
  FFT.windowing(FFTWindow::Hamming, FFTDirection::Forward);
  FFT.compute(FFTDirection::Forward);
  FFT.complexToMagnitude();

  // Peak detection
  double peak = FFT.majorPeak();
  return peak;
}


// process binary data 
void process_binary_signal()
{
    // next we want to listen for 1 or 0:
    // Ready to receive 8 bits
  int bits[8];
  for (int i = 0; i < 8; i++) 
  {
    delay(900); // wait for next bit (can tune this) ~ note: this is a primitive way to "synchronise timing"
                // and is not very reliable. Ideally you would begin transmissions with some sort of synchronisation process

    // Resample
    unsigned long startMicrosBit = micros();
    long sum = 0;
    for (uint16_t i = 0; i < samples; i++) {
      int val = analogRead(micPin);
      sum += val;
      vReal[i] = val - dcOffset;
      vImag[i] = 0;
    }
    Serial.print("Avg raw: ");
    Serial.println(sum / samples);
      
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
  for (uint16_t j = 0; j < samples; j++)
  {
    while (micros() - stopMicros < (j * 1000000.0 / samplingFrequency));
    vReal[j] = analogRead(micPin) - 552;
    vImag[j] = 0;
  }
  FFT.windowing(FFTWindow::Hamming, FFTDirection::Forward);
  FFT.compute(FFTDirection::Forward);
  FFT.complexToMagnitude();
  double stopPeak = FFT.majorPeak();
  if (stopPeak > 950 && stopPeak < 1050)
  {
    Serial.println("Stop bit detected");
    // Reconstruct the byte
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
  return;
}

void process_movement_control_signal(double cmdPeak)
{


  // Decode based on frequency ranges
  if (cmdPeak > mvCtrl_left_lowerBound && cmdPeak < mvCtrl_left_upperBound) {
    Serial.println("→ Command: TURN LEFT");
    // turnLeft();
  }
  else if (cmdPeak > mvCtrl_right_lowerBound && cmdPeak < mvCtrl_right_upperBound) {
    Serial.println("→ Command: TURN RIGHT");
    // turnRight();
  }
  else if (cmdPeak > mvCtrl_forward_lowerBound && cmdPeak < mvCtrl_forward_upperBound) {
    Serial.println("→ Command: MOVE FORWARD");
    // moveForward();
  }
  else {
    Serial.println("Unknown movement command");
  }
  return;
}


void loop() {
  // Peak detection
  double peak = get_fft_major_peak();
  Serial.print("Peak Frequency: ");
  Serial.print(peak, 2);
  Serial.println(" Hz");

  // Binary data 
  if (peak > data_startBit_lowerBound && peak < data_startBit_upperBound) 
  {
      Serial.println("start bit detected");
      process_binary_signal();
  }
  else if (peak > mvCtrl_forward_lowerBound && peak < mvCtrl_backwards_upperBound) 
  {
    Serial.println("Movement control start bit detected");
    process_movement_control_signal(peak);
    delay(2000);
  }
}