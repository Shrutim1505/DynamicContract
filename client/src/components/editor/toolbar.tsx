import { Button } from "@/components/ui/button";
import { 
  Undo, 
  Redo, 
  Bold, 
  Italic, 
  Underline, 
  List, 
  ListOrdered,
  Bot,
  MessageSquare
} from "lucide-react";

export default function Toolbar() {
  const handleFormat = (command: string, value?: string) => {
    document.execCommand(command, false, value);
  };

  const handleAiSuggest = () => {
    // This would trigger AI suggestion generation
    console.log("Generating AI suggestions...");
  };

  const handleAddComment = () => {
    // This would open comment dialog
    console.log("Adding comment...");
  };

  return (
    <div className="flex items-center space-x-1">
      <div className="flex items-center space-x-1 border-r border-gray-200 dark:border-gray-700 pr-3 mr-3">
        <Button 
          variant="ghost" 
          size="sm" 
          onClick={() => handleFormat('undo')}
          className="text-gray-400 hover:text-gray-600 dark:text-gray-500 dark:hover:text-gray-400"
        >
          <Undo className="h-4 w-4" />
        </Button>
        <Button 
          variant="ghost" 
          size="sm" 
          onClick={() => handleFormat('redo')}
          className="text-gray-400 hover:text-gray-600 dark:text-gray-500 dark:hover:text-gray-400"
        >
          <Redo className="h-4 w-4" />
        </Button>
      </div>
      
      <div className="flex items-center space-x-1 border-r border-gray-200 dark:border-gray-700 pr-3 mr-3">
        <Button 
          variant="ghost" 
          size="sm" 
          onClick={() => handleFormat('bold')}
          className="text-gray-700 hover:text-gray-900 dark:text-gray-300 dark:hover:text-gray-100 font-bold"
        >
          <Bold className="h-4 w-4" />
        </Button>
        <Button 
          variant="ghost" 
          size="sm" 
          onClick={() => handleFormat('italic')}
          className="text-gray-400 hover:text-gray-600 dark:text-gray-500 dark:hover:text-gray-400"
        >
          <Italic className="h-4 w-4" />
        </Button>
        <Button 
          variant="ghost" 
          size="sm" 
          onClick={() => handleFormat('underline')}
          className="text-gray-400 hover:text-gray-600 dark:text-gray-500 dark:hover:text-gray-400"
        >
          <Underline className="h-4 w-4" />
        </Button>
      </div>
      
      <div className="flex items-center space-x-1 border-r border-gray-200 dark:border-gray-700 pr-3 mr-3">
        <Button 
          variant="ghost" 
          size="sm" 
          onClick={() => handleFormat('insertUnorderedList')}
          className="text-gray-400 hover:text-gray-600 dark:text-gray-500 dark:hover:text-gray-400"
        >
          <List className="h-4 w-4" />
        </Button>
        <Button 
          variant="ghost" 
          size="sm" 
          onClick={() => handleFormat('insertOrderedList')}
          className="text-gray-400 hover:text-gray-600 dark:text-gray-500 dark:hover:text-gray-400"
        >
          <ListOrdered className="h-4 w-4" />
        </Button>
      </div>
      
      <div className="flex items-center space-x-1">
        <Button 
          size="sm" 
          onClick={handleAiSuggest}
          className="bg-primary-100 text-primary-700 hover:bg-primary-200 dark:bg-primary-900/20 dark:text-primary-300 dark:hover:bg-primary-900/30"
        >
          <Bot className="h-4 w-4 mr-1" />
          AI Suggest
        </Button>
        <Button 
          size="sm" 
          onClick={handleAddComment}
          className="bg-green-100 text-green-700 hover:bg-green-200 dark:bg-green-900/20 dark:text-green-300 dark:hover:bg-green-900/30"
        >
          <MessageSquare className="h-4 w-4 mr-1" />
          Comment
        </Button>
      </div>
    </div>
  );
}
