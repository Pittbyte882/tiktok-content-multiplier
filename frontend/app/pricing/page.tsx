'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { Check, Sparkles, Zap, Crown, ArrowRight } from 'lucide-react';
import Link from 'next/link';

const tiers = [
  {
    name: 'Free',
    price: 0,
    period: 'forever',
    icon: Sparkles,
    color: 'from-gray-400 to-gray-600',
    features: [
      '3 videos per month',
      '10 viral hooks per video',
      'Smart captions & hashtags',
      '20 clips per video',
      'Basic support'
    ],
    cta: 'Get Started Free',
    popular: false
  },
  {
    name: 'Creator',
    price: 29,
    period: 'month',
    icon: Zap,
    color: 'from-tiktok-cyan to-tiktok-purple',
    features: [
      '20 videos per month',
      'Unlimited hooks',
      'Advanced caption AI',
      'Unlimited clips',
      'Priority processing',
      'Download all formats',
      'Priority support'
    ],
    cta: 'Start Creating',
    popular: true
  },
  {
    name: 'Agency',
    price: 99,
    period: 'month',
    icon: Crown,
    color: 'from-tiktok-purple to-tiktok-pink',
    features: [
      'Unlimited videos',
      'White-label branding',
      'API access',
      'Team collaboration',
      'Custom integrations',
      'Dedicated support',
      'Custom AI training'
    ],
    cta: 'Go Enterprise',
    popular: false
  }
];

