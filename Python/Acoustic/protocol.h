#ifndef PROTOCOL_H
#define PROTOCOL_H

#include <stdint.h>

#pragma pack(push, 1)  // Ensure byte alignment for all structs

// ==============================
// Message Type Enumeration
// ==============================
typedef enum {
    MSG_UNKNOWN = 0,
    MSG_STRING,
    MSG_INT,
    MSG_FLOAT,
    MSG_AUDIO,
    MSG_VIDEO,
    MSG_CONTROL,
    MSG_ACKNOWLEDGE,
    MSG_ERROR,
    // Add new types above this line
    MSG_TYPE_COUNT  // Total number of message types
} MESSAGE_TYPE;

// ==============================
// Base Message Header
// ==============================
typedef struct {
    uint8_t messageType;    // MESSAGE_TYPE enum value
    uint32_t messageSize;   // Size of entire message (header + payload)
    uint16_t protocolVersion;  // Protocol versioning
    uint32_t sequenceNumber;   // For ordering/deduplication
    uint32_t timestamp;        // Timestamp in milliseconds
    uint16_t checksum;         // Simple checksum for integrity
} MESSAGE_HEADER;

// ==============================
// Specialized Message Headers
// ==============================
typedef struct {
    MESSAGE_HEADER header;  // Base header
    uint32_t stringLength;  // Length of string data (excluding null terminator)
    uint8_t  encodingType;  // 0=ASCII, 1=UTF8, 2=UTF16
} STRING_HEADER;

typedef struct {
    MESSAGE_HEADER header;
    uint8_t  intSize;       // 1=byte, 2=short, 4=int32, 8=int64
    uint8_t  isSigned;      // 0=unsigned, 1=signed
} INT_HEADER;

typedef struct {
    MESSAGE_HEADER header;
    uint8_t  floatSize;     // 4=float, 8=double
    uint8_t  precision;     // Decimal precision hint
} FLOAT_HEADER;

typedef struct {
    MESSAGE_HEADER header;
    uint32_t sampleRate;    // Hz
    uint16_t bitDepth;      // Bits per sample
    uint8_t  channels;      // Number of audio channels
    uint8_t  format;        // 0=PCM, 1=FLAC, 2=OPUS
} AUDIO_HEADER;

typedef struct {
    MESSAGE_HEADER header;
    uint16_t width;         // Frame width
    uint16_t height;        // Frame height
    uint8_t  colorDepth;    // Bits per pixel
    uint8_t  frameType;     // 0=I-frame, 1=P-frame, 2=B-frame
    uint16_t fps;           // Frames per second
} VIDEO_HEADER;

typedef struct {
    MESSAGE_HEADER header;
    uint32_t errorCode;
    uint16_t messageLength;  // Length of error message
} ERROR_HEADER;

#pragma pack(pop)  // Restore default packing

#endif // PROTOCOL_H