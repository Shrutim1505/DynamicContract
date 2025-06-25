export interface CommentPosition {
  start: number;
  end: number;
  text: string;
}

export interface CommentWithUser {
  id: number;
  content: string;
  contractId: number;
  userId: number;
  user: {
    id: number;
    fullName: string;
    avatar?: string;
  };
  position?: CommentPosition;
  parentId?: number;
  replies?: CommentWithUser[];
  createdAt: Date;
  updatedAt: Date;
}
