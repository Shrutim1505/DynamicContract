import { Link, useLocation } from "wouter";
import { 
  Home, 
  FolderOpen, 
  FileText, 
  MessageSquare, 
  BarChart3, 
  History,
  File
} from "lucide-react";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";

const navigation = [
  { name: "Dashboard", href: "/", icon: Home },
  { name: "Projects", href: "/projects", icon: FolderOpen },
  { name: "Contracts", href: "/contracts", icon: FileText },
  { name: "Comments", href: "/comments", icon: MessageSquare },
  { name: "Analytics", href: "/analytics", icon: BarChart3 },
  { name: "Version History", href: "/version-history", icon: History },
];

export default function Sidebar() {
  const [location] = useLocation();

  return (
    <div className="hidden md:flex md:w-64 md:flex-col">
      <div className="flex flex-col flex-grow pt-5 pb-4 overflow-y-auto bg-white dark:bg-gray-900 border-r border-gray-200 dark:border-gray-800">
        {/* Logo and Brand */}
        <div className="flex items-center flex-shrink-0 px-4">
          <div className="flex items-center">
            <File className="h-8 w-8 text-primary mr-3" />
            <h1 className="text-xl font-bold text-gray-900 dark:text-white">
              DynamicContractOps
            </h1>
          </div>
        </div>
        
        {/* Navigation Menu */}
        <nav className="mt-8 flex-1 px-2 space-y-1">
          {navigation.map((item) => {
            const Icon = item.icon;
            const isActive = location === item.href;
            
            return (
              <Link key={item.name} href={item.href}>
                <a
                  className={`
                    group flex items-center px-2 py-2 text-sm font-medium rounded-md
                    ${isActive 
                      ? 'bg-primary-50 dark:bg-primary-900/20 text-primary-700 dark:text-primary-300' 
                      : 'text-gray-600 dark:text-gray-400 hover:bg-gray-50 dark:hover:bg-gray-800 hover:text-gray-900 dark:hover:text-gray-200'
                    }
                  `}
                >
                  <Icon 
                    className={`mr-3 h-5 w-5 ${
                      isActive 
                        ? 'text-primary-500 dark:text-primary-400' 
                        : 'text-gray-400 dark:text-gray-500 group-hover:text-gray-500 dark:group-hover:text-gray-400'
                    }`} 
                  />
                  {item.name}
                </a>
              </Link>
            );
          })}
        </nav>
        
        {/* User Profile */}
        <div className="flex-shrink-0 flex border-t border-gray-200 dark:border-gray-800 p-4">
          <div className="flex items-center">
            <Avatar className="h-9 w-9">
              <AvatarImage 
                src="https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?ixlib=rb-4.0.3&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=150&h=150" 
                alt="User profile" 
              />
              <AvatarFallback>JS</AvatarFallback>
            </Avatar>
            <div className="ml-3">
              <p className="text-sm font-medium text-gray-700 dark:text-gray-300">
                John Smith
              </p>
              <p className="text-xs font-medium text-gray-500 dark:text-gray-400">
                Legal Counsel
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
