import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Reply } from "lucide-react";
import { Comment } from "@shared/schema";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { useToast } from "@/hooks/use-toast";

interface CommentThreadProps {
  comment: Comment;
  replies: Comment[];
  contractId: number;
  onReplyAdded: () => void;
}

export default function CommentThread({ 
  comment, 
  replies, 
  contractId, 
  onReplyAdded 
}: CommentThreadProps) {
  const [showReplyForm, setShowReplyForm] = useState(false);
  const [replyContent, setReplyContent] = useState("");
  const queryClient = useQueryClient();
  const { toast } = useToast();

  const createReplyMutation = useMutation({
    mutationFn: (replyData: any) => api.createComment(contractId, replyData),
    onSuccess: () => {
      queryClient.invalidateQueries({ 
        queryKey: ['/api/contracts', contractId, 'comments'] 
      });
      setReplyContent("");
      setShowReplyForm(false);
      onReplyAdded();
      toast({
        title: "Reply added",
        description: "Your reply has been posted successfully.",
      });
    },
  });

  const handleSubmitReply = () => {
    if (!replyContent.trim()) return;

    createReplyMutation.mutate({
      content: replyContent.trim(),
      userId: 1, // Mock user ID
      parentId: comment.id,
    });
  };

  const formatDate = (date: Date) => {
    return new Date(date).toLocaleString();
  };

  // Mock user data - in real app this would come from joined query or separate user fetch
  const mockUsers = {
    1: { fullName: "John Smith", avatar: "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?ixlib=rb-4.0.3&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=100&h=100" },
    2: { fullName: "Sarah Johnson", avatar: "https://pixabay.com/get/gfc4d0c7a4586ab980d5794e4f0e959409f67923283ae78c60fbed63305eb371181b2b726cc0c4018b22e1dca41975bdd974d5544f5d26020a0e25f5775166865_1280.jpg" },
    3: { fullName: "Michael Chen", avatar: "https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?ixlib=rb-4.0.3&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=100&h=100" },
  };

  const getUser = (userId: number) => mockUsers[userId as keyof typeof mockUsers] || { fullName: "Unknown User", avatar: "" };

  return (
    <div className="space-y-3">
      {/* Main Comment */}
      <div className="flex space-x-3">
        <Avatar className="h-6 w-6">
          <AvatarImage src={getUser(comment.userId).avatar} alt="Commenter" />
          <AvatarFallback>
            {getUser(comment.userId).fullName.split(' ').map(n => n[0]).join('')}
          </AvatarFallback>
        </Avatar>
        <div className="flex-1">
          <div className="bg-gray-50 dark:bg-gray-800 rounded-lg p-3">
            <div className="flex items-center justify-between mb-1">
              <span className="text-sm font-medium text-gray-900 dark:text-white">
                {getUser(comment.userId).fullName}
              </span>
              <span className="text-xs text-gray-500 dark:text-gray-400">
                {formatDate(comment.createdAt)}
              </span>
            </div>
            <p className="text-sm text-gray-700 dark:text-gray-300">
              {comment.content}
            </p>
          </div>
          <div className="mt-1">
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setShowReplyForm(!showReplyForm)}
              className="text-xs text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200"
            >
              <Reply className="h-3 w-3 mr-1" />
              Reply
            </Button>
          </div>
        </div>
      </div>

      {/* Replies */}
      {replies.map((reply) => (
        <div key={reply.id} className="flex space-x-3 ml-9">
          <Avatar className="h-6 w-6">
            <AvatarImage src={getUser(reply.userId).avatar} alt="Commenter" />
            <AvatarFallback>
              {getUser(reply.userId).fullName.split(' ').map(n => n[0]).join('')}
            </AvatarFallback>
          </Avatar>
          <div className="flex-1">
            <div className="bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-lg p-3">
              <div className="flex items-center justify-between mb-1">
                <span className="text-sm font-medium text-gray-900 dark:text-white">
                  {getUser(reply.userId).fullName}
                </span>
                <span className="text-xs text-gray-500 dark:text-gray-400">
                  {formatDate(reply.createdAt)}
                </span>
              </div>
              <p className="text-sm text-gray-700 dark:text-gray-300">
                {reply.content}
              </p>
            </div>
          </div>
        </div>
      ))}

      {/* Reply Form */}
      {showReplyForm && (
        <div className="flex space-x-3 ml-9">
          <Avatar className="h-6 w-6">
            <AvatarImage 
              src="https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?ixlib=rb-4.0.3&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=100&h=100" 
              alt="Your profile" 
            />
            <AvatarFallback>JS</AvatarFallback>
          </Avatar>
          <div className="flex-1 space-y-2">
            <Textarea
              value={replyContent}
              onChange={(e) => setReplyContent(e.target.value)}
              placeholder="Write a reply..."
              className="text-sm resize-none"
              rows={2}
            />
            <div className="flex justify-end space-x-2">
              <Button 
                variant="outline" 
                size="sm"
                onClick={() => {
                  setShowReplyForm(false);
                  setReplyContent("");
                }}
              >
                Cancel
              </Button>
              <Button 
                size="sm"
                onClick={handleSubmitReply}
                disabled={!replyContent.trim() || createReplyMutation.isPending}
              >
                {createReplyMutation.isPending ? "Replying..." : "Reply"}
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
