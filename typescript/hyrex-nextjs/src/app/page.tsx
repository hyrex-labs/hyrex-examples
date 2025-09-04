'use client';

import { useState, useEffect } from "react";
import { triggerHelloWorld, triggerUserOnboarding } from "./actions";

type Toast = {
  id: number;
  message: string;
  type: 'success' | 'error';
};

export default function Home() {
  const [loading, setLoading] = useState(false);
  const [workflowLoading, setWorkflowLoading] = useState(false);
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

  const handleTriggerTask = async () => {
    setLoading(true);
    
    const response = await triggerHelloWorld("Hyrex User");
    addToast(
      response.success ? response.message! : response.error!,
      response.success ? 'success' : 'error'
    );
    setLoading(false);
  };

  const handleTriggerWorkflow = async () => {
    setWorkflowLoading(true);
    
    const response = await triggerUserOnboarding();
    addToast(
      response.success ? response.message! : response.error!,
      response.success ? 'success' : 'error'
    );
    setWorkflowLoading(false);
  };

  return (
    <div className="font-sans flex items-center justify-center min-h-screen p-8">
      <main className="flex flex-col gap-8 items-center max-w-6xl w-full">
        <h1 className="text-4xl font-bold text-center">Hyrex Task Runner</h1>
        
        <div className="w-full max-w-4xl mx-auto">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <section className="border p-4 rounded-lg">
              <h2 className="text-xl font-semibold mb-3">Simple Task</h2>
              <p className="text-center text-gray-600 dark:text-gray-400 mb-4">
                Click the button below to trigger the Hello World task
              </p>

              <button
                onClick={handleTriggerTask}
                disabled={loading}
                className="rounded-full border border-solid border-transparent transition-colors flex items-center justify-center bg-foreground text-background gap-2 hover:bg-[#383838] dark:hover:bg-[#ccc] font-medium text-base h-12 px-8 w-full disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {loading ? "Running..." : "Run Hello World Task"}
              </button>
            </section>

            <section className="border p-4 rounded-lg">
              <h2 className="text-xl font-semibold mb-3">User Onboarding Workflow</h2>
              <p className="text-center text-gray-600 dark:text-gray-400 mb-4">
                Start a complex user onboarding workflow with parallel validations
              </p>

              <button
                onClick={handleTriggerWorkflow}
                disabled={workflowLoading}
                className="rounded-full border border-solid border-transparent transition-colors flex items-center justify-center bg-blue-600 text-white gap-2 hover:bg-blue-700 font-medium text-base h-12 px-8 w-full disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {workflowLoading ? "Starting Workflow..." : "Start User Onboarding"}
              </button>
            </section>
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
