"use client";

import React, { useState, useEffect, useCallback } from "react";
import {
  Trophy,
  Target,
  BookOpen,
  Star,
  Flame,
  ChevronRight,
  Download,
  Users,
  TrendingUp,
  Award,
  Clock,
  Activity,
  X,
  Play,
  GraduationCap,
  MessageSquare,
  HelpCircle,
  Lightbulb,
  CheckCircle2,
  Sparkles,
  ArrowRight,
  Settings,
  ChevronDown,
  User,
  Save,
  Cpu,
} from "lucide-react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useGlobal } from "@/context/GlobalContext";
import { apiUrl } from "@/lib/api";
import { getTranslation } from "@/lib/i18n";
import { AgentTraceInline } from "@/components/AgentTraceViewer";
import OfflinePackDownload from "@/components/OfflinePackDownload";

// ============================================================================
// Local Storage Keys for Persistence
// ============================================================================
const STORAGE_KEYS = {
  STUDENT_ID: "syncora_student_id",
  STUDENT_NAME: "syncora_student_name",
  STUDENT_GRADE: "syncora_student_grade",
  SHOW_WELCOME: "syncora_show_welcome",
  STUDY_TIME: "syncora_study_time",
  QUESTIONS_ASKED: "syncora_questions_asked",
  LAST_ACTIVITY: "syncora_last_activity",
} as const;

// Available grades for Pakistani curriculum
const AVAILABLE_GRADES = [
  { value: 6, label: "Grade 6", labelUr: "جماعت 6" },
  { value: 7, label: "Grade 7", labelUr: "جماعت 7" },
  { value: 8, label: "Grade 8", labelUr: "جماعت 8" },
  { value: 9, label: "Grade 9", labelUr: "جماعت 9" },
  { value: 10, label: "Grade 10", labelUr: "جماعت 10" },
  { value: 11, label: "Grade 11 (FSc)", labelUr: "جماعت 11 (ایف ایس سی)" },
  { value: 12, label: "Grade 12 (FSc)", labelUr: "جماعت 12 (ایف ایس سی)" },
];

// ============================================================================
// Type Definitions
// ============================================================================
interface StudentProfile {
  id: string;
  name: string;
  name_ur?: string;
  grade: number;
  language: string;
  points: number;
  streak_days: number;
  badges: string[];
  created_at?: string;
}

interface SubjectProgress {
  subject: string;
  subject_ur: string;
  mastery_score: number;
  topics_completed: number;
  total_topics: number;
}

interface StudentStats {
  total_study_time: number;
  questions_asked: number;
  assessments_completed: number;
  average_score: number;
  subjects_progress: SubjectProgress[];
}

interface CurriculumTopic {
  id: string;
  name: string;
  name_ur?: string;
  subject_id?: string;
  difficulty: string;
}

interface Subject {
  id: string;
  name: string;
  name_ur?: string;
  grade: number;
}

