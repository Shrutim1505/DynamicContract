export interface ContractPosition {
  line: number;
  character: number;
}

export interface ContractChange {
  type: 'added' | 'removed' | 'modified';
  content: string;
  position?: {
    start: number;
    end: number;
  };
  userId: number;
  timestamp: string;
}

export interface ContractAnalytics {
  wordCount: number;
  readingLevel: string;
  riskScore: 'low' | 'medium' | 'high';
  completeness: number;
  riskFactors: Array<{
    type: 'error' | 'warning' | 'info';
    message: string;
  }>;
}
