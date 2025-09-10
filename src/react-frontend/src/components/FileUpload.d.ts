import React from 'react';

export interface FileUploadSettings {
  provider: string;
  language: string;
  enableDiarization: boolean;
  maxSpeakers: number;
  includeTimestamps: boolean;
  showCost: boolean;
}

export interface FileUploadProps {
  onFilesUploaded: (audioBlob: Blob, fileName?: string) => void | Promise<void>;
  isLoading: boolean;
  settings: FileUploadSettings;
}

declare const FileUpload: React.FC<FileUploadProps>;

export default FileUpload;