// ============================================================================
// Main Dashboard Component
// ============================================================================
export default function StudentDashboard() {
  const router = useRouter();
  const { uiSettings } = useGlobal();
  const isUrdu = uiSettings.language === "ur";
  const t = (key: string) => getTranslation(uiSettings.language, key);

  // State
  const [profile, setProfile] = useState<StudentProfile | null>(null);
  const [stats, setStats] = useState<StudentStats | null>(null);
  const [topics, setTopics] = useState<CurriculumTopic[]>([]);
  const [subjects, setSubjects] = useState<Subject[]>([]);
  const [loading, setLoading] = useState(true);
  const [showWelcomeDialog, setShowWelcomeDialog] = useState(false);
  const [showOnboarding, setShowOnboarding] = useState(false);
  const [showProfileSettings, setShowProfileSettings] = useState(false);
  const [selectedGrade, setSelectedGrade] = useState<number>(9);
  const [error, setError] = useState<string | null>(null);
  const [savingProfile, setSavingProfile] = useState(false);
  const [showOfflineModal, setShowOfflineModal] = useState(false);
  const [showAgentTrace, setShowAgentTrace] = useState(false);

  // ============================================================================
  // Data Fetching
  // ============================================================================
  
  // Initialize grade from localStorage
  useEffect(() => {
    const savedGrade = localStorage.getItem(STORAGE_KEYS.STUDENT_GRADE);
    if (savedGrade) {
      setSelectedGrade(parseInt(savedGrade));
    }
  }, []);

  // Get or create student ID
  const getOrCreateStudentId = useCallback(async (): Promise<string> => {
    // Check localStorage first
    const savedId = localStorage.getItem(STORAGE_KEYS.STUDENT_ID);
    const savedName = localStorage.getItem(STORAGE_KEYS.STUDENT_NAME);
    const savedGrade = localStorage.getItem(STORAGE_KEYS.STUDENT_GRADE);
    const grade = savedGrade ? parseInt(savedGrade) : selectedGrade;
    
    if (savedId) {
      // Verify student exists
      try {
        const res = await fetch(apiUrl(`/api/v1/student/students/${savedId}`));
        if (res.ok) {
          return savedId;
        }
      } catch {
        // Student doesn't exist, create new
      }
    }
    
    // Create new student
    try {
      const res = await fetch(apiUrl("/api/v1/student/students"), {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          name: savedName || (isUrdu ? "طالب علم" : "Student"),
          name_ur: "طالب علم",
          grade: grade,
          language: isUrdu ? "ur" : "en",
          board: "punjab",
          subjects: [`math_${grade}`, `science_${grade}`, `english_${grade}`, `urdu_${grade}`],
        }),
      });
      
      if (res.ok) {
        const data = await res.json();
        localStorage.setItem(STORAGE_KEYS.STUDENT_ID, data.id);
        localStorage.setItem(STORAGE_KEYS.STUDENT_GRADE, String(grade));
        localStorage.setItem(STORAGE_KEYS.SHOW_WELCOME, "true");
        return data.id;
      }
    } catch (e) {
      console.error("Failed to create student:", e);
    }
    
    // Fallback to demo ID
    return "demo_student";
  }, [isUrdu, selectedGrade]);

  // Fetch student profile
  const fetchProfile = useCallback(async (studentId: string): Promise<StudentProfile | null> => {
    // Get saved values from localStorage (these take priority)
    const savedName = localStorage.getItem(STORAGE_KEYS.STUDENT_NAME);
    const savedGrade = localStorage.getItem(STORAGE_KEYS.STUDENT_GRADE);
    
    try {
      const res = await fetch(apiUrl(`/api/v1/student/students/${studentId}`));
      if (res.ok) {
        const data = await res.json();
        return {
          id: data.id,
          // Use localStorage values if available (more recent), otherwise use API values
          name: savedName || data.name,
          name_ur: savedName || data.name_ur || data.name,
          grade: savedGrade ? parseInt(savedGrade) : (data.grade || 9),
          language: data.language || "en",
          points: data.points || 0,
          streak_days: data.streak_days || 0,
          badges: data.badges || [],
          created_at: data.created_at,
        };
      }
    } catch (e) {
      console.error("Failed to fetch profile:", e);
    }
    return null;
  }, []);

  // Fetch student stats
  const fetchStats = useCallback(async (studentId: string): Promise<StudentStats | null> => {
    try {
      const res = await fetch(apiUrl(`/api/v1/student/students/${studentId}/stats`));
      if (res.ok) {
        const data = await res.json();
        
        // Also get local storage data for study time and questions
        const localStudyTime = parseInt(localStorage.getItem(STORAGE_KEYS.STUDY_TIME) || "0");
        const localQuestions = parseInt(localStorage.getItem(STORAGE_KEYS.QUESTIONS_ASKED) || "0");
        
        return {
          total_study_time: data.total_study_time || localStudyTime,
          questions_asked: data.questions_asked || localQuestions,
          assessments_completed: data.assessments_completed || 0,
          average_score: data.average_score || 0,
          subjects_progress: data.subjects_progress || [],
        };
      }
    } catch (e) {
      console.error("Failed to fetch stats:", e);
    }
    
    // Return stats from local storage if API fails
    const localStudyTime = parseInt(localStorage.getItem(STORAGE_KEYS.STUDY_TIME) || "0");
    const localQuestions = parseInt(localStorage.getItem(STORAGE_KEYS.QUESTIONS_ASKED) || "0");
    
    return {
      total_study_time: localStudyTime,
      questions_asked: localQuestions,
      assessments_completed: 0,
      average_score: 0,
      subjects_progress: [],
    };
  }, []);

  // Fetch subjects
  const fetchSubjects = useCallback(async (grade: number): Promise<Subject[]> => {
    try {
      const res = await fetch(apiUrl(`/api/v1/curriculum/subjects?grade=${grade}`));
      if (res.ok) {
        return await res.json();
      }
    } catch (e) {
      console.error("Failed to fetch subjects:", e);
    }
    return [];
  }, []);

  // Fetch curriculum topics
  const fetchTopics = useCallback(async (grade: number): Promise<CurriculumTopic[]> => {
    try {
      const res = await fetch(apiUrl(`/api/v1/curriculum/topics?grade=${grade}&limit=6`));
      if (res.ok) {
        return await res.json();
      }
    } catch (e) {
      console.error("Failed to fetch topics:", e);
    }
    return [];
  }, []);

  // Calculate progress from subjects if not in stats
  const calculateSubjectProgress = useCallback((
    subjectsList: Subject[],
    statsProgress: SubjectProgress[],
    gradeToUse: number // Added grade parameter
  ): SubjectProgress[] => {
    if (statsProgress && statsProgress.length > 0) {
      return statsProgress;
    }
    
    // Generate default progress for each subject based on grade
    const getSubjectNames = (grade: number) => {
      const subjects: Record<string, { en: string; ur: string }> = {};
      subjects[`math_${grade}`] = { en: "Mathematics", ur: "ریاضی" };
      subjects[`science_${grade}`] = { en: "Science", ur: "سائنس" };
      subjects[`english_${grade}`] = { en: "English", ur: "انگریزی" };
      subjects[`urdu_${grade}`] = { en: "Urdu", ur: "اردو" };
      if (grade >= 9) {
        subjects[`physics_${grade}`] = { en: "Physics", ur: "طبیعیات" };
        subjects[`chemistry_${grade}`] = { en: "Chemistry", ur: "کیمیا" };
        subjects[`biology_${grade}`] = { en: "Biology", ur: "حیاتیات" };
      }
      return subjects;
    };
    
    const subjectNameMap = getSubjectNames(gradeToUse);
    
    return subjectsList.map((sub) => ({
      subject: subjectNameMap[sub.id]?.en || sub.name,
      subject_ur: subjectNameMap[sub.id]?.ur || sub.name_ur || sub.name,
      mastery_score: 0,
      topics_completed: 0,
      total_topics: 10, // Default
    }));
  }, []);

  // Main data fetching function
  const fetchDashboardData = useCallback(async (grade?: number) => {
    const currentGrade = grade ?? selectedGrade;
    try {
      setLoading(true);
      setError(null);
      
      // Get or create student
      const studentId = await getOrCreateStudentId();
      
      // Fetch all data in parallel
      const [profileData, statsData, subjectsData, topicsData] = await Promise.all([
        fetchProfile(studentId),
        fetchStats(studentId),
        fetchSubjects(currentGrade),
        fetchTopics(currentGrade),
      ]);
      
      // Set profile (with fallback)
      if (profileData) {
        setProfile(profileData);
        setSelectedGrade(profileData.grade);
      } else {
        setProfile({
          id: studentId,
          name: isUrdu ? "طالب علم" : "Student",
          name_ur: "طالب علم",
          grade: currentGrade,
          language: isUrdu ? "ur" : "en",
          points: 0,
          streak_days: 0,
          badges: [],
        });
      }
      
      // Set subjects
      setSubjects(subjectsData);
      
      // Set stats with calculated progress
      if (statsData) {
        const progress = calculateSubjectProgress(subjectsData, statsData.subjects_progress, currentGrade);
        setStats({
          ...statsData,
          subjects_progress: progress,
        });
      } else {
        setStats({
          total_study_time: 0,
          questions_asked: 0,
          assessments_completed: 0,
          average_score: 0,
          subjects_progress: calculateSubjectProgress(subjectsData, [], currentGrade),
        });
      }
      
      // Set topics
      setTopics(topicsData);
      
      // Check if we should show welcome dialog
      const showWelcome = localStorage.getItem(STORAGE_KEYS.SHOW_WELCOME);
      if (showWelcome === "true") {
        setShowWelcomeDialog(true);
        localStorage.setItem(STORAGE_KEYS.SHOW_WELCOME, "false");
      }
      
      // Update streak
      try {
        await fetch(apiUrl(`/api/v1/student/students/${studentId}/streak`), {
          method: "POST",
        });
      } catch {
        // Ignore streak update errors
      }
      
    } catch (err) {
      console.error("Failed to fetch dashboard data:", err);
      setError(isUrdu ? "ڈیٹا لوڈ کرنے میں ناکام" : "Failed to load data");
    } finally {
      setLoading(false);
    }
  }, [getOrCreateStudentId, fetchProfile, fetchStats, fetchSubjects, fetchTopics, calculateSubjectProgress, isUrdu]);

  // Update student profile (name, grade)
  const updateStudentProfile = useCallback(async (newName: string, newGrade: number) => {
    if (!profile) return;
    
    setSavingProfile(true);
    try {
      // Try to update on backend
      let apiSuccess = false;
      try {
        const res = await fetch(apiUrl(`/api/v1/student/students/${profile.id}`), {
          method: "PUT",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            name: newName,
            name_ur: newName,
            grade: newGrade,
          }),
        });
        apiSuccess = res.ok;
      } catch {
        console.log("API update failed, continuing with local update");
      }
      
      // Always update localStorage regardless of API result
      localStorage.setItem(STORAGE_KEYS.STUDENT_NAME, newName);
      localStorage.setItem(STORAGE_KEYS.STUDENT_GRADE, String(newGrade));
      
      // Update local state immediately
      setProfile(prev => prev ? { 
        ...prev, 
        name: newName, 
        name_ur: newName, 
        grade: newGrade 
      } : null);
      setSelectedGrade(newGrade);
      
      // Close dialog
      setShowProfileSettings(false);
      
      // Fetch new subjects and topics for the new grade
      const [newSubjects, newTopics] = await Promise.all([
        fetchSubjects(newGrade),
        fetchTopics(newGrade),
      ]);
      
      setSubjects(newSubjects);
      setTopics(newTopics);
      
      // Update stats with new grade's subject progress
      if (stats) {
        const newProgress = calculateSubjectProgress(newSubjects, [], newGrade);
        setStats(prev => prev ? { ...prev, subjects_progress: newProgress } : null);
      }
      
    } catch (e) {
      console.error("Failed to update profile:", e);
    } finally {
      setSavingProfile(false);
    }
  }, [profile, fetchSubjects, fetchTopics, calculateSubjectProgress, stats]);

  // Fetch data on mount only (not on every dependency change)
  useEffect(() => {
    fetchDashboardData();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Track study time (update every 5 minutes)
  useEffect(() => {
    const interval = setInterval(() => {
      const current = parseInt(localStorage.getItem(STORAGE_KEYS.STUDY_TIME) || "0");
      localStorage.setItem(STORAGE_KEYS.STUDY_TIME, String(current + 5));
      localStorage.setItem(STORAGE_KEYS.LAST_ACTIVITY, new Date().toISOString());
    }, 5 * 60 * 1000); // Every 5 minutes
    
    return () => clearInterval(interval);
  }, []);

  // ============================================================================
  // Helper Functions
  // ============================================================================
  
  const getBadgeInfo = (badge: string): { icon: React.ReactNode; label: string; labelUr: string } => {
    const badgesMap: Record<string, { icon: React.ReactNode; label: string; labelUr: string }> = {
      first_question: {
        icon: <Star className="w-5 h-5 text-yellow-500" />,
        label: "First Question",
        labelUr: "پہلا سوال",
      },
      week_streak: {
        icon: <Flame className="w-5 h-5 text-orange-500" />,
        label: "Week Streak",
        labelUr: "ہفتہ کا سلسلہ",
      },
      math_master: {
        icon: <Trophy className="w-5 h-5 text-purple-500" />,
        label: "Math Master",
        labelUr: "ریاضی ماہر",
      },
      science_explorer: {
        icon: <Activity className="w-5 h-5 text-green-500" />,
        label: "Science Explorer",
        labelUr: "سائنس ایکسپلورر",
      },
      quick_learner: {
        icon: <Lightbulb className="w-5 h-5 text-blue-500" />,
        label: "Quick Learner",
        labelUr: "تیز سیکھنے والا",
      },
    };
    return badgesMap[badge] || { icon: <Award className="w-5 h-5" />, label: badge, labelUr: badge };
  };

  // ============================================================================
  // Render
  // ============================================================================
  
  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen" dir={isUrdu ? "rtl" : "ltr"}>
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-green-600 mx-auto"></div>
          <p className="mt-4 text-gray-600 dark:text-gray-400">
            {isUrdu ? "لوڈ ہو رہا ہے..." : "Loading..."}
          </p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center min-h-screen" dir={isUrdu ? "rtl" : "ltr"}>
        <div className="text-center">
          <p className="text-red-500 mb-4">{error}</p>
          <button
            onClick={() => fetchDashboardData()}
            className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700"
          >
            {isUrdu ? "دوبارہ کوشش کریں" : "Try Again"}
          </button>
        </div>
      </div>
    );
  }

  return (
    <div 
      className="min-h-screen p-6"
      style={{ backgroundColor: '#000000' }}
      dir={isUrdu ? "rtl" : "ltr"}
    >
      {/* Welcome Dialog */}
      {showWelcomeDialog && (
        <WelcomeDialog
          isUrdu={isUrdu}
          onClose={() => setShowWelcomeDialog(false)}
          onStartOnboarding={() => {
            setShowWelcomeDialog(false);
            setShowOnboarding(true);
          }}
        />
      )}

      {/* How to Start Study Dialog */}
      {showOnboarding && (
        <HowToStartStudyDialog
          isUrdu={isUrdu}
          onClose={() => setShowOnboarding(false)}
          router={router}
        />
      )}

      {/* Profile Settings Dialog */}
      {showProfileSettings && (
        <ProfileSettingsDialog
          isUrdu={isUrdu}
          profile={profile}
          selectedGrade={selectedGrade}
          onClose={() => setShowProfileSettings(false)}
          onSave={updateStudentProfile}
          saving={savingProfile}
        />
      )}

      {/* Header */}
      <div className="max-w-7xl mx-auto mb-8">
        <div className="flex items-center justify-between flex-wrap gap-4">
          <div className="flex items-center gap-4">
            <div>
              <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
                {isUrdu ? "خوش آمدید" : "Welcome"}, {isUrdu && profile?.name_ur ? profile.name_ur : profile?.name}! 👋
              </h1>
              <p className="text-gray-600 dark:text-gray-400 mt-1">
                {isUrdu
                  ? `جماعت ${profile?.grade} - PCTB نصاب`
                  : `Grade ${profile?.grade} - PCTB Curriculum`}
              </p>
            </div>
            {/* Profile Settings Button */}
            <button
              onClick={() => setShowProfileSettings(true)}
              className="p-2 rounded-full transition-colors"
              style={{ backgroundColor: '#0F0F0F' }}
              onMouseEnter={(e) => e.currentTarget.style.backgroundColor = '#161616'}
              onMouseLeave={(e) => e.currentTarget.style.backgroundColor = '#0F0F0F'}
              title={isUrdu ? "پروفائل سیٹنگز" : "Profile Settings"}
            >
              <Settings className="w-5 h-5 text-gray-600 dark:text-gray-400" />
            </button>
          </div>
          <div className="flex items-center gap-4 flex-wrap">
            <div className="flex items-center gap-2 bg-green-100 dark:bg-green-900/30 px-4 py-2 rounded-full">
              <Star className="w-5 h-5 text-green-600 dark:text-green-400" />
              <span className="font-bold text-green-700 dark:text-green-300">
                {profile?.points || 0} {isUrdu ? "پوائنٹس" : "points"}
              </span>
            </div>
            <div className="flex items-center gap-2 bg-orange-100 dark:bg-orange-900/30 px-4 py-2 rounded-full">
              <Flame className="w-5 h-5 text-orange-600 dark:text-orange-400" />
              <span className="font-bold text-orange-700 dark:text-orange-300">
                {profile?.streak_days || 0} {isUrdu ? "دن کا سلسلہ" : "day streak"}
              </span>
            </div>
            {/* How to Study Button */}
            <button
              onClick={() => setShowOnboarding(true)}
              className="flex items-center gap-2 px-4 py-2 rounded-full transition-colors"
              style={{ backgroundColor: '#0F0F0F', border: '1px solid #1F1F1F' }}
              onMouseEnter={(e) => e.currentTarget.style.backgroundColor = '#161616'}
              onMouseLeave={(e) => e.currentTarget.style.backgroundColor = '#0F0F0F'}
            >
              <HelpCircle className="w-5 h-5" style={{ color: '#10B981' }} />
              <span className="font-medium" style={{ color: '#10B981' }}>
                {isUrdu ? "مطالعہ کیسے کریں؟" : "How to Study?"}
              </span>
            </button>
          </div>
        </div>
      </div>

      {/* Stats Grid */}
      <div className="max-w-7xl mx-auto grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <StatCard
          icon={<Clock className="w-6 h-6 text-blue-500" />}
          label={isUrdu ? "کل مطالعہ کا وقت" : "Study Time"}
          value={`${Math.round((stats?.total_study_time || 0) / 60)}h`}
          trend={isUrdu ? "آج فعال" : "Active today"}
          trendUp={true}
        />
        <StatCard
          icon={<BookOpen className="w-6 h-6 text-purple-500" />}
          label={isUrdu ? "سوالات پوچھے" : "Questions Asked"}
          value={stats?.questions_asked?.toString() || "0"}
          trend={isUrdu ? "جاری رکھیں!" : "Keep going!"}
          trendUp={true}
        />
        <StatCard
          icon={<Target className="w-6 h-6 text-green-500" />}
          label={isUrdu ? "امتحانات مکمل" : "Assessments"}
          value={stats?.assessments_completed?.toString() || "0"}
          trend={isUrdu ? "اور لیں" : "Take more"}
          trendUp={false}
        />
        <StatCard
          icon={<TrendingUp className="w-6 h-6 text-orange-500" />}
          label={isUrdu ? "اوسط سکور" : "Average Score"}
          value={`${Math.round(stats?.average_score || 0)}%`}
          trend={stats?.average_score && stats.average_score > 70 
            ? (isUrdu ? "بہترین!" : "Great!") 
            : (isUrdu ? "بہتر کریں" : "Improve")}
          trendUp={(stats?.average_score || 0) > 70}
        />
      </div>

      {/* Main Content Grid */}
      <div className="max-w-7xl mx-auto grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Subject Progress */}
        <div className="lg:col-span-2 rounded-2xl shadow-sm p-6" style={{ backgroundColor: '#161616' }}>
          <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-6">
            {isUrdu ? "مضامین کی پیش رفت" : "Subject Progress"}
          </h2>
          {stats?.subjects_progress && stats.subjects_progress.length > 0 ? (
            <div className="space-y-6">
              {stats.subjects_progress.map((subject) => (
                <SubjectProgressBar
                  key={subject.subject}
                  subject={isUrdu ? subject.subject_ur : subject.subject}
                  progress={subject.mastery_score * 100}
                  completed={subject.topics_completed}
                  total={subject.total_topics}
                  isUrdu={isUrdu}
                />
              ))}
            </div>
          ) : (
            <div className="text-center py-8 text-gray-500 dark:text-gray-400">
              <BookOpen className="w-12 h-12 mx-auto mb-4 opacity-50" />
              <p>{isUrdu ? "ابھی کوئی پیش رفت نہیں" : "No progress yet"}</p>
              <p className="text-sm mt-2">
                {isUrdu ? "سیکھنا شروع کریں!" : "Start learning to track progress!"}
              </p>
            </div>
          )}
        </div>

        {/* Badges */}
        <div className="rounded-2xl shadow-sm p-6" style={{ backgroundColor: '#161616' }}>
          <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-6">
            {isUrdu ? "حاصل کیے گئے بیجز" : "Earned Badges"}
          </h2>
          {profile?.badges && profile.badges.length > 0 ? (
            <div className="grid grid-cols-3 gap-4">
              {profile.badges.map((badge) => {
                const badgeInfo = getBadgeInfo(badge);
                return (
                  <div
                    key={badge}
                    className="flex flex-col items-center p-3 rounded-xl"
                    style={{ backgroundColor: '#0F0F0F' }}
                  >
                    <div className="w-12 h-12 rounded-full flex items-center justify-center mb-2 shadow-sm" style={{ backgroundColor: '#161616' }}>
                      {badgeInfo.icon}
                    </div>
                    <span className="text-xs text-center text-gray-600 dark:text-gray-300">
                      {isUrdu ? badgeInfo.labelUr : badgeInfo.label}
                    </span>
                  </div>
                );
              })}
            </div>
          ) : (
            <div className="text-center py-8 text-gray-500 dark:text-gray-400">
              <Award className="w-12 h-12 mx-auto mb-4 opacity-50" />
              <p>{isUrdu ? "ابھی کوئی بیج نہیں" : "No badges yet"}</p>
              <p className="text-sm mt-2">
                {isUrdu ? "سیکھ کر بیج حاصل کریں!" : "Earn badges by learning!"}
              </p>
            </div>
          )}
        </div>
      </div>

      {/* Continue Learning Section */}
      <div className="max-w-7xl mx-auto mt-8 rounded-2xl shadow-sm p-6" style={{ backgroundColor: '#161616' }}>
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-xl font-bold" style={{ 
            background: 'linear-gradient(to right, #10B981, #34D399)',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
            backgroundClip: 'text'
          }}>
            {isUrdu ? "سیکھنا جاری رکھیں" : "Continue Learning"}
          </h2>
          <Link
            href="/guide"
            className="text-green-600 dark:text-green-400 hover:underline flex items-center gap-1"
          >
            {isUrdu ? "تمام دیکھیں" : "View all"}
            <ChevronRight className="w-4 h-4" />
          </Link>
        </div>
        {topics && topics.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {topics.map((topic) => (
              <TopicCard
                key={topic.id}
                topic={topic}
                isUrdu={isUrdu}
              />
            ))}
          </div>
        ) : (
          <div className="text-center py-8 text-gray-500 dark:text-gray-400">
            <Target className="w-12 h-12 mx-auto mb-4 opacity-50" />
            <p>{isUrdu ? "کوئی عنوانات دستیاب نہیں" : "No topics available"}</p>
            <button
              onClick={() => setShowOnboarding(true)}
              className="mt-4 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700"
            >
              {isUrdu ? "مطالعہ شروع کریں" : "Start Learning"}
            </button>
          </div>
        )}
      </div>

      {/* Quick Actions */}
      <div className="max-w-7xl mx-auto mt-8 grid grid-cols-1 md:grid-cols-4 gap-6">
        <QuickActionCard
          icon={<Target className="w-8 h-8 text-white" />}
          title={isUrdu ? "امتحان دیں" : "Take Assessment"}
          description={isUrdu ? "اپنے علم کی جانچ کریں" : "Test your knowledge"}
          href="/solver"
          bgColor="bg-gradient-to-r from-green-500 to-green-600"
        />
        <QuickActionCard
          icon={<Download className="w-8 h-8 text-white" />}
          title={isUrdu ? "آف لائن پیک" : "Offline Pack"}
          description={isUrdu ? "بغیر انٹرنیٹ کے سیکھیں" : "Learn without internet"}
          onClick={() => setShowOfflineModal(true)}
          bgColor="bg-gradient-to-r from-emerald-500 to-emerald-600"
        />
        <QuickActionCard
          icon={<Cpu className="w-8 h-8 text-white" />}
          title={isUrdu ? "ایجنٹ لاگز" : "Agent Logs"}
          description={isUrdu ? "AI تعاون دیکھیں" : "View AI collaboration"}
          onClick={() => setShowAgentTrace(true)}
          bgColor="bg-gradient-to-r from-amber-500 to-orange-600"
        />
        <QuickActionCard
          icon={<Users className="w-8 h-8 text-white" />}
          title={isUrdu ? "مدد حاصل کریں" : "Get Help"}
          description={isUrdu ? "AI ٹیوٹر سے پوچھیں" : "Ask AI tutor"}
          href="/"
          bgColor="bg-gradient-to-r from-purple-500 to-purple-600"
        />
      </div>

      {/* Offline Pack Modal */}
      {showOfflineModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="rounded-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto shadow-xl" style={{ backgroundColor: '#161616' }}>
            <div className="sticky top-0 p-4 flex justify-between items-center" style={{ backgroundColor: '#161616', borderBottom: '1px solid #1F1F1F' }}>
              <h2 className="text-xl font-bold text-gray-900 dark:text-white flex items-center gap-2">
                <Download className="w-6 h-6 text-green-500" />
                {isUrdu ? "آف لائن لرننگ پیک" : "Offline Learning Pack"}
              </h2>
              <button
                onClick={() => setShowOfflineModal(false)}
                className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-200"
              >
                <X className="w-6 h-6" />
              </button>
            </div>
            <OfflinePackDownload 
              isUrdu={isUrdu} 
              defaultGrade={selectedGrade}
              onClose={() => setShowOfflineModal(false)}
            />
          </div>
        </div>
      )}

      {/* Agent Trace Modal */}
      {showAgentTrace && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="rounded-2xl max-w-4xl w-full max-h-[90vh] overflow-y-auto shadow-xl" style={{ backgroundColor: '#161616' }}>
            <div className="sticky top-0 p-4 flex justify-between items-center" style={{ backgroundColor: '#161616', borderBottom: '1px solid #1F1F1F' }}>
              <h2 className="text-xl font-bold text-gray-900 dark:text-white flex items-center gap-2">
                <Cpu className="w-6 h-6 text-amber-500" />
                {isUrdu ? "ایجنٹ تعاون لاگز" : "Agent Collaboration Logs"}
              </h2>
              <button
                onClick={() => setShowAgentTrace(false)}
                className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-200"
              >
                <X className="w-6 h-6" />
              </button>
            </div>
            <div className="p-4">
              <AgentTraceInline isUrdu={isUrdu} />
            </div>
          </div>
        </div>
      )}

      {/* Footer */}
      <div className="max-w-7xl mx-auto mt-8 text-center text-gray-500 dark:text-gray-400 text-sm">
        <p>🇵🇰 {isUrdu ? "پاکستانی طلباء کے لیے بنایا گیا" : "Made for Pakistani Students"} | PCTB Aligned</p>
        <p>Syncora - EDU TECH Challenge 2025</p>
      </div>
    </div>
  );
}

