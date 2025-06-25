import { useParams } from "wouter";
import { useState, useRef, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Download, Save } from "lucide-react";
import { useContract } from "@/hooks/use-contract";
import { usePresence } from "@/hooks/use-presence";
import ContractEditorComponent from "@/components/editor/contract-editor";
import Toolbar from "@/components/editor/toolbar";
import AiSuggestions from "@/components/editor/ai-suggestions";
import CommentPanel from "@/components/comments/comment-panel";
import SemanticDiffViewer from "@/components/diff/semantic-diff-viewer";
import DocumentAnalytics from "@/components/analytics/document-analytics";
import VersionHistory from "@/components/version/version-history";
import { useToast } from "@/hooks/use-toast";

export default function ContractEditor() {
  const params = useParams();
  const contractId = parseInt(params.id as string);
  const { toast } = useToast();
  
  const [content, setContent] = useState("");
  const [isAutoSaving, setIsAutoSaving] = useState(false);
  const autoSaveTimeoutRef = useRef<NodeJS.Timeout>();
  
  // Mock user ID - in real app this would come from authentication
  const userId = 1;
  
  const { 
    contract, 
    isLoading, 
    updateContract, 
    isUpdating,
    comments,
    suggestions,
    versions,
    refetchComments,
    refetchSuggestions,
  } = useContract(contractId);
  
  const { activeUsers, cursors, updateCursorPosition, sendContentChange } = usePresence(userId, contractId);

  useEffect(() => {
    if (contract) {
      setContent(contract.content);
    }
  }, [contract]);

  const handleContentChange = (newContent: string) => {
    setContent(newContent);
    
    // Auto-save logic
    if (autoSaveTimeoutRef.current) {
      clearTimeout(autoSaveTimeoutRef.current);
    }
    
    autoSaveTimeoutRef.current = setTimeout(() => {
      handleAutoSave(newContent);
    }, 2000);

    // Send content change to other users
    const wordCount = newContent.split(/\s+/).filter(word => word.length > 0).length;
    sendContentChange(newContent, wordCount);
  };

  const handleAutoSave = async (newContent: string) => {
    setIsAutoSaving(true);
    try {
      const wordCount = newContent.split(/\s+/).filter(word => word.length > 0).length;
      await updateContract({ 
        content: newContent, 
        wordCount,
        updatedAt: new Date(),
      });
      
      toast({
        title: "Auto-saved",
        description: "Changes saved successfully",
      });
    } catch (error) {
      toast({
        title: "Auto-save failed",
        description: "Your changes could not be saved automatically",
        variant: "destructive",
      });
    } finally {
      setIsAutoSaving(false);
    }
  };

  const handleManualSave = () => {
    if (autoSaveTimeoutRef.current) {
      clearTimeout(autoSaveTimeoutRef.current);
    }
    handleAutoSave(content);
  };

  const handleExport = () => {
    const blob = new Blob([content], { type: 'text/html' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${contract?.title || 'contract'}.html`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    
    toast({
      title: "Contract exported",
      description: "Contract has been downloaded successfully",
    });
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto mb-4"></div>
          <p className="text-gray-500 dark:text-gray-400">Loading contract...</p>
        </div>
      </div>
    );
  }

  if (!contract) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-center">
          <p className="text-gray-500 dark:text-gray-400">Contract not found</p>
        </div>
      </div>
    );
  }

  return (
    <div className="py-6">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 md:px-8">
        {/* Contract Editor Header */}
        <div className="flex items-center justify-between mb-6">
          <div>
            <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
              {contract.title}
            </h1>
            <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
              Last modified {new Date(contract.updatedAt).toLocaleString()}
              {isAutoSaving && " • Auto-saving..."}
            </p>
          </div>
          <div className="flex space-x-3">
            <Button variant="outline" onClick={handleExport}>
              <Download className="h-4 w-4 mr-2" />
              Export
            </Button>
            <Button onClick={handleManualSave} disabled={isUpdating}>
              <Save className="h-4 w-4 mr-2" />
              {isUpdating ? "Saving..." : "Save Changes"}
            </Button>
          </div>
        </div>

        {/* Main Editor Layout */}
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          {/* Contract Editor */}
          <div className="lg:col-span-3 space-y-6">
            <Card>
              {/* Editor Toolbar */}
              <div className="px-4 py-3 border-b border-gray-200 dark:border-gray-700">
                <Toolbar />
              </div>

              {/* Editor Content */}
              <CardContent className="p-0">
                <ContractEditorComponent
                  content={content}
                  onChange={handleContentChange}
                  cursors={cursors}
                  onCursorMove={updateCursorPosition}
                />
              </CardContent>
            </Card>

            {/* Semantic Diff Viewer */}
            <SemanticDiffViewer contractId={contractId} />
          </div>

          {/* Right Sidebar */}
          <div className="lg:col-span-1 space-y-6">
            {/* Comments Panel */}
            <CommentPanel 
              contractId={contractId}
              comments={comments}
              onCommentAdded={refetchComments}
            />

            {/* AI Suggestions Panel */}
            <AiSuggestions 
              contractId={contractId}
              suggestions={suggestions}
              onSuggestionUpdated={refetchSuggestions}
            />

            {/* Document Analytics */}
            <DocumentAnalytics contract={contract} />

            {/* Version History */}
            <VersionHistory 
              contractId={contractId}
              versions={versions}
            />
          </div>
        </div>
      </div>
    </div>
  );
}
