import { 
  users, projects, contracts, comments, aiSuggestions, contractVersions, presenceData,
  type User, type InsertUser, type Project, type InsertProject,
  type Contract, type InsertContract, type Comment, type InsertComment,
  type AiSuggestion, type InsertAiSuggestion, type ContractVersion, type InsertContractVersion,
  type PresenceData, type InsertPresenceData
} from "@shared/schema";

export interface IStorage {
  // Users
  getUser(id: number): Promise<User | undefined>;
  getUserByUsername(username: string): Promise<User | undefined>;
  getUserByEmail(email: string): Promise<User | undefined>;
  createUser(user: InsertUser): Promise<User>;
  updateUser(id: number, updates: Partial<User>): Promise<User | undefined>;

  // Projects
  getProject(id: number): Promise<Project | undefined>;
  getProjectsByUser(userId: number): Promise<Project[]>;
  createProject(project: InsertProject): Promise<Project>;
  updateProject(id: number, updates: Partial<Project>): Promise<Project | undefined>;
  deleteProject(id: number): Promise<boolean>;

  // Contracts
  getContract(id: number): Promise<Contract | undefined>;
  getContractsByProject(projectId: number): Promise<Contract[]>;
  getContractsByUser(userId: number): Promise<Contract[]>;
  createContract(contract: InsertContract): Promise<Contract>;
  updateContract(id: number, updates: Partial<Contract>): Promise<Contract | undefined>;
  deleteContract(id: number): Promise<boolean>;

  // Comments
  getComment(id: number): Promise<Comment | undefined>;
  getCommentsByContract(contractId: number): Promise<Comment[]>;
  createComment(comment: InsertComment): Promise<Comment>;
  updateComment(id: number, updates: Partial<Comment>): Promise<Comment | undefined>;
  deleteComment(id: number): Promise<boolean>;

  // AI Suggestions
  getAiSuggestion(id: number): Promise<AiSuggestion | undefined>;
  getAiSuggestionsByContract(contractId: number): Promise<AiSuggestion[]>;
  createAiSuggestion(suggestion: InsertAiSuggestion): Promise<AiSuggestion>;
  updateAiSuggestion(id: number, updates: Partial<AiSuggestion>): Promise<AiSuggestion | undefined>;
  deleteAiSuggestion(id: number): Promise<boolean>;

  // Contract Versions
  getContractVersion(id: number): Promise<ContractVersion | undefined>;
  getContractVersionsByContract(contractId: number): Promise<ContractVersion[]>;
  createContractVersion(version: InsertContractVersion): Promise<ContractVersion>;

  // Presence Data
  getPresenceByContract(contractId: number): Promise<PresenceData[]>;
  upsertPresence(presence: InsertPresenceData): Promise<PresenceData>;
  removePresence(userId: number, contractId: number): Promise<boolean>;
}

export class MemStorage implements IStorage {
  private users: Map<number, User> = new Map();
  private projects: Map<number, Project> = new Map();
  private contracts: Map<number, Contract> = new Map();
  private comments: Map<number, Comment> = new Map();
  private aiSuggestions: Map<number, AiSuggestion> = new Map();
  private contractVersions: Map<number, ContractVersion> = new Map();
  private presenceData: Map<string, PresenceData> = new Map();
  
  private userIdCounter = 1;
  private projectIdCounter = 1;
  private contractIdCounter = 1;
  private commentIdCounter = 1;
  private suggestionIdCounter = 1;
  private versionIdCounter = 1;

  constructor() {
    // Initialize with sample data
    this.initializeSampleData();
  }

