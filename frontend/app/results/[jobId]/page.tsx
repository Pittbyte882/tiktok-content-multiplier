'use client';

import { useEffect, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { ArrowLeft, Download, Copy, Check, Sparkles, AlertCircle } from 'lucide-react';
import AIThinkingLoader from '@/components/AIThinkingLoader';
import { api, JobStatusResponse } from '@/lib/api';

// Define types for the results structure
interface ViralHook {
  text: string;
  virality_score: number;
}

interface Caption {
  caption: string;
  hashtags: string[];
  character_count: number;
}

interface Clip {
  start_time: number;
  end_time: number;
  description: string;
}

interface ProcessingResults {
  transcript: string;
  viral_hooks: string[];
  captions: Caption[];
  clips: Clip[];
}

export default function ResultsPage() {
  const params = useParams();
  const router = useRouter();
  const jobId = params.jobId as string;

  const [jobStatus, setJobStatus] = useState<JobStatusResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [copiedItems, setCopiedItems] = useState<Set<string>>(new Set());

  useEffect(() => {
    if (!jobId) return;

    // Poll job status
    api.pollJobStatus(jobId, (status) => {
      setJobStatus(status);
    }).catch((err) => {
      setError(err.message);
    });
  }, [jobId]);

  const handleCopy = async (text: string, id: string) => {
    try {
      await navigator.clipboard.writeText(text);
      setCopiedItems(prev => new Set(prev).add(id));
      setTimeout(() => {
        setCopiedItems(prev => {
          const newSet = new Set(prev);
          newSet.delete(id);
          return newSet;
        });
      }, 2000);
    } catch (err) {
      console.error('Failed to copy:', err);
    }
  };

  const handleDownload = () => {
    if (!jobStatus?.results) return;

    const content = {
      transcript: jobStatus.results.transcript,
      viral_hooks: jobStatus.results.viral_hooks,
      captions: jobStatus.results.captions,
      clips: jobStatus.results.clips,
    };

    const blob = new Blob([JSON.stringify(content, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `tiktok-content-${jobId}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  if (error) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-black via-dark-surface to-black flex items-center justify-center p-4">
        <div className="max-w-md w-full bg-red-500/10 border border-red-500/20 rounded-3xl p-8 text-center">
          <AlertCircle className="w-16 h-16 text-red-400 mx-auto mb-4" />
          <h2 className="text-2xl font-bold text-white mb-2">Processing Failed</h2>
          <p className="text-white/60 mb-6">{error}</p>
          <button
            onClick={() => router.push('/upload')}
            className="px-6 py-3 rounded-full bg-white/10 hover:bg-white/20 transition-colors"
          >
            Try Again
          </button>
        </div>
      </div>
    );
  }

  if (!jobStatus || jobStatus.status !== 'completed') {
    return (
      <div className="min-h-screen bg-gradient-to-br from-black via-dark-surface to-black flex items-center justify-center p-4">
        <div className="max-w-2xl w-full">
          <AIThinkingLoader size="lg" message={jobStatus?.message || "Processing your video"} />
          
          {jobStatus && (
            <div className="mt-12 space-y-6">
              {/* Processing stages */}
              <ProcessingStage label="Transcribing audio" status={jobStatus.progress_percent > 0 ? 'complete' : 'processing'} icon="🎤" />
              <ProcessingStage label="Finding viral hooks" status={jobStatus.progress_percent > 30 ? 'complete' : jobStatus.progress_percent > 0 ? 'processing' : 'waiting'} icon="🔥" />
              <ProcessingStage label="Writing captions" status={jobStatus.progress_percent > 60 ? 'complete' : jobStatus.progress_percent > 30 ? 'processing' : 'waiting'} icon="✍️" />
              <ProcessingStage label="Cutting clips" status={jobStatus.progress_percent > 80 ? 'complete' : jobStatus.progress_percent > 60 ? 'processing' : 'waiting'} icon="🎬" />
              <ProcessingStage label="Packaging results" status={jobStatus.progress_percent > 95 ? 'complete' : jobStatus.progress_percent > 80 ? 'processing' : 'waiting'} icon="📦" />
            </div>
          )}

          <div className="mt-8 text-center">
            <div className="text-white/60 text-sm mb-2">Overall Progress</div>
            <div className="flex items-center gap-4 justify-center">
              <div className="flex-1 max-w-xs h-2 bg-white/5 rounded-full overflow-hidden">
                <div 
                  className="h-full bg-gradient-to-r from-tiktok-cyan via-tiktok-purple to-tiktok-pink transition-all duration-500"
                  style={{ width: `${jobStatus?.progress_percent || 0}%` }}
                />
              </div>
              <span className="text-white/90 font-semibold min-w-[4ch] text-right">
                {jobStatus?.progress_percent || 0}%
              </span>
            </div>
          </div>
        </div>
      </div>
    );
  }

  const { results } = jobStatus;
  if (!results) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-black via-dark-surface to-black flex items-center justify-center p-4">
        <AIThinkingLoader size="lg" message="Loading results..." />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-black via-dark-surface to-black">
      <div className="container mx-auto px-4 py-8">
        
        {/* Header */}
        <div className="flex items-center justify-between mb-12">
          <button
            onClick={() => router.push('/upload')}
            className="flex items-center gap-2 text-white/60 hover:text-white transition-colors"
          >
            <ArrowLeft className="w-5 h-5" />
            <span>New Upload</span>
          </button>
          
          <div className="flex items-center gap-2">
            <Sparkles className="w-6 h-6 text-tiktok-cyan" />
            <span className="text-xl font-bold bg-gradient-to-r from-tiktok-cyan via-tiktok-purple to-tiktok-pink bg-clip-text text-transparent">
              TikTok Multiplier
            </span>
          </div>

          <button
            onClick={handleDownload}
            className="flex items-center gap-2 px-4 py-2 rounded-full bg-white/10 hover:bg-white/20 transition-colors"
          >
            <Download className="w-4 h-4" />
            <span>Download All</span>
          </button>
        </div>

        {/* Success Message */}
        <div className="max-w-4xl mx-auto mb-12">
          <div className="text-center mb-8">
            <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-gradient-to-br from-green-400/20 to-green-600/20 mb-4">
              <Check className="w-8 h-8 text-green-400" />
            </div>
            <h1 className="text-4xl md:text-5xl font-bold mb-4 bg-gradient-to-r from-white via-tiktok-cyan to-tiktok-pink bg-clip-text text-transparent">
              Your Content is Ready!
            </h1>
            <p className="text-white/60 text-lg">
              AI generated 20+ pieces of viral content from your video
            </p>
          </div>

          {/* Viral Hooks */}
          <section className="mb-12">
            <h2 className="text-2xl font-bold mb-6 flex items-center gap-2">
              <span className="text-3xl">🔥</span>
              Viral Hooks ({results.viral_hooks?.length || 0})
            </h2>
            <div className="grid md:grid-cols-2 gap-4">
              {results.viral_hooks?.map((hook: string, index: number) => (
                <div key={index} className="p-6 rounded-2xl bg-white/5 border border-white/10 hover:border-tiktok-cyan/30 transition-colors group">
                  <div className="flex items-start justify-between mb-3">
                    <span className="text-sm text-white/40">Hook #{index + 1}</span>
                    <button
                      onClick={() => handleCopy(hook, `hook-${index}`)}
                      className="p-2 rounded-lg bg-white/5 hover:bg-white/10 transition-colors"
                    >
                      {copiedItems.has(`hook-${index}`) ? (
                        <Check className="w-4 h-4 text-green-400" />
                      ) : (
                        <Copy className="w-4 h-4" />
                      )}
                    </button>
                  </div>
                  <p className="text-white font-medium text-lg">{hook}</p>
                  <div className="mt-3 flex items-center gap-2">
                    <div className="flex gap-1">
                      {[...Array(5)].map((_, i: number) => (
                        <span key={i} className="text-yellow-400">⭐</span>
                      ))}
                    </div>
                    <span className="text-xs text-white/40">High viral potential</span>
                  </div>
                </div>
              ))}
            </div>
          </section>

          {/* Captions */}
          <section className="mb-12">
            <h2 className="text-2xl font-bold mb-6 flex items-center gap-2">
              <span className="text-3xl">✍️</span>
              Smart Captions ({results.captions?.length || 0})
            </h2>
            <div className="space-y-4">
              {results.captions?.map((caption: Caption, index: number) => (
                <div key={index} className="p-6 rounded-2xl bg-white/5 border border-white/10 hover:border-tiktok-purple/30 transition-colors">
                  <div className="flex items-start justify-between mb-4">
                    <span className="text-sm text-white/40">Caption #{index + 1}</span>
                    <button
                      onClick={() => handleCopy(`${caption.caption}\n\n${caption.hashtags.join(' ')}`, `caption-${index}`)}
                      className="p-2 rounded-lg bg-white/5 hover:bg-white/10 transition-colors"
                    >
                      {copiedItems.has(`caption-${index}`) ? (
                        <Check className="w-4 h-4 text-green-400" />
                      ) : (
                        <Copy className="w-4 h-4" />
                      )}
                    </button>
                  </div>
                  <p className="text-white mb-4 whitespace-pre-wrap">{caption.caption}</p>
                  <div className="flex flex-wrap gap-2 mb-3">
                    {caption.hashtags?.map((tag: string, tagIndex: number) => (
                      <span key={tagIndex} className="px-3 py-1 rounded-full bg-tiktok-cyan/10 text-tiktok-cyan text-sm">
                        {tag}
                      </span>
                    ))}
                  </div>
                  <div className="text-xs text-white/40">
                    {caption.character_count} characters
                  </div>
                </div>
              ))}
            </div>
          </section>

          {/* Transcript */}
          {results.transcript && (
            <section className="mb-12">
              <h2 className="text-2xl font-bold mb-6 flex items-center gap-2">
                <span className="text-3xl">🎤</span>
                Transcript
              </h2>
              <div className="p-6 rounded-2xl bg-white/5 border border-white/10">
                <div className="flex items-start justify-between mb-4">
                  <span className="text-sm text-white/40">Full transcription</span>
                  <button
                    onClick={() => handleCopy(results.transcript, 'transcript')}
                    className="p-2 rounded-lg bg-white/5 hover:bg-white/10 transition-colors"
                  >
                    {copiedItems.has('transcript') ? (
                      <Check className="w-4 h-4 text-green-400" />
                    ) : (
                      <Copy className="w-4 h-4" />
                    )}
                  </button>
                </div>
                <p className="text-white/80 leading-relaxed">{results.transcript}</p>
              </div>
            </section>
          )}

          {/* Clips */}
          {results.clips && results.clips.length > 0 && (
            <section>
              <h2 className="text-2xl font-bold mb-6 flex items-center gap-2">
                <span className="text-3xl">🎬</span>
                Viral Moment Clips ({results.clips.length})
              </h2>
              <div className="grid md:grid-cols-2 gap-4">
                {results.clips.map((clip: Clip, index: number) => (
                  <div key={index} className="p-6 rounded-2xl bg-white/5 border border-white/10 hover:border-tiktok-pink/30 transition-colors">
                    <div className="flex items-start justify-between mb-3">
                      <span className="text-sm text-white/40">Clip #{index + 1}</span>
                      <span className="text-xs text-tiktok-cyan">
                        {clip.start_time}s - {clip.end_time}s
                      </span>
                    </div>
                    <p className="text-white">{clip.description}</p>
                  </div>
                ))}
              </div>
            </section>
          )}
        </div>
      </div>
    </div>
  );
}

function ProcessingStage({ 
  label, 
  status, 
  icon 
}: { 
  label: string; 
  status: 'waiting' | 'processing' | 'complete';
  icon: string;
}) {
  return (
    <div className={`
      p-4 rounded-xl transition-all
      ${status === 'processing' 
        ? 'bg-gradient-to-r from-tiktok-cyan/10 to-tiktok-purple/10 border border-tiktok-cyan/20' 
        : status === 'complete'
        ? 'bg-green-500/5 border border-green-500/20'
        : 'bg-white/5 border border-white/5'
      }
    `}>
      <div className="flex items-center gap-4">
        <div className={`
          flex-shrink-0 w-10 h-10 rounded-full flex items-center justify-center text-xl
          ${status === 'processing' 
            ? 'bg-gradient-to-br from-tiktok-cyan/20 to-tiktok-purple/20 animate-pulse' 
            : status === 'complete'
            ? 'bg-green-500/20'
            : 'bg-white/5'
          }
        `}>
          {status === 'complete' ? '✓' : icon}
        </div>

        <div className="flex-1">
          <h3 className={`
            font-semibold
            ${status === 'processing' 
              ? 'text-white' 
              : status === 'complete'
              ? 'text-green-400'
              : 'text-white/50'
            }
          `}>
            {label}
          </h3>
        </div>

        {status === 'processing' && (
          <span className="text-xs text-tiktok-cyan flex items-center gap-2">
            <span className="w-2 h-2 bg-tiktok-cyan rounded-full animate-ping" />
            Processing
          </span>
        )}
        {status === 'complete' && (
          <span className="text-xs text-green-400 flex items-center gap-2">
            <span className="w-2 h-2 bg-green-400 rounded-full" />
            Done
          </span>
        )}
      </div>
    </div>
  );
}