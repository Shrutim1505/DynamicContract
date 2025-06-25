export interface PresenceUser {
  id: number;
  fullName: string;
  avatar?: string;
  position?: {
    line: number;
    character: number;
  };
  isActive: boolean;
  lastSeen: Date;
}

export interface CursorPosition {
  userId: number;
  position: {
    line: number;
    character: number;
  };
  user: {
    fullName: string;
    avatar?: string;
  };
}
