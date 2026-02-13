// API client for backend communication

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'https://stacksliceai.onrender.com';

export interface UploadResponse {
  video_id: string;
  job_id: string;
  credits_used: number;
  credits_remaining: number;
  message: string;
}

export interface JobStatusResponse {
  job_id: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  progress_percent: number;
  message: string;
  results?: {
    transcript: string;
    viral_hooks: string[];
    captions: Array<{
      caption: string;
      hashtags: string[];
      character_count: number;
    }>;
    clips: Array<{
      start_time: number;
      end_time: number;
      description: string;
    }>;
    download_url?: string;
  };
}

export interface ApiError {
  detail: string;
}

class ApiClient {
  private baseUrl: string;

  constructor() {
    this.baseUrl = API_URL;
  }

  // Get auth token from localStorage
  private getToken(): string | null {
    if (typeof window !== 'undefined') {
      return localStorage.getItem('token');
    }
    return null;
  }

  // Upload video
  async uploadVideo(file: File, onProgress?: (progress: number) => void): Promise<UploadResponse> {
    const formData = new FormData();
    formData.append('file', file);

    const token = this.getToken();
    if (!token) {
      throw new Error('Not authenticated. Please log in.');
    }

    return new Promise((resolve, reject) => {
      const xhr = new XMLHttpRequest();

      // Track upload progress
      xhr.upload.addEventListener('progress', (e) => {
        if (e.lengthComputable && onProgress) {
          const progress = Math.round((e.loaded / e.total) * 100);
          onProgress(progress);
        }
      });

      // Handle completion
      xhr.addEventListener('load', () => {
        if (xhr.status >= 200 && xhr.status < 300) {
          try {
            const response = JSON.parse(xhr.responseText);
            resolve(response);
          } catch (error) {
            reject(new Error('Invalid response from server'));
          }
        } else {
          try {
            const error = JSON.parse(xhr.responseText);
            reject(new Error(error.detail || 'Upload failed'));
          } catch {
            reject(new Error(`Upload failed with status ${xhr.status}`));
          }
        }
      });

      // Handle errors
      xhr.addEventListener('error', () => {
        reject(new Error('Network error during upload'));
      });

      // Send request
      xhr.open('POST', `${this.baseUrl}/upload`);
      xhr.setRequestHeader('Authorization', `Bearer ${token}`); // ✅ ADD THIS LINE!
      xhr.send(formData);
    });
  }

  // Get job status
  async getJobStatus(jobId: string): Promise<JobStatusResponse> {
    const token = this.getToken();
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
    };
    
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    const response = await fetch(`${this.baseUrl}/jobs/${jobId}`, {
      headers,
    });
    
    if (!response.ok) {
      const error: ApiError = await response.json();
      throw new Error(error.detail || 'Failed to get job status');
    }

    return response.json();
  }

  // Poll job status until complete
  async pollJobStatus(
    jobId: string, 
    onUpdate?: (status: JobStatusResponse) => void,
    interval: number = 2000
  ): Promise<JobStatusResponse> {
    return new Promise((resolve, reject) => {
      const poll = async () => {
        try {
          const status = await this.getJobStatus(jobId);
          
          if (onUpdate) {
            onUpdate(status);
          }

          if (status.status === 'completed') {
            resolve(status);
          } else if (status.status === 'failed') {
            reject(new Error(status.message || 'Job failed'));
          } else {
            // Continue polling
            setTimeout(poll, interval);
          }
        } catch (error) {
          reject(error);
        }
      };

      poll();
    });
  }

  // Health check
  async healthCheck(): Promise<{ status: string }> {
    const response = await fetch(`${this.baseUrl}/health`);
    
    if (!response.ok) {
      throw new Error('Backend is not healthy');
    }

    return response.json();
  }
}

export const api = new ApiClient();