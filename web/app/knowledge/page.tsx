"use client";

import { useState, useEffect } from "react";
import {
  BookOpen,
  Upload,
  Loader2,
  X,
  Send,
  MessageCircle,
  FileText,
  Plus,
} from "lucide-react";
import { apiUrl } from "@/lib/api";

interface PDFCollection {
  collection_name: string;
  file_name: string;
  file_path: string;
  num_chunks: number;
  upload_time: string;
}

interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  timestamp: Date;
}

export default function KnowledgePage() {
  const [collections, setCollections] = useState<PDFCollection[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [uploadModalOpen, setUploadModalOpen] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [file, setFile] = useState<File | null>(null);
  const [fileName, setFileName] = useState("");
  
  // RAG Chat states
  const [chatModalOpen, setChatModalOpen] = useState(false);
  const [selectedCollection, setSelectedCollection] = useState<string>("");
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputQuestion, setInputQuestion] = useState("");
  const [isQuerying, setIsQuerying] = useState(false);

  // Fetch collections from new RAG system
  useEffect(() => {
    fetchCollections();
  }, []);

  const fetchCollections = async () => {
    try {
      setLoading(true);
      const res = await fetch(apiUrl("/api/v1/rag/collections"));
      
      if (!res.ok) {
        throw new Error(`Failed to fetch collections: ${res.status}`);
      }

      const data = await res.json();
      console.log("Collections data:", data);
      
      // Handle different response formats
      let pdfs = [];
      if (Array.isArray(data)) {
        pdfs = data;
      } else if (Array.isArray(data.pdfs)) {
        pdfs = data.pdfs;
      } else if (data.collections && Array.isArray(data.collections)) {
        pdfs = data.collections;
      }
      
      setCollections(pdfs);
      setError(null);
    } catch (err) {
      console.error("Error fetching collections:", err);
      setError(err instanceof Error ? err.message : "Failed to fetch collections");
      setCollections([]);
    } finally {
      setLoading(false);
    }
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0];
    if (selectedFile) {
      if (selectedFile.type !== "application/pdf") {
        setError("Please select a PDF file");
        return;
      }
      setFile(selectedFile);
      setFileName(selectedFile.name);
      setError("");
    }
  };

  const handleUpload = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!file) return;

    try {
      setUploading(true);
      setError("");

      const formData = new FormData();
      formData.append("file", file);

      const response = await fetch(apiUrl("/api/v1/rag/upload"), {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `Upload failed: ${response.status}`);
      }

      const data = await response.json();
      
      setUploadModalOpen(false);
      setFile(null);
      setFileName("");
      
      // Refresh collections list
      await fetchCollections();
      
      alert(`✅ PDF uploaded successfully!\nCollection: ${data.collection_name}\nChunks: ${data.num_chunks}`);
    } catch (err) {
      console.error(err);
      setError(err instanceof Error ? err.message : "Upload failed");
    } finally {
      setUploading(false);
    }
  };

  const handleOpenChat = (collectionName: string) => {
    setSelectedCollection(collectionName);
    setMessages([]);
    setChatModalOpen(true);
  };

  const handleAskQuestion = async () => {
    if (!inputQuestion.trim() || !selectedCollection) return;

    try {
      setIsQuerying(true);
      setError("");

      const question = inputQuestion;
      const userMessage: Message = {
        id: Date.now().toString(),
        role: "user",
        content: question,
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, userMessage]);
      setInputQuestion("");

      // Use new RAG endpoint
      const response = await fetch(apiUrl("/api/v1/rag/query"), {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          question: question,
          collection_name: selectedCollection,
          top_k: 3,
        }),
      });

      if (!response.ok) {
        try {
          const errorData = await response.json();
          throw new Error(errorData.detail || `Server error: ${response.status}`);
        } catch (parseErr) {
          throw new Error(`Server error: ${response.status}`);
        }
      }

      const data = await response.json();
      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: "assistant",
        content: data.answer || "No answer found.",
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, assistantMessage]);
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : "Query failed";
      setError(errorMsg);
      const errorMessage: Message = {
        id: (Date.now() + 2).toString(),
        role: "assistant",
        content: `❌ Error: ${errorMsg}`,
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsQuerying(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey && !isQuerying) {
      e.preventDefault();
      handleAskQuestion();
    }
  };

  return (
    <div className="h-screen flex flex-col" style={{ backgroundColor: '#000000' }}>
      {/* Header */}
      <div className="px-6 py-4" style={{ backgroundColor: '#000000', borderBottom: '1px solid #1F1F1F' }}>
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold flex items-center gap-2" style={{ color: '#F8FAFC' }}>
              <BookOpen className="h-6 w-6" style={{ color: '#10B981' }} />
              Knowledge Bases
            </h1>
            <p className="text-sm mt-1" style={{ color: '#94A3B8' }}>
              Upload PDFs and query them with AI
            </p>
          </div>
          <button
            onClick={() => setUploadModalOpen(true)}
            className="flex items-center gap-2 px-4 py-2 rounded-lg transition-all"
            style={{
              background: 'linear-gradient(135deg, #10B981 0%, #059669 100%)',
              color: '#FFFFFF',
            }}
          >
            <Plus className="h-4 w-4" />
            Upload PDF
          </button>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 overflow-y-auto p-6">
        {loading ? (
          <div className="flex items-center justify-center h-64">
            <Loader2 className="h-8 w-8 animate-spin" style={{ color: '#10B981' }} />
          </div>
        ) : error ? (
          <div className="p-4 rounded-lg" style={{ backgroundColor: '#1F1F1F', borderLeft: '4px solid #EF4444' }}>
            <p style={{ color: '#FCA5A5' }}>{error}</p>
          </div>
        ) : collections.length === 0 ? (
          <div className="text-center py-12">
            <BookOpen className="h-16 w-16 mx-auto mb-4" style={{ color: '#374151' }} />
            <h3 className="text-lg font-medium mb-2" style={{ color: '#9CA3AF' }}>
              No documents yet
            </h3>
            <p className="text-sm mb-4" style={{ color: '#6B7280' }}>
              Upload your first PDF to get started
            </p>
            <button
              onClick={() => setUploadModalOpen(true)}
              className="px-4 py-2 rounded-lg transition-all"
              style={{
                background: 'linear-gradient(135deg, #10B981 0%, #059669 100%)',
                color: '#FFFFFF',
              }}
            >
              Upload PDF
            </button>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {collections.map((collection, index) => (
              <div
                key={collection.collection_name || index}
                className="p-4 rounded-lg transition-all cursor-pointer hover:shadow-lg"
                style={{
                  backgroundColor: '#000000',
                  border: '1px solid #1F1F1F',
                }}
                onClick={() => handleOpenChat(collection.collection_name)}
              >
                <div className="flex items-start gap-3">
                  <FileText className="h-8 w-8 flex-shrink-0" style={{ color: '#10B981' }} />
                  <div className="flex-1 min-w-0">
                    <h3 className="font-medium truncate" style={{ color: '#F8FAFC' }}>
                      {collection.file_name || collection.collection_name || 'Untitled'}
                    </h3>
                    {collection.num_chunks !== undefined && (
                      <p className="text-xs mt-1" style={{ color: '#6B7280' }}>
                        {collection.num_chunks} chunks
                      </p>
                    )}
                    {collection.upload_time && (
                      <p className="text-xs mt-1" style={{ color: '#6B7280' }}>
                        {new Date(collection.upload_time).toLocaleDateString()}
                      </p>
                    )}
                  </div>
                  <MessageCircle className="h-5 w-5 flex-shrink-0" style={{ color: '#10B981' }} />
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Upload Modal */}
      {uploadModalOpen && (
        <div className="fixed inset-0 flex items-center justify-center z-50" style={{ backgroundColor: 'rgba(0, 0, 0, 0.95)' }}>
          <div className="w-full max-w-md p-6 rounded-lg" style={{ backgroundColor: '#000000', border: '1px solid #1F1F1F' }}>
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-bold" style={{ color: '#F8FAFC' }}>
                Upload PDF
              </h2>
              <button onClick={() => setUploadModalOpen(false)}>
                <X className="h-5 w-5" style={{ color: '#9CA3AF' }} />
              </button>
            </div>

            <form onSubmit={handleUpload} className="space-y-4">
              <div>
                <label className="block text-sm font-medium mb-2" style={{ color: '#E5E7EB' }}>
                  Select PDF File
                </label>
                <input
                  type="file"
                  accept=".pdf"
                  onChange={handleFileSelect}
                  className="w-full px-3 py-2 rounded-lg"
                  style={{
                    backgroundColor: '#1F1F1F',
                    border: '1px solid #374151',
                    color: '#F8FAFC',
                  }}
                />
                {fileName && (
                  <p className="text-sm mt-2" style={{ color: '#10B981' }}>
                    Selected: {fileName}
                  </p>
                )}
              </div>

              {error && (
                <div className="p-3 rounded-lg" style={{ backgroundColor: '#1F1F1F', borderLeft: '4px solid #EF4444' }}>
                  <p className="text-sm" style={{ color: '#FCA5A5' }}>{error}</p>
                </div>
              )}

              <div className="flex gap-2">
                <button
                  type="button"
                  onClick={() => setUploadModalOpen(false)}
                  className="flex-1 px-4 py-2 rounded-lg transition-all"
                  style={{
                    backgroundColor: '#1F1F1F',
                    color: '#9CA3AF',
                  }}
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={!file || uploading}
                  className="flex-1 px-4 py-2 rounded-lg flex items-center justify-center gap-2 transition-all disabled:opacity-50"
                  style={{
                    background: 'linear-gradient(135deg, #10B981 0%, #059669 100%)',
                    color: '#FFFFFF',
                  }}
                >
                  {uploading ? (
                    <>
                      <Loader2 className="h-4 w-4 animate-spin" />
                      Uploading...
                    </>
                  ) : (
                    <>
                      <Upload className="h-4 w-4" />
                      Upload
                    </>
                  )}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Chat Modal */}
      {chatModalOpen && (
        <div className="fixed inset-0 flex items-center justify-center z-50" style={{ backgroundColor: 'rgba(0, 0, 0, 0.95)' }}>
          <div className="w-full max-w-3xl h-[80vh] flex flex-col rounded-lg" style={{ backgroundColor: '#000000', border: '1px solid #1F1F1F' }}>
            <div className="flex items-center justify-between p-4" style={{ borderBottom: '1px solid #1F1F1F' }}>
              <h2 className="text-xl font-bold" style={{ color: '#F8FAFC' }}>
                Chat with {selectedCollection}
              </h2>
              <button onClick={() => setChatModalOpen(false)}>
                <X className="h-5 w-5" style={{ color: '#9CA3AF' }} />
              </button>
            </div>

            <div className="flex-1 overflow-y-auto p-4 space-y-4">
              {messages.length === 0 ? (
                <div className="text-center py-12">
                  <MessageCircle className="h-12 w-12 mx-auto mb-3" style={{ color: '#374151' }} />
                  <p style={{ color: '#6B7280' }}>Ask a question about this document</p>
                </div>
              ) : (
                messages.map((msg) => (
                  <div
                    key={msg.id}
                    className={`p-3 rounded-lg ${msg.role === "user" ? "ml-12" : "mr-12"}`}
                    style={{
                      backgroundColor: msg.role === "user" ? '#0A0A0A' : '#000000',
                      border: msg.role === "assistant" ? '1px solid #10B981' : '1px solid #1F1F1F',
                    }}
                  >
                    <p style={{ color: '#F8FAFC' }}>{msg.content}</p>
                  </div>
                ))
              )}
            </div>

            <div className="p-4" style={{ borderTop: '1px solid #1F1F1F' }}>
              <div className="flex gap-2">
                <input
                  type="text"
                  value={inputQuestion}
                  onChange={(e) => setInputQuestion(e.target.value)}
                  onKeyDown={handleKeyDown}
                  placeholder="Ask a question..."
                  className="flex-1 px-4 py-2 rounded-lg"
                  style={{
                    backgroundColor: '#1F1F1F',
                    border: '1px solid #374151',
                    color: '#F8FAFC',
                  }}
                  disabled={isQuerying}
                />
                <button
                  onClick={handleAskQuestion}
                  disabled={isQuerying || !inputQuestion.trim()}
                  className="px-4 py-2 rounded-lg flex items-center gap-2 transition-all disabled:opacity-50"
                  style={{
                    background: 'linear-gradient(135deg, #10B981 0%, #059669 100%)',
                    color: '#FFFFFF',
                  }}
                >
                  {isQuerying ? (
                    <Loader2 className="h-4 w-4 animate-spin" />
                  ) : (
                    <Send className="h-4 w-4" />
                  )}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
