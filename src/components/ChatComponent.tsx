"use client";

import { CopilotChat } from "@copilotkit/react-ui";
import "@copilotkit/react-ui/styles.css";

export default function ChatComponent() {
  return (
    <div className="h-screen w-full bg-gray-50">
      {/* Simple Header */}
      <div className="bg-white border-b border-gray-200 px-6 py-4">
        <div className="flex items-center justify-center">
          <h1 className="text-2xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
            🤖 Kubernetes Agentic Chat
          </h1>
        </div>
        <p className="text-center text-sm text-gray-600 mt-1">
          Powered by <span className="font-medium text-blue-600">BDVN Infra Team</span>
        </p>
      </div>

      {/* Full-Screen Chat Interface */}
      <div className="h-[calc(100vh-100px)] p-4">
        <div className="h-full max-w-4xl mx-auto bg-white rounded-lg shadow-lg">
          <CopilotChat
            instructions="You are a helpful AI assistant to chat with your Kubernetes cluster. You have access to Kubernetes operations and can help users manage their clusters, troubleshoot issues, check resource status, and provide insights about their deployments, pods, services, and more. Be helpful, clear, and provide actionable guidance for Kubernetes operations."
            labels={{
              title: "☸️ Kubernetes Assistant",
              initial: "Hi! 👋 I'm your Kubernetes AI assistant.\n\nI can help you with:\n• Cluster status and health checks\n• Pod and deployment management\n• Service and networking issues\n• Resource monitoring and scaling\n• Troubleshooting and logs analysis\n• Best practices and recommendations\n\nAsk me anything about your Kubernetes cluster!",
            }}
            className="h-full"
          />
        </div>
      </div>
    </div>
  );
}