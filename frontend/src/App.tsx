import { useState, useEffect } from 'react';
import { Navbar } from './components/Navbar';
import { ChatPage } from './pages/ChatPage';
import { ResearchDashboard } from './pages/ResearchDashboard';
import { apiClient } from './services/api';

export function App() {
  const [activeTab, setActiveTab] = useState<'chat' | 'dashboard'>('chat');
  const [systemStatus, setSystemStatus] = useState<{
    status: string;
    database: string;
    mcp_mode: string;
  } | null>(null);

  useEffect(() => {
    const checkStatus = async () => {
      try {
        const res = await apiClient.checkHealth();
        setSystemStatus({
          status: res.status,
          database: res.database,
          mcp_mode: res.mcp_mode,
        });
      } catch (e) {
        console.warn('Backend currently offline or unreachable', e);
        setSystemStatus({
          status: 'connecting',
          database: 'pending',
          mcp_mode: 'local',
        });
      }
    };
    checkStatus();
  }, []);

  return (
    <div className="min-h-screen flex flex-col bg-[#07090e] text-slate-100 selection:bg-indigo-500 selection:text-white">
      {/* Top Navigation */}
      <Navbar
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        systemStatus={systemStatus}
      />

      {/* Main Content Area */}
      <main className="flex-1 max-w-7xl w-full mx-auto p-6">
        {activeTab === 'chat' ? <ChatPage /> : <ResearchDashboard />}
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-800/60 py-4 px-6 text-center text-slate-500 text-xs font-mono">
        AI Fabric — Intelligent Closed-Loop AI Orchestration Control Plane (Research Prototype)
      </footer>
    </div>
  );
}

export default App;
