/**
 * FinVerse AI — Zustand State Store
 * Central state management for the entire app.
 */

import { create } from 'zustand';

const useAppStore = create((set, get) => ({
    // ── Navigation ────────────────────────
    activeView: 'dashboard', // 'dashboard', 'transactions', 'agents', 'settings'
    setActiveView: (view) => set({ activeView: view }),

    // ── Chat ──────────────────────────────
    messages: [
        {
            id: 'welcome',
            role: 'assistant',
            content: `Welcome to **FinVerse AI** 🏦\n\nI'm your intelligent financial operating system. I can:\n\n• 📊 Analyze your spending patterns\n• 💰 Check your budget health\n• 🛡️ Validate compliance\n• 🔍 Search for the best deals (visible mode)\n• 📚 Look up financial policies\n\nTry asking:\n- "Analyze my recent spending"\n- "Can I afford an iPhone 15?"\n- "Find me the best deal on a laptop"\n- "What are the AML compliance rules?"`,
            timestamp: new Date().toISOString(),
        }
    ],
    isProcessing: false,

    addMessage: (message) => set((state) => ({
        messages: [...state.messages, { ...message, id: Date.now().toString(), timestamp: new Date().toISOString() }]
    })),

    setProcessing: (val) => set({ isProcessing: val }),

    // ── Agent Events ──────────────────────
    currentEvents: [],
    addEvent: (event) => set((state) => ({
        currentEvents: [...state.currentEvents, event]
    })),
    clearEvents: () => set({ currentEvents: [] }),

    // ── Avatar State ──────────────────────
    avatarState: 'idle', // idle, thinking, searching, analyzing, alert, recommending
    setAvatarState: (state) => set({ avatarState: state }),

    // ── Transactions ──────────────────────
    transactions: [],
    setTransactions: (txns) => set({ transactions: txns }),

    // ── Financial Summary ─────────────────
    financialSummary: null,
    setFinancialSummary: (summary) => set({ financialSummary: summary }),

    // ── Agent Activity Log ────────────────
    agentLog: [],
    addAgentLog: (entry) => set((state) => ({
        agentLog: [...state.agentLog.slice(-50), entry] // Keep last 50
    })),
}));

export default useAppStore;
