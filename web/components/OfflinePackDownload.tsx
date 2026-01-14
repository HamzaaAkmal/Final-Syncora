"use client";

import React, { useState, useEffect } from "react";
import {
  Download,
  FileArchive,
  Loader2,
  CheckCircle2,
  Globe,
  BookOpen,
  Wifi,
  WifiOff,
  RefreshCw,
  ChevronDown,
  X,
  Sparkles,
  Edit3,
  Plus,
  Trash2,
} from "lucide-react";
import { apiUrl } from "@/lib/api";

interface OfflinePack {
  pack_id: string;
  grade: number;
  subject: string;
  language: string;
  size_bytes: number;
  download_url: string;
  created_at?: string;
  topics?: string[];
}

interface OfflinePackDownloadProps {
  isUrdu?: boolean;
  currentGrade?: number;
  defaultGrade?: number;
  onClose?: () => void;
}

const SUBJECTS = [
  { id: "mathematics", name: "Mathematics", nameUr: "ریاضی", icon: "📐" },
  { id: "science", name: "Science", nameUr: "سائنس", icon: "🔬" },
  { id: "english", name: "English", nameUr: "انگریزی", icon: "📚" },
  { id: "urdu", name: "Urdu", nameUr: "اردو", icon: "✍️" },
  { id: "all", name: "All Subjects", nameUr: "تمام مضامین", icon: "📖" },
];

const GRADES = [6, 7, 8, 9, 10, 11, 12];

// Suggested topics per subject
const SUGGESTED_TOPICS: Record<string, string[]> = {
  mathematics: ["Linear Equations", "Quadratic Equations", "Matrices", "Trigonometry", "Geometry"],
  science: ["Motion and Force", "Energy", "Atoms", "Chemical Reactions", "Human Body"],
  english: ["Grammar", "Sentence Structure", "Vocabulary", "Essay Writing", "Comprehension"],
  urdu: ["قواعد", "نظم", "نثر", "مضمون نویسی", "ادب"],
  all: ["Math: Equations", "Science: Force", "English: Grammar", "Urdu: قواعد"],
};

