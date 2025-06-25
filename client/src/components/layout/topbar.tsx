import { Search, Bell, Menu } from "lucide-react";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import PresenceIndicator from "@/components/presence/presence-indicator";

export default function TopBar() {
  return (
    <div className="relative z-10 flex-shrink-0 flex h-16 bg-white dark:bg-gray-900 shadow border-b border-gray-200 dark:border-gray-800">
      <Button
        variant="ghost"
        size="sm"
        className="px-4 border-r border-gray-200 dark:border-gray-800 text-gray-500 dark:text-gray-400 md:hidden"
      >
        <Menu className="h-6 w-6" />
      </Button>
      
      <div className="flex-1 px-4 flex justify-between items-center">
        <div className="flex-1 flex">
          <div className="w-full flex md:ml-0">
            <div className="relative w-64">
              <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <Search className="h-5 w-5 text-gray-400 dark:text-gray-500" />
              </div>
              <Input
                className="block w-full pl-10 pr-3 py-2 border border-gray-300 dark:border-gray-700 rounded-md leading-5 bg-white dark:bg-gray-800 placeholder-gray-500 dark:placeholder-gray-400 focus:outline-none focus:ring-1 focus:ring-primary-500 focus:border-primary-500 text-sm"
                placeholder="Search contracts..."
                type="search"
              />
            </div>
          </div>
        </div>
        
        {/* Real-time Presence Indicators */}
        <div className="ml-4 flex items-center md:ml-6">
          <PresenceIndicator />
          
          <Button
            variant="ghost"
            size="sm"
            className="ml-4 text-gray-400 dark:text-gray-500 hover:text-gray-500 dark:hover:text-gray-400"
          >
            <Bell className="h-6 w-6" />
          </Button>
        </div>
      </div>
    </div>
  );
}
