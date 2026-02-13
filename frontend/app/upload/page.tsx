'use client';

import { useState, useCallback } from 'react';
import { Upload as UploadIcon, X, CheckCircle, AlertCircle, ArrowLeft, Sparkles } from 'lucide-react';
import { useRouter } from 'next/navigation';
import AIThinkingLoader from '@/components/AIThinkingLoader';
import { api } from '@/lib/api';
import ProtectedRoute from '@/components/ProtectedRoute';
import UserProfile from '@/components/UserProfile';

interface UploadedFile {
  file: File;
  preview: string;
  size: string;
}

export default function UploadPage() {
  const router = useRouter();
  const [uploadedFile, setUploadedFile] = useState<UploadedFile | null>(null);
  const [isDragging, setIsDragging] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [uploadProgress, setUploadProgress] = useState(0);

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
  }, []);

  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
  };

  const validateFile = (file: File): string | null => {
    const validTypes = ['video/mp4', 'video/quicktime', 'video/x-msvideo'];
    const maxSize = 500 * 1024 * 1024; // 500MB

    if (!validTypes.includes(file.type)) {
      return 'Please upload a valid video file (MP4, MOV, AVI)';
    }

    if (file.size > maxSize) {
      return 'File size must be less than 500MB';
    }

    return null;
  };

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    setError(null);

    const file = e.dataTransfer.files[0];
    if (!file) return;

    const validationError = validateFile(file);
    if (validationError) {
      setError(validationError);
      return;
    }

    const preview = URL.createObjectURL(file);
    
    setUploadedFile({
      file,
      preview,
      size: formatFileSize(file.size),
    });
  }, []);

  const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    setError(null);
    const file = e.target.files?.[0];
    if (!file) return;

    const validationError = validateFile(file);
    if (validationError) {
      setError(validationError);
      return;
    }

    const preview = URL.createObjectURL(file);
    
    setUploadedFile({
      file,
      preview,
      size: formatFileSize(file.size),
    });
  };

  const handleRemoveFile = () => {
    if (uploadedFile?.preview) {
      URL.revokeObjectURL(uploadedFile.preview);
    }
    setUploadedFile(null);
    setError(null);
    setUploadProgress(0);
  };

  const handleProcess = async () => {
    if (!uploadedFile) return;

    setIsProcessing(true);
    setError(null);
    setUploadProgress(0);

    try {
      const response = await api.uploadVideo(uploadedFile.file, (progress) => {
        setUploadProgress(progress);
      });

      console.log('Upload response:', response);

      setTimeout(() => {
        router.push(`/results/${response.job_id}`);
      }, 500);

    } catch (err) {
      console.error('Upload error:', err);
      setError(err instanceof Error ? err.message : 'Failed to upload video. Please try again.');
      setIsProcessing(false);
      setUploadProgress(0);
    }
  };

  return (
    <ProtectedRoute>
      <div className="min-h-screen bg-gradient-to-br from-black via-dark-surface to-black">
        <div className="container mx-auto px-4 py-8">
          
          {/* Header with UserProfile */}
          <div className="flex items-center justify-between mb-12">
            <button
              onClick={() => router.push('/')}
              className="flex items-center gap-2 text-white/60 hover:text-white transition-colors"
            >
              <ArrowLeft className="w-5 h-5" />
              <span>Back to Home</span>
            </button>
            
            <div className="flex items-center gap-2">
              <Sparkles className="w-6 h-6 text-tiktok-cyan" />
              <span className="text-xl font-bold bg-gradient-to-r from-tiktok-cyan via-tiktok-purple to-tiktok-pink bg-clip-text text-transparent">
                ViralStack
              </span>
            </div>

            <UserProfile />
          </div>

          <div className="max-w-3xl mx-auto">
            
            <div className="text-center mb-12">
              <h1 className="text-4xl md:text-5xl font-bold mb-4 bg-gradient-to-r from-white via-tiktok-cyan to-tiktok-pink bg-clip-text text-transparent">
                Upload Your Video
              </h1>
              <p className="text-white/60 text-lg">
                Upload your video and let AI create 20+ pieces of viral content
              </p>
            </div>

            {!uploadedFile && !isProcessing && (
              <div
                onDragOver={handleDragOver}
                onDragLeave={handleDragLeave}
                onDrop={handleDrop}
                className={`
                  relative border-2 border-dashed rounded-3xl p-12 transition-all
                  ${isDragging 
                    ? 'border-tiktok-cyan bg-tiktok-cyan/5 scale-105' 
                    : 'border-white/20 bg-white/5 hover:border-white/40'
                  }
                `}
              >
                <input
                  type="file"
                  accept="video/*"
                  onChange={handleFileInput}
                  className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
                />

                <div className="text-center">
                  <div className="mb-6 flex justify-center">
                    <div className={`
                      p-6 rounded-full transition-all
                      ${isDragging 
                        ? 'bg-gradient-to-br from-tiktok-cyan/20 to-tiktok-purple/20 scale-110' 
                        : 'bg-gradient-to-br from-white/10 to-white/5'
                      }
                    `}>
                      <UploadIcon className={`w-12 h-12 ${isDragging ? 'text-tiktok-cyan' : 'text-white/60'}`} />
                    </div>
                  </div>

                  <h3 className="text-2xl font-bold mb-2 text-white">
                    {isDragging ? 'Drop your video here' : 'Drag & drop your video'}
                  </h3>
                  <p className="text-white/60 mb-6">
                    or click to browse files
                  </p>

                  <div className="flex items-center justify-center gap-6 text-sm text-white/40">
                    <span>Max 500MB</span>
                    <span>•</span>
                    <span>MP4, MOV, AVI</span>
                    <span>•</span>
                    <span>Up to 5 minutes</span>
                  </div>
                </div>
              </div>
            )}

            {uploadedFile && !isProcessing && (
              <div className="bg-white/5 border border-white/10 rounded-3xl p-8">
                <div className="flex items-start gap-6">
                  <div className="flex-shrink-0">
                    <video
                      src={uploadedFile.preview}
                      className="w-40 h-40 object-cover rounded-xl bg-black"
                    />
                  </div>

                  <div className="flex-1">
                    <div className="flex items-start justify-between mb-4">
                      <div>
                        <h3 className="text-xl font-semibold text-white mb-1">
                          {uploadedFile.file.name}
                        </h3>
                        <p className="text-white/60 text-sm">
                          {uploadedFile.size}
                        </p>
                      </div>
                      <button
                        onClick={handleRemoveFile}
                        className="p-2 rounded-full bg-white/5 hover:bg-white/10 transition-colors"
                      >
                        <X className="w-5 h-5" />
                      </button>
                    </div>

                    <div className="flex items-center gap-2 text-green-400 mb-6">
                      <CheckCircle className="w-5 h-5" />
                      <span className="text-sm">Video ready to process</span>
                    </div>

                    <button
                      onClick={handleProcess}
                      className="w-full py-4 rounded-full bg-gradient-to-r from-tiktok-cyan via-tiktok-purple to-tiktok-pink text-white font-semibold text-lg hover:scale-105 transition-transform"
                    >
                      <span className="flex items-center justify-center gap-2">
                        <Sparkles className="w-5 h-5" />
                        Generate Viral Content
                        <Sparkles className="w-5 h-5" />
                      </span>
                    </button>
                  </div>
                </div>
              </div>
            )}

            {isProcessing && (
              <div className="bg-white/5 border border-white/10 rounded-3xl p-12">
                <AIThinkingLoader 
                  size="lg" 
                  message={uploadProgress < 100 ? "Uploading your video" : "Starting AI processing"} 
                />

                <div className="mt-8">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-white/60 text-sm">Upload Progress</span>
                    <span className="text-white font-semibold">{uploadProgress}%</span>
                  </div>
                  <div className="w-full h-2 bg-white/5 rounded-full overflow-hidden">
                    <div 
                      className="h-full bg-gradient-to-r from-tiktok-cyan via-tiktok-purple to-tiktok-pink transition-all duration-300"
                      style={{ width: `${uploadProgress}%` }}
                    />
                  </div>
                </div>

                <p className="text-center text-white/50 text-sm mt-6">
                  This may take a minute. Don't close this page.
                </p>
              </div>
            )}

            {error && (
              <div className="mt-6 p-4 rounded-2xl bg-red-500/10 border border-red-500/20">
                <div className="flex items-center gap-3 text-red-400">
                  <AlertCircle className="w-5 h-5 flex-shrink-0" />
                  <p>{error}</p>
                </div>
              </div>
            )}

            {!uploadedFile && !isProcessing && (
              <div className="grid md:grid-cols-3 gap-4 mt-12">
                <div className="p-6 rounded-2xl bg-white/5 border border-white/10">
                  <div className="text-3xl mb-2">🎤</div>
                  <h4 className="font-semibold mb-1">Transcription</h4>
                  <p className="text-sm text-white/60">AI transcribes your audio</p>
                </div>
                <div className="p-6 rounded-2xl bg-white/5 border border-white/10">
                  <div className="text-3xl mb-2">🔥</div>
                  <h4 className="font-semibold mb-1">10 Viral Hooks</h4>
                  <p className="text-sm text-white/60">Different opening variations</p>
                </div>
                <div className="p-6 rounded-2xl bg-white/5 border border-white/10">
                  <div className="text-3xl mb-2">✍️</div>
                  <h4 className="font-semibold mb-1">Smart Captions</h4>
                  <p className="text-sm text-white/60">With trending hashtags</p>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </ProtectedRoute>
  );
}