import type { Express } from "express";
import { createServer, type Server } from "http";
import { WebSocketServer, WebSocket } from "ws";
import { storage } from "./storage";
import { 
  insertUserSchema, insertProjectSchema, insertContractSchema, 
  insertCommentSchema, insertAiSuggestionSchema, insertContractVersionSchema,
  insertPresenceDataSchema
} from "@shared/schema";

export async function registerRoutes(app: Express): Promise<Server> {
  const httpServer = createServer(app);

  // WebSocket setup for real-time collaboration
  const wss = new WebSocketServer({ server: httpServer, path: '/ws' });
  
  const clients = new Map<number, Set<WebSocket>>();
  
  wss.on('connection', (ws, request) => {
    let userId: number | undefined;
    let contractId: number | undefined;

    ws.on('message', async (data) => {
      try {
        const message = JSON.parse(data.toString());
        
        switch (message.type) {
          case 'join':
            userId = message.userId;
            contractId = message.contractId;
            
            if (!userId || !contractId) break;
            
            if (!clients.has(contractId)) {
              clients.set(contractId, new Set());
            }
            clients.get(contractId)!.add(ws);
            
            // Update presence
            await storage.upsertPresence({
              userId,
              contractId,
              position: message.position || null,
              isActive: true,
            });
            
            // Broadcast presence update
            broadcastToContract(contractId, {
              type: 'presence_update',
              userId,
              position: message.position,
              action: 'joined'
            }, ws);
            break;

          case 'cursor_move':
            if (userId && contractId) {
              await storage.upsertPresence({
                userId,
                contractId,
                position: message.position,
                isActive: true,
              });
              
              broadcastToContract(contractId, {
                type: 'cursor_update',
                userId,
                position: message.position
              }, ws);
            }
            break;

          case 'content_change':
            if (contractId) {
              // Update contract content
              await storage.updateContract(contractId, {
                content: message.content,
                wordCount: message.wordCount || 0,
              });
              
              // Broadcast content change
              broadcastToContract(contractId, {
                type: 'content_update',
                content: message.content,
                userId,
                timestamp: new Date().toISOString()
              }, ws);
            }
            break;
        }
      } catch (error) {
        console.error('WebSocket message error:', error);
        ws.send(JSON.stringify({ type: 'error', message: 'Invalid message format' }));
      }
    });

    ws.on('close', async () => {
      if (userId && contractId) {
        await storage.removePresence(userId, contractId);
        
        const contractClients = clients.get(contractId);
        if (contractClients) {
          contractClients.delete(ws);
          if (contractClients.size === 0) {
            clients.delete(contractId);
          }
        }
        
        broadcastToContract(contractId, {
          type: 'presence_update',
          userId,
          action: 'left'
        });
      }
    });
  });

  function broadcastToContract(contractId: number, message: any, excludeWs?: WebSocket) {
    const contractClients = clients.get(contractId);
    if (contractClients) {
      contractClients.forEach(client => {
        if (client !== excludeWs && client.readyState === WebSocket.OPEN) {
          client.send(JSON.stringify(message));
        }
      });
    }
  }

  // Authentication endpoint
  app.post("/api/auth/login", async (req, res) => {
    try {
      const { username, password } = req.body;
      
      const user = await storage.getUserByUsername(username);
      if (!user || user.password !== password) {
        return res.status(401).json({ message: "Invalid credentials" });
      }
      
      res.json({ user: { ...user, password: undefined } });
    } catch (error) {
      res.status(500).json({ message: "Login failed" });
    }
  });

  // User routes
  app.get("/api/users/:id", async (req, res) => {
    try {
      const user = await storage.getUser(parseInt(req.params.id));
      if (!user) {
        return res.status(404).json({ message: "User not found" });
      }
      res.json({ ...user, password: undefined });
    } catch (error) {
      res.status(500).json({ message: "Failed to fetch user" });
    }
  });

  app.post("/api/users", async (req, res) => {
    try {
      const userData = insertUserSchema.parse(req.body);
      const user = await storage.createUser(userData);
      res.status(201).json({ ...user, password: undefined });
    } catch (error) {
      res.status(400).json({ message: "Invalid user data" });
    }
  });

  // Project routes
  app.get("/api/projects", async (req, res) => {
    try {
      const userId = parseInt(req.query.userId as string);
      const projects = await storage.getProjectsByUser(userId);
      res.json(projects);
    } catch (error) {
      res.status(500).json({ message: "Failed to fetch projects" });
    }
  });

  app.get("/api/projects/:id", async (req, res) => {
    try {
      const project = await storage.getProject(parseInt(req.params.id));
      if (!project) {
        return res.status(404).json({ message: "Project not found" });
      }
      res.json(project);
    } catch (error) {
      res.status(500).json({ message: "Failed to fetch project" });
    }
  });

  app.post("/api/projects", async (req, res) => {
    try {
      const projectData = insertProjectSchema.parse(req.body);
      const project = await storage.createProject(projectData);
      res.status(201).json(project);
    } catch (error) {
      res.status(400).json({ message: "Invalid project data" });
    }
  });

  app.put("/api/projects/:id", async (req, res) => {
    try {
      const id = parseInt(req.params.id);
      const updates = req.body;
      const project = await storage.updateProject(id, updates);
      if (!project) {
        return res.status(404).json({ message: "Project not found" });
      }
      res.json(project);
    } catch (error) {
      res.status(500).json({ message: "Failed to update project" });
    }
  });

  app.delete("/api/projects/:id", async (req, res) => {
    try {
      const id = parseInt(req.params.id);
      const deleted = await storage.deleteProject(id);
      if (!deleted) {
        return res.status(404).json({ message: "Project not found" });
      }
      res.status(204).send();
    } catch (error) {
      res.status(500).json({ message: "Failed to delete project" });
    }
  });

  // Contract routes
  app.get("/api/contracts", async (req, res) => {
    try {
      const projectId = req.query.projectId ? parseInt(req.query.projectId as string) : undefined;
      const userId = req.query.userId ? parseInt(req.query.userId as string) : undefined;
      
      let contracts;
      if (projectId) {
        contracts = await storage.getContractsByProject(projectId);
      } else if (userId) {
        contracts = await storage.getContractsByUser(userId);
      } else {
        contracts = [];
      }
      
      res.json(contracts);
    } catch (error) {
      res.status(500).json({ message: "Failed to fetch contracts" });
    }
  });

  app.get("/api/contracts/:id", async (req, res) => {
    try {
      const contract = await storage.getContract(parseInt(req.params.id));
      if (!contract) {
        return res.status(404).json({ message: "Contract not found" });
      }
      res.json(contract);
    } catch (error) {
      res.status(500).json({ message: "Failed to fetch contract" });
    }
  });

  app.post("/api/contracts", async (req, res) => {
    try {
      const contractData = insertContractSchema.parse(req.body);
      const contract = await storage.createContract(contractData);
      res.status(201).json(contract);
    } catch (error) {
      res.status(400).json({ message: "Invalid contract data" });
    }
  });

  app.put("/api/contracts/:id", async (req, res) => {
    try {
      const id = parseInt(req.params.id);
      const updates = req.body;
      const contract = await storage.updateContract(id, updates);
      if (!contract) {
        return res.status(404).json({ message: "Contract not found" });
      }
      res.json(contract);
    } catch (error) {
      res.status(500).json({ message: "Failed to update contract" });
    }
  });

  app.delete("/api/contracts/:id", async (req, res) => {
    try {
      const id = parseInt(req.params.id);
      const deleted = await storage.deleteContract(id);
      if (!deleted) {
        return res.status(404).json({ message: "Contract not found" });
      }
      res.status(204).send();
    } catch (error) {
      res.status(500).json({ message: "Failed to delete contract" });
    }
  });

  // Comment routes
  app.get("/api/contracts/:id/comments", async (req, res) => {
    try {
      const contractId = parseInt(req.params.id);
      const comments = await storage.getCommentsByContract(contractId);
      res.json(comments);
    } catch (error) {
      res.status(500).json({ message: "Failed to fetch comments" });
    }
  });

  app.post("/api/contracts/:id/comments", async (req, res) => {
    try {
      const contractId = parseInt(req.params.id);
      const commentData = insertCommentSchema.parse({
        ...req.body,
        contractId
      });
      const comment = await storage.createComment(commentData);
      res.status(201).json(comment);
    } catch (error) {
      res.status(400).json({ message: "Invalid comment data" });
    }
  });

  app.put("/api/comments/:id", async (req, res) => {
    try {
      const id = parseInt(req.params.id);
      const updates = req.body;
      const comment = await storage.updateComment(id, updates);
      if (!comment) {
        return res.status(404).json({ message: "Comment not found" });
      }
      res.json(comment);
    } catch (error) {
      res.status(500).json({ message: "Failed to update comment" });
    }
  });

  app.delete("/api/comments/:id", async (req, res) => {
    try {
      const id = parseInt(req.params.id);
      const deleted = await storage.deleteComment(id);
      if (!deleted) {
        return res.status(404).json({ message: "Comment not found" });
      }
      res.status(204).send();
    } catch (error) {
      res.status(500).json({ message: "Failed to delete comment" });
    }
  });

  // AI Suggestions routes
  app.get("/api/contracts/:id/suggestions", async (req, res) => {
    try {
      const contractId = parseInt(req.params.id);
      const suggestions = await storage.getAiSuggestionsByContract(contractId);
      res.json(suggestions);
    } catch (error) {
      res.status(500).json({ message: "Failed to fetch AI suggestions" });
    }
  });

  app.post("/api/contracts/:id/suggestions", async (req, res) => {
    try {
      const contractId = parseInt(req.params.id);
      const suggestionData = insertAiSuggestionSchema.parse({
        ...req.body,
        contractId
      });
      const suggestion = await storage.createAiSuggestion(suggestionData);
      res.status(201).json(suggestion);
    } catch (error) {
      res.status(400).json({ message: "Invalid suggestion data" });
    }
  });

  app.put("/api/suggestions/:id", async (req, res) => {
    try {
      const id = parseInt(req.params.id);
      const updates = req.body;
      const suggestion = await storage.updateAiSuggestion(id, updates);
      if (!suggestion) {
        return res.status(404).json({ message: "Suggestion not found" });
      }
      res.json(suggestion);
    } catch (error) {
      res.status(500).json({ message: "Failed to update suggestion" });
    }
  });

  // Contract Version routes
  app.get("/api/contracts/:id/versions", async (req, res) => {
    try {
      const contractId = parseInt(req.params.id);
      const versions = await storage.getContractVersionsByContract(contractId);
      res.json(versions);
    } catch (error) {
      res.status(500).json({ message: "Failed to fetch contract versions" });
    }
  });

  app.post("/api/contracts/:id/versions", async (req, res) => {
    try {
      const contractId = parseInt(req.params.id);
      const versionData = insertContractVersionSchema.parse({
        ...req.body,
        contractId
      });
      const version = await storage.createContractVersion(versionData);
      res.status(201).json(version);
    } catch (error) {
      res.status(400).json({ message: "Invalid version data" });
    }
  });

  // Presence routes
  app.get("/api/contracts/:id/presence", async (req, res) => {
    try {
      const contractId = parseInt(req.params.id);
      const presence = await storage.getPresenceByContract(contractId);
      res.json(presence);
    } catch (error) {
      res.status(500).json({ message: "Failed to fetch presence data" });
    }
  });

  return httpServer;
}