// ============================================================================
// Welcome Dialog Component
// ============================================================================
function WelcomeDialog({
  isUrdu,
  onClose,
  onStartOnboarding,
}: {
  isUrdu: boolean;
  onClose: () => void;
  onStartOnboarding: () => void;
}) {
  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div 
        className="rounded-2xl max-w-md w-full p-6 shadow-xl relative"
        style={{ backgroundColor: '#161616' }}
        dir={isUrdu ? "rtl" : "ltr"}
      >
        <button
          onClick={onClose}
          className="absolute top-4 right-4 text-gray-400 hover:text-gray-600 dark:hover:text-gray-200"
        >
          <X className="w-5 h-5" />
        </button>
        <div className="text-center">
          <div className="w-20 h-20 rounded-full flex items-center justify-center mx-auto mb-4" style={{ background: 'linear-gradient(135deg, #10B981 0%, #059669 100%)' }}>
            <Sparkles className="w-10 h-10" style={{ color: '#050505' }} />
          </div>
          <h2 className="text-2xl font-bold mb-2" style={{ 
            background: 'linear-gradient(to right, #10B981, #34D399)',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
            backgroundClip: 'text'
          }}>
            {isUrdu ? "Synchore میں خوش آمدید! 🎉" : "Welcome to Synchore! 🎉"}
          </h2>
          <p className="text-gray-600 dark:text-gray-400 mb-6">
            {isUrdu 
              ? "آپ کا ذاتی AI ٹیوٹر جو PCTB نصاب کے مطابق ہے"
              : "Your personal AI tutor aligned with PCTB curriculum"}
          </p>
          
          <div className="space-y-3">
            <button
              onClick={onStartOnboarding}
              className="w-full py-3 rounded-xl font-medium transition-all duration-300 flex items-center justify-center gap-2 shadow-emerald-glow"
              style={{ background: 'linear-gradient(135deg, #10B981 0%, #059669 100%)', color: '#050505' }}
            >
              <Play className="w-5 h-5" />
              {isUrdu ? "شروع کرنے کا طریقہ دیکھیں" : "See How to Start"}
            </button>
            <button
              onClick={onClose}
              className="w-full py-3 rounded-xl font-medium transition-colors"
              style={{ backgroundColor: '#1F1F1F', color: '#9CA3AF' }}
              onMouseEnter={(e) => e.currentTarget.style.backgroundColor = '#2A2A2A'}
              onMouseLeave={(e) => e.currentTarget.style.backgroundColor = '#1F1F1F'}
            >
              {isUrdu ? "بعد میں" : "Maybe Later"}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

// ============================================================================
// How to Start Study Dialog Component
// ============================================================================
function HowToStartStudyDialog({
  isUrdu,
  onClose,
  router,
}: {
  isUrdu: boolean;
  onClose: () => void;
  router: ReturnType<typeof useRouter>;
}) {
  const [step, setStep] = useState(0);
  
  const steps = [
    {
      icon: <GraduationCap className="w-12 h-12 text-green-600" />,
      title: isUrdu ? "گائیڈڈ لرننگ" : "Guided Learning",
      titleDesc: isUrdu ? "قدم بہ قدم سیکھیں" : "Step-by-Step Learning",
      description: isUrdu
        ? "AI ٹیوٹر آپ کو PCTB نصاب کے مطابق قدم بہ قدم سکھائے گا۔ ہر عنوان کی مکمل وضاحت اور مثالیں ملیں گی۔"
        : "AI tutor will teach you step by step according to PCTB curriculum. Get complete explanations and examples for each topic.",
      action: () => router.push("/guide"),
      actionLabel: isUrdu ? "گائیڈ شروع کریں" : "Start Guide",
    },
    {
      icon: <MessageSquare className="w-12 h-12 text-blue-600" />,
      title: isUrdu ? "سوالات پوچھیں" : "Ask Questions",
      titleDesc: isUrdu ? "کوئی بھی سوال پوچھیں" : "Ask Anything",
      description: isUrdu
        ? "اپنے کسی بھی مضمون کے بارے میں سوالات پوچھیں۔ AI ٹیوٹر آپ کو اردو یا انگریزی میں جواب دے گا۔"
        : "Ask questions about any subject. The AI tutor will answer in Urdu or English as you prefer.",
      action: () => router.push("/"),
      actionLabel: isUrdu ? "چیٹ شروع کریں" : "Start Chat",
    },
    {
      icon: <Target className="w-12 h-12 text-purple-600" />,
      title: isUrdu ? "مسائل حل کریں" : "Solve Problems",
      titleDesc: isUrdu ? "ذہین حل کار" : "Smart Solver",
      description: isUrdu
        ? "ریاضی، سائنس یا کوئی بھی سوال دیں۔ AI اسے قدم بہ قدم حل کر کے دکھائے گا۔"
        : "Give any math, science, or other question. AI will solve it step by step.",
      action: () => router.push("/solver"),
      actionLabel: isUrdu ? "سوال حل کریں" : "Solve Problem",
    },
    {
      icon: <HelpCircle className="w-12 h-12 text-orange-600" />,
      title: isUrdu ? "سوالات بنائیں" : "Generate Questions",
      titleDesc: isUrdu ? "مشق کے لیے سوالات" : "Practice Questions",
      description: isUrdu
        ? "کسی بھی عنوان پر مشق کے سوالات بنوائیں۔ امتحان کی تیاری کے لیے بہترین۔"
        : "Generate practice questions on any topic. Perfect for exam preparation.",
      action: () => router.push("/question"),
      actionLabel: isUrdu ? "سوالات بنائیں" : "Generate Questions",
    },
  ];

  const currentStep = steps[step];

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div 
        className="rounded-2xl max-w-lg w-full p-6 shadow-xl relative"
        style={{ backgroundColor: '#161616' }}
        dir={isUrdu ? "rtl" : "ltr"}
      >
        {/* Close Button */}
        <button
          onClick={onClose}
          className="absolute top-4 right-4 text-gray-400 hover:text-gray-600 dark:hover:text-gray-200"
        >
          <X className="w-6 h-6" />
        </button>

        {/* Progress Dots */}
        <div className="flex justify-center gap-2 mb-6">
          {steps.map((_, i) => (
            <button
              key={i}
              onClick={() => setStep(i)}
              className="w-3 h-3 rounded-full transition-colors"
              style={{ backgroundColor: i === step ? '#10B981' : '#2A2A2A' }}
            />
          ))}
        </div>

        {/* Content */}
        <div className="text-center">
          <div className="w-24 h-24 rounded-full flex items-center justify-center mx-auto mb-4" style={{ backgroundColor: '#0F0F0F' }}>
            {currentStep.icon}
          </div>
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-1">
            {currentStep.title}
          </h2>
          <p className="text-green-600 dark:text-green-400 font-medium mb-4">
            {currentStep.titleDesc}
          </p>
          <p className="text-gray-600 dark:text-gray-400 mb-6 leading-relaxed">
            {currentStep.description}
          </p>

          {/* Action Buttons */}
          <div className="flex gap-3">
            {step > 0 && (
              <button
                onClick={() => setStep(step - 1)}
                className="flex-1 py-3 rounded-xl font-medium transition-colors"
                style={{ backgroundColor: '#1F1F1F', color: '#9CA3AF' }}
                onMouseEnter={(e) => e.currentTarget.style.backgroundColor = '#2A2A2A'}
                onMouseLeave={(e) => e.currentTarget.style.backgroundColor = '#1F1F1F'}
              >
                {isUrdu ? "پچھلا" : "Previous"}
              </button>
            )}
            {step < steps.length - 1 ? (
              <button
                onClick={() => setStep(step + 1)}
                className="flex-1 py-3 bg-green-600 text-white rounded-xl font-medium hover:bg-green-700 transition-colors flex items-center justify-center gap-2"
              >
                {isUrdu ? "اگلا" : "Next"}
                <ArrowRight className="w-5 h-5" />
              </button>
            ) : (
              <button
                onClick={() => {
                  onClose();
                  currentStep.action();
                }}
                className="flex-1 py-3 bg-green-600 text-white rounded-xl font-medium hover:bg-green-700 transition-colors flex items-center justify-center gap-2"
              >
                <CheckCircle2 className="w-5 h-5" />
                {currentStep.actionLabel}
              </button>
            )}
          </div>

          {/* Skip Link */}
          <button
            onClick={onClose}
            className="mt-4 text-sm text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-200"
          >
            {isUrdu ? "چھوڑیں اور ڈیش بورڈ پر جائیں" : "Skip and go to dashboard"}
          </button>
        </div>
      </div>
    </div>
  );
}

