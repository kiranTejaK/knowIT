import React, { useState, useRef, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiRequest } from '../lib/api';
import { Navbar } from '../components/Navbar';
import { MarkdownRenderer } from '../components/MarkdownRenderer';
import {
  Send,
  Sparkles,
  Bot,
  User as UserIcon,
  ArrowLeft,
  BookOpen,
  Zap,
  CheckCircle2,
} from 'lucide-react';

interface Citation {
  document_id: string;
  chunk_id: string;
  page_number: number;
  content_snippet: string;
  similarity_score: number;
}

interface MessageItem {
  id: string;
  chat_id: string;
  role: 'user' | 'assistant';
  content: string;
  citations?: Citation[];
  token_count: number;
  latency_ms?: number;
  created_at: string;
}

interface ChatDetail {
  id: string;
  title: string;
  collection_id: string;
  model: string;
}

export const ChatView: React.FC = () => {
  const { chatId } = useParams<{ chatId: string }>();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const [input, setInput] = useState('');
  const [activeCitations, setActiveCitations] = useState<Citation[] | null>(null);

  // Fetch Chat Metadata
  const { data: chat } = useQuery<ChatDetail>({
    queryKey: ['chat', chatId],
    queryFn: () => apiRequest<ChatDetail>(`/chats/${chatId}`),
    enabled: !!chatId,
  });

  // Fetch Chat Messages
  const { data: paginatedMessages, isLoading: messagesLoading } = useQuery<{ items: MessageItem[] }>({
    queryKey: ['messages', chatId],
    queryFn: () => apiRequest<{ items: MessageItem[] }>(`/chats/${chatId}/messages`),
    enabled: !!chatId,
  });

  const messages = paginatedMessages?.items || [];

  // Scroll to bottom on new message
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Send Message Mutation
  const sendMessageMutation = useMutation({
    mutationFn: (text: string) =>
      apiRequest<MessageItem>(`/chats/${chatId}/messages`, {
        method: 'POST',
        body: JSON.stringify({ content: text, top_k: 5 }),
      }),
    onSuccess: () => {
      setInput('');
      queryClient.invalidateQueries({ queryKey: ['messages', chatId] });
    },
  });

  const handleSend = (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || sendMessageMutation.isPending) return;
    sendMessageMutation.mutate(input.trim());
  };

  return (
    <div className="min-h-screen bg-[#0b0f19] text-slate-100 flex flex-col">
      <Navbar />

      <div className="flex-1 flex max-w-7xl w-full mx-auto p-6 gap-6 overflow-hidden">
        {/* Main Chat Area */}
        <div className="flex-1 flex flex-col glass-panel rounded-2xl border border-slate-800 overflow-hidden">
          {/* Header */}
          <div className="h-16 px-6 border-b border-slate-800 flex items-center justify-between bg-slate-900/60">
            <div className="flex items-center gap-3">
              <button
                onClick={() => navigate('/')}
                className="p-2 rounded-xl bg-slate-800 text-slate-400 hover:text-white transition-colors"
              >
                <ArrowLeft className="h-4 w-4" />
              </button>
              <div>
                <h2 className="text-base font-semibold text-slate-100">{chat?.title || 'RAG Chat Session'}</h2>
                <p className="text-xs text-slate-500">Model: {chat?.model || 'openai/gpt-oss-20b'}</p>
              </div>
            </div>

            <div className="flex items-center gap-2">
              <span className="text-xs px-2.5 py-1 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 font-medium flex items-center gap-1">
                <CheckCircle2 className="h-3 w-3" /> Grounded RAG Active
              </span>
            </div>
          </div>

          {/* Message List */}
          <div className="flex-1 p-6 overflow-y-auto space-y-6">
            {messagesLoading ? (
              <div className="text-center py-12 text-sm text-slate-500">Loading conversation history...</div>
            ) : messages.length === 0 ? (
              <div className="text-center py-16">
                <div className="h-12 w-12 rounded-2xl bg-indigo-600/20 text-indigo-400 flex items-center justify-center mx-auto mb-3">
                  <Sparkles className="h-6 w-6" />
                </div>
                <h3 className="text-base font-semibold text-slate-200">Start the Conversation</h3>
                <p className="text-xs text-slate-400 mt-1 max-w-sm mx-auto">
                  Ask any question about your uploaded collection documents. RAG will retrieve relevant passages and generate grounded answers.
                </p>
              </div>
            ) : (
              messages.map((msg) => (
                <div
                  key={msg.id}
                  className={`flex gap-4 ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
                >
                  {msg.role === 'assistant' && (
                    <div className="h-9 w-9 rounded-xl bg-indigo-600/20 border border-indigo-500/30 text-indigo-400 flex items-center justify-center shrink-0 mt-0.5">
                      <Bot className="h-5 w-5" />
                    </div>
                  )}

                  <div
                    className={`rounded-2xl p-5 border ${
                      msg.role === 'user'
                        ? 'max-w-2xl bg-indigo-600 text-white border-indigo-500 shadow-md shadow-indigo-600/20'
                        : 'max-w-3xl lg:max-w-4xl w-full bg-slate-900/90 text-slate-200 border-slate-800/90 shadow-sm overflow-hidden'
                    }`}
                  >
                    {msg.role === 'user' ? (
                      <p className="text-sm whitespace-pre-wrap leading-relaxed">{msg.content}</p>
                    ) : (
                      <MarkdownRenderer content={msg.content} />
                    )}

                    {/* Citations & Metrics for Assistant */}
                    {msg.role === 'assistant' && (
                      <div className="mt-4 pt-3 border-t border-slate-800/80 flex items-center justify-between text-xs text-slate-400">
                        {msg.citations && msg.citations.length > 0 ? (
                          <button
                            onClick={() => setActiveCitations(msg.citations || null)}
                            className="flex items-center gap-1.5 text-indigo-400 hover:text-indigo-300 font-medium"
                          >
                            <BookOpen className="h-3.5 w-3.5" />
                            <span>{msg.citations.length} Citations</span>
                          </button>
                        ) : (
                          <span className="text-slate-500">No citations</span>
                        )}

                        <div className="flex items-center gap-3 text-slate-500">
                          {msg.latency_ms && (
                            <span className="flex items-center gap-1">
                              <Zap className="h-3 w-3 text-amber-400" /> {msg.latency_ms} ms
                            </span>
                          )}
                          <span>{msg.token_count} tokens</span>
                        </div>
                      </div>
                    )}
                  </div>

                  {msg.role === 'user' && (
                    <div className="h-9 w-9 rounded-xl bg-slate-800 border border-slate-700 text-slate-300 flex items-center justify-center shrink-0 mt-0.5">
                      <UserIcon className="h-5 w-5" />
                    </div>
                  )}
                </div>
              ))
            )}

            {sendMessageMutation.isPending && (
              <div className="flex gap-4">
                <div className="h-9 w-9 rounded-xl bg-indigo-600/20 text-indigo-400 flex items-center justify-center shrink-0 animate-pulse">
                  <Bot className="h-5 w-5" />
                </div>
                <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-4 text-xs text-indigo-400 flex items-center gap-2">
                  <Sparkles className="h-4 w-4 animate-spin" />
                  <span>Searching PGVector & Generating grounded response...</span>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Prompt Input Form */}
          <div className="p-4 border-t border-slate-800 bg-slate-900/40">
            <form onSubmit={handleSend} className="flex gap-3">
              <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder="Ask a question about your knowledge collection..."
                className="flex-1 px-4 py-3 bg-slate-900 border border-slate-800 rounded-xl text-sm text-slate-200 placeholder-slate-500 focus:outline-none focus:border-indigo-500"
              />
              <button
                type="submit"
                disabled={!input.trim() || sendMessageMutation.isPending}
                className="px-5 py-3 bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl transition-all shadow-lg shadow-indigo-600/30 disabled:opacity-50 flex items-center gap-2 font-medium text-sm"
              >
                <span>Send</span>
                <Send className="h-4 w-4" />
              </button>
            </form>
          </div>
        </div>

        {/* Citations Side Drawer */}
        {activeCitations && (
          <div className="w-80 glass-panel rounded-2xl border border-slate-800 p-5 flex flex-col">
            <div className="flex items-center justify-between mb-4 border-b border-slate-800 pb-3">
              <h3 className="text-sm font-semibold text-slate-200 flex items-center gap-2">
                <BookOpen className="h-4 w-4 text-indigo-400" />
                <span>Source Citations</span>
              </h3>
              <button
                onClick={() => setActiveCitations(null)}
                className="text-xs text-slate-500 hover:text-slate-300"
              >
                Close
              </button>
            </div>

            <div className="flex-1 overflow-y-auto space-y-3">
              {activeCitations.map((cite, idx) => (
                <div key={idx} className="p-3.5 rounded-xl bg-slate-900/60 border border-slate-800 text-xs space-y-2">
                  <div className="flex items-center justify-between text-slate-400">
                    <span className="font-semibold text-indigo-400">Page {cite.page_number}</span>
                    <span className="bg-indigo-500/10 text-indigo-300 px-2 py-0.5 rounded border border-indigo-500/20 font-mono">
                      {(cite.similarity_score * 100).toFixed(1)}% Match
                    </span>
                  </div>
                  <p className="text-slate-300 italic leading-relaxed">"{cite.content_snippet}"</p>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
