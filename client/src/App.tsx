import { Switch, Route } from "wouter";
import { queryClient } from "./lib/queryClient";
import { QueryClientProvider } from "@tanstack/react-query";
import { Toaster } from "@/components/ui/toaster";
import { TooltipProvider } from "@/components/ui/tooltip";
import Dashboard from "@/pages/dashboard";
import ContractEditor from "@/pages/contract-editor";
import Projects from "@/pages/projects";
import Contracts from "@/pages/contracts";  
import Comments from "@/pages/comments";
import Analytics from "@/pages/analytics";
import VersionHistory from "@/pages/version-history";
import NotFound from "@/pages/not-found";
import Sidebar from "@/components/layout/sidebar";
import TopBar from "@/components/layout/topbar";

function Router() {
  return (
    <div className="flex h-screen overflow-hidden">
      <Sidebar />
      <div className="flex flex-col w-0 flex-1 overflow-hidden">
        <TopBar />
        <main className="flex-1 relative overflow-y-auto focus:outline-none">
          <Switch>
            <Route path="/" component={Dashboard} />
            <Route path="/projects" component={Projects} />
            <Route path="/contracts" component={Contracts} />
            <Route path="/contracts/:id/edit" component={ContractEditor} />
            <Route path="/comments" component={Comments} />
            <Route path="/analytics" component={Analytics} />
            <Route path="/version-history" component={VersionHistory} />
            <Route component={NotFound} />
          </Switch>
        </main>
      </div>
    </div>
  );
}

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <TooltipProvider>
        <Toaster />
        <Router />
      </TooltipProvider>
    </QueryClientProvider>
  );
}

export default App;