// ============================================================================
// Stat Card Component
// ============================================================================
function StatCard({
  icon,
  label,
  value,
  trend,
  trendUp,
}: {
  icon: React.ReactNode;
  label: string;
  value: string;
  trend: string;
  trendUp: boolean;
}) {
  return (
    <div className="rounded-2xl shadow-sm p-6" style={{ backgroundColor: '#0F0F0F', border: '1px solid #1F1F1F' }}>
      <div className="flex items-center gap-4">
        <div className="p-3 rounded-xl" style={{ backgroundColor: '#161616' }}>
          {icon}
        </div>
        <div>
          <p className="text-sm text-gray-500 dark:text-gray-400">{label}</p>
          <p className="text-2xl font-bold text-gray-900 dark:text-white">{value}</p>
          <p className={`text-xs ${trendUp ? "text-green-500" : "text-gray-500"}`}>
            {trend}
          </p>
        </div>
      </div>
    </div>
  );
}

// ============================================================================
// Subject Progress Bar Component
// ============================================================================
function SubjectProgressBar({
  subject,
  progress,
  completed,
  total,
  isUrdu,
}: {
  subject: string;
  progress: number;
  completed: number;
  total: number;
  isUrdu: boolean;
}) {
  return (
    <div>
      <div className="flex items-center justify-between mb-2">
        <span className="font-medium text-gray-900 dark:text-white">{subject}</span>
        <span className="text-sm text-gray-500 dark:text-gray-400">
          {completed}/{total} {isUrdu ? "عنوانات" : "topics"}
        </span>
      </div>
      <div className="h-3 rounded-full overflow-hidden" style={{ backgroundColor: '#1F1F1F' }}>
        <div
          className="h-full bg-gradient-to-r from-green-500 to-green-600 rounded-full transition-all duration-500"
          style={{ width: `${Math.min(progress, 100)}%` }}
        />
      </div>
      <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
        {Math.round(progress)}% {isUrdu ? "مکمل" : "complete"}
      </p>
    </div>
  );
}

