'use client';

import { Check, Sparkles } from 'lucide-react';
import { useState } from 'react';

interface PricingCardProps {
  name: string;
  price: number;
  priceId: string;
  features: string[];
  popular?: boolean;
}

export default function PricingCard({ name, price, priceId, features, popular }: PricingCardProps) {
  const [isLoading, setIsLoading] = useState(false);

  const handleCheckout = async () => {
    setIsLoading(true);
    
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/payments/create-checkout-session`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ price_id: priceId })
      });

      const data = await response.json();
      
      // Redirect to Stripe checkout
      window.location.href = data.checkout_url;
      
    } catch (error) {
      console.error('Checkout error:', error);
      setIsLoading(false);
    }
  };

  return (
    <div className={`
      p-6 rounded-2xl relative
      ${popular 
        ? 'bg-gradient-to-br from-tiktok-cyan/10 to-tiktok-purple/10 border-2 border-tiktok-cyan/50' 
        : 'bg-white/5 border border-white/10 hover:border-white/20'
      }
      transition-colors
    `}>
      {popular && (
        <div className="absolute -top-3 left-1/2 -translate-x-1/2 px-3 py-1 rounded-full bg-tiktok-cyan text-black text-xs font-bold">
          MOST POPULAR
        </div>
      )}
      
      <h3 className="text-lg font-semibold mb-2">{name}</h3>
      <div className="text-3xl font-bold mb-4">
        ${price}
        <span className="text-lg text-white/60">/mo</span>
      </div>
      
      <ul className={`space-y-2 text-sm mb-6 ${popular ? 'text-white/80' : 'text-white/60'}`}>
        {features.map((feature, index) => (
          <li key={index} className="flex items-center gap-2">
            <Check className="w-4 h-4 text-tiktok-cyan flex-shrink-0" />
            <span>{feature}</span>
          </li>
        ))}
      </ul>
      
      <button
        onClick={handleCheckout}
        disabled={isLoading}
        className={`
          w-full py-2 rounded-full font-semibold transition-all
          ${popular
            ? 'bg-gradient-to-r from-tiktok-cyan to-tiktok-purple hover:scale-105'
            : 'bg-white/10 hover:bg-white/20'
          }
          disabled:opacity-50 disabled:cursor-not-allowed
        `}
      >
        {isLoading ? (
          <span className="flex items-center justify-center gap-2">
            <div className="w-4 h-4 border-2 border-white/20 border-t-white rounded-full animate-spin" />
            Loading...
          </span>
        ) : (
          popular ? 'Start Free Trial' : 'Get Started'
        )}
      </button>
    </div>
  );
}