export default function OfflinePackDownload({
  isUrdu = false,
  currentGrade = 9,
  defaultGrade,
  onClose,
}: OfflinePackDownloadProps) {
  const [selectedGrade, setSelectedGrade] = useState(defaultGrade || currentGrade);
  const [selectedSubject, setSelectedSubject] = useState("all");
  const [selectedLanguage, setSelectedLanguage] = useState<"en" | "ur" | "both">("both");
  const [availablePacks, setAvailablePacks] = useState<OfflinePack[]>([]);
  const [loading, setLoading] = useState(false);
  const [generating, setGenerating] = useState(false);
  const [downloadProgress, setDownloadProgress] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  
  // Custom topics state
  const [useCustomTopics, setUseCustomTopics] = useState(false);
  const [customTopics, setCustomTopics] = useState<string[]>([]);
  const [newTopicInput, setNewTopicInput] = useState("");
  const [generationStatus, setGenerationStatus] = useState<string | null>(null);

  // Fetch available packs on mount
  useEffect(() => {
    fetchAvailablePacks();
  }, []);

  // Load suggested topics when subject changes
  useEffect(() => {
    if (useCustomTopics && customTopics.length === 0) {
      setCustomTopics(SUGGESTED_TOPICS[selectedSubject] || []);
    }
  }, [selectedSubject, useCustomTopics]);

  const fetchAvailablePacks = async () => {
    setLoading(true);
    try {
      const res = await fetch(apiUrl("/api/v1/offline/prebuilt"));
      if (res.ok) {
        const data = await res.json();
        setAvailablePacks([...(data.prebuilt || []), ...(data.generated || [])]);
      }
    } catch (e) {
      console.error("Failed to fetch packs:", e);
    } finally {
      setLoading(false);
    }
  };

  const addCustomTopic = () => {
    if (newTopicInput.trim() && customTopics.length < 10) {
      setCustomTopics(prev => [...prev, newTopicInput.trim()]);
      setNewTopicInput("");
    }
  };

  const removeTopic = (index: number) => {
    setCustomTopics(prev => prev.filter((_, i) => i !== index));
  };

  const generatePack = async () => {
    setGenerating(true);
    setError(null);
    setGenerationStatus(isUrdu ? "AI مواد تیار کر رہا ہے..." : "AI is generating content...");
    
    try {
      const requestBody: any = {
        grade: selectedGrade,
        subject: selectedSubject,
        language: selectedLanguage,
      };

      // Add custom topics if enabled
      if (useCustomTopics && customTopics.length > 0) {
        requestBody.custom_topics = customTopics;
      }

      const res = await fetch(apiUrl("/api/v1/offline/generate"), {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(requestBody),
      });

      if (res.ok) {
        const pack = await res.json();
        setAvailablePacks(prev => [...prev, pack]);
        setGenerationStatus(isUrdu ? "پیکج تیار ہو گیا!" : "Pack ready!");
        // Auto-download the generated pack
        downloadPack(pack.download_url, pack.pack_id);
      } else {
        const errData = await res.json().catch(() => ({}));
        setError(errData.detail || (isUrdu ? "پیکج بنانے میں ناکام" : "Failed to generate pack"));
        setGenerationStatus(null);
      }
    } catch (e) {
      setError(isUrdu ? "نیٹ ورک کی خرابی" : "Network error");
      setGenerationStatus(null);
    } finally {
      setGenerating(false);
      setTimeout(() => setGenerationStatus(null), 3000);
    }
  };

  const downloadPack = async (url: string, packId: string) => {
    setDownloadProgress(packId);
    try {
      const fullUrl = apiUrl(url);
      
      // Create a hidden link and trigger download
      const link = document.createElement("a");
      link.href = fullUrl;
      link.download = `syncora_offline_${packId}.zip`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      
      // Show success briefly
      setTimeout(() => setDownloadProgress(null), 2000);
    } catch (e) {
      console.error("Download failed:", e);
      setDownloadProgress(null);
    }
  };

  const formatSize = (bytes: number) => {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  };

  // Find matching pre-built pack
  const matchingPack = availablePacks.find(
    p => p.grade === selectedGrade && 
    (p.language === selectedLanguage || selectedLanguage === "both")
  );

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4" dir={isUrdu ? "rtl" : "ltr"}>
      <div className="bg-white dark:bg-slate-800 rounded-2xl max-w-lg w-full shadow-xl overflow-hidden">
        {/* Header */}
        <div className="bg-gradient-to-r from-blue-600 to-indigo-600 p-6 text-white">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-12 h-12 bg-white/20 rounded-xl flex items-center justify-center">
                <WifiOff className="w-6 h-6" />
              </div>
              <div>
                <h2 className="text-xl font-bold">
                  {isUrdu ? "آف لائن تعلیمی پیکج" : "Offline Learning Pack"}
                </h2>
                <p className="text-blue-100 text-sm">
                  {isUrdu ? "بغیر انٹرنیٹ کے سیکھیں" : "Learn without internet"}
                </p>
              </div>
            </div>
            {onClose && (
              <button onClick={onClose} className="text-white/80 hover:text-white">
                <X className="w-6 h-6" />
              </button>
            )}
          </div>
        </div>

        {/* Content */}
        <div className="p-6">
          {/* Features */}
          <div className="grid grid-cols-3 gap-4 mb-6">
            <div className="text-center p-3 bg-slate-50 dark:bg-slate-700/50 rounded-xl">
              <BookOpen className="w-6 h-6 mx-auto text-blue-500 mb-2" />
              <p className="text-xs text-slate-600 dark:text-slate-300">
                {isUrdu ? "1 دن کا مواد" : "1-Day Content"}
              </p>
            </div>
            <div className="text-center p-3 bg-slate-50 dark:bg-slate-700/50 rounded-xl">
              <Globe className="w-6 h-6 mx-auto text-green-500 mb-2" />
              <p className="text-xs text-slate-600 dark:text-slate-300">
                {isUrdu ? "اردو / انگریزی" : "Urdu / English"}
              </p>
            </div>
            <div className="text-center p-3 bg-slate-50 dark:bg-slate-700/50 rounded-xl">
              <FileArchive className="w-6 h-6 mx-auto text-purple-500 mb-2" />
              <p className="text-xs text-slate-600 dark:text-slate-300">
                {isUrdu ? "PCTB نصاب" : "PCTB Aligned"}
              </p>
            </div>
          </div>

          {/* Selection */}
          <div className="space-y-4">
            {/* Grade Selection */}
            <div>
              <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
                {isUrdu ? "جماعت منتخب کریں" : "Select Grade"}
              </label>
              <div className="flex flex-wrap gap-2">
                {GRADES.map(grade => (
                  <button
                    key={grade}
                    onClick={() => setSelectedGrade(grade)}
                    className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                      selectedGrade === grade
                        ? "bg-blue-600 text-white"
                        : "bg-slate-100 dark:bg-slate-700 text-slate-700 dark:text-slate-300 hover:bg-slate-200 dark:hover:bg-slate-600"
                    }`}
                  >
                    {isUrdu ? `جماعت ${grade}` : `Grade ${grade}`}
                  </button>
                ))}
              </div>
            </div>

            {/* Subject Selection */}
            <div>
              <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
                {isUrdu ? "مضمون منتخب کریں" : "Select Subject"}
              </label>
              <div className="grid grid-cols-3 gap-2">
                {SUBJECTS.map(subject => (
                  <button
                    key={subject.id}
                    onClick={() => setSelectedSubject(subject.id)}
                    className={`p-3 rounded-lg text-center transition-colors ${
                      selectedSubject === subject.id
                        ? "bg-green-100 dark:bg-green-900/30 border-2 border-green-500"
                        : "bg-slate-50 dark:bg-slate-700 border-2 border-transparent hover:border-slate-200 dark:hover:border-slate-600"
                    }`}
                  >
                    <span className="text-xl">{subject.icon}</span>
                    <p className="text-xs mt-1 text-slate-700 dark:text-slate-300">
                      {isUrdu ? subject.nameUr : subject.name}
                    </p>
                  </button>
                ))}
              </div>
            </div>

            {/* Language Selection */}
            <div>
              <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
                {isUrdu ? "زبان" : "Language"}
              </label>
              <div className="flex gap-2">
                {[
                  { id: "en" as const, label: "English", labelUr: "انگریزی" },
                  { id: "ur" as const, label: "اردو", labelUr: "اردو" },
                  { id: "both" as const, label: "Both", labelUr: "دونوں" },
                ].map(lang => (
                  <button
                    key={lang.id}
                    onClick={() => setSelectedLanguage(lang.id)}
                    className={`flex-1 py-2 rounded-lg text-sm font-medium transition-colors ${
                      selectedLanguage === lang.id
                        ? "bg-indigo-600 text-white"
                        : "bg-slate-100 dark:bg-slate-700 text-slate-700 dark:text-slate-300"
                    }`}
                  >
                    {isUrdu ? lang.labelUr : lang.label}
                  </button>
                ))}
              </div>
            </div>

            {/* Custom Topics Toggle */}
            <div className="border-t border-slate-200 dark:border-slate-700 pt-4">
              <button
                onClick={() => setUseCustomTopics(!useCustomTopics)}
                className={`w-full flex items-center justify-between p-3 rounded-xl transition-colors ${
                  useCustomTopics
                    ? "bg-purple-100 dark:bg-purple-900/30 border-2 border-purple-500"
                    : "bg-slate-50 dark:bg-slate-700 border-2 border-transparent hover:border-purple-300"
                }`}
              >
                <div className="flex items-center gap-3">
                  <Sparkles className={`w-5 h-5 ${useCustomTopics ? "text-purple-600" : "text-slate-400"}`} />
                  <div className="text-left">
                    <p className="font-medium text-sm text-slate-700 dark:text-slate-300">
                      {isUrdu ? "اپنے عنوانات منتخب کریں" : "Choose Your Own Topics"}
                    </p>
                    <p className="text-xs text-slate-500">
                      {isUrdu ? "AI آپ کے مطلوبہ عنوانات پر مواد بنائے گا" : "AI will generate content on topics you want"}
                    </p>
                  </div>
                </div>
                <div className={`w-10 h-6 rounded-full transition-colors ${useCustomTopics ? "bg-purple-600" : "bg-slate-300"} relative`}>
                  <div className={`absolute w-4 h-4 bg-white rounded-full top-1 transition-all ${useCustomTopics ? "right-1" : "left-1"}`} />
                </div>
              </button>
            </div>

            {/* Custom Topics Input */}
            {useCustomTopics && (
              <div className="space-y-3 p-4 bg-purple-50 dark:bg-purple-900/20 rounded-xl border border-purple-200 dark:border-purple-800">
                <label className="block text-sm font-medium text-purple-700 dark:text-purple-300">
                  {isUrdu ? "سیکھنے کے عنوانات (زیادہ سے زیادہ 10)" : "Topics to Learn (max 10)"}
                </label>
                
                {/* Topic Input */}
                <div className="flex gap-2">
                  <input
                    type="text"
                    value={newTopicInput}
                    onChange={(e) => setNewTopicInput(e.target.value)}
                    onKeyPress={(e) => e.key === "Enter" && addCustomTopic()}
                    placeholder={isUrdu ? "عنوان لکھیں..." : "Type a topic..."}
                    className="flex-1 px-3 py-2 border border-purple-300 dark:border-purple-600 rounded-lg bg-white dark:bg-slate-800 text-sm focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                    disabled={customTopics.length >= 10}
                  />
                  <button
                    onClick={addCustomTopic}
                    disabled={!newTopicInput.trim() || customTopics.length >= 10}
                    className="px-3 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    <Plus className="w-4 h-4" />
                  </button>
                </div>

                {/* Topics List */}
                {customTopics.length > 0 && (
                  <div className="flex flex-wrap gap-2">
                    {customTopics.map((topic, idx) => (
                      <span
                        key={idx}
                        className="inline-flex items-center gap-1 px-3 py-1 bg-white dark:bg-slate-700 border border-purple-300 dark:border-purple-600 rounded-full text-sm"
                      >
                        {topic}
                        <button
                          onClick={() => removeTopic(idx)}
                          className="text-red-500 hover:text-red-700 ml-1"
                        >
                          <X className="w-3 h-3" />
                        </button>
                      </span>
                    ))}
                  </div>
                )}

                {/* Suggested Topics */}
                <div>
                  <p className="text-xs text-purple-600 dark:text-purple-400 mb-2">
                    {isUrdu ? "تجویز کردہ عنوانات:" : "Suggested:"}
                  </p>
                  <div className="flex flex-wrap gap-1">
                    {SUGGESTED_TOPICS[selectedSubject]?.slice(0, 5).map((topic, idx) => (
                      <button
                        key={idx}
                        onClick={() => {
                          if (!customTopics.includes(topic) && customTopics.length < 10) {
                            setCustomTopics(prev => [...prev, topic]);
                          }
                        }}
                        disabled={customTopics.includes(topic) || customTopics.length >= 10}
                        className="px-2 py-1 text-xs bg-purple-100 dark:bg-purple-800 text-purple-700 dark:text-purple-300 rounded hover:bg-purple-200 dark:hover:bg-purple-700 disabled:opacity-50 disabled:cursor-not-allowed"
                      >
                        + {topic}
                      </button>
                    ))}
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Generation Status */}
          {generationStatus && (
            <div className="mt-4 p-3 bg-purple-50 dark:bg-purple-900/20 text-purple-600 dark:text-purple-400 rounded-lg text-sm flex items-center gap-2">
              <Sparkles className="w-4 h-4 animate-pulse" />
              {generationStatus}
            </div>
          )}

          {/* Error */}
          {error && (
            <div className="mt-4 p-3 bg-red-50 dark:bg-red-900/20 text-red-600 dark:text-red-400 rounded-lg text-sm">
              {error}
            </div>
          )}

          {/* Download Button */}
          <div className="mt-6">
            <button
              onClick={generatePack}
              disabled={generating || (useCustomTopics && customTopics.length === 0)}
              className="w-full py-4 bg-gradient-to-r from-green-600 to-emerald-600 text-white rounded-xl font-semibold hover:from-green-700 hover:to-emerald-700 transition-all flex items-center justify-center gap-3 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {generating ? (
                <>
                  <Loader2 className="w-5 h-5 animate-spin" />
                  {isUrdu ? "AI مواد تیار کر رہا ہے..." : "AI Generating Content..."}
                </>
              ) : (
                <>
                  <Sparkles className="w-5 h-5" />
                  {useCustomTopics 
                    ? (isUrdu ? `${customTopics.length} عنوانات پر پیکج بنائیں` : `Generate Pack with ${customTopics.length} Topics`)
                    : (isUrdu ? "AI آف لائن پیکج بنائیں" : "Generate AI Offline Pack")
                  }
                </>
              )}
            </button>
            
            <p className="text-center text-xs text-slate-500 dark:text-slate-400 mt-3">
              {isUrdu 
                ? "AI آپ کے لیے تعلیمی مواد تیار کرے گا - PCTB نصاب کے مطابق"
                : "AI will generate educational content for you - PCTB curriculum aligned"}
            </p>
          </div>

          {/* Available Packs */}
          {availablePacks.length > 0 && (
            <div className="mt-6 pt-6 border-t border-slate-200 dark:border-slate-700">
              <h3 className="text-sm font-medium text-slate-700 dark:text-slate-300 mb-3">
                {isUrdu ? "آپ کے پیکجز" : "Your Generated Packs"}
              </h3>
              <div className="space-y-2 max-h-48 overflow-y-auto">
                {availablePacks.slice(-5).reverse().map(pack => (
                  <div
                    key={pack.pack_id}
                    className="p-3 bg-slate-50 dark:bg-slate-700/50 rounded-lg"
                  >
                    <div className="flex items-center justify-between mb-2">
                      <div className="flex items-center gap-3">
                        <FileArchive className="w-5 h-5 text-blue-500" />
                        <div>
                          <p className="text-sm font-medium text-slate-700 dark:text-slate-300">
                            {isUrdu ? `جماعت ${pack.grade}` : `Grade ${pack.grade}`} - {pack.subject}
                          </p>
                          <p className="text-xs text-slate-500 dark:text-slate-400">
                            {formatSize(pack.size_bytes)} • {pack.language.toUpperCase()}
                          </p>
                        </div>
                      </div>
                      <button
                        onClick={() => downloadPack(pack.download_url, pack.pack_id)}
                        disabled={downloadProgress === pack.pack_id}
                        className="p-2 text-blue-600 hover:bg-blue-100 dark:hover:bg-blue-900/30 rounded-lg transition-colors"
                      >
                        {downloadProgress === pack.pack_id ? (
                          <CheckCircle2 className="w-5 h-5 text-green-500" />
                        ) : (
                          <Download className="w-5 h-5" />
                        )}
                      </button>
                    </div>
                    {pack.topics && pack.topics.length > 0 && (
                      <div className="flex flex-wrap gap-1 mt-2">
                        {pack.topics.slice(0, 4).map((topic, idx) => (
                          <span key={idx} className="px-2 py-0.5 text-xs bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-400 rounded">
                            {topic}
                          </span>
                        ))}
                        {pack.topics.length > 4 && (
                          <span className="px-2 py-0.5 text-xs bg-slate-200 dark:bg-slate-600 text-slate-600 dark:text-slate-300 rounded">
                            +{pack.topics.length - 4} more
                          </span>
                        )}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