export default function PricingPage() {
  const router = useRouter();
  const [billingPeriod, setBillingPeriod] = useState<'monthly' | 'annual'>('monthly');

  const handleSelectPlan = (tierName: string) => {
    if (tierName === 'Free') {
      router.push('/signup');
    } else {
      // TODO: Integrate with Stripe
      router.push('/signup');
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-black via-dark-surface to-black">
      <div className="container mx-auto px-4 py-16">
        
        {/* Header */}
        <div className="text-center mb-16">
          <div className="inline-flex items-center gap-2 mb-6">
            <Sparkles className="w-8 h-8 text-tiktok-cyan" />
            <span className="text-2xl font-bold bg-gradient-to-r from-tiktok-cyan via-tiktok-purple to-tiktok-pink bg-clip-text text-transparent">
              StackSlice AI
            </span>
          </div>
          
          <h1 className="text-5xl md:text-6xl font-bold mb-6 bg-gradient-to-r from-white via-tiktok-cyan to-tiktok-pink bg-clip-text text-transparent">
            Choose Your Plan
          </h1>
          <p className="text-white/60 text-xl max-w-2xl mx-auto">
            Transform your long-form videos into viral TikTok content with AI
          </p>

          {/* Billing Toggle */}
          <div className="mt-8 inline-flex items-center gap-4 p-2 bg-white/5 border border-white/10 rounded-full">
            <button
              onClick={() => setBillingPeriod('monthly')}
              className={`px-6 py-2 rounded-full font-semibold transition-all ${
                billingPeriod === 'monthly'
                  ? 'bg-gradient-to-r from-tiktok-cyan to-tiktok-purple text-white'
                  : 'text-white/60 hover:text-white'
              }`}
            >
              Monthly
            </button>
            <button
              onClick={() => setBillingPeriod('annual')}
              className={`px-6 py-2 rounded-full font-semibold transition-all ${
                billingPeriod === 'annual'
                  ? 'bg-gradient-to-r from-tiktok-cyan to-tiktok-purple text-white'
                  : 'text-white/60 hover:text-white'
              }`}
            >
              Annual
              <span className="ml-2 px-2 py-1 text-xs bg-green-500/20 text-green-400 rounded-full">
                Save 20%
              </span>
            </button>
          </div>
        </div>

        {/* Pricing Cards */}
        <div className="grid md:grid-cols-3 gap-8 max-w-7xl mx-auto mb-16">
          {tiers.map((tier) => {
            const Icon = tier.icon;
            const price = billingPeriod === 'annual' && tier.price > 0 
              ? Math.round(tier.price * 0.8) 
              : tier.price;

            return (
              <div
                key={tier.name}
                className={`relative rounded-3xl p-8 transition-all hover:scale-105 ${
                  tier.popular
                    ? 'bg-gradient-to-br from-white/10 to-white/5 border-2 border-tiktok-cyan shadow-2xl shadow-tiktok-cyan/20'
                    : 'bg-white/5 border border-white/10'
                }`}
              >
                {tier.popular && (
                  <div className="absolute -top-4 left-1/2 -translate-x-1/2 px-4 py-1 rounded-full bg-gradient-to-r from-tiktok-cyan to-tiktok-purple text-white text-sm font-semibold">
                    Most Popular
                  </div>
                )}

                <div className="mb-6">
                  <div className={`inline-flex p-3 rounded-2xl bg-gradient-to-br ${tier.color} bg-opacity-10 mb-4`}>
                    <Icon className="w-8 h-8 text-white" />
                  </div>
                  <h3 className="text-2xl font-bold text-white mb-2">{tier.name}</h3>
                  <div className="flex items-baseline gap-1">
                    <span className="text-5xl font-bold text-white">${price}</span>
                    {tier.price > 0 && (
                      <span className="text-white/60">/{tier.period}</span>
                    )}
                  </div>
                  {billingPeriod === 'annual' && tier.price > 0 && (
                    <p className="text-sm text-green-400 mt-1">
                      ${tier.price * 12 - price * 12} saved per year
                    </p>
                  )}
                </div>

                <ul className="space-y-4 mb-8">
                  {tier.features.map((feature, index) => (
                    <li key={index} className="flex items-start gap-3">
                      <Check className="w-5 h-5 text-tiktok-cyan flex-shrink-0 mt-0.5" />
                      <span className="text-white/80">{feature}</span>
                    </li>
                  ))}
                </ul>

                <button
                  onClick={() => handleSelectPlan(tier.name)}
                  className={`w-full py-4 rounded-xl font-semibold transition-all flex items-center justify-center gap-2 ${
                    tier.popular
                      ? 'bg-gradient-to-r from-tiktok-cyan via-tiktok-purple to-tiktok-pink text-white hover:scale-105'
                      : 'bg-white/10 text-white hover:bg-white/20'
                  }`}
                >
                  {tier.cta}
                  <ArrowRight className="w-5 h-5" />
                </button>
              </div>
            );
          })}
        </div>

        {/* FAQ Section */}
        <div className="max-w-3xl mx-auto">
          <h2 className="text-3xl font-bold text-center mb-12 text-white">Frequently Asked Questions</h2>
          
          <div className="space-y-6">
            <FAQItem
              question="What counts as a video?"
              answer="Each video upload counts as 1 credit, regardless of length (up to 5 minutes). You can generate unlimited hooks, captions, and clips from each video."
            />
            <FAQItem
              question="Can I upgrade or downgrade anytime?"
              answer="Yes! You can change your plan at any time. Upgrades take effect immediately, and downgrades take effect at the start of your next billing cycle."
            />
            <FAQItem
              question="What happens if I run out of credits?"
              answer="Free users can wait until next month or upgrade to a paid plan. Creator and Agency users can purchase additional credits or upgrade to unlimited."
            />
            <FAQItem
              question="Do you offer refunds?"
              answer="Yes! We offer a 7-day money-back guarantee on all paid plans, no questions asked."
            />
          </div>
        </div>

        {/* CTA */}
        <div className="max-w-4xl mx-auto mt-20 text-center p-12 rounded-3xl bg-gradient-to-br from-white/10 to-white/5 border border-white/10">
          <h2 className="text-4xl font-bold mb-4 text-white">Ready to Go Viral?</h2>
          <p className="text-white/60 text-lg mb-8">
            Join thousands of creators multiplying their TikTok success with AI
          </p>
          <Link
            href="/signup"
            className="inline-flex items-center gap-2 px-8 py-4 rounded-full bg-gradient-to-r from-tiktok-cyan via-tiktok-purple to-tiktok-pink text-white font-semibold text-lg hover:scale-105 transition-transform"
          >
            Start Free Trial
            <ArrowRight className="w-5 h-5" />
          </Link>
        </div>
      </div>
    </div>
  );
}

function FAQItem({ question, answer }: { question: string; answer: string }) {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <div className="bg-white/5 border border-white/10 rounded-2xl p-6">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="w-full flex items-center justify-between text-left"
      >
        <h3 className="text-lg font-semibold text-white">{question}</h3>
        <span className={`text-2xl text-white transition-transform ${isOpen ? 'rotate-180' : ''}`}>
          ↓
        </span>
      </button>
      {isOpen && (
        <p className="mt-4 text-white/60 leading-relaxed">{answer}</p>
      )}
    </div>
  );
}