// ============================================================================
// Topic Card Component
// ============================================================================
function TopicCard({
  topic,
  isUrdu,
}: {
  topic: CurriculumTopic;
  isUrdu: boolean;
}) {
  const difficultyColors: Record<string, { bg: string; text: string; border: string }> = {
    beginner: { bg: '#0F3D2F', text: '#10B981', border: '#10B981' },
    intermediate: { bg: '#4A3D0F', text: '#FBBF24', border: '#FBBF24' },
    advanced: { bg: '#4A0F0F', text: '#EF4444', border: '#EF4444' },
  };

  const difficultyLabels: Record<string, { en: string; ur: string }> = {
    beginner: { en: "Easy", ur: "آسان" },
    intermediate: { en: "Medium", ur: "درمیانی" },
    advanced: { en: "Hard", ur: "مشکل" },
  };

  const difficulty = topic.difficulty || 'intermediate';
  const colors = difficultyColors[difficulty] || difficultyColors.intermediate;

  return (
    <Link
      href={`/guide?topic=${topic.id}`}
      className="block p-4 rounded-xl transition-all duration-300"
      style={{ 
        backgroundColor: '#0F0F0F',
        border: '1px solid #1F1F1F'
      }}
      onMouseEnter={(e) => {
        e.currentTarget.style.backgroundColor = '#161616';
        e.currentTarget.style.borderColor = '#10B981';
      }}
      onMouseLeave={(e) => {
        e.currentTarget.style.backgroundColor = '#0F0F0F';
        e.currentTarget.style.borderColor = '#1F1F1F';
      }}
    >
      <div className="flex items-start justify-between mb-3">
        <div className="flex-1">
          <h3 className="font-medium text-white mb-2">
            {isUrdu && topic.name_ur ? topic.name_ur : topic.name}
          </h3>
          <span
            className="inline-block px-3 py-1 text-xs font-semibold rounded-full"
            style={{
              backgroundColor: colors.bg,
              color: colors.text,
              border: `1px solid ${colors.border}`
            }}
          >
            {isUrdu
              ? difficultyLabels[difficulty]?.ur || difficulty
              : difficultyLabels[difficulty]?.en || difficulty}
          </span>
        </div>
        <ChevronRight className="w-5 h-5 flex-shrink-0 ml-2" style={{ color: '#10B981' }} />
      </div>
    </Link>
  );
}

