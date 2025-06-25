import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Lightbulb, AlertTriangle, X } from "lucide-react";
import { AiSuggestion } from "@shared/schema";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { useToast } from "@/hooks/use-toast";

interface AiSuggestionsProps {
  contractId: number;
  suggestions: AiSuggestion[];
  onSuggestionUpdated: () => void;
}

export default function AiSuggestions({ 
  contractId, 
  suggestions, 
  onSuggestionUpdated 
}: AiSuggestionsProps) {
  const queryClient = useQueryClient();
  const { toast } = useToast();

  const updateSuggestionMutation = useMutation({
    mutationFn: ({ id, updates }: { id: number; updates: any }) => 
      api.updateSuggestion(id, updates),
    onSuccess: () => {
      queryClient.invalidateQueries({ 
        queryKey: ['/api/contracts', contractId, 'suggestions'] 
      });
      onSuggestionUpdated();
    },
  });

  const handleApplySuggestion = (suggestion: AiSuggestion) => {
    updateSuggestionMutation.mutate({
      id: suggestion.id,
      updates: { status: 'accepted' }
    });

    toast({
      title: "Suggestion applied",
      description: "The AI suggestion has been applied to your contract.",
    });
  };

  const handleDismissSuggestion = (suggestion: AiSuggestion) => {
    updateSuggestionMutation.mutate({
      id: suggestion.id,
      updates: { status: 'dismissed' }
    });

    toast({
      title: "Suggestion dismissed",
      description: "The AI suggestion has been dismissed.",
    });
  };

  const getIcon = (type: string) => {
    switch (type) {
      case 'enhancement':
        return <Lightbulb className="h-4 w-4 text-blue-500" />;
      case 'warning':
        return <AlertTriangle className="h-4 w-4 text-yellow-500" />;
      case 'missing_clause':
        return <AlertTriangle className="h-4 w-4 text-red-500" />;
      default:
        return <Lightbulb className="h-4 w-4 text-blue-500" />;
    }
  };

  const getTypeColor = (type: string) => {
    switch (type) {
      case 'enhancement':
        return 'bg-blue-50 border-blue-200 dark:bg-blue-900/20 dark:border-blue-800';
      case 'warning':
        return 'bg-yellow-50 border-yellow-200 dark:bg-yellow-900/20 dark:border-yellow-800';
      case 'missing_clause':
        return 'bg-red-50 border-red-200 dark:bg-red-900/20 dark:border-red-800';
      default:
        return 'bg-blue-50 border-blue-200 dark:bg-blue-900/20 dark:border-blue-800';
    }
  };

  const pendingSuggestions = suggestions.filter(s => s.status === 'pending');

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center">
          <Lightbulb className="h-5 w-5 mr-2" />
          AI Suggestions
        </CardTitle>
      </CardHeader>
      <CardContent>
        {pendingSuggestions.length === 0 ? (
          <p className="text-sm text-gray-500 dark:text-gray-400 text-center py-4">
            No AI suggestions available
          </p>
        ) : (
          <div className="space-y-3">
            {pendingSuggestions.map((suggestion) => (
              <div 
                key={suggestion.id} 
                className={`border rounded-lg p-3 ${getTypeColor(suggestion.type)}`}
              >
                <div className="flex items-start">
                  {getIcon(suggestion.type)}
                  <div className="flex-1 ml-2">
                    <div className="flex items-center justify-between mb-1">
                      <p className="text-sm font-medium text-gray-900 dark:text-white">
                        {suggestion.title}
                      </p>
                      <Badge variant="outline" className="text-xs">
                        {suggestion.type.replace('_', ' ')}
                      </Badge>
                    </div>
                    <p className="text-xs text-gray-700 dark:text-gray-300 mb-2">
                      {suggestion.description}
                    </p>
                    {suggestion.suggestedText && (
                      <div className="bg-white/50 dark:bg-gray-800/50 rounded p-2 mb-2 text-xs font-mono">
                        {suggestion.suggestedText}
                      </div>
                    )}
                    <div className="flex space-x-2">
                      <Button 
                        size="sm" 
                        onClick={() => handleApplySuggestion(suggestion)}
                        disabled={updateSuggestionMutation.isPending}
                        className="text-xs bg-primary text-primary-foreground hover:bg-primary/90"
                      >
                        Apply
                      </Button>
                      <Button 
                        variant="outline" 
                        size="sm" 
                        onClick={() => handleDismissSuggestion(suggestion)}
                        disabled={updateSuggestionMutation.isPending}
                        className="text-xs"
                      >
                        Dismiss
                      </Button>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
