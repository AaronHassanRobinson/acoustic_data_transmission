#include <driver/i2s.h>
#include <arduinoFFT.h>

// === I2S Microphone Configuration ===
#define I2S_WS  18 // LRCL (Word Select)
#define I2S_SD  17 // DOUT (Serial Data)
#define I2S_SCK 16 // BCLK (Serial Clock)
#define I2S_PORT I2S_NUM_0

// FFT Configuration
const uint16_t FFT_SAMPLES = 512;
const double SAMPLING_FREQ = 16000.0;
const uint32_t I2S_SAMPLE_RATE = 16000;
const uint8_t BIT_SHIFT = 14;
const uint16_t FREQ_RANGE_MIN = 50;
const uint16_t FREQ_RANGE_MAX = 4000;

double vReal[FFT_SAMPLES];
double vImag[FFT_SAMPLES];
ArduinoFFT<double> FFT = ArduinoFFT<double>(vReal, vImag, FFT_SAMPLES, SAMPLING_FREQ);

// DC Offset
double dcOffset = 0;
bool firstCalibrationDone = false;

void calculateDCOffset() {
  const uint16_t samplesToAverage = 1024;
  int32_t buffer[samplesToAverage];
  size_t bytesRead;

  double sum = 0;
  uint16_t samplesRead = 0;

  while (samplesRead < samplesToAverage) {
    size_t samplesAvailable = samplesToAverage - samplesRead;
    i2s_read(I2S_PORT, buffer + samplesRead, samplesAvailable * sizeof(int32_t), &bytesRead, portMAX_DELAY);
    samplesRead += bytesRead / sizeof(int32_t);
  }

  for (uint16_t i = 0; i < samplesToAverage; i++) {
    sum += (buffer[i] >> BIT_SHIFT);
  }

  dcOffset = sum / samplesToAverage;
  Serial.print("DC Offset calibrated: ");
  Serial.println(dcOffset, 3);
}

double calculateDominantFrequency() {
  int32_t rawSamples[FFT_SAMPLES];
  size_t bytesRead;

  i2s_read(I2S_PORT, rawSamples, sizeof(rawSamples), &bytesRead, portMAX_DELAY);

  double minSample = 32767;
  double maxSample = -32768;
  
  for (int i = 0; i < FFT_SAMPLES; i++) {
    int32_t sample = (rawSamples[i] >> BIT_SHIFT) - dcOffset;
    vReal[i] = sample;
    vImag[i] = 0;

    if (sample < minSample) minSample = sample;
    if (sample > maxSample) maxSample = sample;
  }

  // Recenter dynamic DC drift if needed (slow adjustment)
  if (firstCalibrationDone) {
    double dynamicDC = (maxSample + minSample) / 2.0;
    dcOffset = 0.98 * dcOffset + 0.02 * (dcOffset + dynamicDC); // Smooth update
  } else {
    firstCalibrationDone = true;
  }

  // Optional light "gain" to boost weak signals
  double signalSpan = maxSample - minSample;
  double gain = 1.0;
  if (signalSpan < 1000) gain = 4.0;
  else if (signalSpan < 2000) gain = 2.0;

  for (int i = 0; i < FFT_SAMPLES; i++) {
    vReal[i] *= gain;
  }

  // Apply window (Hamming window — keeps more energy at edges)
  FFT.windowing(FFTWindow::Hamming, FFTDirection::Forward);

  // Compute FFT
  FFT.compute(FFTDirection::Forward);
  FFT.complexToMagnitude();

  uint16_t startBin = FREQ_RANGE_MIN * FFT_SAMPLES / SAMPLING_FREQ;
  uint16_t endBin = FREQ_RANGE_MAX * FFT_SAMPLES / SAMPLING_FREQ;
  endBin = min(endBin, static_cast<uint16_t>(FFT_SAMPLES/2));

  double maxMagnitude = 0;
  uint16_t peakBin = startBin;

  for (uint16_t i = startBin; i <= endBin; i++) {
    if (vReal[i] > maxMagnitude) {
      maxMagnitude = vReal[i];
      peakBin = i;
    }
  }

  // Lower threshold for detection
  if (maxMagnitude < 3) {  // LOWERED from 10 → 3
    return 0;
  }

  // Quadratic interpolation
  double left = vReal[peakBin - 1];
  double center = vReal[peakBin];
  double right = vReal[peakBin + 1];

  double delta = 0.0;
  double divisor = center * 2 - left - right;

  if (divisor != 0) {
    delta = 0.5 * (right - left) / divisor;
  }

  double interpolatedBin = peakBin + delta;
  double frequency = interpolatedBin * SAMPLING_FREQ / FFT_SAMPLES;

  if (frequency < 0 || frequency > (SAMPLING_FREQ / 2)) {
    frequency = 0;
  }

  return frequency;
}

void setup() {
  Serial.begin(115200);
  while (!Serial);

  // I2S Setup
  i2s_config_t i2sConfig = {
    .mode = (i2s_mode_t)(I2S_MODE_MASTER | I2S_MODE_RX),
    .sample_rate = I2S_SAMPLE_RATE,
    .bits_per_sample = I2S_BITS_PER_SAMPLE_32BIT,
    .channel_format = I2S_CHANNEL_FMT_ONLY_LEFT,
    .communication_format = I2S_COMM_FORMAT_I2S,
    .intr_alloc_flags = ESP_INTR_FLAG_LEVEL1,
    .dma_buf_count = 8,
    .dma_buf_len = 256,
    .use_apll = true,
    .tx_desc_auto_clear = false,
    .fixed_mclk = 0
  };

  i2s_pin_config_t pinConfig = {
    .bck_io_num = I2S_SCK,
    .ws_io_num = I2S_WS,
    .data_out_num = I2S_PIN_NO_CHANGE,
    .data_in_num = I2S_SD
  };

  i2s_driver_install(I2S_PORT, &i2sConfig, 0, NULL);
  i2s_set_pin(I2S_PORT, &pinConfig);

  calculateDCOffset();
  Serial.println("System ready - Play audio from your phone!");
}

void loop() {
  double frequency = calculateDominantFrequency();

  if (frequency == 0) {
    Serial.println("No strong audio detected");
  } else {
    Serial.print("Dominant Frequency: ");
    Serial.print(frequency, 1);
    Serial.println(" Hz");
  }

  delay(50);
}