"use client";

import { useState } from "react";
import { Upload, Send, Loader2, FileText, X, Download } from "lucide-react";
import Link from "next/link";
import { apiUrl } from "@/lib/api";

interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  timestamp: Date;
}

export default function NotesAssistantPage() {
  const [file, setFile] = useState<File | null>(null);
  const [fileName, setFileName] = useState("");
  const [collectionName, setCollectionName] = useState("");
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputQuestion, setInputQuestion] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [error, setError] = useState("");
  const [pdfUploaded, setPdfUploaded] = useState(false);

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
      setUploadProgress(0);
    }
  };

  const handleUploadPDF = async () => {
    if (!file) return;

    try {
      setIsLoading(true);
      setError("");
      setUploadProgress(10);

      console.log("[Upload] Starting upload:", file.name, "Size:", file.size);

      const formData = new FormData();
      formData.append("file", file);

      console.log("[Upload] Sending request to:", apiUrl("/api/v1/rag/upload"));

      // Create AbortController for timeout
      const controller = new AbortController();
      const timeoutId = setTimeout(() => {
        controller.abort();
        console.log("[Upload] Request timed out after 5 minutes");
      }, 300000); // 5 minute timeout for large files

      const response = await fetch(apiUrl("/api/v1/rag/upload"), {
        method: "POST",
        body: formData,
        signal: controller.signal,
      }).finally(() => {
        clearTimeout(timeoutId);
      });

      console.log("[Upload] Response received:", response.status, response.statusText);

      setUploadProgress(50);

      let errorMessage = "Upload failed";
      
      if (!response.ok) {
        try {
          const errorData = await response.json();
          errorMessage = errorData.detail || `Server error: ${response.status}`;
        } catch {
          // If response is not JSON, try to get text
          try {
            const errorText = await response.text();
            errorMessage = errorText || `Server error: ${response.status}`;
          } catch {
            errorMessage = `Server error: ${response.status} ${response.statusText}`;
          }
        }
        throw new Error(errorMessage);
      }

      let data;
      try {
        data = await response.json();
      } catch {
        const responseText = await response.text();
        console.error("Failed to parse response as JSON:", responseText);
        throw new Error(`Invalid response format: ${responseText.substring(0, 100)}`);
      }
      
      setUploadProgress(100);

      setMessages([
        {
          id: "1",
          role: "assistant",
          content: `✅ PDF "${fileName}" uploaded successfully!\n\nYou now have access to the document. Ask me any questions about its content.`,
          timestamp: new Date(),
        },
      ]);

      setFile(null);
      setPdfUploaded(true);
      // Store the actual collection name from backend response
      setCollectionName(data.collection_name || fileName.replace(".pdf", ""));
      setFileName("");
      setTimeout(() => setUploadProgress(0), 1000);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Upload failed");
      setUploadProgress(0);
    } finally {
      setIsLoading(false);
    }
  };

  const handleAskQuestion = async () => {
    if (!inputQuestion.trim()) return;

    try {
      setIsLoading(true);
      setError("");

      // Store the question before clearing
      const question = inputQuestion;

      // Add user message
      const userMessage: Message = {
        id: Date.now().toString(),
        role: "user",
        content: question,
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, userMessage]);
      setInputQuestion("");

      // Query the RAG system
      const response = await fetch(apiUrl("/api/v1/rag/query"), {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          question: question,
          collection_name: collectionName,
          top_k: 3,
        }),
      });

      let errorMessage = "Failed to get response";
      
      if (!response.ok) {
        try {
          const errorData = await response.json();
          errorMessage = errorData.detail || `Server error: ${response.status}`;
        } catch {
          try {
            const errorText = await response.text();
            errorMessage = errorText || `Server error: ${response.status}`;
          } catch {
            errorMessage = `Server error: ${response.status}`;
          }
        }
        throw new Error(errorMessage);
      }

      let data;
      try {
        data = await response.json();
      } catch {
        const responseText = await response.text();
        console.error("Failed to parse response as JSON:", responseText);
        throw new Error(`Invalid response format: ${responseText.substring(0, 100)}`);
      }

      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: "assistant",
        content: data.answer || "No answer found. Please upload a PDF first.",
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
      setIsLoading(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey && !isLoading) {
      e.preventDefault();
      handleAskQuestion();
    }
  };

  return (
    <div className="h-screen flex flex-col" style={{ backgroundColor: '#050505' }}>
      {/* Header */}
      <div className="px-6 py-4" style={{ backgroundColor: '#0F0F0F', borderBottom: '1px solid #1F1F1F' }}>
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold" style={{ color: '#F8FAFC' }}>
              📝 Notes Assistant
            </h1>
            <p className="text-sm" style={{ color: 'rgba(248, 250, 252, 0.6)' }}>
              Upload PDFs and ask questions about their content
            </p>
          </div>
          <Link
            href="/"
            style={{ color: 'rgba(248, 250, 252, 0.6)' }}
          >
            <X size={24} />
          </Link>
        </div>
      </div>

      <div className="flex-1 flex overflow-hidden">
        {/* Main Content */}
        <div className="flex-1 flex flex-col">
          {/* Messages Area */}
          <div className="flex-1 overflow-y-auto p-6 space-y-4">
            {messages.length === 0 ? (
              <div className="h-full flex items-center justify-center">
                <div className="text-center">
                  <FileText size={48} className="mx-auto text-slate-300 mb-4" />
                  <p className="text-slate-500 dark:text-slate-400">
                    Upload a PDF to get started
                  </p>
                </div>
              </div>
            ) : (
              messages.map((msg) => (
                <div
                  key={msg.id}
                  className={`flex ${
                    msg.role === "user" ? "justify-end" : "justify-start"
                  }`}
                >
                  <div
                    className={`max-w-xl px-4 py-3 rounded-lg ${
                      msg.role === "user"
                        ? "bg-blue-500 text-white rounded-br-none"
                        : "bg-slate-200 dark:bg-slate-700 text-slate-900 dark:text-slate-100 rounded-bl-none"
                    }`}
                  >
                    <p className="whitespace-pre-wrap">{msg.content}</p>
                    <p
                      className={`text-xs mt-2 ${
                        msg.role === "user"
                          ? "text-blue-100"
                          : "text-slate-500 dark:text-slate-400"
                      }`}
                    >
                      {msg.timestamp.toLocaleTimeString()}
                    </p>
                  </div>
                </div>
              ))
            )}
            {isLoading && (
              <div className="flex justify-start">
                <div className="bg-slate-200 dark:bg-slate-700 px-4 py-3 rounded-lg">
                  <Loader2 className="animate-spin text-slate-600 dark:text-slate-300" />
                </div>
              </div>
            )}
          </div>

          {/* Input Area */}
          <div className="border-t border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-800 p-6">
            <div className="flex gap-3">
              <input
                type="text"
                value={inputQuestion}
                onChange={(e) => setInputQuestion(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder="Ask a question about the PDF..."
                disabled={isLoading || !pdfUploaded}
                className="flex-1 px-4 py-2 border border-slate-300 dark:border-slate-600 rounded-lg bg-white dark:bg-slate-700 text-slate-900 dark:text-slate-100 placeholder-slate-500 dark:placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
              <button
                onClick={handleAskQuestion}
                disabled={isLoading || !inputQuestion.trim() || !pdfUploaded}
                className="px-6 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:bg-slate-300 dark:disabled:bg-slate-600 disabled:cursor-not-allowed flex items-center gap-2"
              >
                {isLoading ? (
                  <Loader2 className="animate-spin" size={18} />
                ) : (
                  <Send size={18} />
                )}
              </button>
            </div>
            {error && (
              <p className="text-red-500 text-sm mt-2">❌ {error}</p>
            )}
          </div>
        </div>

        {/* Sidebar - PDF Upload */}
        <div className="w-80 border-l border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-800 p-6 flex flex-col">
          <h2 className="text-lg font-semibold text-slate-900 dark:text-slate-100 mb-4">
            📄 Document
          </h2>

          {!fileName ? (
            <div className="flex-1 flex flex-col items-center justify-center">
              <label className="w-full">
                <input
                  type="file"
                  accept=".pdf"
                  onChange={handleFileSelect}
                  className="hidden"
                />
                <div className="border-2 border-dashed border-slate-300 dark:border-slate-600 rounded-lg p-6 text-center cursor-pointer hover:border-blue-500 transition">
                  <Upload className="mx-auto text-slate-400 mb-2" size={32} />
                  <p className="text-sm font-medium text-slate-700 dark:text-slate-300">
                    Click to upload
                  </p>
                  <p className="text-xs text-slate-500 dark:text-slate-400">
                    PDF only
                  </p>
                </div>
              </label>
            </div>
          ) : (
            <div className="flex-1 flex flex-col">
              <div className="bg-slate-100 dark:bg-slate-700 rounded-lg p-4 mb-4">
                <p className="text-sm font-medium text-slate-900 dark:text-slate-100 break-words">
                  {fileName}
                </p>
                <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
                  {((file?.size ?? 0) / 1024 / 1024).toFixed(2)} MB
                </p>
              </div>

              {uploadProgress > 0 && uploadProgress < 100 && (
                <div className="mb-4">
                  <div className="w-full bg-slate-200 dark:bg-slate-600 rounded-full h-2">
                    <div
                      className="bg-blue-500 h-2 rounded-full transition-all"
                      style={{ width: `${uploadProgress}%` }}
                    />
                  </div>
                  <p className="text-xs text-slate-500 mt-2">{uploadProgress}%</p>
                </div>
              )}

              <button
                onClick={handleUploadPDF}
                disabled={isLoading || uploadProgress === 100}
                className="w-full px-4 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600 disabled:bg-slate-300 dark:disabled:bg-slate-600 disabled:cursor-not-allowed flex items-center justify-center gap-2 mb-2"
              >
                {isLoading ? (
                  <>
                    <Loader2 className="animate-spin" size={16} />
                    Uploading...
                  </>
                ) : uploadProgress === 100 ? (
                  <>
                    <Download size={16} />
                    Uploaded!
                  </>
                ) : (
                  <>
                    <Upload size={16} />
                    Upload PDF
                  </>
                )}
              </button>

              <button
                onClick={() => {
                  setFile(null);
                  setFileName("");
                  setCollectionName("");
                  setMessages([]);
                  setUploadProgress(0);
                  setPdfUploaded(false);
                }}
                disabled={isLoading}
                className="w-full px-4 py-2 bg-slate-200 dark:bg-slate-700 text-slate-700 dark:text-slate-300 rounded-lg hover:bg-slate-300 dark:hover:bg-slate-600"
              >
                Clear
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
