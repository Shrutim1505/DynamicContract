import { apiRequest } from "./queryClient";

export const api = {
  // Auth
  login: async (username: string, password: string) => {
    const response = await apiRequest("POST", "/api/auth/login", { username, password });
    return response.json();
  },

  // Users
  getUser: async (id: number) => {
    const response = await apiRequest("GET", `/api/users/${id}`);
    return response.json();
  },

  createUser: async (userData: any) => {
    const response = await apiRequest("POST", "/api/users", userData);
    return response.json();
  },

  // Projects
  getProjects: async (userId: number) => {
    const response = await apiRequest("GET", `/api/projects?userId=${userId}`);
    return response.json();
  },

  getProject: async (id: number) => {
    const response = await apiRequest("GET", `/api/projects/${id}`);
    return response.json();
  },

  createProject: async (projectData: any) => {
    const response = await apiRequest("POST", "/api/projects", projectData);
    return response.json();
  },

  updateProject: async (id: number, updates: any) => {
    const response = await apiRequest("PUT", `/api/projects/${id}`, updates);
    return response.json();
  },

  deleteProject: async (id: number) => {
    await apiRequest("DELETE", `/api/projects/${id}`);
  },

  // Contracts
  getContracts: async (params: { projectId?: number; userId?: number }) => {
    const queryParams = new URLSearchParams();
    if (params.projectId) queryParams.set('projectId', params.projectId.toString());
    if (params.userId) queryParams.set('userId', params.userId.toString());
    
    const response = await apiRequest("GET", `/api/contracts?${queryParams}`);
    return response.json();
  },

  getContract: async (id: number) => {
    const response = await apiRequest("GET", `/api/contracts/${id}`);
    return response.json();
  },

  createContract: async (contractData: any) => {
    const response = await apiRequest("POST", "/api/contracts", contractData);
    return response.json();
  },

  updateContract: async (id: number, updates: any) => {
    const response = await apiRequest("PUT", `/api/contracts/${id}`, updates);
    return response.json();
  },

  deleteContract: async (id: number) => {
    await apiRequest("DELETE", `/api/contracts/${id}`);
  },

  // Comments
  getContractComments: async (contractId: number) => {
    const response = await apiRequest("GET", `/api/contracts/${contractId}/comments`);
    return response.json();
  },

  createComment: async (contractId: number, commentData: any) => {
    const response = await apiRequest("POST", `/api/contracts/${contractId}/comments`, commentData);
    return response.json();
  },

  updateComment: async (id: number, updates: any) => {
    const response = await apiRequest("PUT", `/api/comments/${id}`, updates);
    return response.json();
  },

  deleteComment: async (id: number) => {
    await apiRequest("DELETE", `/api/comments/${id}`);
  },

  // AI Suggestions
  getContractSuggestions: async (contractId: number) => {
    const response = await apiRequest("GET", `/api/contracts/${contractId}/suggestions`);
    return response.json();
  },

  createSuggestion: async (contractId: number, suggestionData: any) => {
    const response = await apiRequest("POST", `/api/contracts/${contractId}/suggestions`, suggestionData);
    return response.json();
  },

  updateSuggestion: async (id: number, updates: any) => {
    const response = await apiRequest("PUT", `/api/suggestions/${id}`, updates);
    return response.json();
  },

  // Contract Versions
  getContractVersions: async (contractId: number) => {
    const response = await apiRequest("GET", `/api/contracts/${contractId}/versions`);
    return response.json();
  },

  createContractVersion: async (contractId: number, versionData: any) => {
    const response = await apiRequest("POST", `/api/contracts/${contractId}/versions`, versionData);
    return response.json();
  },

  // Presence
  getContractPresence: async (contractId: number) => {
    const response = await apiRequest("GET", `/api/contracts/${contractId}/presence`);
    return response.json();
  },
};
