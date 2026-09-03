import React from 'react';

interface FormattedMarkdownProps {
  content: string;
  className?: string;
  strongClassName?: string;
  bulletClassName?: string;
}

export const FormattedMarkdown: React.FC<FormattedMarkdownProps> = ({
  content,
  className = "text-zinc-800",
  strongClassName = "font-bold text-zinc-950",
  bulletClassName = "text-blue-600"
}) => {
  if (!content) return null;

  // Helper to parse inline markdown (bold, italic, inline code, links)
  const renderInline = (text: string): React.ReactNode[] => {
    // Matches **bold**, __bold__, `code`, *italic*, _italic_
    const regex = /(\*\*[^*]+?\*\*|__[^_]+?__|`[^`]+?`|\*[^*]+?\*|_[^_]+?_)/g;
    const parts = text.split(regex);

    return parts.map((part, index) => {
      if (!part) return null;

      // Bold: **text** or __text__
      if ((part.startsWith('**') && part.endsWith('**') && part.length >= 4) ||
          (part.startsWith('__') && part.endsWith('__') && part.length >= 4)) {
        return (
          <strong key={index} className={strongClassName}>
            {part.slice(2, -2)}
          </strong>
        );
      }

      // Inline code: `code`
      if (part.startsWith('`') && part.endsWith('`') && part.length >= 2) {
        return (
          <code key={index} className="px-1.5 py-0.5 rounded bg-zinc-100 dark:bg-zinc-800 text-[11px] font-mono text-blue-600 border border-zinc-200/60">
            {part.slice(1, -1)}
          </code>
        );
      }

      // Italic: *text* or _text_
      if ((part.startsWith('*') && part.endsWith('*') && part.length >= 2) ||
          (part.startsWith('_') && part.endsWith('_') && part.length >= 2)) {
        return (
          <em key={index} className="italic text-zinc-600">
            {part.slice(1, -1)}
          </em>
        );
      }

      return <span key={index}>{part}</span>;
    });
  };

  const lines = content.split('\n');

  // Check for table blocks
  const renderContent = () => {
    const elements: React.ReactNode[] = [];
    let inTable = false;
    let tableRows: string[] = [];

    const flushTable = (keyIdx: number) => {
      if (tableRows.length === 0) return;
      const headers = tableRows[0].split('|').map(c => c.trim()).filter(Boolean);
      // Skip separator row (|---|---|)
      const dataRows = tableRows.slice(1).filter(r => !/^\s*\|?\s*[-:]+[-| :]*\s*\|?\s*$/.test(r));

      elements.push(
        <div key={`table-${keyIdx}`} className="overflow-x-auto my-3 rounded-xl border border-zinc-200 shadow-xs">
          <table className="w-full text-xs text-left">
            {headers.length > 0 && (
              <thead className="bg-zinc-100/80 font-bold text-zinc-800 uppercase text-[10px] tracking-wider border-b border-zinc-200">
                <tr>
                  {headers.map((h, hIdx) => (
                    <th key={hIdx} className="px-3 py-2">{renderInline(h)}</th>
                  ))}
                </tr>
              </thead>
            )}
            <tbody className="divide-y divide-zinc-100 bg-white text-zinc-700">
              {dataRows.map((row, rIdx) => {
                const cols = row.split('|').map(c => c.trim()).filter(Boolean);
                return (
                  <tr key={rIdx} className="hover:bg-blue-50/30 transition-colors">
                    {cols.map((col, cIdx) => (
                      <td key={cIdx} className="px-3 py-2">{renderInline(col)}</td>
                    ))}
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      );
      tableRows = [];
      inTable = false;
    };

    lines.forEach((line, lineIdx) => {
      const trimmed = line.trim();

      // Table detection: lines containing pipe characters
      if (trimmed.startsWith('|') && trimmed.endsWith('|') && trimmed.length > 2) {
        inTable = true;
        tableRows.push(trimmed);
        return;
      } else if (inTable) {
        flushTable(lineIdx);
      }

      if (!trimmed) {
        elements.push(<div key={lineIdx} className="h-1.5" />);
        return;
      }

      // Headers: ###, ##, #
      if (trimmed.startsWith('### ')) {
        elements.push(
          <h4 key={lineIdx} className="text-sm font-bold text-zinc-950 mt-2.5 mb-1">
            {renderInline(trimmed.slice(4))}
          </h4>
        );
        return;
      }
      if (trimmed.startsWith('## ')) {
        elements.push(
          <h3 key={lineIdx} className="text-base font-bold text-zinc-950 mt-3 mb-1.5">
            {renderInline(trimmed.slice(3))}
          </h3>
        );
        return;
      }
      if (trimmed.startsWith('# ')) {
        elements.push(
          <h2 key={lineIdx} className="text-lg font-black text-zinc-950 mt-3.5 mb-2">
            {renderInline(trimmed.slice(2))}
          </h2>
        );
        return;
      }

      // Bullet point lines: •, -, *, +
      const isBullet = /^[•\-\*\+]\s+/.test(trimmed) || trimmed.startsWith('•');
      if (isBullet) {
        const bulletContent = trimmed.replace(/^[•\-\*\+]\s*/, '');
        elements.push(
          <div key={lineIdx} className="flex items-start space-x-2 pl-1 py-0.5">
            <span className={`${bulletClassName} font-bold select-none text-xs mt-0.5 shrink-0`}>•</span>
            <div className="flex-1 leading-relaxed">
              {renderInline(bulletContent)}
            </div>
          </div>
        );
        return;
      }

      // Numbered list item: 1. 2. etc.
      const numberMatch = trimmed.match(/^(\d+)\.\s+(.*)$/);
      if (numberMatch) {
        elements.push(
          <div key={lineIdx} className="flex items-start space-x-2 pl-1 py-0.5">
            <span className="font-bold text-blue-600 text-xs select-none min-w-[1.2rem] mt-0.5 shrink-0">
              {numberMatch[1]}.
            </span>
            <div className="flex-1 leading-relaxed">
              {renderInline(numberMatch[2])}
            </div>
          </div>
        );
        return;
      }

      // Blockquote
      if (trimmed.startsWith('> ')) {
        elements.push(
          <div key={lineIdx} className="border-l-2 border-blue-500 pl-3 py-1.5 my-1.5 italic text-zinc-600 bg-blue-50/50 rounded-r text-xs">
            {renderInline(trimmed.slice(2))}
          </div>
        );
        return;
      }

      // Regular paragraph
      elements.push(
        <p key={lineIdx} className="leading-relaxed">
          {renderInline(line)}
        </p>
      );
    });

    if (inTable) {
      flushTable(lines.length);
    }

    return elements;
  };

  return (
    <div className={`space-y-1.5 ${className}`}>
      {renderContent()}
    </div>
  );
};

