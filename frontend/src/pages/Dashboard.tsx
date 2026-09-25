import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiRequest } from '../lib/api';
import { Navbar } from '../components/Navbar';
import {
  FolderPlus,
  Upload,
  FileText,
  MessageSquare,
  Trash2,
  Clock,
  CheckCircle2,
  AlertCircle,
  Plus,
  Sparkles,
} from 'lucide-react';
import { useNavigate } from 'react-router-dom';

interface Collection {
  id: string;
  name: string;
  description?: string;
  color?: string;
  created_at: string;
}

interface DocumentItem {
  id: string;
  title: string;
  extension: string;
  file_size: number;
  status: string;
  progress: number;
  total_chunks: number;
  total_pages: number;
  created_at: string;
}

export const Dashboard: React.FC = () => {
  const queryClient = useQueryClient();
  const navigate = useNavigate();

  const [selectedCollection, setSelectedCollection] = useState<Collection | null>(null);
  const [newCollectionName, setNewCollectionName] = useState('');
  const [newCollectionDesc, setNewCollectionDesc] = useState('');
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [uploadFile, setUploadFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);

  // 1. Fetch Collections
  const { data: collections = [], isLoading: collectionsLoading } = useQuery<Collection[]>({
    queryKey: ['collections'],
    queryFn: () => apiRequest<Collection[]>('/collections'),
  });

  // Select first collection by default
  React.useEffect(() => {
    if (collections.length > 0 && !selectedCollection) {
      setSelectedCollection(collections[0]);
    }
  }, [collections, selectedCollection]);

  // 2. Fetch Documents for selected collection
  const { data: documents = [], refetch: refetchDocuments } = useQuery<DocumentItem[]>({
    queryKey: ['documents', selectedCollection?.id],
    queryFn: () => apiRequest<DocumentItem[]>(`/collections/${selectedCollection?.id}/documents`),
    enabled: !!selectedCollection?.id,
    refetchInterval: (query) => {
      // Poll if any document is processing
      const hasProcessing = query.state.data?.some((d) => d.status === 'PROCESSING' || d.status === 'UPLOADING');
      return hasProcessing ? 2000 : false;
    },
  });

  // Create Collection Mutation
  const createCollectionMutation = useMutation({
    mutationFn: (newCol: { name: string; description?: string }) =>
      apiRequest<Collection>('/collections', {
        method: 'POST',
        body: JSON.stringify(newCol),
      }),
    onSuccess: (created) => {
      queryClient.invalidateQueries({ queryKey: ['collections'] });
      setSelectedCollection(created);
      setShowCreateModal(false);
      setNewCollectionName('');
      setNewCollectionDesc('');
    },
  });

  // Create Chat Session
  const createChatMutation = useMutation({
    mutationFn: (collectionId: string) =>
      apiRequest<{ id: string }>('/chats', {
        method: 'POST',
        body: JSON.stringify({ collection_id: collectionId }),
      }),
    onSuccess: (chat) => {
      navigate(`/chats/${chat.id}`);
    },
  });

  // Handle Document Upload
  const handleUpload = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!uploadFile || !selectedCollection) return;

    setUploading(true);
    try {
      const formData = new FormData();
      formData.append('file', uploadFile);

      await apiRequest(`/collections/${selectedCollection.id}/documents`, {
        method: 'POST',
        body: formData,
      });

      setUploadFile(null);
      refetchDocuments();
    } catch (err: any) {
      alert(err.message || 'Upload failed');
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#0b0f19] text-slate-100 flex flex-col">
      <Navbar />

      <div className="flex-1 flex max-w-7xl w-full mx-auto p-6 gap-6">
        {/* Left Sidebar: Collections */}
        <div className="w-80 glass-panel rounded-2xl p-5 border border-slate-800 flex flex-col gap-4">
          <div className="flex items-center justify-between">
            <h2 className="text-sm font-semibold uppercase tracking-wider text-slate-400">Collections</h2>
            <button
              onClick={() => setShowCreateModal(true)}
              className="p-1.5 rounded-lg bg-indigo-600/20 text-indigo-400 hover:bg-indigo-600/30 transition-colors"
              title="Create Collection"
            >
              <Plus className="h-4 w-4" />
            </button>
          </div>

          <div className="flex-1 overflow-y-auto space-y-2">
            {collectionsLoading ? (
              <p className="text-xs text-slate-500">Loading collections...</p>
            ) : collections.length === 0 ? (
              <p className="text-xs text-slate-500">No collections found. Create one to get started.</p>
            ) : (
              collections.map((col) => (
                <button
                  key={col.id}
                  onClick={() => setSelectedCollection(col)}
                  className={`w-full text-left p-3 rounded-xl transition-all border flex items-center gap-3 ${
                    selectedCollection?.id === col.id
                      ? 'bg-indigo-600/15 border-indigo-500/40 text-indigo-200 shadow-md shadow-indigo-500/10'
                      : 'bg-slate-900/40 border-slate-800/60 text-slate-400 hover:bg-slate-800/40'
                  }`}
                >
                  <div
                    className="h-8 w-8 rounded-lg flex items-center justify-center font-bold text-white shrink-0"
                    style={{ backgroundColor: col.color || '#4F46E5' }}
                  >
                    {col.name.substring(0, 1).toUpperCase()}
                  </div>
                  <div className="truncate">
                    <p className="text-sm font-medium truncate text-slate-200">{col.name}</p>
                    <p className="text-xs text-slate-500 truncate">{col.description || 'Knowledge Collection'}</p>
                  </div>
                </button>
              ))
            )}
          </div>
        </div>

        {/* Right Content Area */}
        <div className="flex-1 flex flex-col gap-6">
          {selectedCollection ? (
            <>
              {/* Header Banner */}
              <div className="glass-panel p-6 rounded-2xl border border-slate-800 flex items-center justify-between">
                <div>
                  <div className="flex items-center gap-3">
                    <h1 className="text-2xl font-bold text-white">{selectedCollection.name}</h1>
                    <span className="text-xs px-2.5 py-1 rounded-full bg-slate-800 text-slate-300 font-medium">
                      Active Knowledge Context
                    </span>
                  </div>
                  <p className="text-sm text-slate-400 mt-1">{selectedCollection.description || 'Collection workspace'}</p>
                </div>

                <button
                  onClick={() => createChatMutation.mutate(selectedCollection.id)}
                  className="px-5 py-2.5 bg-indigo-600 hover:bg-indigo-500 text-white font-semibold rounded-xl transition-all shadow-lg shadow-indigo-600/30 flex items-center gap-2"
                >
                  <MessageSquare className="h-4 w-4" />
                  <span>Start RAG Chat</span>
                </button>
              </div>

              {/* Upload Card */}
              <div className="glass-panel p-6 rounded-2xl border border-slate-800">
                <h3 className="text-sm font-semibold text-slate-300 mb-3 flex items-center gap-2">
                  <Upload className="h-4 w-4 text-indigo-400" />
                  <span>Upload Knowledge Document</span>
                </h3>

                <form onSubmit={handleUpload} className="flex gap-4">
                  <input
                    type="file"
                    accept=".pdf,.docx,.txt,.md"
                    onChange={(e) => setUploadFile(e.target.files?.[0] || null)}
                    className="flex-1 text-sm text-slate-400 file:mr-4 file:py-2 file:px-4 file:rounded-xl file:border-0 file:text-xs file:font-semibold file:bg-indigo-500/10 file:text-indigo-400 hover:file:bg-indigo-500/20 bg-slate-900/60 border border-slate-800 rounded-xl p-1"
                  />
                  <button
                    type="submit"
                    disabled={!uploadFile || uploading}
                    className="px-5 py-2 bg-indigo-600 hover:bg-indigo-500 text-white font-medium text-sm rounded-xl transition-all disabled:opacity-50"
                  >
                    {uploading ? 'Uploading...' : 'Upload'}
                  </button>
                </form>
              </div>

              {/* Document List */}
              <div className="glass-panel p-6 rounded-2xl border border-slate-800 flex-1">
                <h3 className="text-sm font-semibold text-slate-300 mb-4 flex items-center gap-2">
                  <FileText className="h-4 w-4 text-indigo-400" />
                  <span>Documents ({documents.length})</span>
                </h3>

                {documents.length === 0 ? (
                  <div className="text-center py-12 border border-dashed border-slate-800 rounded-xl">
                    <FileText className="h-8 w-8 text-slate-600 mx-auto mb-2" />
                    <p className="text-sm text-slate-400">No documents uploaded to this collection yet.</p>
                  </div>
                ) : (
                  <div className="space-y-3">
                    {documents.map((doc) => (
                      <div
                        key={doc.id}
                        className="p-4 rounded-xl bg-slate-900/60 border border-slate-800 flex items-center justify-between"
                      >
                        <div className="flex items-center gap-3">
                          <div className="h-10 w-10 rounded-lg bg-indigo-500/10 border border-indigo-500/20 flex items-center justify-center text-indigo-400 font-semibold uppercase text-xs">
                            {doc.extension.replace('.', '')}
                          </div>
                          <div>
                            <p className="text-sm font-medium text-slate-200">{doc.title}</p>
                            <p className="text-xs text-slate-500">
                              {(doc.file_size / 1024).toFixed(1)} KB • {doc.total_chunks} Chunks • {doc.total_pages} Pages
                            </p>
                          </div>
                        </div>

                        <div>
                          {doc.status === 'READY' && (
                            <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 text-xs font-medium">
                              <CheckCircle2 className="h-3.5 w-3.5" />
                              Ready
                            </span>
                          )}
                          {doc.status === 'PROCESSING' && (
                            <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-amber-500/10 text-amber-400 border border-amber-500/20 text-xs font-medium">
                              <Clock className="h-3.5 w-3.5 animate-spin" />
                              Processing ({doc.progress}%)
                            </span>
                          )}
                          {doc.status === 'FAILED' && (
                            <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-red-500/10 text-red-400 border border-red-500/20 text-xs font-medium">
                              <AlertCircle className="h-3.5 w-3.5" />
                              Failed
                            </span>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </>
          ) : (
            <div className="flex-1 flex items-center justify-center glass-panel rounded-2xl border border-slate-800 p-12 text-center">
              <div>
                <Sparkles className="h-12 w-12 text-indigo-500/40 mx-auto mb-4" />
                <h3 className="text-lg font-semibold text-slate-200">Select or Create a Collection</h3>
                <p className="text-sm text-slate-400 mt-1 max-w-sm">
                  Organize your documents into collections to power targeted semantic search and AI generation.
                </p>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Create Collection Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-black/70 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="glass-panel w-full max-w-md p-6 rounded-2xl border border-slate-800">
            <h3 className="text-lg font-bold text-slate-100 mb-4">Create Collection</h3>
            <form
              onSubmit={(e) => {
                e.preventDefault();
                createCollectionMutation.mutate({ name: newCollectionName, description: newCollectionDesc });
              }}
              className="space-y-4"
            >
              <div>
                <label className="block text-xs font-semibold text-slate-300 uppercase mb-1">Collection Name</label>
                <input
                  type="text"
                  required
                  value={newCollectionName}
                  onChange={(e) => setNewCollectionName(e.target.value)}
                  placeholder="e.g. Technical Specifications"
                  className="w-full px-3.5 py-2 bg-slate-900 border border-slate-800 rounded-xl text-sm text-slate-200"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-300 uppercase mb-1">Description</label>
                <textarea
                  value={newCollectionDesc}
                  onChange={(e) => setNewCollectionDesc(e.target.value)}
                  placeholder="Optional brief description"
                  className="w-full px-3.5 py-2 bg-slate-900 border border-slate-800 rounded-xl text-sm text-slate-200 h-20 resize-none"
                />
              </div>

              <div className="flex gap-3 pt-2">
                <button
                  type="button"
                  onClick={() => setShowCreateModal(false)}
                  className="flex-1 py-2 rounded-xl bg-slate-800 text-slate-300 text-sm font-medium hover:bg-slate-700"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="flex-1 py-2 rounded-xl bg-indigo-600 text-white text-sm font-semibold hover:bg-indigo-500"
                >
                  Create
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
