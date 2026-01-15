"use client";

import { useState } from "react";
import Link from "next/link";
import Image from "next/image";
import { usePathname } from "next/navigation";
import {
  Home,
  History,
  BookOpen,
  PenTool,
  Calculator,
  Microscope,
  Settings,
  Book,
  GraduationCap,
  Lightbulb,
  Github,
  Globe,
  ChevronsLeft,
  ChevronsRight,
  LayoutDashboard,
  FileText,
} from "lucide-react";
import { useGlobal } from "@/context/GlobalContext";
import { getTranslation } from "@/lib/i18n";

const SIDEBAR_EXPANDED_WIDTH = 256;
const SIDEBAR_COLLAPSED_WIDTH = 64;

export default function Sidebar() {
  const pathname = usePathname();
  const { uiSettings, sidebarCollapsed, toggleSidebar } = useGlobal();
  const lang = uiSettings.language;

  const t = (key: string) => getTranslation(lang, key);

  const [showTooltip, setShowTooltip] = useState<string | null>(null);

  const navGroups = [
    {
      name: "",
      items: [
        { name: t("Home"), href: "/", icon: Home },
        { name: t("Dashboard"), href: "/dashboard", icon: LayoutDashboard },
        { name: t("History"), href: "/history", icon: History },
        { name: t("Knowledge Bases"), href: "/knowledge", icon: BookOpen },
        { name: t("Notes Assistant"), href: "/notes-assistant", icon: FileText },
        { name: t("Notebooks"), href: "/notebook", icon: Book },
      ],
    },
    {
      name: t("Learn"),
      items: [
        { name: t("Question Generator"), href: "/question", icon: PenTool },
        { name: t("Smart Solver"), href: "/solver", icon: Calculator },
        { name: t("Guided Learning"), href: "/guide", icon: GraduationCap },
      ],
    },
    {
      name: t("Research"),
      items: [
        { name: t("IdeaGen"), href: "/ideagen", icon: Lightbulb },
        { name: t("Deep Research"), href: "/research", icon: Microscope },
      ],
    },
  ];

  const currentWidth = sidebarCollapsed
    ? SIDEBAR_COLLAPSED_WIDTH
    : SIDEBAR_EXPANDED_WIDTH;

  // Collapsed sidebar
  if (sidebarCollapsed) {
    return (
      <div
        className="relative flex-shrink-0 h-full flex flex-col"
        style={{ 
          width: SIDEBAR_COLLAPSED_WIDTH,
          background: '#0F0F0F',
          borderRight: '1px solid #1F1F1F'
        }}
      >
        {/* Header */}
        <div className="px-2 py-4 flex justify-center" style={{ borderBottom: '1px solid #1F1F1F' }}>
          <div className="w-10 h-10 flex items-center justify-center overflow-hidden shadow-emerald-glow" style={{ borderRadius: '20px', background: 'linear-gradient(135deg, #10B981 0%, #059669 100%)' }}>
            <Image
              src="/logo.png"
              alt="Synchora Logo"
              width={36}
              height={36}
              className="object-contain"
              priority
            />
          </div>
        </div>

        {/* Navigation */}
        <nav className="flex-1 overflow-y-auto py-4 space-y-2 scrollbar-thin">
          {navGroups.map((group, idx) => (
            <div key={idx} className="space-y-1 px-2">
              {group.items.map((item) => {
                const isActive = pathname === item.href;
                return (
                  <div key={item.href} className="relative">
                    <Link
                      href={item.href}
                      className="group flex items-center justify-center p-3 transition-all duration-300"
                      style={{
                        borderRadius: '20px',
                        background: isActive ? 'linear-gradient(135deg, #10B981 0%, #059669 100%)' : 'transparent',
                        color: isActive ? '#050505' : 'rgba(248, 250, 252, 0.6)',
                        boxShadow: isActive ? '0 0 20px rgba(16, 185, 129, 0.3)' : 'none'
                      }}
                      onMouseEnter={() => setShowTooltip(item.href)}
                      onMouseLeave={() => setShowTooltip(null)}
                    >
                      <item.icon
                        className="w-5 h-5 flex-shrink-0 transition-transform group-hover:scale-110"
                        style={{ color: isActive ? '#050505' : undefined }}
                      />
                    </Link>
                    {showTooltip === item.href && (
                      <div className="absolute left-full ml-3 top-1/2 -translate-y-1/2 z-50 px-3 py-2 text-xs font-medium rounded-xl whitespace-nowrap pointer-events-none animate-fade-in" style={{ background: '#161616', color: '#10B981', border: '1px solid #1F1F1F', boxShadow: '0 0 20px rgba(16, 185, 129, 0.2)' }}>
                        {item.name}
                        <div className="absolute right-full top-1/2 -translate-y-1/2 border-[6px] border-transparent" style={{ borderRightColor: '#161616' }} />
                      </div>
                    )}
                  </div>
                );
              })}
              {idx < navGroups.length - 1 && (
                <div className="h-px my-3" style={{ background: 'linear-gradient(to right, transparent, #1F1F1F, transparent)' }} />
              )}
            </div>
          ))}
        </nav>

        {/* Footer */}
        <div className="px-2 py-3" style={{ borderTop: '1px solid #1F1F1F', background: 'rgba(15, 15, 15, 0.5)' }}>
          <div className="relative">
            <Link
              href="/settings"
              className="flex items-center justify-center p-3 transition-all duration-300"
              style={{
                borderRadius: '20px',
                background: pathname === "/settings" ? 'linear-gradient(135deg, #10B981 0%, #059669 100%)' : 'transparent',
                color: pathname === "/settings" ? '#050505' : 'rgba(248, 250, 252, 0.6)',
                boxShadow: pathname === "/settings" ? '0 0 20px rgba(16, 185, 129, 0.3)' : 'none'
              }}
              onMouseEnter={() => setShowTooltip("/settings")}
              onMouseLeave={() => setShowTooltip(null)}
            >
              <Settings className="w-5 h-5 flex-shrink-0" />
            </Link>
            {showTooltip === "/settings" && (
              <div className="absolute left-full ml-3 top-1/2 -translate-y-1/2 z-50 px-3 py-2 text-xs font-medium rounded-xl whitespace-nowrap pointer-events-none animate-fade-in" style={{ background: '#161616', color: '#10B981', border: '1px solid #1F1F1F', boxShadow: '0 0 20px rgba(16, 185, 129, 0.2)' }}>
                {t("Settings")}
                <div className="absolute right-full top-1/2 -translate-y-1/2 border-[6px] border-transparent" style={{ borderRightColor: '#161616' }} />
              </div>
            )}
          </div>

          {/* Expand button at bottom */}
          <button
            onClick={toggleSidebar}
            className="w-full mt-2 flex items-center justify-center p-3 transition-all duration-300"
            style={{ borderRadius: '20px', color: 'rgba(248, 250, 252, 0.6)' }}
            title={t("Expand sidebar")}
          >
            <ChevronsRight className="w-4 h-4" />
          </button>
        </div>
      </div>
    );
  }

  // Expanded sidebar
  return (
    <div
      className="relative flex-shrink-0 h-full flex flex-col"
      style={{ 
        width: currentWidth,
        background: '#0F0F0F',
        borderRight: '1px solid #1F1F1F'
      }}
    >
      {/* Header */}
      <div className="px-4 py-4" style={{ borderBottom: '1px solid #1F1F1F' }}>
        <div className="flex flex-col gap-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 flex items-center justify-center overflow-hidden shadow-emerald-glow" style={{ borderRadius: '20px', background: 'linear-gradient(135deg, #10B981 0%, #059669 100%)' }}>
                <Image
                  src="/logo.png"
                  alt="Synchora Logo"
                  width={36}
                  height={36}
                  className="object-contain"
                  priority
                />
              </div>
              <h1 className="font-bold tracking-tight text-lg truncate" style={{ 
                background: 'linear-gradient(to right, #10B981, #34D399)',
                WebkitBackgroundClip: 'text',
                WebkitTextFillColor: 'transparent',
                backgroundClip: 'text'
              }}>
                Syncora
              </h1>
            </div>
            <div className="flex items-center gap-1">
              {/* Collapse button */}
              <button
                onClick={toggleSidebar}
                className="p-2 transition-all duration-300"
                style={{ borderRadius: '12px', color: 'rgba(248, 250, 252, 0.6)' }}
                title={t("Collapse sidebar")}
              >
                <ChevronsLeft className="w-4 h-4" />
              </button>
              <a
                href="https://hkuds.github.io/DeepTutor/"
                target="_blank"
                rel="noopener noreferrer"
                className="p-2 transition-all duration-300"
                style={{ borderRadius: '12px', color: 'rgba(248, 250, 252, 0.6)' }}
                title="Visit Syncora Homepage"
              >
                <Globe className="w-4 h-4" />
              </a>
              <a
                href="#"
                target="_blank"
                rel="noopener noreferrer"
                className="p-2 transition-all duration-300"
                style={{ borderRadius: '12px', color: 'rgba(248, 250, 252, 0.6)' }}
                title="View on GitHub"
              >
                <Github className="w-4 h-4" />
              </a>
            </div>
          </div>

          <div className="text-xs font-semibold px-3 py-2 truncate" style={{ 
            background: 'rgba(16, 185, 129, 0.1)', 
            color: '#10B981', 
            borderRadius: '12px',
            border: '1px solid rgba(16, 185, 129, 0.2)'
          }}>
            ✨ Synchora Team
          </div>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 overflow-y-auto px-3 py-4 space-y-4 scrollbar-thin">
        {navGroups.map((group, idx) => (
          <div key={idx}>
            {group.name && (
              <div className="text-xs font-bold uppercase tracking-wider px-3 mb-2 truncate" style={{ color: 'rgba(16, 185, 129, 0.7)' }}>
                {group.name}
              </div>
            )}
            <div className="space-y-1">
              {group.items.map((item) => {
                const isActive = pathname === item.href;
                return (
                  <Link
                    key={item.href}
                    href={item.href}
                    className="group flex items-center gap-3 px-3 py-2.5 transition-all duration-300"
                    style={{
                      borderRadius: '20px',
                      background: isActive ? 'linear-gradient(135deg, #10B981 0%, #059669 100%)' : 'transparent',
                      color: isActive ? '#050505' : 'rgba(248, 250, 252, 0.85)',
                      boxShadow: isActive ? '0 0 20px rgba(16, 185, 129, 0.3)' : 'none',
                      fontWeight: '600'
                    }}
                  >
                    <item.icon
                      className="w-5 h-5 flex-shrink-0 transition-transform group-hover:scale-110"
                      style={{ color: isActive ? '#050505' : undefined }}
                    />
                    <span className="text-sm truncate">
                      {item.name}
                    </span>
                  </Link>
                );
              })}
            </div>
          </div>
        ))}
      </nav>

      {/* Footer */}
      <div className="px-3 py-3" style={{ borderTop: '1px solid #1F1F1F', background: 'rgba(15, 15, 15, 0.5)' }}>
        <Link
          href="/settings"
          className="w-full flex items-center gap-3 px-3 py-2.5 text-sm transition-all duration-300"
          style={{
            borderRadius: '20px',
            background: pathname === "/settings" ? 'linear-gradient(135deg, #10B981 0%, #059669 100%)' : 'transparent',
            color: pathname === "/settings" ? '#050505' : 'rgba(248, 250, 252, 0.85)',
            boxShadow: pathname === "/settings" ? '0 0 20px rgba(16, 185, 129, 0.3)' : 'none',
            fontWeight: '600'
          }}
        >
          <Settings
            className="w-5 h-5 flex-shrink-0"
            style={{ color: pathname === "/settings" ? '#050505' : undefined }}
          />
          <span>{t("Settings")}</span>
        </Link>
      </div>
    </div>
  );
}
