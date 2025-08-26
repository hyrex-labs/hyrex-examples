'use client';

import { useState } from "react";
import { triggerHelloWorld } from "./actions";

export default function Home() {
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<{ success: boolean; message?: string; error?: string } | null>(null);

  const handleTriggerTask = async () => {
    setLoading(true);
    setResult(null);
    
    const response = await triggerHelloWorld("Hyrex User");
    setResult(response);
    setLoading(false);
  };

  return (
    <div className="font-sans flex items-center justify-center min-h-screen p-8">
      <main className="flex flex-col gap-8 items-center max-w-md w-full">
        <h1 className="text-4xl font-bold text-center">Hyrex Task Runner</h1>
        
        <p className="text-center text-gray-600 dark:text-gray-400">
          Click the button below to trigger the Hello World task
        </p>

        <button
          onClick={handleTriggerTask}
          disabled={loading}
          className="rounded-full border border-solid border-transparent transition-colors flex items-center justify-center bg-foreground text-background gap-2 hover:bg-[#383838] dark:hover:bg-[#ccc] font-medium text-base h-12 px-8 w-full sm:w-auto disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {loading ? "Running..." : "Run Hello World Task"}
        </button>
        
        {result && (
          <div className={`p-4 rounded-lg w-full text-center ${result.success ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200' : 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200'}`}>
            {result.success ? result.message : result.error}
          </div>
        )}
      </main>
    </div>
  );
}
