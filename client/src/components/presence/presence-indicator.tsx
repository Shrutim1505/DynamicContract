import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Tooltip, TooltipContent, TooltipTrigger } from "@/components/ui/tooltip";

interface PresenceUser {
  id: number;
  fullName: string;
  avatar?: string;
  isActive: boolean;
}

interface PresenceIndicatorProps {
  users?: PresenceUser[];
}

export default function PresenceIndicator({ 
  users = [
    {
      id: 1,
      fullName: "Sarah Johnson",
      avatar: "https://pixabay.com/get/g66b1c0034ad6678e247e96c1668ca4fd071197bc3d192b6c8a146cebd96038d122b85cfe07fe753b9520679a4ae3dc330b5b1922aea0da1b208750be338e9e30_1280.jpg",
      isActive: true,
    },
    {
      id: 2,
      fullName: "Michael Chen",
      avatar: "https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?ixlib=rb-4.0.3&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=150&h=150",
      isActive: true,
    },
  ]
}: PresenceIndicatorProps) {
  const activeUsers = users.filter(user => user.isActive);
  const visibleUsers = activeUsers.slice(0, 3);
  const extraCount = activeUsers.length - visibleUsers.length;

  if (activeUsers.length === 0) {
    return null;
  }

  return (
    <div className="flex items-center space-x-2">
      <span className="text-sm text-gray-500 dark:text-gray-400">Active Users:</span>
      <div className="flex -space-x-2">
        {visibleUsers.map((user) => (
          <Tooltip key={user.id}>
            <TooltipTrigger asChild>
              <Avatar className="h-8 w-8 ring-2 ring-white dark:ring-gray-900 presence-indicator">
                <AvatarImage src={user.avatar} alt={user.fullName} />
                <AvatarFallback>
                  {user.fullName.split(' ').map(name => name[0]).join('')}
                </AvatarFallback>
              </Avatar>
            </TooltipTrigger>
            <TooltipContent>
              <p>{user.fullName} - Online</p>
            </TooltipContent>
          </Tooltip>
        ))}
        
        {extraCount > 0 && (
          <Tooltip>
            <TooltipTrigger asChild>
              <div className="inline-flex items-center justify-center h-8 w-8 rounded-full ring-2 ring-white dark:ring-gray-900 bg-primary text-primary-foreground text-xs font-medium presence-indicator">
                +{extraCount}
              </div>
            </TooltipTrigger>
            <TooltipContent>
              <p>{extraCount} more users online</p>
            </TooltipContent>
          </Tooltip>
        )}
      </div>
    </div>
  );
}
