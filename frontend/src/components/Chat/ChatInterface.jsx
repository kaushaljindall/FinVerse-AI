/**
 * FinVerse AI — Chat Interface
 * Conversational UI with agent event streaming and visible search display.
 */

import React, { useState, useRef, useEffect, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import useAppStore from '../../store/appStore';

export default function ChatInterface() {
    const [input, setInput] = useState('');
    const messagesEndRef = useRef(null);
    const inputRef = useRef(null);

    const { messages, isProcessing, addMessage, setProcessing, addEvent, setAvatarState, clearEvents, currentEvents } = useAppStore();

    const scrollToBottom = useCallback(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, []);

    useEffect(() => {
        scrollToBottom();
    }, [messages, currentEvents, scrollToBottom]);

    const handleSend = async () => {
        if (!input.trim() || isProcessing) return;

        const userMessage = input.trim();
        setInput('');
        addMessage({ role: 'user', content: userMessage });
        setProcessing(true);
        setAvatarState('thinking');
        clearEvents();

        try {
            const response = await fetch('/api/chat/query', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ query: userMessage, stream: true }),
            });

            if (!response.ok) throw new Error('API request failed');

            const reader = response.body.getReader();
            const decoder = new TextDecoder();
            let buffer = '';

            while (true) {
                const { done, value } = await reader.read();
                if (done) break;

                buffer += decoder.decode(value, { stream: true });
                const lines = buffer.split('\n');
                buffer = lines.pop() || '';

                for (const line of lines) {
                    if (line.startsWith('data: ')) {
                        const data = line.slice(6).trim();
                        if (data === '[DONE]') continue;

                        try {
                            const event = JSON.parse(data);

                            // Update avatar state
                            if (event.avatar_state) {
                                setAvatarState(event.avatar_state);
                            }

                            // Add event to stream
                            addEvent(event);

                            // If this is the final response, add it as a message
                            if (event.type === 'final' && event.content) {
                                addMessage({
                                    role: 'assistant',
                                    content: event.content.response || 'Processing complete.',
                                    agents: event.content.agents_used || [],
                                    citations: event.content.citations || [],
                                    processingTime: event.content.processing_time || 0,
                                });
                            }
                        } catch (e) {
                            // Skip malformed JSON
                        }
                    }
                }
            }
        } catch (error) {
            console.error('Chat error:', error);
            addMessage({
                role: 'assistant',
                content: `I apologize, but I encountered an error while processing your request. Please ensure the backend server is running at http://localhost:8000.\n\nError: ${error.message}`,
            });
        } finally {
            setProcessing(false);
            setAvatarState('idle');
        }
    };

    const handleKeyDown = (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSend();
        }
    };

    return (
        <div className="chat-panel">
            <div className="chat-header">
                <div className="chat-avatar-mini">🧠</div>
                <div className="chat-header-info">
                    <h3>FinVerse AI</h3>
                    <p>{isProcessing ? 'Processing...' : 'Online'}</p>
                </div>
            </div>

            <div className="chat-messages">
                <AnimatePresence>
                    {messages.map((msg) => (
                        <motion.div
                            key={msg.id}
                            className={`chat-message ${msg.role}`}
                            initial={{ opacity: 0, y: 10 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ duration: 0.3 }}
                        >
                            <div className="chat-message-avatar">
                                {msg.role === 'assistant' ? '🧠' : '👤'}
                            </div>
                            <div className="chat-message-bubble">
                                <MessageContent content={msg.content} />
                                {msg.agents && msg.agents.length > 0 && (
                                    <div style={{ marginTop: 8, fontSize: 10, opacity: 0.6 }}>
                                        Agents: {msg.agents.join(', ')} • {msg.processingTime}s
                                    </div>
                                )}
                            </div>
                        </motion.div>
                    ))}
                </AnimatePresence>

                {/* Streaming agent events */}
                {isProcessing && currentEvents.length > 0 && (
                    <div className="agent-events-stream">
                        {currentEvents.slice(-8).map((event, i) => (
                            <AgentEventCard key={i} event={event} />
                        ))}
                    </div>
                )}

                {/* Typing indicator */}
                {isProcessing && (
                    <div className="chat-message assistant">
                        <div className="chat-message-avatar">🧠</div>
                        <div className="typing-indicator">
                            <div className="typing-dot" />
                            <div className="typing-dot" />
                            <div className="typing-dot" />
                        </div>
                    </div>
                )}

                <div ref={messagesEndRef} />
            </div>

            <div className="chat-input-area">
                <div className="chat-input-container">
                    <input
                        ref={inputRef}
                        type="text"
                        className="chat-input"
                        placeholder="Ask FinVerse AI anything..."
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        onKeyDown={handleKeyDown}
                        disabled={isProcessing}
                        id="chat-input"
                    />
                    <button
                        className="chat-send-btn"
                        onClick={handleSend}
                        disabled={!input.trim() || isProcessing}
                        id="chat-send"
                    >
                        ➤
                    </button>
                </div>
            </div>
        </div>
    );
}

