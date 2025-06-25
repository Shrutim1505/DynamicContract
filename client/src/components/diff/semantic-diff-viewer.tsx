import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Plus, Minus, Edit, Clock } from "lucide-react";

interface SemanticDiffViewerProps {
  contractId: number;
}

export default function SemanticDiffViewer({ contractId }: SemanticDiffViewerProps) {
  // Mock diff data - in real app this would come from API
  const mockChanges = [
    {
      id: 1,
      type: 'removed',
      content: 'The total project fee shall be $75,000',
      userId: 2,
      user: {
        fullName: "Sarah Johnson",
        avatar: "https://pixabay.com/get/gfc4d0c7a4586ab980d5794e4f0e959409f67923283ae78c60fbed63305eb371181b2b726cc0c4018b22e1dca41975bdd974d5544f5d26020a0e25f5775166865_1280.jpg"
      },
      timestamp: new Date(Date.now() - 3 * 60 * 60 * 1000), // 3 hours ago
      section: "Payment Terms"
    },
    {
      id: 2,
      type: 'added',
      content: 'Client agrees to pay Provider a total fee of ${{AMOUNT}}',
      userId: 2,
      user: {
        fullName: "Sarah Johnson",
        avatar: "https://pixabay.com/get/gfc4d0c7a4586ab980d5794e4f0e959409f67923283ae78c60fbed63305eb371181b2b726cc0c4018b22e1dca41975bdd974d5544f5d26020a0e25f5775166865_1280.jpg"
      },
      timestamp: new Date(Date.now() - 3 * 60 * 60 * 1000), // 3 hours ago
      section: "Payment Terms"
    },
    {
      id: 3,
      type: 'modified',
      content: 'Modified payment terms section structure',
      userId: 3,
      user: {
        fullName: "Michael Chen",
        avatar: "https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?ixlib=rb-4.0.3&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=100&h=100"
      },
      timestamp: new Date(Date.now() - 1 * 60 * 60 * 1000), // 1 hour ago
      section: "Payment Terms"
    },
    {
      id: 4,
      type: 'added',
      content: 'Added liability limitation clause to protect both parties',
      userId: 1,
      user: {
        fullName: "John Smith",
        avatar: "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?ixlib=rb-4.0.3&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=100&h=100"
      },
      timestamp: new Date(Date.now() - 30 * 60 * 1000), // 30 minutes ago
      section: "Liability"
    },
  ];

  const getChangeIcon = (type: string) => {
    switch (type) {
      case 'added':
        return <Plus className="h-4 w-4 text-green-500" />;
      case 'removed':
        return <Minus className="h-4 w-4 text-red-500" />;
      case 'modified':
        return <Edit className="h-4 w-4 text-blue-500" />;
      default:
        return null;
    }
  };

  const getChangeColor = (type: string) => {
    switch (type) {
      case 'added':
        return 'bg-green-50 border-green-200 dark:bg-green-900/20 dark:border-green-800';
      case 'removed':
        return 'bg-red-50 border-red-200 dark:bg-red-900/20 dark:border-red-800';
      case 'modified':
        return 'bg-blue-50 border-blue-200 dark:bg-blue-900/20 dark:border-blue-800';
      default:
        return 'bg-gray-50 border-gray-200 dark:bg-gray-900/20 dark:border-gray-800';
    }
  };

  const getTextColor = (type: string) => {
    switch (type) {
      case 'added':
        return 'text-green-700 dark:text-green-300';
      case 'removed':
        return 'text-red-700 dark:text-red-300 line-through';
      case 'modified':
        return 'text-blue-700 dark:text-blue-300';
      default:
        return 'text-gray-700 dark:text-gray-300';
    }
  };

  const formatTimeAgo = (date: Date) => {
    const now = new Date();
    const diffInMinutes = Math.floor((now.getTime() - date.getTime()) / (1000 * 60));
    
    if (diffInMinutes < 60) {
      return `${diffInMinutes}m ago`;
    } else if (diffInMinutes < 1440) {
      return `${Math.floor(diffInMinutes / 60)}h ago`;
    } else {
      return `${Math.floor(diffInMinutes / 1440)}d ago`;
    }
  };

  if (mockChanges.length === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Recent Changes</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-center py-8">
            <Clock className="mx-auto h-8 w-8 text-gray-400 dark:text-gray-500 mb-4" />
            <p className="text-sm text-gray-500 dark:text-gray-400">
              No recent changes to display
            </p>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Recent Changes</CardTitle>
        <p className="text-sm text-gray-500 dark:text-gray-400">
          Showing changes from last 24 hours
        </p>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {mockChanges.map((change) => (
            <div 
              key={change.id} 
              className={`p-4 border rounded-lg ${getChangeColor(change.type)}`}
            >
              <div className="flex items-start space-x-3">
                {getChangeIcon(change.type)}
                <div className="flex-1 min-w-0">
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center space-x-2">
                      <Avatar className="h-6 w-6">
                        <AvatarImage src={change.user.avatar} alt={change.user.fullName} />
                        <AvatarFallback>
                          {change.user.fullName.split(' ').map(n => n[0]).join('')}
                        </AvatarFallback>
                      </Avatar>
                      <span className="text-sm font-medium text-gray-900 dark:text-white">
                        {change.user.fullName}
                      </span>
                      <Badge variant="outline" className="text-xs">
                        {change.section}
                      </Badge>
                    </div>
                    <span className="text-xs text-gray-500 dark:text-gray-400">
                      {formatTimeAgo(change.timestamp)}
                    </span>
                  </div>
                  
                  <p className={`text-sm ${getTextColor(change.type)}`}>
                    {change.content}
                  </p>
                  
                  {change.type === 'modified' && (
                    <div className="mt-2 text-xs text-gray-500 dark:text-gray-400">
                      Structure and formatting changes applied
                    </div>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}
