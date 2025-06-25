import { useRef, useEffect } from "react";
import { CursorPosition } from "@/types/presence";

interface ContractEditorProps {
  content: string;
  onChange: (content: string) => void;
  cursors: CursorPosition[];
  onCursorMove: (position: { line: number; character: number }) => void;
}

export default function ContractEditor({ 
  content, 
  onChange, 
  cursors, 
  onCursorMove 
}: ContractEditorProps) {
  const editorRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (editorRef.current && editorRef.current.innerHTML !== content) {
      editorRef.current.innerHTML = content;
    }
  }, [content]);

  const handleInput = () => {
    if (editorRef.current) {
      const newContent = editorRef.current.innerHTML;
      onChange(newContent);
    }
  };

  const handleSelectionChange = () => {
    const selection = window.getSelection();
    if (selection && selection.rangeCount > 0) {
      const range = selection.getRangeAt(0);
      // Convert DOM position to line/character position
      // This is a simplified implementation
      const position = {
        line: 0, // Would need to calculate actual line number
        character: range.startOffset,
      };
      onCursorMove(position);
    }
  };

  return (
    <div className="relative">
      <div
        ref={editorRef}
        className="p-6 editor-content min-h-[500px] focus:outline-none"
        contentEditable
        onInput={handleInput}
        onMouseUp={handleSelectionChange}
        onKeyUp={handleSelectionChange}
        suppressContentEditableWarning={true}
        dangerouslySetInnerHTML={{ __html: content }}
      />
      
      {/* Render other users' cursors */}
      {cursors.map((cursor) => (
        <div
          key={cursor.userId}
          className="cursor-indicator"
          style={{
            left: `${cursor.position.character * 8}px`, // Approximate character width
            top: `${cursor.position.line * 24 + 24}px`, // Approximate line height
          }}
          data-user={cursor.user.fullName}
        />
      ))}
    </div>
  );
}
