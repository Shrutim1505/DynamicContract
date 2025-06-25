import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { History, Search, FileText, Clock, User, GitBranch, Download, Eye } from "lucide-react";
import { api } from "@/lib/api";
import { Link } from "wouter";

export default function VersionHistory() {
  const [searchTerm, setSearchTerm] = useState("");
  const [contractFilter, setContractFilter] = useState("all");
  
  // Mock user ID - in real app this would come from authentication
  const userId = 1;

  const contractsQuery = useQuery({
    queryKey: ['/api/contracts', { userId }],
    queryFn: () => api.getContracts({ userId }),
  });

  // Mock version history data - in real app this would come from API
  const mockVersions = [
    {
      id: 1,
      contractId: 1,
      contractTitle: "Service Agreement - TechCorp Inc.",
      version: "2.1",
      createdById: 2,
      createdBy: {
        fullName: "Sarah Johnson",
        avatar: "https://pixabay.com/get/gfc4d0c7a4586ab980d5794e4f0e959409f67923283ae78c60fbed63305eb371181b2b726cc0c4018b22e1dca41975bdd974d5544f5d26020a0e25f5775166865_1280.jpg"
      },
      createdAt: new Date(Date.now() - 2 * 60 * 60 * 1000), // 2 hours ago
      changes: [
        { type: "modified", section: "Payment Terms", description: "Updated payment schedule format" },
        { type: "added", section: "Section 2.1", description: "Added late payment penalty clause" },
      ],
      isCurrent: true,
    },
    {
      id: 2,
      contractId: 1,
      contractTitle: "Service Agreement - TechCorp Inc.",
      version: "2.0",
      createdById: 3,
      createdBy: {
        fullName: "Michael Chen",
        avatar: "https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?ixlib=rb-4.0.3&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=100&h=100"
      },
      createdAt: new Date(Date.now() - 24 * 60 * 60 * 1000), // 1 day ago
      changes: [
        { type: "modified", section: "IP Rights", description: "Clarified intellectual property ownership" },
        { type: "removed", section: "Section 4.2", description: "Removed outdated compliance requirement" },
      ],
      isCurrent: false,
    },
    {
      id: 3,
      contractId: 2,
      contractTitle: "Employment Contract - Jane Doe",
      version: "1.2",
      createdById: 1,
      createdBy: {
        fullName: "John Smith",
        avatar: "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?ixlib=rb-4.0.3&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=100&h=100"
      },
      createdAt: new Date(Date.now() - 3 * 24 * 60 * 60 * 1000), // 3 days ago
      changes: [
        { type: "added", section: "Benefits", description: "Added remote work policy details" },
        { type: "modified", section: "Termination", description: "Updated notice period requirements" },
      ],
      isCurrent: true,
    },
    {
      id: 4,
      contractId: 1,
      contractTitle: "Service Agreement - TechCorp Inc.",
      version: "1.9",
      createdById: 2,
      createdBy: {
        fullName: "Sarah Johnson",
        avatar: "https://pixabay.com/get/gfc4d0c7a4586ab980d5794e4f0e959409f67923283ae78c60fbed63305eb371181b2b726cc0c4018b22e1dca41975bdd974d5544f5d26020a0e25f5775166865_1280.jpg"
      },
      createdAt: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000), // 1 week ago
      changes: [
        { type: "modified", section: "Scope of Work", description: "Expanded technical consulting services" },
        { type: "added", section: "Liability", description: "Added liability limitation clause" },
      ],
      isCurrent: false,
    },
  ];

  const contracts = contractsQuery.data || [];

  // Filter versions based on search and contract
  const filteredVersions = mockVersions.filter(version => {
    const matchesSearch = version.contractTitle.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         version.version.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         version.createdBy.fullName.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesContract = contractFilter === "all" || version.contractId.toString() === contractFilter;
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

  const getChangeTypeColor = (type: string) => {
    switch (type) {
      case 'added': return 'bg-green-100 text-green-800 dark:bg-green-900/20 dark:text-green-400';
      case 'removed': return 'bg-red-100 text-red-800 dark:bg-red-900/20 dark:text-red-400';
      case 'modified': return 'bg-blue-100 text-blue-800 dark:bg-blue-900/20 dark:text-blue-400';
      default: return 'bg-gray-100 text-gray-800 dark:bg-gray-900/20 dark:text-gray-400';
    }
  };

  const getChangeTypeIcon = (type: string) => {
    switch (type) {
      case 'added': return '+';
      case 'removed': return '-';
      case 'modified': return '~';
      default: return '';
    }
  };

  return (
    <div className="py-6">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 md:px-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Version History</h1>
          <p className="mt-2 text-gray-600 dark:text-gray-400">
            Track all changes and versions across your contracts
          </p>
        </div>

        {/* Filters */}
        <div className="flex items-center space-x-4 mb-6">
          <div className="relative flex-1 max-w-md">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
            <Input
              placeholder="Search versions, contracts, or authors..."
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

        {/* Version History Timeline */}
        {filteredVersions.length === 0 ? (
          <div className="text-center py-12">
            <History className="mx-auto h-12 w-12 text-gray-400 dark:text-gray-500" />
            <h3 className="mt-2 text-sm font-medium text-gray-900 dark:text-white">
              {mockVersions.length === 0 ? "No version history" : "No versions match your search"}
            </h3>
            <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
              {mockVersions.length === 0 
                ? "Version history will appear here as you make changes to contracts." 
                : "Try adjusting your search terms or filters."
              }
            </p>
          </div>
        ) : (
          <div className="space-y-6">
            {filteredVersions.map((version, index) => (
              <Card key={version.id} className={`relative ${version.isCurrent ? 'ring-2 ring-primary' : ''}`}>
                {/* Timeline line */}
                {index < filteredVersions.length - 1 && (
                  <div className="absolute left-8 top-16 w-px h-full bg-gray-200 dark:bg-gray-700 z-0" />
                )}
                
                <CardContent className="p-6 relative z-10">
                  <div className="flex items-start space-x-4">
                    {/* Version indicator */}
                    <div className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center ${
                      version.isCurrent 
                        ? 'bg-primary text-primary-foreground' 
                        : 'bg-gray-200 dark:bg-gray-700 text-gray-600 dark:text-gray-400'
                    }`}>
                      <GitBranch className="h-4 w-4" />
                    </div>
                    
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center justify-between mb-2">
                        <div className="flex items-center space-x-3">
                          <Link href={`/contracts/${version.contractId}/edit`}>
                            <h3 className="font-medium text-gray-900 dark:text-white hover:text-primary cursor-pointer">
                              {version.contractTitle}
                            </h3>
                          </Link>
                          <Badge variant="outline">
                            v{version.version}
                          </Badge>
                          {version.isCurrent && (
                            <Badge className="bg-primary text-primary-foreground">
                              Current
                            </Badge>
                          )}
                        </div>
                        
                        <div className="flex items-center space-x-2">
                          <Button variant="outline" size="sm">
                            <Eye className="h-4 w-4 mr-1" />
                            View
                          </Button>
                          <Button variant="outline" size="sm">
                            <Download className="h-4 w-4 mr-1" />
                            Export
                          </Button>
                        </div>
                      </div>
                      
                      <div className="flex items-center space-x-4 mb-4 text-sm text-gray-500 dark:text-gray-400">
                        <div className="flex items-center">
                          <Avatar className="h-6 w-6 mr-2">
                            <AvatarImage src={version.createdBy.avatar} alt={version.createdBy.fullName} />
                            <AvatarFallback>
                              {version.createdBy.fullName.split(' ').map(n => n[0]).join('')}
                            </AvatarFallback>
                          </Avatar>
                          <span>{version.createdBy.fullName}</span>
                        </div>
                        <div className="flex items-center">
                          <Clock className="h-4 w-4 mr-1" />
                          {formatTimeAgo(version.createdAt)}
                        </div>
                      </div>
                      
                      {/* Changes */}
                      <div className="space-y-2">
                        <h4 className="text-sm font-medium text-gray-900 dark:text-white">Changes:</h4>
                        {version.changes.map((change, changeIndex) => (
                          <div key={changeIndex} className="flex items-start space-x-3 p-3 bg-gray-50 dark:bg-gray-800 rounded-lg">
                            <Badge className={`${getChangeTypeColor(change.type)} font-mono text-xs`}>
                              {getChangeTypeIcon(change.type)}
                            </Badge>
                            <div className="flex-1">
                              <div className="flex items-center space-x-2 mb-1">
                                <span className="text-sm font-medium text-gray-900 dark:text-white">
                                  {change.section}
                                </span>
                                <Badge variant="outline" className="text-xs">
                                  {change.type}
                                </Badge>
                              </div>
                              <p className="text-sm text-gray-600 dark:text-gray-400">
                                {change.description}
                              </p>
                            </div>
                          </div>
                        ))}
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
