'use client';

import { useState, useEffect } from "react";
import { triggerSendConfirmationEmail, triggerUserOnboarding } from "./actions";

type Toast = {
  id: number;
  message: string;
  type: 'success' | 'error';
};

export default function Home() {
  const [newsletterLoading, setNewsletterLoading] = useState(false);
  const [joinLoading, setJoinLoading] = useState(false);
  const [email, setEmail] = useState('');
  const [joinEmail, setJoinEmail] = useState('');
  const [joinPassword, setJoinPassword] = useState('');
  const [toasts, setToasts] = useState<Toast[]>([]);

  const addToast = (message: string, type: 'success' | 'error') => {
    const id = Date.now();
    setToasts(prev => [...prev, { id, message, type }]);
    setTimeout(() => {
      setToasts(prev => prev.filter(toast => toast.id !== id));
    }, 5000);
  };

  const removeToast = (id: number) => {
    setToasts(prev => prev.filter(toast => toast.id !== id));
  };

  const handleNewsletterSignup = async () => {
    if (!email || !email.includes('@')) {
      addToast('Please enter a valid email address', 'error');
      return;
    }

    setNewsletterLoading(true);
    
    const response = await triggerSendConfirmationEmail(email);
    addToast(
      response.success ? response.message! : response.error!,
      response.success ? 'success' : 'error'
    );
    
    if (response.success) {
      setEmail('');
    }
    
    setNewsletterLoading(false);
  };

  const handleJoin = async () => {
    if (!joinEmail || !joinEmail.includes('@')) {
      addToast('Please enter a valid email address', 'error');
      return;
    }
    
    if (!joinPassword || joinPassword.length < 6) {
      addToast('Password must be at least 6 characters long', 'error');
      return;
    }

    setJoinLoading(true);
    
    const response = await triggerUserOnboarding();
    addToast(
      response.success ? response.message! : response.error!,
      response.success ? 'success' : 'error'
    );
    
    if (response.success) {
      setJoinEmail('');
      setJoinPassword('');
    }
    
    setJoinLoading(false);
  };

  return (
    <div className="font-sans flex items-center justify-center min-h-screen p-8 bg-gray-50 dark:bg-gray-900">
      <main className="flex flex-col gap-8 items-center max-w-4xl w-full">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-900 dark:text-white mb-2">Hyrex Next.js Demo</h1>
          <p className="text-gray-600 dark:text-gray-400">Get started with our platform</p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-20 w-full max-w-4xl">
          {/* Newsletter Signup */}
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6 h-fit">
            <h3 className="text-xl font-semibold mb-3 text-gray-900 dark:text-white">📧 Newsletter</h3>
            <p className="text-gray-600 dark:text-gray-400 mb-6 text-sm">
              Stay updated with our latest news and features
            </p>
            
            <div className="space-y-4">
              <input
                type="email"
                placeholder="Enter your email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500 dark:bg-gray-700 dark:text-white"
                onKeyDown={(e) => e.key === 'Enter' && handleNewsletterSignup()}
              />
              
              <button
                onClick={handleNewsletterSignup}
                disabled={newsletterLoading}
                className="w-full bg-green-600 text-white py-2 px-4 rounded-md hover:bg-green-700 transition-colors font-medium disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {newsletterLoading ? "Subscribing..." : "Subscribe to Newsletter"}
              </button>
            </div>
          </div>

          {/* Join/Onboarding */}
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6">
            <h3 className="text-xl font-semibold mb-4 text-gray-900 dark:text-white">🚀 Join Us</h3>
            <p className="text-gray-600 dark:text-gray-400 mb-4 text-sm">
              Create your account and begin your journey with our onboarding process
            </p>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Email
                </label>
                <input
                  type="email"
                  placeholder="Enter your email"
                  value={joinEmail}
                  onChange={(e) => setJoinEmail(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500 dark:bg-gray-700 dark:text-white"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Password
                </label>
                <input
                  type="password"
                  placeholder="Create a password (min 6 characters)"
                  value={joinPassword}
                  onChange={(e) => setJoinPassword(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500 dark:bg-gray-700 dark:text-white"
                  onKeyDown={(e) => e.key === 'Enter' && handleJoin()}
                />
              </div>
              
              <button
                onClick={handleJoin}
                disabled={joinLoading}
                className="w-full bg-purple-600 text-white py-2 px-4 rounded-md hover:bg-purple-700 transition-colors font-medium disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {joinLoading ? "Starting Onboarding..." : "Join & Start Onboarding"}
              </button>
            </div>
          </div>
        </div>
      </main>
      
      {/* Toast Container */}
      <div className="fixed top-4 right-4 z-50 space-y-2">
        {toasts.map((toast) => (
          <div
            key={toast.id}
            className={`max-w-sm px-4 py-3 rounded-lg shadow-lg transition-all duration-300 ease-in-out transform translate-x-0 ${
              toast.type === 'success'
                ? 'bg-green-500 text-white'
                : 'bg-red-500 text-white'
            }`}
          >
            <div className="flex justify-between items-center">
              <span className="text-sm font-medium">{toast.message}</span>
              <button
                onClick={() => removeToast(toast.id)}
                className="ml-2 text-white hover:text-gray-200 focus:outline-none"
              >
                ✕
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
