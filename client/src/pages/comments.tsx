import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Badge } from "@/components/ui/badge";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { MessageSquare, Search, Clock, FileText } from "lucide-react";
import { api } from "@/lib/api";
import { Link } from "wouter";

export default function Comments() {
  const [searchTerm, setSearchTerm] = useState("");
  const [contractFilter, setContractFilter] = useState("all");
  
  // Mock user ID - in real app this would come from authentication
  const userId = 1;

  const contractsQuery = useQuery({
    queryKey: ['/api/contracts', { userId }],
    queryFn: () => api.getContracts({ userId }),
  });

  // Mock comments data - in real app this would come from a combined API endpoint
  const mockComments = [
    {
      id: 1,
      content: "Should we add more specificity to the technical consulting services? The current language might be too broad.",
      contractId: 1,
      contractTitle: "Service Agreement - TechCorp Inc.",
      userId: 2,
      user: {
        fullName: "Sarah Johnson",
        avatar: "https://pixabay.com/get/gfc4d0c7a4586ab980d5794e4f0e959409f67923283ae78c60fbed63305eb371181b2b726cc0c4018b22e1dca41975bdd974d5544f5d26020a0e25f5775166865_1280.jpg"
      },
      parentId: null,
      replies: 1,
      createdAt: new Date(Date.now() - 2 * 60 * 60 * 1000), // 2 hours ago
      status: "unresolved"
    },
    {
      id: 2,
      content: "The IP section looks comprehensive. Are we planning to include any shared IP provisions?",
      contractId: 1,
      contractTitle: "Service Agreement - TechCorp Inc.",
      userId: 3,
      user: {
        fullName: "David Park",
        avatar: "https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?ixlib=rb-4.0.3&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=100&h=100"
      },
      parentId: null,
      replies: 0,
      createdAt: new Date(Date.now() - 30 * 60 * 1000), // 30 minutes ago
      status: "unresolved"
    },
    {
      id: 3,
      content: "Please review the termination clause for compliance with local employment laws.",
      contractId: 2,
      contractTitle: "Employment Contract - Jane Doe",
      userId: 2,
      user: {
        fullName: "Sarah Johnson",
        avatar: "https://pixabay.com/get/gfc4d0c7a4586ab980d5794e4f0e959409f67923283ae78c60fbed63305eb371181b2b726cc0c4018b22e1dca41975bdd974d5544f5d26020a0e25f5775166865_1280.jpg"
      },
      parentId: null,
      replies: 2,
      createdAt: new Date(Date.now() - 24 * 60 * 60 * 1000), // 1 day ago
      status: "resolved"
    },
    {
      id: 4,
      content: "The liability limitation section needs more clarity. Can we schedule a call to discuss?",
      contractId: 1,
      contractTitle: "Service Agreement - TechCorp Inc.",
      userId: 4,
      user: {
        fullName: "Michael Chen",
        avatar: "https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?ixlib=rb-4.0.3&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=150&h=150"
      },
      parentId: null,
      replies: 3,
      createdAt: new Date(Date.now() - 3 * 24 * 60 * 60 * 1000), // 3 days ago
      status: "resolved"
    },
  ];

  const contracts = contractsQuery.data || [];

  // Filter comments based on search and contract
  const filteredComments = mockComments.filter(comment => {
    const matchesSearch = comment.content.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         comment.contractTitle.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesContract = contractFilter === "all" || comment.contractId.toString() === contractFilter;
    return matchesSearch && matchesContract;
  });

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

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'resolved': return 'bg-green-100 text-green-800 dark:bg-green-900/20 dark:text-green-400';
      case 'unresolved': return 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/20 dark:text-yellow-400';
      default: return 'bg-gray-100 text-gray-800 dark:bg-gray-900/20 dark:text-gray-400';
    }
  };

  return (
    <div className="py-6">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 md:px-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Comments & Discussions</h1>
          <p className="mt-2 text-gray-600 dark:text-gray-400">
            Track all contract discussions and feedback in one place
          </p>
        </div>

        {/* Filters */}
        <div className="flex items-center space-x-4 mb-6">
          <div className="relative flex-1 max-w-md">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
            <Input
              placeholder="Search comments and contracts..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-10"
            />
          </div>
          <Select value={contractFilter} onValueChange={setContractFilter}>
            <SelectTrigger className="w-64">
              <SelectValue placeholder="Filter by contract" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Contracts</SelectItem>
              {contracts.map((contract) => (
                <SelectItem key={contract.id} value={contract.id.toString()}>
                  {contract.title}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        {/* Comments List */}
        {filteredComments.length === 0 ? (
          <div className="text-center py-12">
            <MessageSquare className="mx-auto h-12 w-12 text-gray-400 dark:text-gray-500" />
            <h3 className="mt-2 text-sm font-medium text-gray-900 dark:text-white">
              {mockComments.length === 0 ? "No comments yet" : "No comments match your search"}
            </h3>
            <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
              {mockComments.length === 0 
                ? "Comments and discussions will appear here as your team collaborates on contracts." 
                : "Try adjusting your search terms or filters."
              }
            </p>
          </div>
        ) : (
          <div className="space-y-4">
            {filteredComments.map((comment) => (
              <Card key={comment.id} className="hover:shadow-md transition-shadow">
                <CardContent className="p-6">
                  <div className="flex items-start space-x-4">
                    <Avatar className="h-10 w-10">
                      <AvatarImage src={comment.user.avatar} alt={comment.user.fullName} />
                      <AvatarFallback>
                        {comment.user.fullName.split(' ').map(n => n[0]).join('')}
                      </AvatarFallback>
                    </Avatar>
                    
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center justify-between mb-2">
                        <div className="flex items-center space-x-2">
                          <span className="font-medium text-gray-900 dark:text-white">
                            {comment.user.fullName}
                          </span>
                          <Badge className={getStatusColor(comment.status)}>
                            {comment.status}
                          </Badge>
                        </div>
                        <div className="flex items-center space-x-2 text-sm text-gray-500 dark:text-gray-400">
                          <Clock className="h-4 w-4" />
                          {formatTimeAgo(comment.createdAt)}
                        </div>
                      </div>
                      
                      <p className="text-gray-700 dark:text-gray-300 mb-3">
                        {comment.content}
                      </p>
                      
                      <div className="flex items-center justify-between">
                        <Link href={`/contracts/${comment.contractId}/edit`}>
                          <div className="flex items-center text-sm text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-200 cursor-pointer">
                            <FileText className="h-4 w-4 mr-1" />
                            {comment.contractTitle}
                          </div>
                        </Link>
                        
                        <div className="flex items-center space-x-4 text-sm text-gray-500 dark:text-gray-400">
                          {comment.replies > 0 && (
                            <span className="flex items-center">
                              <MessageSquare className="h-4 w-4 mr-1" />
                              {comment.replies} {comment.replies === 1 ? 'reply' : 'replies'}
                            </span>
                          )}
                          <Link href={`/contracts/${comment.contractId}/edit`}>
                            <span className="hover:text-gray-700 dark:hover:text-gray-200 cursor-pointer">
                              View in contract
                            </span>
                          </Link>
                        </div>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
