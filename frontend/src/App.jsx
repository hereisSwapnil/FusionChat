import React, { useState, useEffect, useRef } from 'react';
import { Plus, MessageSquare, Send, User, Bot, Trash2, Archive, Edit2, Menu, MoreVertical } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import axios from 'axios';
import './App.css';

const API_BASE = 'http://localhost:8000'; // Adjust if needed

function App() {
  const [chats, setChats] = useState([]);
  const [currentChatId, setCurrentChatId] = useState(null);
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [documents, setDocuments] = useState([]);
  const [loading, setLoading] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [uploadingFile, setUploadingFile] = useState(null); // { name, status: 'uploading' | 'success' | 'error' }
  const [editingId, setEditingId] = useState(null);
  const [editingTitle, setEditingTitle] = useState('');
  const [polling, setPolling] = useState(false);

  const messagesEndRef = useRef(null);
  const fileInputRef = useRef(null);

  const handleFileUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    let chatId = currentChatId;
    if (!chatId) {
      const newChat = await createNewChat(`Doc: ${file.name}`);
      if (!newChat) return;
      chatId = newChat.id;
    }

    setUploading(true);
    setUploadingFile({ name: file.name, status: 'uploading' });

    const formData = new FormData();
    formData.append('file', file);
    formData.append('chat_id', chatId);

    const startTime = Date.now();

    try {
      const response = await axios.post(`${API_BASE}/ingest/file`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });

      // Ensure loader shows for at least 800ms
      const elapsed = Date.now() - startTime;
      const minDisplayTime = 800;
      if (elapsed < minDisplayTime) {
        await new Promise(resolve => setTimeout(resolve, minDisplayTime - elapsed));
      }

      setUploadingFile({ name: file.name, status: 'success' });
      setTimeout(() => setUploadingFile(null), 2000); // Hide after 2 seconds

      setDocuments(prev => [...prev, response.data]);
      startPolling(chatId, response.data.id);
    } catch (err) {
      console.error('Upload failed', err);
      setUploadingFile({ name: file.name, status: 'error' });
      setTimeout(() => setUploadingFile(null), 3000); // Hide after 3 seconds
    } finally {
      setUploading(false);
      e.target.value = '';
    }
  };

  // Fetch chats on mount
  useEffect(() => {
    fetchChats();
  }, []);

  const fetchChats = async () => {
    try {
      const response = await axios.get(`${API_BASE}/chats`);
      setChats(response.data);
    } catch (err) {
      console.error("Failed to fetch chats", err);
    }
  };

  const fetchMessages = async (chatId) => {
    try {
      const response = await axios.get(`${API_BASE}/chats/${chatId}`);
      setMessages(response.data.messages || []);
      setDocuments(response.data.documents || []);

      const hasProcessing = (response.data.documents || []).some(d => d.status === 'processing');
      if (hasProcessing && !polling) {
        startPolling(chatId);
      }
    } catch (err) {
      console.error("Failed to fetch messages", err);
    }
  };

  const startPolling = (chatId) => {
    setPolling(true);
    const interval = setInterval(async () => {
      try {
        const response = await axios.get(`${API_BASE}/chats/${chatId}`);
        const docs = response.data.documents || [];
        setDocuments(docs);
        const stillProcessing = docs.some(d => d.status === 'processing');
        if (!stillProcessing) {
          clearInterval(interval);
          setPolling(false);
        }
      } catch (err) {
        console.error("Polling failed", err);
        clearInterval(interval);
        setPolling(false);
      }
    }, 3000);
  };

  useEffect(() => {
    if (currentChatId) {
      fetchMessages(currentChatId);
    }
  }, [currentChatId]);

  const createNewChat = async (title = "New Conversation") => {
    try {
      if (messages.length === 0 && currentChatId) {
        return;
      }
      const response = await axios.post(`${API_BASE}/chats`, { title });
      const newChat = response.data;
      setChats(prev => [newChat, ...prev]);
      setCurrentChatId(newChat.id);
      setMessages([]);
      return newChat;
    } catch (err) {
      console.error("Failed to create chat", err);
      return null;
    }
  };

  const deleteChat = async (e, chatId) => {
    e.stopPropagation();
    try {
      await axios.delete(`${API_BASE}/chats/${chatId}`);
      setChats(chats.filter(c => c.id !== chatId));
      if (currentChatId === chatId) {
        setCurrentChatId(null);
        setMessages([]);
      }
    } catch (err) {
      console.error("Failed to delete chat", err);
    }
  };

  const archiveChat = async (e, chatId) => {
    e.stopPropagation();
    try {
      await axios.patch(`${API_BASE}/chats/${chatId}`, { status: 'archived' });
      setChats(chats.filter(c => c.id !== chatId));
      if (currentChatId === chatId) {
        setCurrentChatId(null);
        setMessages([]);
      }
    } catch (err) {
      console.error("Failed to archive chat", err);
    }
  };

  const renameChat = async (chatId, newTitle) => {
    try {
      const response = await axios.patch(`${API_BASE}/chats/${chatId}`, { title: newTitle });
      setChats(chats.map(c => c.id === chatId ? response.data : c));
      setEditingId(null);
    } catch (err) {
      console.error("Failed to rename chat", err);
    }
  };


  const handleSendMessage = async (e) => {
    e.preventDefault();
    if (!input.trim()) return;

    let chatId = currentChatId;
    let isNewChat = false;

    if (!chatId) {
      const newChat = await createNewChat(input.slice(0, 30) + (input.length > 30 ? '...' : ''));
      if (!newChat) return;
      chatId = newChat.id;
      isNewChat = true;
    }

    const userMessage = { id: Date.now(), role: 'user', content: input };
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setLoading(true);

    try {
      const response = await axios.post(`${API_BASE}/chats/${chatId}/messages`, {
        content: input,
        role: 'user'
      });
      setMessages(prev => [...prev, response.data]);
    } catch (err) {
      console.error("Failed to send message", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  return (
    <div className="app-container">
      {/* Sidebar */}
      <aside className="sidebar">
        <div className="sidebar-header">
          <button className="new-chat-btn" onClick={() => createNewChat()}>
            <Plus size={18} />
            New Chat
          </button>
        </div>

        <div className="chat-list">
          <AnimatePresence>
            {chats.map(chat => (
              <motion.div
                key={chat.id}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -20 }}
                className={`chat-item ${currentChatId === chat.id ? 'active' : ''} group`}
                onClick={() => setCurrentChatId(chat.id)}
                onDoubleClick={() => {
                  setEditingId(chat.id);
                  setEditingTitle(chat.title);
                }}
              >
                <div className="flex items-center justify-between gap-3 w-full">
                  <div className="flex items-center gap-3 overflow-hidden flex-1">
                    <MessageSquare size={16} className="min-w-icon" />
                    {editingId === chat.id ? (
                      <input
                        autoFocus
                        className="bg-transparent border-none outline-none text-foreground w-full p-0"
                        value={editingTitle}
                        onChange={(e) => setEditingTitle(e.target.value)}
                        onBlur={() => renameChat(chat.id, editingTitle)}
                        onKeyDown={(e) => e.key === 'Enter' && renameChat(chat.id, editingTitle)}
                      />
                    ) : (
                      <span className="truncate" style={{ maxWidth: "150px" }}>{chat.title}</span>
                    )}
                  </div>
                  <div className="flex items-center gap-1 opacity-0 group-hover-opacity-100 transition-opacity"
                    style={{
                      color: "black",
                      opacity: 1
                    }}>
                    <button onClick={(e) => archiveChat(e, chat.id)} className="p-1 hover-text-primary">
                      <Archive size={14} />
                    </button>
                    <button onClick={(e) => deleteChat(e, chat.id)} className="p-1 hover-text-destructive">
                      <Trash2 size={14} />
                    </button>
                  </div>
                </div>
              </motion.div>
            ))}
          </AnimatePresence>
        </div>
      </aside>

      {/* Main Content */}
      <main className="main-content">
        <header className="chat-header">
          <div className="flex items-center gap-2">
            <span className="font-semibold text-lg">FusionChat</span>
            <span className="text-xs px-2 py-0.5 rounded-full bg-primary-soft text-primary">v1.2</span>
          </div>
          <div className="flex items-center gap-2">
            <button className="p-2 hover:bg-accent rounded-md"><MoreVertical size={20} /></button>
          </div>
        </header>

        <div className="messages-container">
          {/* Message Wrapper - Centered */}
          <div className="message-wrapper">
            {messages.length === 0 && documents.length === 0 ? (
              <div className="empty-state">
                <motion.div
                  initial={{ scale: 0.8, opacity: 0 }}
                  animate={{ scale: 1, opacity: 1 }}
                  transition={{ duration: 0.5 }}
                >
                  <h1 className="logo-large">FusionChat</h1>
                  <p className="text-muted-foreground mt-4">How can I help you today?</p>
                </motion.div>
              </div>
            ) : (
              <>
                {/* Show documents inline at the start of conversation */}
                {documents.length > 0 && (
                  <div className="inline-documents">
                    {documents.map(doc => (
                      <div key={doc.id} className={`document-chip-inline ${doc.status}`}>
                        <div className="document-icon">
                          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
                          </svg>
                        </div>
                        <div className="document-info">
                          <span className="document-name">{doc.file_name}</span>
                          <span className="document-status-text">
                            {doc.status === 'processing' && 'Processing...'}
                            {doc.status === 'completed' && 'Ready'}
                            {doc.status === 'failed' && 'Failed'}
                          </span>
                        </div>
                        {doc.status === 'processing' && (
                          <motion.div
                            animate={{ rotate: 360 }}
                            transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
                            className="document-spinner"
                          />
                        )}
                      </div>
                    ))}
                  </div>
                )}

                {/* Messages */}
                {messages.map((msg, idx) => (
                  <div key={idx} className={`message-row ${msg.role === 'user' ? 'user-message' : 'ai-message'}`}>
                    <div className="avatar">
                      {msg.role === 'user' ? <User size={18} /> : <Bot size={18} />}
                    </div>
                    <div className="message-content">
                      {msg.content}
                    </div>
                  </div>
                ))}
              </>
            )}
            {loading && (
              <div className="thinking-bubble">
                <div className="avatar">
                  <Bot size={18} />
                </div>
                <div className="thinking-dots">
                  <div className="thinking-dot"></div>
                  <div className="thinking-dot"></div>
                  <div className="thinking-dot"></div>
                </div>
              </div>
            )}
          </div>

          <div ref={messagesEndRef} />
        </div>

        {/* Upload Loader */}
        {uploadingFile && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            className={`upload-loader ${uploadingFile.status}`}
          >
            <div className="upload-loader-content">
              {uploadingFile.status === 'uploading' && (
                <motion.div
                  animate={{ rotate: 360 }}
                  transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
                  className="upload-spinner"
                />
              )}
              {uploadingFile.status === 'success' && (
                <svg className="upload-icon success" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                </svg>
              )}
              {uploadingFile.status === 'error' && (
                <svg className="upload-icon error" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              )}
              <div className="upload-info">
                <span className="upload-filename">{uploadingFile.name}</span>
                <span className="upload-status-text">
                  {uploadingFile.status === 'uploading' && 'Processing document...'}
                  {uploadingFile.status === 'success' && 'Successfully uploaded!'}
                  {uploadingFile.status === 'error' && 'Upload failed'}
                </span>
              </div>
            </div>
          </motion.div>
        )}

        {/* Input Area - ChatGPT Style */}
        <div className="input-area">
          <div className="input-wrapper">
            <form className="input-container" onSubmit={handleSendMessage}>
              <textarea
                className="message-input"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    handleSendMessage(e);
                  }
                }}
                placeholder="Message FusionChat..."
                rows={1}
              />
              <input
                type="file"
                hidden
                ref={fileInputRef}
                onChange={handleFileUpload}
                accept=".pdf,.txt,.md,.doc,.docx"
              />
              <div className="input-actions">
                <button
                  type="button"
                  className="attach-btn"
                  onClick={() => fileInputRef.current?.click()}
                  title="Attach file"
                >
                  <Plus size={20} />
                </button>
                <button className="send-btn" disabled={!input.trim() || loading || uploading} type="submit">
                  <Send size={18} />
                </button>
              </div>
            </form>
          </div>
        </div>
      </main>
    </div>
  );
}

export default App;
