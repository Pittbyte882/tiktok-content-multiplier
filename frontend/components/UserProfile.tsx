'use client';

import { useAuthStore } from '@/lib/authStore';
import { LogOut, User, CreditCard } from 'lucide-react';
import { useRouter } from 'next/navigation';

export default function UserProfile() {
  const router = useRouter();
  const { user, logout } = useAuthStore();

  if (!user) return null;

  const handleLogout = () => {
    logout();
    router.push('/');
  };

  return (
    <div className="relative group">
      <button className="flex items-center gap-2 px-4 py-2 rounded-full bg-white/10 hover:bg-white/20 transition-colors border border-white/10">
        <User className="w-4 h-4" />
        <span className="hidden md:inline">{user.email}</span>
      </button>

      {/* Dropdown */}
      <div className="absolute right-0 top-full mt-2 w-64 bg-dark-surface border border-white/10 rounded-2xl p-4 opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all">
        
        {/* User Info */}
        <div className="pb-3 border-b border-white/10 mb-3">
          <p className="text-white font-semibold truncate">{user.email}</p>
          <p className="text-xs text-white/60 capitalize mt-1">{user.subscription_tier} Plan</p>
        </div>

        {/* Credits */}
        <div className="flex items-center gap-2 mb-3 p-3 rounded-xl bg-tiktok-cyan/10">
          <CreditCard className="w-4 h-4 text-tiktok-cyan" />
          <div>
            <p className="text-xs text-white/60">Credits Remaining</p>
            <p className="text-lg font-bold text-white">{user.credits_remaining}</p>
          </div>
        </div>

        {/* Logout Button */}
        <button
          onClick={handleLogout}
          className="w-full flex items-center gap-2 px-4 py-2 rounded-xl bg-red-500/10 hover:bg-red-500/20 text-red-400 transition-colors"
        >
          <LogOut className="w-4 h-4" />
          <span>Log Out</span>
        </button>
      </div>
    </div>
  );
}