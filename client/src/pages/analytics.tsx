import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { Badge } from "@/components/ui/badge";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, LineChart, Line, PieChart, Pie, Cell } from "recharts";
import { TrendingUp, TrendingDown, FileText, Users, MessageSquare, AlertTriangle, Clock, CheckCircle } from "lucide-react";

export default function Analytics() {
  // Mock analytics data - in real app this would come from API
  const overviewStats = [
    {
      title: "Total Contracts",
      value: "24",
      change: "+12%",
      trend: "up",
      icon: FileText,
    },
    {
      title: "Active Collaborators",
      value: "8",
      change: "+3",
      trend: "up",
      icon: Users,
    },
    {
      title: "Pending Comments",
      value: "15",
      change: "-5",
      trend: "down",
      icon: MessageSquare,
    },
    {
      title: "Avg. Risk Score",
      value: "Medium",
      change: "Stable",
      trend: "neutral",
      icon: AlertTriangle,
    },
  ];

  const contractsByStatus = [
    { name: "Draft", value: 12, color: "#fbbf24" },
    { name: "Review", value: 8, color: "#3b82f6" },
    { name: "Final", value: 4, color: "#10b981" },
  ];

  const weeklyActivity = [
    { day: "Mon", contracts: 4, comments: 12, suggestions: 8 },
    { day: "Tue", contracts: 6, comments: 15, suggestions: 11 },
    { day: "Wed", contracts: 3, comments: 8, suggestions: 6 },
    { day: "Thu", contracts: 8, comments: 20, suggestions: 14 },
    { day: "Fri", contracts: 5, comments: 18, suggestions: 12 },
    { day: "Sat", contracts: 2, comments: 5, suggestions: 3 },
    { day: "Sun", contracts: 1, comments: 3, suggestions: 2 },
  ];

  const riskDistribution = [
    { month: "Jan", low: 45, medium: 35, high: 20 },
    { month: "Feb", low: 50, medium: 30, high: 20 },
    { month: "Mar", low: 55, medium: 28, high: 17 },
    { month: "Apr", low: 48, medium: 32, high: 20 },
    { month: "May", low: 52, medium: 30, high: 18 },
    { month: "Jun", low: 58, medium: 27, high: 15 },
  ];

  const topRiskFactors = [
    { factor: "Missing termination clauses", count: 8, severity: "high" },
    { factor: "Vague payment terms", count: 6, severity: "medium" },
    { factor: "Insufficient liability coverage", count: 5, severity: "high" },
    { factor: "Unclear IP ownership", count: 4, severity: "medium" },
    { factor: "Missing force majeure", count: 3, severity: "low" },
  ];

  const aiSuggestionStats = {
    totalSuggestions: 142,
    accepted: 89,
    dismissed: 34,
    pending: 19,
    acceptanceRate: 72,
  };

  const getTrendIcon = (trend: string) => {
    switch (trend) {
      case 'up':
        return <TrendingUp className="h-4 w-4 text-green-500" />;
      case 'down':
        return <TrendingDown className="h-4 w-4 text-red-500" />;
      default:
        return <div className="h-4 w-4" />;
    }
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'high': return 'bg-red-100 text-red-800 dark:bg-red-900/20 dark:text-red-400';
      case 'medium': return 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/20 dark:text-yellow-400';
      case 'low': return 'bg-green-100 text-green-800 dark:bg-green-900/20 dark:text-green-400';
      default: return 'bg-gray-100 text-gray-800 dark:bg-gray-900/20 dark:text-gray-400';
    }
  };

  return (
    <div className="py-6">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 md:px-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Analytics Dashboard</h1>
          <p className="mt-2 text-gray-600 dark:text-gray-400">
            Insights and metrics for your contract management activities
          </p>
        </div>

        {/* Overview Stats */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          {overviewStats.map((stat) => {
            const Icon = stat.icon;
            return (
              <Card key={stat.title}>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">{stat.title}</CardTitle>
                  <Icon className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{stat.value}</div>
                  <div className="flex items-center text-xs text-muted-foreground">
                    {getTrendIcon(stat.trend)}
                    <span className="ml-1">{stat.change} from last month</span>
                  </div>
                </CardContent>
              </Card>
            );
          })}
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          {/* Contract Status Distribution */}
          <Card>
            <CardHeader>
              <CardTitle>Contract Status Distribution</CardTitle>
              <CardDescription>Current status of all contracts</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={contractsByStatus}
                      cx="50%"
                      cy="50%"
                      innerRadius={60}
                      outerRadius={100}
                      paddingAngle={5}
                      dataKey="value"
                    >
                      {contractsByStatus.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Pie>
                    <Tooltip />
                  </PieChart>
                </ResponsiveContainer>
              </div>
              <div className="flex justify-center space-x-4 mt-4">
                {contractsByStatus.map((item) => (
                  <div key={item.name} className="flex items-center">
                    <div 
                      className="w-3 h-3 rounded-full mr-2" 
                      style={{ backgroundColor: item.color }}
                    />
                    <span className="text-sm">{item.name}: {item.value}</span>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Weekly Activity */}
          <Card>
            <CardHeader>
              <CardTitle>Weekly Activity</CardTitle>
              <CardDescription>Contract creation and collaboration activity</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={weeklyActivity}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="day" />
                    <YAxis />
                    <Tooltip />
                    <Bar dataKey="contracts" fill="#3b82f6" name="Contracts" />
                    <Bar dataKey="comments" fill="#10b981" name="Comments" />
                    <Bar dataKey="suggestions" fill="#f59e0b" name="AI Suggestions" />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </CardContent>
          </Card>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
          {/* Risk Score Trends */}
          <Card className="lg:col-span-2">
            <CardHeader>
              <CardTitle>Risk Score Distribution Over Time</CardTitle>
              <CardDescription>Percentage of contracts by risk level</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={riskDistribution}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="month" />
                    <YAxis />
                    <Tooltip />
                    <Line type="monotone" dataKey="low" stroke="#10b981" name="Low Risk" />
                    <Line type="monotone" dataKey="medium" stroke="#f59e0b" name="Medium Risk" />
                    <Line type="monotone" dataKey="high" stroke="#ef4444" name="High Risk" />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            </CardContent>
          </Card>

          {/* AI Suggestions Performance */}
          <Card>
            <CardHeader>
              <CardTitle>AI Suggestions</CardTitle>
              <CardDescription>AI assistance performance metrics</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600 dark:text-gray-400">Total Suggestions</span>
                <span className="font-medium">{aiSuggestionStats.totalSuggestions}</span>
              </div>
              
              <div className="space-y-2">
                <div className="flex items-center justify-between text-sm">
                  <span className="text-gray-600 dark:text-gray-400">Acceptance Rate</span>
                  <span className="font-medium">{aiSuggestionStats.acceptanceRate}%</span>
                </div>
                <Progress value={aiSuggestionStats.acceptanceRate} className="h-2" />
              </div>

              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <div className="flex items-center">
                    <CheckCircle className="h-4 w-4 text-green-500 mr-2" />
                    <span className="text-sm">Accepted</span>
                  </div>
                  <span className="font-medium">{aiSuggestionStats.accepted}</span>
                </div>
                
                <div className="flex items-center justify-between">
                  <div className="flex items-center">
                    <Clock className="h-4 w-4 text-yellow-500 mr-2" />
                    <span className="text-sm">Pending</span>
                  </div>
                  <span className="font-medium">{aiSuggestionStats.pending}</span>
                </div>
                
                <div className="flex items-center justify-between">
                  <div className="flex items-center">
                    <div className="h-4 w-4 bg-gray-400 rounded-full mr-2" />
                    <span className="text-sm">Dismissed</span>
                  </div>
                  <span className="font-medium">{aiSuggestionStats.dismissed}</span>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Top Risk Factors */}
        <Card>
          <CardHeader>
            <CardTitle>Top Risk Factors</CardTitle>
            <CardDescription>Most common issues identified across contracts</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {topRiskFactors.map((risk, index) => (
                <div key={risk.factor} className="flex items-center justify-between p-4 border border-gray-200 dark:border-gray-700 rounded-lg">
                  <div className="flex items-center space-x-3">
                    <div className="text-sm font-medium text-gray-500 dark:text-gray-400">
                      #{index + 1}
                    </div>
                    <div>
                      <p className="font-medium text-gray-900 dark:text-white">{risk.factor}</p>
                      <p className="text-sm text-gray-500 dark:text-gray-400">
                        Found in {risk.count} contracts
                      </p>
                    </div>
                  </div>
                  <Badge className={getSeverityColor(risk.severity)}>
                    {risk.severity} risk
                  </Badge>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
