"use client";

import React, { useEffect, useRef, useState } from "react";
import mermaid from "mermaid";

interface MermaidProps {
  chart: string;
  className?: string;
}

// Initialize mermaid with custom config
mermaid.initialize({
  startOnLoad: false,
  theme: "neutral",
  securityLevel: "loose",
  fontFamily: "ui-sans-serif, system-ui, sans-serif",
  flowchart: {
    useMaxWidth: true,
    htmlLabels: true,
    curve: "basis",
  },
  themeVariables: {
    primaryColor: "#6366f1",
    primaryTextColor: "#1e293b",
    primaryBorderColor: "#c7d2fe",
    lineColor: "#94a3b8",
    secondaryColor: "#f1f5f9",
    tertiaryColor: "#f8fafc",
  },
});

let mermaidIdCounter = 0;

/**
 * Sanitize and fix common syntax errors in LLM-generated Mermaid diagrams
 */
function sanitizeMermaidCode(code: string): string {
  let cleaned = code.trim();
  
  // Remove markdown code block markers if present
  cleaned = cleaned.replace(/^```mermaid\s*/i, '').replace(/```\s*$/i, '');
  
  // Fix common LLM mistakes:
  
  // 1. Fix "graph LR" or "graph TD" at beginning (ensure proper casing)
  cleaned = cleaned.replace(/^(graph|flowchart)\s+(lr|td|tb|rl|bt)/i, (match, type, dir) => {
    return `${type.toLowerCase()} ${dir.toUpperCase()}`;
  });
  
  // 2. Fix "sequenceDiagram" casing
  cleaned = cleaned.replace(/^sequencediagram/i, 'sequenceDiagram');
  
  // 3. Fix "classDiagram" casing  
  cleaned = cleaned.replace(/^classdiagram/i, 'classDiagram');
  
  // 4. Fix "stateDiagram" casing
  cleaned = cleaned.replace(/^statediagram(-v2)?/i, 'stateDiagram-v2');
  
  // 5. Remove problematic characters from node labels
  // Replace smart quotes with regular quotes
  cleaned = cleaned.replace(/[""]/g, '"').replace(/['']/g, "'");
  
  // 6. Fix arrow syntax: --> should not have spaces around it in some contexts
  cleaned = cleaned.replace(/\s*-->\s*/g, ' --> ');
  cleaned = cleaned.replace(/\s*---\s*/g, ' --- ');
  cleaned = cleaned.replace(/\s*-\.->\s*/g, ' -.-> ');
  
  // 7. Ensure subgraph has proper syntax
  cleaned = cleaned.replace(/subgraph\s+([^\[\n]+)\[/g, 'subgraph $1 [');
  
  // 8. Fix participant declarations in sequence diagrams
  cleaned = cleaned.replace(/participant\s+([^:\n]+):\s*/g, 'participant $1: ');
  
  // 9. Remove trailing whitespace from each line
  cleaned = cleaned.split('\n').map(line => line.trimEnd()).join('\n');
  
  // 10. Remove empty lines at start and end
  cleaned = cleaned.replace(/^\s*\n/, '').replace(/\n\s*$/, '');
  
  return cleaned;
}

export const Mermaid: React.FC<MermaidProps> = ({ chart, className = "" }) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const [svg, setSvg] = useState<string>("");
  const [error, setError] = useState<string | null>(null);
  const [id] = useState(() => `mermaid-${++mermaidIdCounter}`);

  useEffect(() => {
    const renderChart = async () => {
      if (!chart || !containerRef.current) return;

      try {
        // Clean up and sanitize the chart code
        const cleanedChart = sanitizeMermaidCode(chart);
        
        // Skip empty diagrams
        if (!cleanedChart || cleanedChart.length < 5) {
          setError("Empty or invalid diagram");
          return;
        }

        // Validate and render
        const { svg: renderedSvg } = await mermaid.render(id, cleanedChart);
        setSvg(renderedSvg);
        setError(null);
      } catch (err) {
        console.error("Mermaid rendering error:", err);
        setError(
          err instanceof Error ? err.message : "Failed to render diagram",
        );
      }
    };

    renderChart();
  }, [chart, id]);

  if (error) {
    return (
      <div
        className={`my-4 p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg ${className}`}
      >
        <p className="text-red-600 dark:text-red-400 text-sm font-medium mb-2">
          Diagram rendering error
        </p>
        <pre className="text-xs text-red-500 dark:text-red-400 whitespace-pre-wrap">{error}</pre>
        <details className="mt-2">
          <summary className="text-xs text-slate-500 dark:text-slate-400 cursor-pointer">
            Show source
          </summary>
          <pre className="mt-2 p-2 bg-slate-100 dark:bg-slate-800 rounded text-xs overflow-x-auto text-slate-700 dark:text-slate-300">
            {chart}
          </pre>
        </details>
      </div>
    );
  }

  return (
    <div
      ref={containerRef}
      className={`my-6 flex justify-center overflow-x-auto ${className}`}
      dangerouslySetInnerHTML={{ __html: svg }}
    />
  );
};

export default Mermaid;
