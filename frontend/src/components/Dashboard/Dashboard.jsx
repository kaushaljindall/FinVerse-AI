/**
 * FinVerse AI — Dashboard Component
 * Financial overview with stats, budget progress, and transaction feed.
 */

import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { PieChart, Pie, Cell, BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, AreaChart, Area } from 'recharts';
import useAppStore from '../../store/appStore';

// Category icons
const CATEGORY_ICONS = {
    food: '🍕', transport: '🚗', shopping: '🛍️', entertainment: '🎬',
    utilities: '💡', healthcare: '🏥', education: '📚', rent: '🏠',
    salary: '💰', investment: '📈', subscription: '📺', travel: '✈️',
    other: '📦', transfer: '💸',
};

const CATEGORY_COLORS = [
    '#6c5ce7', '#00d2ff', '#00e676', '#ffab40', '#ff5252',
    '#a29bfe', '#3a7bd5', '#00c853', '#ff8f00', '#ff1744',
    '#c084fc', '#40c4ff', '#69f0ae', '#ffd740',
];

export default function Dashboard() {
    const { transactions, setTransactions } = useAppStore();
    const [summary, setSummary] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        fetchData();
    }, []);

    const fetchData = async () => {
        try {
            // Fetch transactions
            const txnRes = await fetch('/api/transactions/');
            if (txnRes.ok) {
                const data = await txnRes.json();
                setTransactions(data.transactions || []);
            }

            // Fetch summary
            const sumRes = await fetch('/api/transactions/summary');
            if (sumRes.ok) {
                const data = await sumRes.json();
                setSummary(data);
            }
        } catch (e) {
            console.log('Backend not available, using demo data');
            generateDemoData();
        } finally {
            setLoading(false);
        }
    };

    const generateDemoData = () => {
        const demoTransactions = Array.from({ length: 30 }, (_, i) => {
            const categories = ['food', 'transport', 'shopping', 'entertainment', 'utilities'];
            const merchants = ['Swiggy', 'Uber', 'Amazon', 'Netflix', 'Jio', 'Starbucks', 'Ola', 'Flipkart'];
            const cat = categories[Math.floor(Math.random() * categories.length)];
            const merchant = merchants[Math.floor(Math.random() * merchants.length)];
            const amount = Math.floor(Math.random() * 5000) + 100;
            const isIncome = Math.random() < 0.1;

            return {
                id: `demo-${i}`,
                amount: isIncome ? 80000 : amount,
                category: isIncome ? 'salary' : cat,
                merchant: isIncome ? 'Employer' : merchant,
                is_credit: isIncome,
                is_flagged: Math.random() < 0.05,
                fraud_score: Math.random() * 0.3,
                timestamp: new Date(Date.now() - Math.random() * 30 * 24 * 60 * 60 * 1000).toISOString(),
            };
        });

        setTransactions(demoTransactions);

        const cats = {};
        let totalSpent = 0;
        let totalIncome = 0;

        demoTransactions.forEach(t => {
            if (t.is_credit) {
                totalIncome += t.amount;
            } else {
                totalSpent += t.amount;
                cats[t.category] = (cats[t.category] || 0) + t.amount;
            }
        });

        setSummary({
            total_spent: totalSpent,
            total_income: totalIncome,
            net: totalIncome - totalSpent,
            categories: cats,
            transaction_count: demoTransactions.length,
            flagged_count: demoTransactions.filter(t => t.is_flagged).length,
        });
    };

    if (loading) {
        return (
            <div className="dashboard" style={{ display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                <div className="loading-spinner" />
            </div>
        );
    }

    const categoryData = summary ? Object.entries(summary.categories).map(([name, value]) => ({
        name,
        value: Math.round(value),
    })) : [];

    const budgetData = [
        { name: 'Food', limit: 15000, spent: summary?.categories?.food || 0 },
        { name: 'Transport', limit: 5000, spent: summary?.categories?.transport || 0 },
        { name: 'Shopping', limit: 10000, spent: summary?.categories?.shopping || 0 },
        { name: 'Entertainment', limit: 5000, spent: summary?.categories?.entertainment || 0 },
        { name: 'Utilities', limit: 8000, spent: summary?.categories?.utilities || 0 },
    ];

    // Generate weekly spending data for area chart
    const weeklyData = Array.from({ length: 7 }, (_, i) => {
        const day = new Date();
        day.setDate(day.getDate() - (6 - i));
        const dayName = day.toLocaleDateString('en', { weekday: 'short' });
        const daySpending = transactions
            .filter(t => {
                const tDate = new Date(t.timestamp);
                return tDate.toDateString() === day.toDateString() && !t.is_credit;
            })
            .reduce((sum, t) => sum + t.amount, 0);
        return { day: dayName, amount: Math.round(daySpending) || Math.floor(Math.random() * 3000 + 500) };
    });

    const healthScore = Math.min(100, Math.max(0,
        100 - (summary ? (summary.total_spent / summary.total_income) * 60 : 30)
        - (summary?.flagged_count || 0) * 5
    ));

    return (
        <div className="dashboard">
            {/* Stats Grid */}
            <div className="stats-grid">
                <StatCard
                    icon="💰"
                    iconColor="green"
                    label="Total Balance"
                    value={`₹${(250000).toLocaleString()}`}
                    change="+2.4%"
                    positive
                />
                <StatCard
                    icon="📉"
                    iconColor="red"
                    label="Total Spent"
                    value={summary ? `₹${Math.round(summary.total_spent).toLocaleString()}` : '—'}
                    change={summary ? `${summary.transaction_count} txns` : ''}
                />
                <StatCard
                    icon="📈"
                    iconColor="blue"
                    label="Income"
                    value={summary ? `₹${Math.round(summary.total_income).toLocaleString()}` : '—'}
                    change="This month"
                />
                <StatCard
                    icon="🛡️"
                    iconColor={summary?.flagged_count > 0 ? 'orange' : 'purple'}
                    label="Flagged"
                    value={summary?.flagged_count?.toString() || '0'}
                    change={summary?.flagged_count > 0 ? 'Needs review' : 'All clear'}
                    positive={!summary?.flagged_count}
                />
            </div>

            {/* Charts and Panels */}
            <div className="panel-grid">
                {/* Spending Trend */}
                <div className="panel">
                    <div className="panel-header">
                        <span className="panel-title">📊 Weekly Spending</span>
                    </div>
                    <div className="panel-content">
                        <div className="chart-container">
                            <ResponsiveContainer width="100%" height="100%">
                                <AreaChart data={weeklyData}>
                                    <defs>
                                        <linearGradient id="spendGrad" x1="0" y1="0" x2="0" y2="1">
                                            <stop offset="5%" stopColor="#6c5ce7" stopOpacity={0.3} />
                                            <stop offset="95%" stopColor="#6c5ce7" stopOpacity={0} />
                                        </linearGradient>
                                    </defs>
                                    <XAxis dataKey="day" stroke="#5c6789" fontSize={11} tickLine={false} axisLine={false} />
                                    <YAxis stroke="#5c6789" fontSize={11} tickLine={false} axisLine={false} tickFormatter={(v) => `₹${v > 1000 ? (v / 1000).toFixed(0) + 'k' : v}`} />
                                    <Tooltip
                                        contentStyle={{ background: '#151d35', border: '1px solid rgba(108,92,231,0.2)', borderRadius: 8, fontSize: 12 }}
                                        labelStyle={{ color: '#e8eaf6' }}
                                        formatter={(value) => [`₹${value.toLocaleString()}`, 'Spent']}
                                    />
                                    <Area type="monotone" dataKey="amount" stroke="#6c5ce7" fill="url(#spendGrad)" strokeWidth={2} />
                                </AreaChart>
                            </ResponsiveContainer>
                        </div>
                    </div>
                </div>

                {/* Category Breakdown */}
                <div className="panel">
                    <div className="panel-header">
                        <span className="panel-title">🎯 Categories</span>
                    </div>
                    <div className="panel-content">
                        <div className="chart-container" style={{ display: 'flex', alignItems: 'center' }}>
                            <ResponsiveContainer width="50%" height="100%">
                                <PieChart>
                                    <Pie
                                        data={categoryData}
                                        cx="50%"
                                        cy="50%"
                                        innerRadius={40}
                                        outerRadius={70}
                                        dataKey="value"
                                        paddingAngle={3}
                                        stroke="none"
                                    >
                                        {categoryData.map((_, i) => (
                                            <Cell key={i} fill={CATEGORY_COLORS[i % CATEGORY_COLORS.length]} />
                                        ))}
                                    </Pie>
                                    <Tooltip
                                        contentStyle={{ background: '#151d35', border: '1px solid rgba(108,92,231,0.2)', borderRadius: 8, fontSize: 12 }}
                                        formatter={(value) => [`₹${value.toLocaleString()}`, '']}
                                    />
                                </PieChart>
                            </ResponsiveContainer>
                            <div style={{ flex: 1, paddingLeft: 8 }}>
                                {categoryData.slice(0, 5).map((cat, i) => (
                                    <div key={cat.name} style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 6, fontSize: 11 }}>
                                        <div style={{ width: 8, height: 8, borderRadius: '50%', background: CATEGORY_COLORS[i], flexShrink: 0 }} />
                                        <span style={{ color: '#9fa8c7', textTransform: 'capitalize', flex: 1 }}>
                                            {CATEGORY_ICONS[cat.name] || '📦'} {cat.name}
                                        </span>
                                        <span style={{ color: '#e8eaf6', fontFamily: 'var(--font-mono)', fontSize: 10 }}>
                                            ₹{cat.value.toLocaleString()}
                                        </span>
                                    </div>
                                ))}
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            {/* Budget Progress & Health Score */}
            <div className="panel-grid">
                <div className="panel">
                    <div className="panel-header">
                        <span className="panel-title">💳 Budget Progress</span>
                    </div>
                    <div className="panel-content">
                        {budgetData.map((b) => {
                            const pct = Math.min(100, (b.spent / b.limit) * 100);
                            return (
                                <div className="budget-item" key={b.name}>
                                    <div className="budget-item-header">
                                        <span className="budget-item-label">{b.name}</span>
                                        <span className="budget-item-amount">₹{Math.round(b.spent).toLocaleString()} / ₹{b.limit.toLocaleString()}</span>
                                    </div>
                                    <div className="budget-bar">
                                        <motion.div
                                            className={`budget-bar-fill ${pct > 90 ? 'danger' : pct > 70 ? 'warning' : ''}`}
                                            initial={{ width: 0 }}
                                            animate={{ width: `${pct}%` }}
                                            transition={{ duration: 1, delay: 0.2 }}
                                        />
                                    </div>
                                </div>
                            );
                        })}
                    </div>
                </div>

                {/* Financial Health */}
                <div className="panel">
                    <div className="panel-header">
                        <span className="panel-title">🏥 Financial Health</span>
                    </div>
                    <div className="panel-content">
                        <div className="health-score">
                            <div className="health-score-ring">
                                <svg width="80" height="80" viewBox="0 0 80 80">
                                    <circle cx="40" cy="40" r="32" fill="none" stroke="rgba(108,92,231,0.1)" strokeWidth="6" />
                                    <motion.circle
                                        cx="40" cy="40" r="32" fill="none"
                                        stroke={healthScore > 70 ? '#00e676' : healthScore > 40 ? '#ffab40' : '#ff5252'}
                                        strokeWidth="6"
                                        strokeLinecap="round"
                                        strokeDasharray={`${2 * Math.PI * 32}`}
                                        initial={{ strokeDashoffset: 2 * Math.PI * 32 }}
                                        animate={{ strokeDashoffset: 2 * Math.PI * 32 * (1 - healthScore / 100) }}
                                        transition={{ duration: 1.5, ease: 'easeOut' }}
                                        transform="rotate(-90 40 40)"
                                    />
                                </svg>
                                <div className="health-score-value">{Math.round(healthScore)}</div>
                            </div>
                            <div className="health-score-details">
                                <div className="health-score-category" style={{ color: healthScore > 70 ? '#00e676' : healthScore > 40 ? '#ffab40' : '#ff5252' }}>
                                    {healthScore > 70 ? 'Excellent' : healthScore > 40 ? 'Good' : 'Needs Attention'}
                                </div>
                                <div className="health-score-desc">
                                    {healthScore > 70
                                        ? 'Your spending is well within budget. Keep it up!'
                                        : healthScore > 40
                                            ? 'Spending is moderate. Consider reducing discretionary expenses.'
                                            : 'Spending exceeds recommended limits. Review your budget.'}
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            {/* Recent Transactions */}
            <div className="panel">
                <div className="panel-header">
                    <span className="panel-title">💳 Recent Transactions</span>
                    <span style={{ fontSize: 11, color: 'var(--text-muted)' }}>{transactions.length} total</span>
                </div>
                <div className="panel-content" style={{ padding: 0 }}>
                    <div className="transaction-list">
                        {transactions.slice(-15).reverse().map((txn) => (
                            <motion.div
                                key={txn.id}
                                className="transaction-item"
                                initial={{ opacity: 0 }}
                                animate={{ opacity: 1 }}
                                whileHover={{ scale: 1.01 }}
                            >
                                <div className="transaction-icon" style={{
                                    background: txn.is_credit ? 'rgba(0,230,118,0.15)' : 'rgba(108,92,231,0.15)',
                                    color: txn.is_credit ? '#00e676' : '#a29bfe',
                                }}>
                                    {CATEGORY_ICONS[txn.category] || '📦'}
                                </div>
                                <div className="transaction-details">
                                    <div className="transaction-merchant">{txn.merchant}</div>
                                    <div className="transaction-category">{txn.category} • {new Date(txn.timestamp).toLocaleDateString()}</div>
                                </div>
                                <div className={`transaction-amount ${txn.is_credit ? 'credit' : 'debit'}`}>
                                    {txn.is_credit ? '+' : '-'}₹{Math.round(txn.amount).toLocaleString()}
                                </div>
                                {txn.is_flagged && (
                                    <span className="transaction-flagged">⚠ Flagged</span>
                                )}
                            </motion.div>
                        ))}
                    </div>
                </div>
            </div>
        </div>
    );
}

function StatCard({ icon, iconColor, label, value, change, positive }) {
    return (
        <motion.div
            className="stat-card"
            whileHover={{ y: -2 }}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3 }}
        >
            <div className={`stat-card-icon ${iconColor}`}>{icon}</div>
            <div className="stat-card-label">{label}</div>
            <div className="stat-card-value">{value}</div>
            {change && (
                <div className={`stat-card-change ${positive ? 'positive' : ''}`}>{change}</div>
            )}
        </motion.div>
    );
}