function MessageContent({ content }) {
    // Simple markdown-like rendering
    const lines = content.split('\n');

    return (
        <div>
            {lines.map((line, i) => {
                // Bold
                let rendered = line.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
                // Inline code
                rendered = rendered.replace(/`(.*?)`/g, '<code style="background:rgba(108,92,231,0.15);padding:1px 4px;border-radius:3px;font-family:var(--font-mono);font-size:11px">$1</code>');
                // Bullet points
                if (rendered.startsWith('• ') || rendered.startsWith('- ')) {
                    rendered = '  ' + rendered;
                }

                return (
                    <span key={i}>
                        <span dangerouslySetInnerHTML={{ __html: rendered }} />
                        {i < lines.length - 1 && <br />}
                    </span>
                );
            })}
        </div>
    );
}

function AgentEventCard({ event }) {
    const getIcon = () => {
        switch (event.type) {
            case 'plan': return '🧠';
            case 'search': return event.content?.icon || '🔎';
            case 'thinking': return '💭';
            case 'tool_call': return '🔧';
            case 'result': return '📊';
            case 'routing': return '🎯';
            case 'error': return '❌';
            default: return '📌';
        }
    };

    return (
        <motion.div
            className={`agent-event ${event.type}`}
            initial={{ opacity: 0, x: -10 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.2 }}
        >
            <div className="agent-event-header">
                <span className="agent-event-icon">{getIcon()}</span>
                <span className="agent-event-type">{event.type}</span>
                {event.agent && <span className="agent-event-agent">• {event.agent}</span>}
            </div>
            <div className="agent-event-content">
                {event.type === 'search' && (
                    <div>
                        <span className="search-query">{event.content?.query}</span>
                        <span style={{ marginLeft: 8, fontSize: 10, color: 'var(--text-muted)' }}>
                            {event.content?.status}
                        </span>
                    </div>
                )}
                {event.type === 'plan' && event.content?.steps && (
                    <ul className="plan-steps">
                        {event.content.steps.map((step, j) => (
                            <li key={j}>{step}</li>
                        ))}
                    </ul>
                )}
                {event.type === 'thinking' && (
                    <span>{event.content?.message}</span>
                )}
                {event.type === 'routing' && (
                    <span>{event.content?.message}</span>
                )}
                {event.type === 'tool_call' && (
                    <span style={{ fontFamily: 'var(--font-mono)', fontSize: 11 }}>
                        {event.content?.tool} → {event.content?.action}
                    </span>
                )}
                {event.type === 'result' && event.type !== 'final' && (
                    <span style={{ fontSize: 11 }}>
                        {event.content?.message || `${event.content?.agent || 'Agent'} completed analysis`}
                    </span>
                )}
            </div>
        </motion.div>
    );
}
