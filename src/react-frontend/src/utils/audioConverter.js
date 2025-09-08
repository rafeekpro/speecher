/**
 * Audio conversion utilities for converting WebM to WAV format
 */

/**
 * Convert WebM blob to WAV blob
 * @param {Blob} webmBlob - The WebM audio blob
 * @returns {Promise<Blob>} WAV audio blob
 */
export const convertWebMToWav = async (webmBlob) => {
  console.log('Starting WebM to WAV conversion, blob type:', webmBlob.type, 'size:', webmBlob.size);
  
  return new Promise((resolve, reject) => {
    const audioContext = new (window.AudioContext || window.webkitAudioContext)();
    const fileReader = new FileReader();

    fileReader.onloadend = async () => {
      try {
        const arrayBuffer = fileReader.result;
        const audioBuffer = await audioContext.decodeAudioData(arrayBuffer);
        
        // Convert AudioBuffer to WAV
        const wavArrayBuffer = audioBufferToWav(audioBuffer);
        const wavBlob = new Blob([wavArrayBuffer], { type: 'audio/wav' });
        
        audioContext.close();
        console.log('Conversion complete! WAV blob type:', wavBlob.type, 'size:', wavBlob.size);
        resolve(wavBlob);
      } catch (error) {
        console.error('Error converting WebM to WAV:', error);
        audioContext.close();
        reject(error);
      }
    };

    fileReader.onerror = () => {
      reject(new Error('Failed to read audio file'));
    };

    fileReader.readAsArrayBuffer(webmBlob);
  });
};

/**
 * Convert AudioBuffer to WAV ArrayBuffer
 * @param {AudioBuffer} audioBuffer - The audio buffer to convert
 * @returns {ArrayBuffer} WAV format array buffer
 */
function audioBufferToWav(audioBuffer) {
  const numOfChan = audioBuffer.numberOfChannels;
  const sampleRate = audioBuffer.sampleRate;
  const length = audioBuffer.length * numOfChan * 2 + 44;
  const buffer = new ArrayBuffer(length);
  const view = new DataView(buffer);
  const channels = [];
  let offset = 0;
  let pos = 0;

  // Helper functions to write data
  const setUint16 = (data) => {
    view.setUint16(pos, data, true);
    pos += 2;
  };

  const setUint32 = (data) => {
    view.setUint32(pos, data, true);
    pos += 4;
  };

  // Write WAV header
  // "RIFF" identifier
  setUint32(0x46464952);
  // File length minus RIFF identifier length and file description length
  setUint32(length - 8);
  // "WAVE" identifier
  setUint32(0x45564157);
  // "fmt " chunk identifier
  setUint32(0x20746d66);
  // Format chunk length
  setUint32(16);
  // Sample format (PCM)
  setUint16(1);
  // Channel count
  setUint16(numOfChan);
  // Sample rate
  setUint32(sampleRate);
  // Byte rate (sample rate * block align)
  setUint32(sampleRate * numOfChan * 2);
  // Block align (channel count * bytes per sample)
  setUint16(numOfChan * 2);
  // Bits per sample
  setUint16(16);
  // "data" chunk identifier
  setUint32(0x61746164);
  // Data chunk length
  setUint32(length - pos - 4);

  // Extract channel data
  for (let i = 0; i < audioBuffer.numberOfChannels; i++) {
    channels.push(audioBuffer.getChannelData(i));
  }

  // Write interleaved PCM samples
  while (pos < length) {
    for (let i = 0; i < numOfChan; i++) {
      // Interleave channels
      let sample = channels[i][offset];
      
      // Clamp sample to [-1, 1] range
      sample = Math.max(-1, Math.min(1, sample));
      
      // Convert to 16-bit PCM
      sample = sample < 0 ? sample * 0x8000 : sample * 0x7FFF;
      
      // Write 16-bit sample
      view.setInt16(pos, sample, true);
      pos += 2;
    }
    offset++;
  }

  return buffer;
}

/**
 * Alternative simple conversion using MediaRecorder with WAV mime type
 * @param {MediaStream} stream - The media stream to record
 * @returns {Promise<Blob>} WAV audio blob
 */
export const recordAsWav = (stream) => {
  return new Promise((resolve, reject) => {
    const chunks = [];
    
    // Try to use WAV mime type if supported
    const mimeTypes = [
      'audio/wav',
      'audio/wave',
      'audio/webm',
      'audio/ogg'
    ];
    
    let selectedMimeType = 'audio/webm'; // Default fallback
    for (const mimeType of mimeTypes) {
      if (MediaRecorder.isTypeSupported(mimeType)) {
        selectedMimeType = mimeType;
        break;
      }
    }
    
    const mediaRecorder = new MediaRecorder(stream, {
      mimeType: selectedMimeType
    });
    
    mediaRecorder.ondataavailable = (event) => {
      if (event.data.size > 0) {
        chunks.push(event.data);
      }
    };
    
    mediaRecorder.onstop = async () => {
      const blob = new Blob(chunks, { type: selectedMimeType });
      
      // If already WAV, return as is
      if (selectedMimeType.includes('wav')) {
        resolve(blob);
      } else {
        // Convert to WAV
        try {
          const wavBlob = await convertWebMToWav(blob);
          resolve(wavBlob);
        } catch (error) {
          // Fallback: return original blob
          console.warn('WAV conversion failed, using original format:', error);
          resolve(blob);
        }
      }
    };
    
    mediaRecorder.onerror = (error) => {
      reject(error);
    };
    
    return mediaRecorder;
  });
};

/**
 * Get supported audio MIME type for recording
 * @returns {string} The best supported MIME type
 */
export const getSupportedMimeType = () => {
  const types = [
    'audio/wav',
    'audio/webm;codecs=opus',
    'audio/webm',
    'audio/ogg;codecs=opus',
    'audio/mp4'
  ];
  
  for (const type of types) {
    if (MediaRecorder.isTypeSupported(type)) {
      return type;
    }
  }
  
  return 'audio/webm'; // Default fallback
};

const audioConverter = {
  convertWebMToWav,
  recordAsWav,
  getSupportedMimeType
};

export default audioConverter;