import React from 'react';

export interface AudioRecorderSettings {
  provider: string;
  language: string;
  enableDiarization: boolean;
  maxSpeakers: number;
  includeTimestamps: boolean;
  showCost: boolean;
}

export interface AudioRecorderProps {
  onAudioRecorded: (audioBlob: Blob, fileName?: string) => void | Promise<void>;
  isLoading: boolean;
  settings: AudioRecorderSettings;
}

declare const AudioRecorder: React.FC<AudioRecorderProps>;

export default AudioRecorder;