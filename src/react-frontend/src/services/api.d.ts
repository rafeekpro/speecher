export interface TranscriptionResponse {
  id?: string;
  text: string;
  provider: string;
  cost?: number;
  processingTime?: number;
  timestamp?: string;
  language?: string;
  diarization?: any;
  segments?: Array<{
    text: string;
    start?: number;
    end?: number;
    speaker?: string;
  }>;
}

export interface HealthResponse {
  status: 'healthy' | 'unhealthy';
  error?: string;
}

export interface StatisticsResponse {
  totalTranscriptions: number;
  totalCost: number;
  averageProcessingTime: number;
  providerBreakdown: {
    [provider: string]: {
      count: number;
      totalCost: number;
      averageProcessingTime: number;
    };
  };
  recentActivity: Array<{
    date: string;
    count: number;
    cost: number;
  }>;
}

export interface ProviderInfo {
  provider: string;
  configured: boolean;
  enabled: boolean;
  source: 'env' | 'mongodb';
}

export function transcribeAudio(formData: FormData): Promise<TranscriptionResponse>;
export function getTranscriptionHistory(limit?: number): Promise<TranscriptionResponse[]>;
export function getTranscriptionById(id: string): Promise<TranscriptionResponse>;
export function deleteTranscription(id: string): Promise<{ success: boolean }>;
export function getStatistics(): Promise<StatisticsResponse>;
export function checkHealth(): Promise<HealthResponse>;
export function getProviders(): Promise<ProviderInfo[]>;