  private initializeSampleData() {
    // Create sample users
    const sampleUser: User = {
      id: this.userIdCounter++,
      username: "john.smith",
      email: "john.smith@example.com",
      password: "hashed_password",
      fullName: "John Smith",
      role: "legal_counsel",
      avatar: "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?ixlib=rb-4.0.3&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=150&h=150",
      createdAt: new Date(),
    };
    this.users.set(sampleUser.id, sampleUser);

    // Create sample project
    const sampleProject: Project = {
      id: this.projectIdCounter++,
      name: "TechCorp Service Agreement",
      description: "Service agreement contract for TechCorp Inc.",
      ownerId: sampleUser.id,
      createdAt: new Date(),
      updatedAt: new Date(),
    };
    this.projects.set(sampleProject.id, sampleProject);

    // Create sample contract
    const sampleContract: Contract = {
      id: this.contractIdCounter++,
      title: "Service Agreement - TechCorp Inc.",
      content: `<h2>SERVICE AGREEMENT</h2>
      
<p>This Service Agreement ("Agreement") is entered into on {{DATE}} between {{CLIENT_NAME}} ("Client") and TechCorp Inc. ("Provider").</p>

<h3>1. SCOPE OF SERVICES</h3>
<p>The Provider agrees to perform the following services:</p>
<ul>
<li>Software development and maintenance services</li>
<li>Technical consulting and support</li>
<li>Quality assurance and testing</li>
</ul>

<h3>2. PAYMENT TERMS</h3>
<p>Client agrees to pay Provider a total fee of $50,000 according to the following schedule:</p>

<h3>3. INTELLECTUAL PROPERTY</h3>
<p>All intellectual property rights in work product created under this Agreement shall be owned by the Client, except for Provider's pre-existing intellectual property.</p>

<h3>4. TERMINATION</h3>
<p>Either party may terminate this Agreement with thirty (30) days written notice.</p>`,
      projectId: sampleProject.id,
      createdById: sampleUser.id,
      version: "2.1",
      status: "draft",
      riskScore: "medium",
      completeness: 87,
      wordCount: 1247,
      readingLevel: "Grade 12",
      createdAt: new Date(),
      updatedAt: new Date(),
    };
    this.contracts.set(sampleContract.id, sampleContract);
  }

  // User methods
  async getUser(id: number): Promise<User | undefined> {
    return this.users.get(id);
  }

  async getUserByUsername(username: string): Promise<User | undefined> {
    return Array.from(this.users.values()).find(user => user.username === username);
  }

  async getUserByEmail(email: string): Promise<User | undefined> {
    return Array.from(this.users.values()).find(user => user.email === email);
  }

  async createUser(insertUser: InsertUser): Promise<User> {
    const user: User = {
      ...insertUser,
      id: this.userIdCounter++,
      createdAt: new Date(),
    };
    this.users.set(user.id, user);
    return user;
  }

  async updateUser(id: number, updates: Partial<User>): Promise<User | undefined> {
    const user = this.users.get(id);
    if (!user) return undefined;
    
    const updatedUser = { ...user, ...updates };
    this.users.set(id, updatedUser);
    return updatedUser;
  }

  // Project methods
  async getProject(id: number): Promise<Project | undefined> {
    return this.projects.get(id);
  }

  async getProjectsByUser(userId: number): Promise<Project[]> {
    return Array.from(this.projects.values()).filter(project => project.ownerId === userId);
  }

  async createProject(insertProject: InsertProject): Promise<Project> {
    const project: Project = {
      ...insertProject,
      id: this.projectIdCounter++,
      createdAt: new Date(),
      updatedAt: new Date(),
    };
    this.projects.set(project.id, project);
    return project;
  }

  async updateProject(id: number, updates: Partial<Project>): Promise<Project | undefined> {
    const project = this.projects.get(id);
    if (!project) return undefined;
    
    const updatedProject = { ...project, ...updates, updatedAt: new Date() };
    this.projects.set(id, updatedProject);
    return updatedProject;
  }

  async deleteProject(id: number): Promise<boolean> {
    return this.projects.delete(id);
  }

  // Contract methods
  async getContract(id: number): Promise<Contract | undefined> {
    return this.contracts.get(id);
  }

  async getContractsByProject(projectId: number): Promise<Contract[]> {
    return Array.from(this.contracts.values()).filter(contract => contract.projectId === projectId);
  }

  async getContractsByUser(userId: number): Promise<Contract[]> {
    return Array.from(this.contracts.values()).filter(contract => contract.createdById === userId);
  }

  async createContract(insertContract: InsertContract): Promise<Contract> {
    const contract: Contract = {
      ...insertContract,
      id: this.contractIdCounter++,
      createdAt: new Date(),
      updatedAt: new Date(),
    };
    this.contracts.set(contract.id, contract);
    return contract;
  }

