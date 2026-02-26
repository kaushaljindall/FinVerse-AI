/**
 * FinVerse AI — Main App Component
 * Assembles sidebar, header, dashboard, 3D avatar, and chat.
 */

import React, { Suspense } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import Sidebar from './components/Sidebar/Sidebar';
import Dashboard from './components/Dashboard/Dashboard';
import ChatInterface from './components/Chat/ChatInterface';
import FinVerseAvatar from './components/Avatar/FinVerseAvatar';
import useAppStore from './store/appStore';

function LoadingFallback() {
    return (
        <div style={{
            width: '100%',
            height: '200px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            background: 'radial-gradient(ellipse at center, rgba(108, 92, 231, 0.05) 0%, transparent 70%)',
        }}>
            <div className="loading-spinner" />
        </div>
    );
}

export default function App() {
    const { activeView } = useAppStore();

    return (
        <div className="app-layout">
            {/* Sidebar Navigation */}
            <Sidebar />

            {/* Main Content Area */}
            <div className="main-content">
                <div className="content-area chat-active">
                    {/* Header */}
                    <header className="header">
                        <div className="header-title">
                            <h1>FinVerse AI</h1>
                            <span>v1.0 • Agentic Financial OS</span>
                        </div>
                        <div className="header-status">
                            <div className="status-indicator">
                                <div className="status-dot" />
                                <span>6 Agents Active</span>
                            </div>
                            <div className="status-indicator">
                                <span style={{ fontSize: 14 }}>🧠</span>
                                <span>Multi-LLM Fallback</span>
                            </div>
                        </div>
                    </header>

                    {/* Dashboard Panel */}
                    <div className="dashboard">
                        <AnimatePresence mode="wait">
                            <motion.div
                                key={activeView}
                                initial={{ opacity: 0, y: 10 }}
                                animate={{ opacity: 1, y: 0 }}
                                exit={{ opacity: 0, y: -10 }}
                                transition={{ duration: 0.2 }}
                                style={{ height: '100%' }}
                            >
                                <Dashboard />
                            </motion.div>
                        </AnimatePresence>
                    </div>

                    {/* Right Panel: Avatar + Chat */}
                    <div className="chat-panel" style={{ display: 'flex', flexDirection: 'column' }}>
                        {/* 3D Avatar */}
                        <Suspense fallback={<LoadingFallback />}>
                            <FinVerseAvatar />
                        </Suspense>

                        {/* Chat Interface */}
                        <div style={{ flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
                            <ChatInterface />
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
