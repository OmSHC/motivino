import React, { useRef, useEffect, useState } from 'react';
import { 
  BoldIcon as Bold, 
  ItalicIcon as Italic, 
  UnderlineIcon as Underline, 
  ListBulletIcon as List, 
  Bars3BottomRightIcon as ListOrdered, 
  ChatBubbleLeftRightIcon as Quote, 
  LinkIcon,
  PhotoIcon as ImageIcon,
  ArrowUturnLeftIcon as Undo,
  ArrowUturnRightIcon as Redo
} from '@heroicons/react/24/outline';

interface SimpleRichEditorProps {
  content: string;
  onChange: (content: string) => void;
  placeholder?: string;
  minHeight?: number;
}

const SimpleRichEditor: React.FC<SimpleRichEditorProps> = ({ 
  content, 
  onChange, 
  placeholder = "Start writing...",
  minHeight = 300 
}) => {
  const editorRef = useRef<HTMLDivElement>(null);
  const [isActive, setIsActive] = useState(false);

  useEffect(() => {
    if (editorRef.current && content !== editorRef.current.innerHTML) {
      editorRef.current.innerHTML = content;
    }
  }, [content]);

  const execCommand = (command: string, value?: string) => {
    document.execCommand(command, false, value);
    editorRef.current?.focus();
    handleContentChange();
  };

  const handleContentChange = () => {
    if (editorRef.current) {
      const html = editorRef.current.innerHTML;
      onChange(html);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.ctrlKey || e.metaKey) {
      switch (e.key) {
        case 'b':
          e.preventDefault();
          execCommand('bold');
          break;
        case 'i':
          e.preventDefault();
          execCommand('italic');
          break;
        case 'u':
          e.preventDefault();
          execCommand('underline');
          break;
      }
    }
  };

  const insertLink = () => {
    const url = prompt('Enter URL:');
    if (url) {
      execCommand('createLink', url);
    }
  };

  const insertImage = () => {
    const url = prompt('Enter image URL:');
    if (url) {
      const img = `<img src="${url}" alt="Image" style="max-width: 100%; height: auto;" />`;
      execCommand('insertHTML', img);
    }
  };

  const insertHeading = (level: number) => {
    const heading = `<h${level}>Heading ${level}</h${level}>`;
    execCommand('insertHTML', heading);
  };

  const insertList = (ordered: boolean = false) => {
    if (ordered) {
      execCommand('insertOrderedList');
    } else {
      execCommand('insertUnorderedList');
    }
  };

  const insertQuote = () => {
    const quote = '<blockquote style="border-left: 4px solid #3b82f6; padding-left: 16px; margin: 16px 0; font-style: italic; color: #6b7280;">Quote text...</blockquote>';
    execCommand('insertHTML', quote);
  };

  return (
    <div className="simple-rich-editor" style={{ 
      border: '1px solid #d1d5db', 
      borderRadius: '0.5rem',
      overflow: 'hidden',
      backgroundColor: 'white'
    }}>
      {/* Debug indicator */}
      <div style={{ 
        padding: '8px', 
        backgroundColor: '#f0f9ff', 
        border: '2px dashed #3b82f6',
        marginBottom: '8px',
        borderRadius: '4px',
        fontSize: '12px',
        color: '#1e40af'
      }}>
        🎯 Simple Rich Editor Active - React 19 Compatible
      </div>

      {/* Toolbar */}
      <div className="flex items-center gap-1 p-2 bg-gray-50 border-b border-gray-200 flex-wrap">
        {/* Text Formatting */}
        <div className="flex items-center gap-1 mr-4">
          <button
            type="button"
            onClick={() => execCommand('bold')}
            className="p-2 rounded hover:bg-gray-200 transition-colors"
            title="Bold (Ctrl+B)"
          >
            <Bold className="h-4 w-4" />
          </button>
          <button
            type="button"
            onClick={() => execCommand('italic')}
            className="p-2 rounded hover:bg-gray-200 transition-colors"
            title="Italic (Ctrl+I)"
          >
            <Italic className="h-4 w-4" />
          </button>
          <button
            type="button"
            onClick={() => execCommand('underline')}
            className="p-2 rounded hover:bg-gray-200 transition-colors"
            title="Underline (Ctrl+U)"
          >
            <Underline className="h-4 w-4" />
          </button>
        </div>

        {/* Headings */}
        <div className="flex items-center gap-1 mr-4">
          <button
            type="button"
            onClick={() => insertHeading(1)}
            className="p-2 rounded hover:bg-gray-200 transition-colors text-sm font-bold"
            title="Heading 1"
          >
            H1
          </button>
          <button
            type="button"
            onClick={() => insertHeading(2)}
            className="p-2 rounded hover:bg-gray-200 transition-colors text-sm font-bold"
            title="Heading 2"
          >
            H2
          </button>
          <button
            type="button"
            onClick={() => insertHeading(3)}
            className="p-2 rounded hover:bg-gray-200 transition-colors text-sm font-bold"
            title="Heading 3"
          >
            H3
          </button>
        </div>

        {/* Lists */}
        <div className="flex items-center gap-1 mr-4">
          <button
            type="button"
            onClick={() => insertList(false)}
            className="p-2 rounded hover:bg-gray-200 transition-colors"
            title="Bullet List"
          >
            <List className="h-4 w-4" />
          </button>
          <button
            type="button"
            onClick={() => insertList(true)}
            className="p-2 rounded hover:bg-gray-200 transition-colors"
            title="Numbered List"
          >
            <ListOrdered className="h-4 w-4" />
          </button>
        </div>

        {/* Special Elements */}
        <div className="flex items-center gap-1 mr-4">
          <button
            type="button"
            onClick={insertQuote}
            className="p-2 rounded hover:bg-gray-200 transition-colors"
            title="Quote"
          >
            <Quote className="h-4 w-4" />
          </button>
          <button
            type="button"
            onClick={insertLink}
            className="p-2 rounded hover:bg-gray-200 transition-colors"
            title="Add Link"
          >
            <LinkIcon className="h-4 w-4" />
          </button>
          <button
            type="button"
            onClick={insertImage}
            className="p-2 rounded hover:bg-gray-200 transition-colors"
            title="Add Image"
          >
            <ImageIcon className="h-4 w-4" />
          </button>
        </div>

        {/* Undo/Redo */}
        <div className="flex items-center gap-1">
          <button
            type="button"
            onClick={() => execCommand('undo')}
            className="p-2 rounded hover:bg-gray-200 transition-colors"
            title="Undo"
          >
            <Undo className="h-4 w-4" />
          </button>
          <button
            type="button"
            onClick={() => execCommand('redo')}
            className="p-2 rounded hover:bg-gray-200 transition-colors"
            title="Redo"
          >
            <Redo className="h-4 w-4" />
          </button>
        </div>
      </div>

      {/* Editor Content */}
      <div
        ref={editorRef}
        contentEditable
        suppressContentEditableWarning={true}
        onInput={handleContentChange}
        onKeyDown={handleKeyDown}
        onFocus={() => setIsActive(true)}
        onBlur={() => setIsActive(false)}
        className="w-full focus:outline-none p-4 text-gray-900 leading-relaxed"
        style={{
          minHeight: `${minHeight}px`,
          fontSize: '14px',
          lineHeight: '1.6',
          outline: 'none',
          backgroundColor: 'white'
        }}
        data-placeholder={placeholder}
      />

      {/* Placeholder */}
      {!content && !isActive && (
        <div 
          className="absolute pointer-events-none text-gray-400 italic"
          style={{ 
            top: '60px', 
            left: '16px',
            fontSize: '14px'
          }}
        >
          {placeholder}
        </div>
      )}
    </div>
  );
};

export default SimpleRichEditor;