  async updateContract(id: number, updates: Partial<Contract>): Promise<Contract | undefined> {
    const contract = this.contracts.get(id);
    if (!contract) return undefined;
    
    const updatedContract = { ...contract, ...updates, updatedAt: new Date() };
    this.contracts.set(id, updatedContract);
    return updatedContract;
  }

  async deleteContract(id: number): Promise<boolean> {
    return this.contracts.delete(id);
  }

  // Comment methods
  async getComment(id: number): Promise<Comment | undefined> {
    return this.comments.get(id);
  }

  async getCommentsByContract(contractId: number): Promise<Comment[]> {
    return Array.from(this.comments.values()).filter(comment => comment.contractId === contractId);
  }

  async createComment(insertComment: InsertComment): Promise<Comment> {
    const comment: Comment = {
      ...insertComment,
      id: this.commentIdCounter++,
      createdAt: new Date(),
      updatedAt: new Date(),
    };
    this.comments.set(comment.id, comment);
    return comment;
  }

  async updateComment(id: number, updates: Partial<Comment>): Promise<Comment | undefined> {
    const comment = this.comments.get(id);
    if (!comment) return undefined;
    
    const updatedComment = { ...comment, ...updates, updatedAt: new Date() };
    this.comments.set(id, updatedComment);
    return updatedComment;
  }

  async deleteComment(id: number): Promise<boolean> {
    return this.comments.delete(id);
  }

  // AI Suggestion methods
  async getAiSuggestion(id: number): Promise<AiSuggestion | undefined> {
    return this.aiSuggestions.get(id);
  }

  async getAiSuggestionsByContract(contractId: number): Promise<AiSuggestion[]> {
    return Array.from(this.aiSuggestions.values()).filter(suggestion => suggestion.contractId === contractId);
  }

  async createAiSuggestion(insertSuggestion: InsertAiSuggestion): Promise<AiSuggestion> {
    const suggestion: AiSuggestion = {
      ...insertSuggestion,
      id: this.suggestionIdCounter++,
      createdAt: new Date(),
    };
    this.aiSuggestions.set(suggestion.id, suggestion);
    return suggestion;
  }

  async updateAiSuggestion(id: number, updates: Partial<AiSuggestion>): Promise<AiSuggestion | undefined> {
    const suggestion = this.aiSuggestions.get(id);
    if (!suggestion) return undefined;
    
    const updatedSuggestion = { ...suggestion, ...updates };
    this.aiSuggestions.set(id, updatedSuggestion);
    return updatedSuggestion;
  }

  async deleteAiSuggestion(id: number): Promise<boolean> {
    return this.aiSuggestions.delete(id);
  }

  // Contract Version methods
  async getContractVersion(id: number): Promise<ContractVersion | undefined> {
    return this.contractVersions.get(id);
  }

  async getContractVersionsByContract(contractId: number): Promise<ContractVersion[]> {
    return Array.from(this.contractVersions.values())
      .filter(version => version.contractId === contractId)
      .sort((a, b) => b.createdAt.getTime() - a.createdAt.getTime());
  }

  async createContractVersion(insertVersion: InsertContractVersion): Promise<ContractVersion> {
    const version: ContractVersion = {
      ...insertVersion,
      id: this.versionIdCounter++,
      createdAt: new Date(),
    };
    this.contractVersions.set(version.id, version);
    return version;
  }

  // Presence methods
  async getPresenceByContract(contractId: number): Promise<PresenceData[]> {
    return Array.from(this.presenceData.values())
      .filter(presence => presence.contractId === contractId && presence.isActive);
  }

  async upsertPresence(insertPresence: InsertPresenceData): Promise<PresenceData> {
    const key = `${insertPresence.userId}-${insertPresence.contractId}`;
    const existing = this.presenceData.get(key);
    
    const presence: PresenceData = {
      ...insertPresence,
      id: existing?.id || crypto.randomUUID(),
      lastSeen: new Date(),
    };
    
    this.presenceData.set(key, presence);
    return presence;
  }

  async removePresence(userId: number, contractId: number): Promise<boolean> {
    const key = `${userId}-${contractId}`;
    const presence = this.presenceData.get(key);
    if (presence) {
      presence.isActive = false;
      this.presenceData.set(key, presence);
      return true;
    }
    return false;
  }
}

export const storage = new MemStorage();
