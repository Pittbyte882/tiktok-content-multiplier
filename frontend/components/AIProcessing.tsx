'use client';

import { useEffect, useState } from 'react';
import AIThinkingLoader from './AIThinkingLoader';

interface ProcessingStage {
  id: string;
  label: string;
  icon: string;
  status: 'waiting' | 'processing' | 'complete' | 'error';
  progress?: number;
}

interface AIProcessingProps {
  onComplete?: () => void;
  autoStart?: boolean;
}

export default function AIProcessing({ onComplete, autoStart = true }: AIProcessingProps) {
  const [currentStage, setCurrentStage] = useState(0);
  const [stages, setStages] = useState<ProcessingStage[]>([
    { id: 'transcribe', label: 'Transcribing audio', icon: '🎤', status: 'waiting', progress: 0 },
    { id: 'hooks', label: 'Finding viral hooks', icon: '🔥', status: 'waiting', progress: 0 },
    { id: 'captions', label: 'Writing captions', icon: '✍️', status: 'waiting', progress: 0 },
    { id: 'clips', label: 'Cutting clips', icon: '🎬', status: 'waiting', progress: 0 },
    { id: 'package', label: 'Packaging results', icon: '📦', status: 'waiting', progress: 0 },
  ]);

  useEffect(() => {
    if (!autoStart) return;

    const processStages = async () => {
      for (let i = 0; i < stages.length; i++) {
        setCurrentStage(i);
        
        // Mark as processing
        setStages(prev => prev.map((stage: ProcessingStage, idx: number) => 
          idx === i ? { ...stage, status: 'processing' as const, progress: 0 } : stage
        ));

        // Simulate progress
        for (let progress = 0; progress <= 100; progress += 10) {
          await new Promise(resolve => setTimeout(resolve, 200));
          setStages(prev => prev.map((stage: ProcessingStage, idx: number) => 
            idx === i ? { ...stage, progress } : stage
          ));
        }

        // Mark as complete
        setStages(prev => prev.map((stage: ProcessingStage, idx: number) => 
          idx === i ? { ...stage, status: 'complete' as const, progress: 100 } : stage
        ));
      }

      // All done!
      setTimeout(() => {
        onComplete?.();
      }, 500);
    };

    processStages();
  }, [autoStart, onComplete, stages.length]);

  return (
    <div className="w-full max-w-2xl mx-auto p-8">
      {/* Main Loader */}
      <div className="mb-12">
        <AIThinkingLoader 
          size="lg" 
          message={stages[currentStage]?.label || "Processing..."} 
        />
      </div>

      {/* Progress Stages */}
      <div className="space-y-4">
        {stages.map((stage: ProcessingStage) => (
          <div 
            key={stage.id}
            className={`
              relative overflow-hidden rounded-xl p-4 transition-all duration-300
              ${stage.status === 'processing' 
                ? 'bg-gradient-to-r from-cyan-500/10 via-purple-500/10 to-pink-500/10 border border-cyan-500/20' 
                : stage.status === 'complete'
                ? 'bg-green-500/5 border border-green-500/20'
                : 'bg-white/5 border border-white/5'
              }
            `}
          >
            <div className="flex items-center gap-4">
              {/* Stage Icon */}
              <div className={`
                flex-shrink-0 w-12 h-12 rounded-full flex items-center justify-center text-2xl
                transition-all duration-300
                ${stage.status === 'processing' 
                  ? 'bg-gradient-to-br from-cyan-500/20 to-purple-500/20 animate-pulse' 
                  : stage.status === 'complete'
                  ? 'bg-green-500/20'
                  : 'bg-white/5'
                }
              `}>
                {stage.status === 'complete' ? '✓' : stage.icon}
              </div>

              {/* Stage Info */}
              <div className="flex-1">
                <div className="flex items-center justify-between mb-2">
                  <h3 className={`
                    font-semibold transition-colors
                    ${stage.status === 'processing' 
                      ? 'text-white' 
                      : stage.status === 'complete'
                      ? 'text-green-400'
                      : 'text-white/50'
                    }
                  `}>
                    {stage.label}
                  </h3>

                  {/* Status Badge */}
                  {stage.status === 'processing' && (
                    <span className="text-xs text-cyan-400 flex items-center gap-2">
                      <span className="w-2 h-2 bg-cyan-400 rounded-full animate-ping" />
                      Processing
                    </span>
                  )}
                  {stage.status === 'complete' && (
                    <span className="text-xs text-green-400 flex items-center gap-2">
                      <span className="w-2 h-2 bg-green-400 rounded-full" />
                      Done
                    </span>
                  )}
                </div>

                {/* Progress Bar */}
                {stage.status === 'processing' && (
                  <div className="w-full h-1.5 bg-white/5 rounded-full overflow-hidden">
                    <div 
                      className="h-full bg-gradient-to-r from-cyan-400 via-purple-400 to-pink-400 transition-all duration-300"
                      style={{ width: `${stage.progress}%` }}
                    />
                  </div>
                )}
                {stage.status === 'complete' && (
                  <div className="w-full h-1.5 bg-green-500/20 rounded-full overflow-hidden">
                    <div className="h-full bg-green-400 w-full" />
                  </div>
                )}
              </div>
            </div>

            {/* Shimmer effect for processing */}
            {stage.status === 'processing' && (
              <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/5 to-transparent animate-shimmer" />
            )}
          </div>
        ))}
      </div>

      {/* Overall Progress */}
      <div className="mt-8 text-center">
        <div className="text-white/60 text-sm mb-2">
          Overall Progress
        </div>
        <div className="flex items-center gap-4 justify-center">
          <div className="flex-1 max-w-xs h-2 bg-white/5 rounded-full overflow-hidden">
            <div 
              className="h-full bg-gradient-to-r from-cyan-400 via-purple-400 to-pink-400 transition-all duration-500"
              style={{ width: `${((currentStage + 1) / stages.length) * 100}%` }}
            />
          </div>
          <span className="text-white/90 font-semibold min-w-[4ch] text-right">
            {Math.round(((currentStage + 1) / stages.length) * 100)}%
          </span>
        </div>
      </div>
    </div>
  );
}