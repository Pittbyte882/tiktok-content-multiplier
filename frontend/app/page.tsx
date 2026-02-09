'use client';

import { useState } from 'react';
import { Upload, Zap, TrendingUp, Sparkles, Play, X } from 'lucide-react';
import AIThinkingLoader from '@/components/AIThinkingLoader';
import { useRouter } from 'next/navigation';


  

export default function Home() {
  const [showDemo, setShowDemo] = useState(false);
  const [showVideo, setShowVideo] = useState(false);
  const router = useRouter();
  return (
    <div className="min-h-screen bg-gradient-to-br from-black via-dark-surface to-black">
      <div className="container mx-auto px-4 py-20">
        {/* Header */}
        <nav className="flex items-center justify-between mb-20">
          <div className="flex items-center gap-2">
            <Sparkles className="w-8 h-8 text-tiktok-cyan" />
            <span className="text-2xl font-bold bg-gradient-to-r from-tiktok-cyan via-tiktok-purple to-tiktok-pink bg-clip-text text-transparent">
              Content Slicer
            </span>
          </div>
          <button className="px-6 py-2 rounded-full bg-white/10 hover:bg-white/20 transition-colors border border-white/10">
            Sign In
          </button>
        </nav>

        {/* Hero Content */}
        <div className="max-w-5xl mx-auto text-center mb-20">
          <h1 className="text-6xl md:text-7xl font-bold mb-6 bg-gradient-to-r from-white via-tiktok-cyan to-tiktok-pink bg-clip-text text-transparent">
            Turn 1 Video Into
            <br />
            20 Viral Posts
          </h1>
          <p className="text-xl md:text-2xl text-white/70 mb-8 max-w-2xl mx-auto">
            AI-powered content generation for TikTok creators.
            <br />
            Get viral hooks, captions, and clips in{' '}
            <span className="text-tiktok-cyan font-semibold">60 seconds</span> ⚡
          </p>

          {/* CTA Buttons */}
          <div className="flex flex-col sm:flex-row gap-4 justify-center items-center mb-12">
            <button
              onClick={() => router.push('/upload')}
              className="group px-8 py-4 rounded-full bg-gradient-to-r from-tiktok-cyan via-tiktok-purple to-tiktok-pink text-white font-semibold text-lg hover:scale-105 transition-transform"
            >
              <span className="flex items-center gap-2">
                <Upload className="w-5 h-5" />
                Try For Free
                <Zap className="w-5 h-5 group-hover:animate-pulse" />
              </span>
            </button>
            <button 
              onClick={() => setShowVideo(true)}
              className="group px-8 py-4 rounded-full bg-white/5 hover:bg-white/10 border border-white/10 transition-colors font-semibold text-lg"
            >
              <span className="flex items-center gap-2">
                <Play className="w-5 h-5 group-hover:text-tiktok-cyan transition-colors" />
                Watch Demo
              </span>
            </button>
          </div>

          {/* Social Proof */}
          <div className="flex items-center justify-center gap-8 text-white/50 text-sm">
            <div className="flex items-center gap-2">
              <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse" />
              <span>2,453 videos processed this week</span>
            </div>
          </div>
        </div>

        {/* Demo Loader Modal */}
        {showDemo && (
          <div className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
            <div className="max-w-2xl w-full bg-dark-surface/90 backdrop-blur-md border border-white/10 rounded-3xl p-12 relative">
              <button
                onClick={() => setShowDemo(false)}
                className="absolute top-4 right-4 p-2 rounded-full bg-white/5 hover:bg-white/10 transition-colors"
              >
                <X className="w-5 h-5" />
              </button>
              
              <AIThinkingLoader size="lg" message="Analyzing your viral potential" />
              
              <div className="mt-8 space-y-3 text-center">
                <p className="text-white/70 text-sm">This is a demo of our AI processing animation</p>
                <p className="text-white/50 text-xs">In production, this would show real-time progress of your video being processed</p>
              </div>

              <button
                onClick={() => setShowDemo(false)}
                className="mt-8 w-full px-6 py-3 rounded-full bg-gradient-to-r from-tiktok-cyan/20 to-tiktok-purple/20 hover:from-tiktok-cyan/30 hover:to-tiktok-purple/30 transition-colors border border-tiktok-cyan/20"
              >
                Close Demo
              </button>
            </div>
          </div>
        )}

        {/* Video Demo Modal */}
        {showVideo && (
          <div className="fixed inset-0 bg-black/90 backdrop-blur-sm z-50 flex items-center justify-center p-4">
            <div className="max-w-4xl w-full relative">
              <button
                onClick={() => setShowVideo(false)}
                className="absolute -top-12 right-0 p-2 rounded-full bg-white/10 hover:bg-white/20 transition-colors"
              >
                <X className="w-6 h-6" />
              </button>
              
              {/* Video Placeholder */}
              <div className="aspect-video bg-dark-surface/50 backdrop-blur-sm border border-white/10 rounded-2xl flex items-center justify-center">
                <div className="text-center">
                  <Play className="w-20 h-20 text-tiktok-cyan mx-auto mb-4 opacity-50" />
                  <p className="text-white/70 text-lg mb-2">Demo Video Coming Soon</p>
                  <p className="text-white/50 text-sm">
                    We'll add a video showing the entire process:
                    <br />
                    Upload → AI Processing → Results
                  </p>
                </div>
              </div>

              {/* replace the above div with an actual video when ready:
              <video 
                className="w-full rounded-2xl"
                controls
                autoPlay
              >
                <source src="/demo-video.mp4" type="video/mp4" />
              </video>
              */}
            </div>
          </div>
        )}

        {/* Features Grid */}
        {!showDemo && !showVideo && (
          <div className="grid md:grid-cols-3 gap-8 mt-20">
            <div className="group p-8 rounded-2xl bg-gradient-to-br from-white/5 to-white/0 border border-white/10 hover:border-tiktok-cyan/50 transition-all hover:scale-105">
              <div className="w-12 h-12 rounded-full bg-gradient-to-br from-tiktok-cyan/20 to-tiktok-cyan/5 flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
                <Zap className="w-6 h-6 text-tiktok-cyan" />
              </div>
              <h3 className="text-xl font-bold mb-2">10 Viral Hooks</h3>
              <p className="text-white/60">
                AI generates 10 different opening hooks optimized for maximum engagement
              </p>
            </div>

            <div className="group p-8 rounded-2xl bg-gradient-to-br from-white/5 to-white/0 border border-white/10 hover:border-tiktok-purple/50 transition-all hover:scale-105">
              <div className="w-12 h-12 rounded-full bg-gradient-to-br from-tiktok-purple/20 to-tiktok-purple/5 flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
                <TrendingUp className="w-6 h-6 text-tiktok-purple" />
              </div>
              <h3 className="text-xl font-bold mb-2">Smart Captions</h3>
              <p className="text-white/60">
                5 caption variations with trending hashtags and CTAs that convert
              </p>
            </div>

            <div className="group p-8 rounded-2xl bg-gradient-to-br from-white/5 to-white/0 border border-white/10 hover:border-tiktok-pink/50 transition-all hover:scale-105">
              <div className="w-12 h-12 rounded-full bg-gradient-to-br from-tiktok-pink/20 to-tiktok-pink/5 flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
                <Sparkles className="w-6 h-6 text-tiktok-pink" />
              </div>
              <h3 className="text-xl font-bold mb-2">Auto Clips</h3>
              <p className="text-white/60">
                AI finds and cuts your viral moments automatically
              </p>
            </div>
          </div>
        )}

        {/* Pricing */}
        {!showDemo && !showVideo && (
          <div className="mt-32 max-w-4xl mx-auto">
            <h2 className="text-4xl font-bold text-center mb-12">
              Simple Pricing
            </h2>
            <div className="grid md:grid-cols-3 gap-6">
              {/* Free */}
              <div className="p-6 rounded-2xl bg-white/5 border border-white/10 hover:border-white/20 transition-colors">
                <h3 className="text-lg font-semibold mb-2">Free</h3>
                <div className="text-3xl font-bold mb-4">$0</div>
                <ul className="space-y-2 text-white/60 text-sm mb-6">
                  <li>✓ 3 videos per month</li>
                  <li>✓ 10 credits</li>
                  <li>✓ Basic features</li>
                </ul>
                <button className="w-full py-2 rounded-full bg-white/10 hover:bg-white/20 transition-colors">
                  Get Started
                </button>
              </div>

              {/* Creator */}
              <div className="p-6 rounded-2xl bg-gradient-to-br from-tiktok-cyan/10 to-tiktok-purple/10 border-2 border-tiktok-cyan/50 relative hover:border-tiktok-cyan transition-colors">
                <div className="absolute -top-3 left-1/2 -translate-x-1/2 px-3 py-1 rounded-full bg-tiktok-cyan text-black text-xs font-bold">
                  MOST POPULAR
                </div>
                <h3 className="text-lg font-semibold mb-2">Creator</h3>
                <div className="text-3xl font-bold mb-4">
                  $49<span className="text-lg text-white/60">/mo</span>
                </div>
                <ul className="space-y-2 text-white/80 text-sm mb-6">
                  <li>✓ 50 videos per month</li>
                  <li>✓ 1,000 credits</li>
                  <li>✓ All features</li>
                  <li>✓ Priority support</li>
                </ul>
                <button className="w-full py-2 rounded-full bg-gradient-to-r from-tiktok-cyan to-tiktok-purple hover:scale-105 transition-transform font-semibold">
                  Start Free Trial
                </button>
              </div>

              {/* Agency */}
              <div className="p-6 rounded-2xl bg-white/5 border border-white/10 hover:border-white/20 transition-colors">
                <h3 className="text-lg font-semibold mb-2">Agency</h3>
                <div className="text-3xl font-bold mb-4">
                  $149<span className="text-lg text-white/60">/mo</span>
                </div>
                <ul className="space-y-2 text-white/60 text-sm mb-6">
                  <li>✓ Unlimited videos</li>
                  <li>✓ 5,000 credits</li>
                  <li>✓ White-label</li>
                  <li>✓ Team accounts</li>
                </ul>
                <button className="w-full py-2 rounded-full bg-white/10 hover:bg-white/20 transition-colors">
                  Contact Sales
                </button>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Footer */}
      <footer className="border-t border-white/10 mt-32">
        <div className="container mx-auto px-4 py-8 text-center text-white/40 text-sm">
          <p>© 2026 TikTok Content Multiplier. Built by Crystal Pittman.</p>
        </div>
      </footer>
    </div>
  );
}