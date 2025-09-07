import React, { useEffect, useRef, useState } from 'react';
import { Box, Paper, Typography } from '@mui/material';

const AudioVisualizer = ({ stream, isRecording }) => {
  const canvasRef = useRef(null);
  const audioContextRef = useRef(null);
  const analyserRef = useRef(null);
  const animationRef = useRef(null);
  const [audioLevel, setAudioLevel] = useState(0);

  useEffect(() => {
    if (stream && isRecording) {
      setupAudioAnalysis();
    } else {
      cleanup();
    }

    return cleanup;
  }, [stream, isRecording]);

  const setupAudioAnalysis = () => {
    try {
      // Create audio context
      const AudioContext = window.AudioContext || window.webkitAudioContext;
      audioContextRef.current = new AudioContext();
      
      // Create analyser node
      analyserRef.current = audioContextRef.current.createAnalyser();
      analyserRef.current.fftSize = 256;
      analyserRef.current.smoothingTimeConstant = 0.8;
      
      // Connect stream to analyser
      const source = audioContextRef.current.createMediaStreamSource(stream);
      source.connect(analyserRef.current);
      
      // Start visualization
      visualize();
    } catch (error) {
      console.error('Error setting up audio analysis:', error);
    }
  };

  const cleanup = () => {
    if (animationRef.current) {
      cancelAnimationFrame(animationRef.current);
    }
    if (audioContextRef.current) {
      audioContextRef.current.close();
    }
  };

  const visualize = () => {
    if (!analyserRef.current || !canvasRef.current) return;

    const canvas = canvasRef.current;
    const canvasCtx = canvas.getContext('2d');
    const bufferLength = analyserRef.current.frequencyBinCount;
    const dataArray = new Uint8Array(bufferLength);

    const draw = () => {
      animationRef.current = requestAnimationFrame(draw);
      
      analyserRef.current.getByteFrequencyData(dataArray);
      
      // Calculate average audio level
      const average = dataArray.reduce((a, b) => a + b, 0) / bufferLength;
      setAudioLevel(Math.min(100, (average / 255) * 150)); // Scale to 0-100
      
      // Clear canvas
      canvasCtx.fillStyle = 'rgb(245, 245, 245)';
      canvasCtx.fillRect(0, 0, canvas.width, canvas.height);
      
      // Draw frequency bars
      const barWidth = (canvas.width / bufferLength) * 2.5;
      let barHeight;
      let x = 0;
      
      for (let i = 0; i < bufferLength; i++) {
        barHeight = (dataArray[i] / 255) * canvas.height * 0.8;
        
        // Create gradient effect
        const gradient = canvasCtx.createLinearGradient(0, canvas.height - barHeight, 0, canvas.height);
        gradient.addColorStop(0, '#667eea');
        gradient.addColorStop(0.5, '#764ba2');
        gradient.addColorStop(1, '#667eea');
        
        canvasCtx.fillStyle = gradient;
        canvasCtx.fillRect(x, canvas.height - barHeight, barWidth, barHeight);
        
        x += barWidth + 1;
      }
    };

    draw();
  };

  const getAudioLevelColor = () => {
    if (audioLevel < 20) return '#4caf50';
    if (audioLevel < 50) return '#2196f3';
    if (audioLevel < 80) return '#ff9800';
    return '#f44336';
  };

  const getAudioLevelText = () => {
    if (audioLevel < 10) return 'Silent';
    if (audioLevel < 30) return 'Quiet';
    if (audioLevel < 60) return 'Good';
    if (audioLevel < 85) return 'Loud';
    return 'Too Loud';
  };

  return (
    <Box sx={{ width: '100%', mt: 2 }}>
      {/* Waveform Canvas */}
      <Paper 
        elevation={0} 
        sx={{ 
          p: 2, 
          backgroundColor: '#f5f5f5',
          borderRadius: 2,
          position: 'relative',
          overflow: 'hidden'
        }}
      >
        <canvas
          ref={canvasRef}
          width={800}
          height={150}
          style={{
            width: '100%',
            height: '150px',
            borderRadius: '8px'
          }}
        />
        
        {/* Audio Level Indicator */}
        <Box
          sx={{
            position: 'absolute',
            top: 10,
            right: 10,
            backgroundColor: 'rgba(255, 255, 255, 0.95)',
            borderRadius: 2,
            p: 1.5,
            minWidth: 120,
            boxShadow: 1
          }}
        >
          <Typography variant="caption" color="text.secondary">
            Audio Level
          </Typography>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mt: 0.5 }}>
            <Box
              sx={{
                width: 12,
                height: 12,
                borderRadius: '50%',
                backgroundColor: getAudioLevelColor(),
                animation: isRecording ? 'pulse 1s infinite' : 'none',
                '@keyframes pulse': {
                  '0%': { opacity: 1 },
                  '50%': { opacity: 0.5 },
                  '100%': { opacity: 1 }
                }
              }}
            />
            <Typography variant="body2" fontWeight="bold" color={getAudioLevelColor()}>
              {getAudioLevelText()}
            </Typography>
          </Box>
          <Box
            sx={{
              mt: 1,
              height: 4,
              backgroundColor: '#e0e0e0',
              borderRadius: 2,
              overflow: 'hidden'
            }}
          >
            <Box
              sx={{
                height: '100%',
                width: `${audioLevel}%`,
                backgroundColor: getAudioLevelColor(),
                transition: 'width 0.1s ease, background-color 0.3s ease',
                borderRadius: 2
              }}
            />
          </Box>
        </Box>
      </Paper>

      {/* Volume Meter Bars */}
      <Box sx={{ mt: 2, display: 'flex', gap: 0.5, height: 40, alignItems: 'flex-end' }}>
        {Array.from({ length: 20 }).map((_, i) => {
          const threshold = (i + 1) * 5;
          const isActive = audioLevel >= threshold;
          let barColor = '#e0e0e0';
          
          if (isActive) {
            if (threshold <= 40) barColor = '#4caf50';
            else if (threshold <= 70) barColor = '#ff9800';
            else barColor = '#f44336';
          }
          
          return (
            <Box
              key={i}
              sx={{
                flex: 1,
                height: `${20 + (i * 1.5)}px`,
                backgroundColor: barColor,
                borderRadius: 0.5,
                transition: 'background-color 0.1s ease',
                opacity: isActive ? 1 : 0.3
              }}
            />
          );
        })}
      </Box>

      {/* Instructions */}
      {isRecording && (
        <Box sx={{ mt: 2, textAlign: 'center' }}>
          <Typography variant="body2" color="text.secondary">
            {audioLevel < 10 
              ? "📢 Please speak louder or move closer to the microphone"
              : audioLevel > 85 
              ? "🔇 You're too loud! Please speak softer or move away from the microphone"
              : "✅ Perfect audio level - keep speaking clearly"}
          </Typography>
        </Box>
      )}
    </Box>
  );
};

export default AudioVisualizer;