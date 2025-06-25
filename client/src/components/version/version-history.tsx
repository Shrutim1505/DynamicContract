import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { History, Eye, Download } from "lucide-react";
import { ContractVersion } from "@shared/schema";

interface VersionHistoryProps {
  contractId: number;
  versions: ContractVersion[];
}

export default function VersionHistory({ contractId, versions }: VersionHistoryProps) {
  // Mock version data if none provided
  const mockVersions = [
    {
      id: 1,
      contractId,
      version: "Current Version",
      content: "",
      changes: [],
      createdById: 1,
      createdAt: new Date(Date.now() - 0), // now
    },
    {
      id: 2,
      contractId,
      version: "Version 2.1",
      content: "",
      changes: [],
      createdById: 2,
      createdAt: new Date(Date.now() - 24 * 60 * 60 * 1000), // 1 day ago
    },
    {
      id: 3,
      contractId,
      version: "Version 2.0",
      content: "",
      changes: [],
      createdById: 3,
      createdAt: new Date(Date.now() - 3 * 24 * 60 * 60 * 1000), // 3 days ago
    },
  ];

  const displayVersions = versions.length > 0 ? versions : mockVersions;

  const formatTimeAgo = (date: Date) => {
    const now = new Date();
    const diffInMinutes = Math.floor((now.getTime() - new Date(date).getTime()) / (1000 * 60));
    
    if (diffInMinutes < 60) {
      return `${diffInMinutes}m ago`;
    } else if (diffInMinutes < 1440) {
      return `${Math.floor(diffInMinutes / 60)}h ago`;
    } else {
      return `${Math.floor(diffInMinutes / 1440)}d ago`;
    }
  };

  const handleViewVersion = (versionId: number) => {
    console.log('Viewing version:', versionId);
    // In real app, this would open a version comparison view
  };

  const handleDownloadVersion = (versionId: number) => {
    console.log('Downloading version:', versionId);
    // In real app, this would download the version
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center">
          <History className="h-5 w-5 mr-2" />
          Version History
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-3">
          {displayVersions.map((version, index) => (
            <div 
              key={version.id} 
              className="flex items-center space-x-3 p-3 hover:bg-gray-50 dark:hover:bg-gray-800/50 rounded-lg transition-colors"
            >
              <div className={`w-2 h-2 rounded-full ${
                index === 0 
                  ? 'bg-green-400' 
                  : 'bg-gray-300 dark:bg-gray-600'
              }`} />
              
              <div className="flex-1 min-w-0">
                <div className="flex items-center space-x-2 mb-1">
                  <p className={`text-sm font-medium ${
                    index === 0 
                      ? 'text-gray-900 dark:text-white' 
                      : 'text-gray-700 dark:text-gray-300'
                  }`}>
                    {version.version}
                  </p>
                  {index === 0 && (
                    <Badge className="bg-green-100 text-green-800 dark:bg-green-900/20 dark:text-green-400 text-xs">
                      Current
                    </Badge>
                  )}
                </div>
                <p className="text-xs text-gray-500 dark:text-gray-400">
                  Modified {formatTimeAgo(version.createdAt)}
                </p>
              </div>
              
              <div className="flex items-center space-x-1">
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => handleViewVersion(version.id)}
                  className="h-8 w-8 p-0"
                >
                  <Eye className="h-4 w-4" />
                </Button>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => handleDownloadVersion(version.id)}
                  className="h-8 w-8 p-0"
                >
                  <Download className="h-4 w-4" />
                </Button>
              </div>
            </div>
          ))}
        </div>
        
        {displayVersions.length === 0 && (
          <div className="text-center py-6">
            <History className="mx-auto h-8 w-8 text-gray-400 dark:text-gray-500 mb-2" />
            <p className="text-sm text-gray-500 dark:text-gray-400">
              No version history available
            </p>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
