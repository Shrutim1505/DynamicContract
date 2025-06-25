import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { MessageSquare } from "lucide-react";
import { Comment } from "@shared/schema";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { useToast } from "@/hooks/use-toast";
import CommentThread from "./comment-thread";

interface CommentPanelProps {
  contractId: number;
  comments: Comment[];
  onCommentAdded: () => void;
}

export default function CommentPanel({ 
  contractId, 
  comments, 
  onCommentAdded 
}: CommentPanelProps) {
  const [newComment, setNewComment] = useState("");
  const queryClient = useQueryClient();
  const { toast } = useToast();

  const createCommentMutation = useMutation({
    mutationFn: (commentData: any) => api.createComment(contractId, commentData),
    onSuccess: () => {
      queryClient.invalidateQueries({ 
        queryKey: ['/api/contracts', contractId, 'comments'] 
      });
      setNewComment("");
      onCommentAdded();
      toast({
        title: "Comment added",
        description: "Your comment has been posted successfully.",
      });
    },
    onError: () => {
      toast({
        title: "Error",
        description: "Failed to add comment. Please try again.",
        variant: "destructive",
      });
    },
  });

  const handleSubmitComment = () => {
    if (!newComment.trim()) return;

    createCommentMutation.mutate({
      content: newComment.trim(),
      userId: 1, // Mock user ID - in real app this would come from auth
    });
  };

  // Group comments by thread (top-level comments and their replies)
  const topLevelComments = comments.filter(comment => !comment.parentId);
  const commentReplies = comments.filter(comment => comment.parentId);

  const getCommentReplies = (commentId: number) => {
    return commentReplies.filter(reply => reply.parentId === commentId);
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center">
          <MessageSquare className="h-5 w-5 mr-2" />
          Comments & Annotations
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="comment-thread space-y-4 mb-4 max-h-96 overflow-y-auto">
          {topLevelComments.length === 0 ? (
            <p className="text-sm text-gray-500 dark:text-gray-400 text-center py-4">
              No comments yet. Be the first to add one!
            </p>
          ) : (
            topLevelComments.map((comment) => (
              <CommentThread
                key={comment.id}
                comment={comment}
                replies={getCommentReplies(comment.id)}
                contractId={contractId}
                onReplyAdded={onCommentAdded}
              />
            ))
          )}
        </div>

        {/* Add Comment Form */}
        <div className="border-t border-gray-200 dark:border-gray-700 pt-4">
          <div className="flex space-x-3">
            <Avatar className="h-6 w-6">
              <AvatarImage 
                src="https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?ixlib=rb-4.0.3&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=100&h=100" 
                alt="Your profile" 
              />
              <AvatarFallback>JS</AvatarFallback>
            </Avatar>
            <div className="flex-1 space-y-2">
              <Textarea
                value={newComment}
                onChange={(e) => setNewComment(e.target.value)}
                placeholder="Add a comment..."
                className="text-sm resize-none"
                rows={2}
              />
              <div className="flex justify-end">
                <Button 
                  size="sm"
                  onClick={handleSubmitComment}
                  disabled={!newComment.trim() || createCommentMutation.isPending}
                >
                  {createCommentMutation.isPending ? "Adding..." : "Comment"}
                </Button>
              </div>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
