import { useState } from 'react';
import { MessageSquare, LayoutDashboard, Settings, Github } from 'lucide-react';
import Chat from './components/Chat';
import Dashboard from './components/Dashboard';

export default function App() {
  const [activeTab, setActiveTab] = useState<'chat' | 'dashboard'>('chat');

  return (
    <div className="h-screen flex transition-colors duration-300 bg-zinc-950 text-zinc-200 overflow-hidden">
      {/* Sidebar */}
      <aside className="w-20 lg:w-64 bg-zinc-900 border-r border-zinc-800 flex flex-col shrink-0">
        <div className="p-6 flex items-center gap-3">
          <div className="w-8 h-8 bg-emerald-500 rounded-lg flex items-center justify-center shrink-0">
            <MessageSquare className="text-white w-5 h-5" />
          </div>
          <span className="text-white font-bold text-xl hidden lg:block tracking-tight">ChatHub</span>
        </div>

        <nav className="flex-1 px-3 space-y-2 mt-4">
          <NavItem 
            active={activeTab === 'chat'} 
            onClick={() => setActiveTab('chat')}
            icon={<MessageSquare className="w-5 h-5" />}
            label="AI Chat"
          />
          <NavItem 
            active={activeTab === 'dashboard'} 
            onClick={() => setActiveTab('dashboard')}
            icon={<LayoutDashboard className="w-5 h-5" />}
            label="Dashboard"
          />
        </nav>

        <div className="p-4 border-t border-zinc-800 space-y-2">
          <NavItem 
            icon={<Settings className="w-5 h-5" />}
            label="Settings"
          />
          <div className="hidden lg:block p-4 bg-zinc-800/50 rounded-xl mt-4">
            <p className="text-[10px] text-zinc-500 uppercase font-bold tracking-widest mb-2">Project Info</p>
            <div className="flex items-center gap-2 text-zinc-400 hover:text-white transition-colors cursor-pointer">
              <Github className="w-4 h-4" />
              <span className="text-xs font-medium">Source Code</span>
            </div>
          </div>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 flex flex-col overflow-hidden">
        {activeTab !== 'chat' && (
          <header className="h-16 border-b flex items-center justify-between px-8 shrink-0 transition-colors bg-zinc-900 border-zinc-800">
            <h2 className="font-semibold text-white">
              System Analytics
            </h2>
            <div className="flex items-center gap-4">
              <div className="w-8 h-8 rounded-full bg-zinc-700 border border-zinc-600" />
            </div>
          </header>
        )}

        <div className={`flex-1 overflow-hidden ${activeTab === 'chat' ? '' : 'p-8 overflow-y-auto'}`}>
          {activeTab === 'chat' ? <Chat /> : <Dashboard />}
        </div>
      </main>
    </div>
  );
}

function NavItem({ active, onClick, icon, label }: any) {
  return (
    <button
      onClick={onClick}
      className={`w-full flex items-center gap-3 px-4 py-3 rounded-xl transition-all group ${
        active 
          ? 'bg-emerald-500 text-white shadow-lg shadow-emerald-500/20' 
          : 'text-zinc-400 hover:bg-zinc-800 hover:text-zinc-200'
      }`}
    >
      <span className="shrink-0">{icon}</span>
      <span className="font-medium text-sm hidden lg:block">{label}</span>
    </button>
  );
}
