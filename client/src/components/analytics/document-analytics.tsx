import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { Badge } from "@/components/ui/badge";
import { FileText, AlertTriangle, CheckCircle, TrendingUp } from "lucide-react";
import { Contract } from "@shared/schema";

interface DocumentAnalyticsProps {
  contract: Contract;
}

export default function DocumentAnalytics({ contract }: DocumentAnalyticsProps) {
  // Mock risk factors - in real app this would come from AI analysis
  const riskFactors = [
    {
      type: 'error' as const,
      message: 'Missing termination clauses'
    },
    {
      type: 'warning' as const,
      message: 'Vague payment terms'
    },
    {
      type: 'info' as const,
      message: 'IP rights well-defined'
    }
  ];

  const getRiskScoreColor = (score: string) => {
    switch (score?.toLowerCase()) {
      case 'low':
        return 'text-green-600 dark:text-green-400';
      case 'medium':
        return 'text-yellow-600 dark:text-yellow-400';
      case 'high':
        return 'text-red-600 dark:text-red-400';
      default:
        return 'text-gray-600 dark:text-gray-400';
    }
  };

  const getRiskFactorIcon = (type: 'error' | 'warning' | 'info') => {
    switch (type) {
      case 'error':
        return <div className="w-3 h-3 bg-red-400 rounded-full" />;
      case 'warning':
        return <div className="w-3 h-3 bg-yellow-400 rounded-full" />;
      case 'info':
        return <div className="w-3 h-3 bg-green-400 rounded-full" />;
    }
  };

  const completenessColor = (completeness: number) => {
    if (completeness >= 80) return 'text-green-600 dark:text-green-400';
    if (completeness >= 60) return 'text-yellow-600 dark:text-yellow-400';
    return 'text-red-600 dark:text-red-400';
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center">
          <TrendingUp className="h-5 w-5 mr-2" />
          Document Analytics
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          <div className="flex justify-between items-center">
            <span className="text-sm text-gray-600 dark:text-gray-400">Word Count</span>
            <span className="text-sm font-medium text-gray-900 dark:text-white">
              {contract.wordCount?.toLocaleString() || '0'}
            </span>
          </div>
          
          <div className="flex justify-between items-center">
            <span className="text-sm text-gray-600 dark:text-gray-400">Reading Level</span>
            <span className="text-sm font-medium text-gray-900 dark:text-white">
              {contract.readingLevel || 'Not analyzed'}
            </span>
          </div>
          
          <div className="flex justify-between items-center">
            <span className="text-sm text-gray-600 dark:text-gray-400">Risk Score</span>
            <span className={`text-sm font-medium capitalize ${getRiskScoreColor(contract.riskScore || 'medium')}`}>
              {contract.riskScore || 'Medium'}
            </span>
          </div>
          
          <div className="space-y-2">
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-600 dark:text-gray-400">Completeness</span>
              <span className={`text-sm font-medium ${completenessColor(contract.completeness || 0)}`}>
                {contract.completeness || 0}%
              </span>
            </div>
            <Progress 
              value={contract.completeness || 0} 
              className="h-2"
            />
          </div>
          
          {/* Risk Breakdown */}
          <div className="pt-3 border-t border-gray-200 dark:border-gray-700">
            <h4 className="text-sm font-medium text-gray-900 dark:text-white mb-3">Risk Factors</h4>
            <div className="space-y-2">
              {riskFactors.map((factor, index) => (
                <div key={index} className="flex items-center space-x-3">
                  {getRiskFactorIcon(factor.type)}
                  <span className="text-xs text-gray-600 dark:text-gray-400 flex-1">
                    {factor.message}
                  </span>
                </div>
              ))}
            </div>
          </div>

          {/* Additional Metrics */}
          <div className="pt-3 border-t border-gray-200 dark:border-gray-700">
            <div className="grid grid-cols-2 gap-4 text-sm">
              <div className="text-center">
                <div className="text-xs text-gray-500 dark:text-gray-400 mb-1">Clauses</div>
                <div className="font-medium text-gray-900 dark:text-white">12</div>
              </div>
              <div className="text-center">
                <div className="text-xs text-gray-500 dark:text-gray-400 mb-1">Sections</div>
                <div className="font-medium text-gray-900 dark:text-white">4</div>
              </div>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
