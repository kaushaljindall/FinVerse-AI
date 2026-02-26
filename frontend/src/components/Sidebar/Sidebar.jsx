/**
 * FinVerse AI — Sidebar Navigation
 */

import React from 'react';
import { motion } from 'framer-motion';
import useAppStore from '../../store/appStore';

const navItems = [
    { id: 'dashboard', icon: '📊', label: 'Dashboard' },
    { id: 'transactions', icon: '💳', label: 'Transactions' },
    { id: 'agents', icon: '🤖', label: 'Agents' },
];

const bottomItems = [
    { id: 'settings', icon: '⚙️', label: 'Settings' },
];

export default function Sidebar() {
    const { activeView, setActiveView } = useAppStore();

    return (
        <nav className="sidebar">
            <motion.div
                className="sidebar-logo"
                whileHover={{ scale: 1.1 }}
                whileTap={{ scale: 0.95 }}
            >
                🏦
            </motion.div>

            {navItems.map((item) => (
                <motion.div
                    key={item.id}
                    className={`sidebar-item ${activeView === item.id ? 'active' : ''}`}
                    onClick={() => setActiveView(item.id)}
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                    title={item.label}
                >
                    {item.icon}
                </motion.div>
            ))}

            <div className="sidebar-divider" />

            <div className="sidebar-spacer" />

            {bottomItems.map((item) => (
                <motion.div
                    key={item.id}
                    className={`sidebar-item ${activeView === item.id ? 'active' : ''}`}
                    onClick={() => setActiveView(item.id)}
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                    title={item.label}
                >
                    {item.icon}
                </motion.div>
            ))}
        </nav>
    );
}
