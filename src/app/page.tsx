"use client";

import { useState, useEffect } from "react";
import dynamic from "next/dynamic";

// Dynamically import the chat component with SSR disabled
const ChatComponent = dynamic(() => import("../components/ChatComponent"), {
  ssr: false,
  loading: () => (
    <div className="h-screen w-full bg-gray-50 flex items-center justify-center">
      <div className="flex flex-col items-center gap-4">
        <div className="animate-spin h-8 w-8 border-2 border-blue-500 border-t-transparent rounded-full"></div>
        <h1 className="text-2xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
          🤖 Agentic Chat for Kubernetes
        </h1>
        <p className="text-gray-600">Initializing AI assistant...</p>
      </div>
    </div>
  ),
});

export default function AgenticChatPage() {
  return <ChatComponent />;
}