// ============================================================================
// Quick Action Card Component
// ============================================================================
function QuickActionCard({
  icon,
  title,
  description,
  href,
  onClick,
  bgColor,
}: {
  icon: React.ReactNode;
  title: string;
  description: string;
  href?: string;
  onClick?: () => void;
  bgColor: string;
}) {
  const content = (
    <div className="flex items-center gap-4">
      {icon}
      <div>
        <h3 className="font-bold text-lg">{title}</h3>
        <p className="text-white/80 text-sm">{description}</p>
      </div>
    </div>
  );

  if (onClick) {
    return (
      <button
        onClick={onClick}
        className={`${bgColor} rounded-2xl p-6 text-white hover:opacity-90 transition-opacity text-left w-full`}
      >
        {content}
      </button>
    );
  }

  return (
    <Link
      href={href || "#"}
      className={`${bgColor} rounded-2xl p-6 text-white hover:opacity-90 transition-opacity`}
    >
      {content}
    </Link>
  );
}

// ============================================================================
// Profile Settings Dialog Component
// ============================================================================
function ProfileSettingsDialog({
  isUrdu,
  profile,
  selectedGrade,
  onClose,
  onSave,
  saving,
}: {
  isUrdu: boolean;
  profile: StudentProfile | null;
  selectedGrade: number;
  onClose: () => void;
  onSave: (name: string, grade: number) => Promise<void>;
  saving: boolean;
}) {
  const [name, setName] = useState(profile?.name || "");
  const [grade, setGrade] = useState(selectedGrade);

  const handleSave = async () => {
    await onSave(name, grade);
  };

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div 
        className="rounded-2xl max-w-md w-full p-6 shadow-xl relative"
        style={{ backgroundColor: '#161616' }}
        dir={isUrdu ? "rtl" : "ltr"}
      >
        {/* Close Button */}
        <button
          onClick={onClose}
          className="absolute top-4 right-4 text-gray-400 hover:text-gray-600 dark:hover:text-gray-200"
        >
          <X className="w-5 h-5" />
        </button>

        <div className="text-center mb-6">
          <div className="w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4" style={{ backgroundColor: 'rgba(16, 185, 129, 0.1)' }}>
            <User className="w-8 h-8" style={{ color: '#10B981' }} />
          </div>
          <h2 className="text-xl font-bold text-gray-900 dark:text-white">
            {isUrdu ? "پروفائل سیٹنگز" : "Profile Settings"}
          </h2>
          <p className="text-gray-500 dark:text-gray-400 text-sm mt-1">
            {isUrdu ? "اپنا نام اور جماعت تبدیل کریں" : "Change your name and class"}
          </p>
        </div>

        <div className="space-y-4">
          {/* Name Input */}
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              {isUrdu ? "نام" : "Name"}
            </label>
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder={isUrdu ? "اپنا نام لکھیں" : "Enter your name"}
              className="w-full px-4 py-3 rounded-xl text-white focus:ring-2 focus:ring-green-500 focus:border-transparent"
              style={{ backgroundColor: '#0F0F0F', border: '1px solid #1F1F1F' }}
            />
          </div>

          {/* Grade Select */}
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              {isUrdu ? "جماعت" : "Class/Grade"}
            </label>
            <div className="relative">
              <select
                value={grade}
                onChange={(e) => setGrade(parseInt(e.target.value))}
                className="w-full px-4 py-3 rounded-xl text-white focus:ring-2 focus:ring-green-500 focus:border-transparent appearance-none cursor-pointer"
                style={{ backgroundColor: '#0F0F0F', border: '1px solid #1F1F1F' }}
              >
                {AVAILABLE_GRADES.map((g) => (
                  <option key={g.value} value={g.value}>
                    {isUrdu ? g.labelUr : g.label}
                  </option>
                ))}
              </select>
              <ChevronDown className="absolute right-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400 pointer-events-none" />
            </div>
          </div>

          {/* Info Box */}
          <div className="p-4 rounded-xl" style={{ backgroundColor: 'rgba(59, 130, 246, 0.1)', border: '1px solid rgba(59, 130, 246, 0.2)' }}>
            <p className="text-sm" style={{ color: '#60A5FA' }}>
              {isUrdu 
                ? "⚡ جماعت تبدیل کرنے سے نصاب اور عنوانات اپ ڈیٹ ہو جائیں گے"
                : "⚡ Changing your class will update the curriculum and topics"}
            </p>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex gap-3 mt-6">
          <button
            onClick={onClose}
            className="flex-1 py-3 rounded-xl font-medium transition-colors"
            style={{ backgroundColor: '#1F1F1F', color: '#9CA3AF' }}
            onMouseEnter={(e) => e.currentTarget.style.backgroundColor = '#2A2A2A'}
            onMouseLeave={(e) => e.currentTarget.style.backgroundColor = '#1F1F1F'}
          >
            {isUrdu ? "منسوخ" : "Cancel"}
          </button>
          <button
            onClick={handleSave}
            disabled={saving || !name.trim()}
            className="flex-1 py-3 bg-green-600 text-white rounded-xl font-medium hover:bg-green-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
          >
            {saving ? (
              <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
            ) : (
              <>
                <Save className="w-5 h-5" />
                {isUrdu ? "محفوظ کریں" : "Save"}
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  );
}
