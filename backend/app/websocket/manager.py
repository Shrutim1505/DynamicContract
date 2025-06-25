"""
WebSocket connection manager for real-time collaboration
"""
import json
import asyncio
from typing import Dict, Set, List, Any, Optional
from fastapi import WebSocket, WebSocketDisconnect
import logging

logger = logging.getLogger(__name__)

class ConnectionManager:
    """Manages WebSocket connections for real-time collaboration"""
    
    def __init__(self):
        # Contract ID -> Set of WebSocket connections
        self.contract_connections: Dict[int, Set[WebSocket]] = {}
        # WebSocket -> Contract ID mapping
        self.connection_contracts: Dict[WebSocket, int] = {}
        # WebSocket -> User ID mapping
        self.connection_users: Dict[WebSocket, int] = {}
        
    async def connect(self, websocket: WebSocket, contract_id: int, user_id: Optional[int] = None):
        """Accept a new WebSocket connection"""
        await websocket.accept()
        
        # Add to contract connections
        if contract_id not in self.contract_connections:
            self.contract_connections[contract_id] = set()
        self.contract_connections[contract_id].add(websocket)
        
        # Store mappings
        self.connection_contracts[websocket] = contract_id
        if user_id:
            self.connection_users[websocket] = user_id
        
        logger.info(f"WebSocket connected to contract {contract_id} for user {user_id}")
        
        # Notify other users in the contract
        await self.broadcast_to_contract(
            contract_id,
            {
                "type": "user_joined",
                "user_id": user_id,
                "contract_id": contract_id,
                "timestamp": asyncio.get_event_loop().time()
            },
            exclude=websocket
        )
        
    def disconnect(self, websocket: WebSocket, contract_id: int):
        """Disconnect a WebSocket connection"""
        user_id = self.connection_users.get(websocket)
        
        # Remove from contract connections
        if contract_id in self.contract_connections:
            self.contract_connections[contract_id].discard(websocket)
            if not self.contract_connections[contract_id]:
                del self.contract_connections[contract_id]
        
        # Remove mappings
        self.connection_contracts.pop(websocket, None)
        self.connection_users.pop(websocket, None)
        
        logger.info(f"WebSocket disconnected from contract {contract_id} for user {user_id}")
        
        # Notify other users in the contract
        if contract_id in self.contract_connections:
            asyncio.create_task(self.broadcast_to_contract(
                contract_id,
                {
                    "type": "user_left",
                    "user_id": user_id,
                    "contract_id": contract_id,
                    "timestamp": asyncio.get_event_loop().time()
                },
                exclude=websocket
            ))
    
    async def disconnect_all(self):
        """Disconnect all WebSocket connections"""
        for contract_id, connections in self.contract_connections.items():
            for websocket in connections.copy():
                try:
                    await websocket.close()
                except Exception as e:
                    logger.error(f"Error closing WebSocket: {e}")
        
        self.contract_connections.clear()
        self.connection_contracts.clear()
        self.connection_users.clear()
        
    async def send_personal_message(self, message: Dict[str, Any], websocket: WebSocket):
        """Send a message to a specific WebSocket connection"""
        try:
            await websocket.send_text(json.dumps(message))
        except WebSocketDisconnect:
            # Handle disconnection
            contract_id = self.connection_contracts.get(websocket)
            if contract_id:
                self.disconnect(websocket, contract_id)
        except Exception as e:
            logger.error(f"Error sending personal message: {e}")
    
    async def broadcast_to_contract(self, contract_id: int, message: Dict[str, Any], exclude: WebSocket = None):
        """Broadcast a message to all connections in a contract"""
        if contract_id not in self.contract_connections:
            return
        
        message_text = json.dumps(message)
        disconnected_connections = []
        
        for websocket in self.contract_connections[contract_id].copy():
            if websocket != exclude:
                try:
                    await websocket.send_text(message_text)
                except WebSocketDisconnect:
                    disconnected_connections.append(websocket)
                except Exception as e:
                    logger.error(f"Error broadcasting to contract {contract_id}: {e}")
                    disconnected_connections.append(websocket)
        
        # Clean up disconnected connections
        for websocket in disconnected_connections:
            self.disconnect(websocket, contract_id)
    
    async def broadcast_to_user(self, user_id: int, message: Dict[str, Any]):
        """Broadcast a message to all connections for a specific user"""
        user_connections = [
            ws for ws, uid in self.connection_users.items() if uid == user_id
        ]
        
        message_text = json.dumps(message)
        disconnected_connections = []
        
        for websocket in user_connections:
            try:
                await websocket.send_text(message_text)
            except WebSocketDisconnect:
                contract_id = self.connection_contracts.get(websocket)
                if contract_id:
                    disconnected_connections.append((websocket, contract_id))
            except Exception as e:
                logger.error(f"Error broadcasting to user {user_id}: {e}")
                contract_id = self.connection_contracts.get(websocket)
                if contract_id:
                    disconnected_connections.append((websocket, contract_id))
        
        # Clean up disconnected connections
        for websocket, contract_id in disconnected_connections:
            self.disconnect(websocket, contract_id)
    
    async def handle_message(self, websocket: WebSocket, message: Dict[str, Any]):
        """Handle incoming WebSocket message"""
        message_type = message.get("type")
        contract_id = self.connection_contracts.get(websocket)
        user_id = self.connection_users.get(websocket)
        
        if not contract_id:
            await self.send_personal_message(
                {"type": "error", "message": "Not connected to any contract"},
                websocket
            )
            return
        
        # Handle different message types
        if message_type == "cursor_update":
            await self._handle_cursor_update(websocket, contract_id, user_id, message)
        elif message_type == "text_change":
            await self._handle_text_change(websocket, contract_id, user_id, message)
        elif message_type == "selection_change":
            await self._handle_selection_change(websocket, contract_id, user_id, message)
        elif message_type == "typing_start":
            await self._handle_typing_start(websocket, contract_id, user_id, message)
        elif message_type == "typing_stop":
            await self._handle_typing_stop(websocket, contract_id, user_id, message)
        elif message_type == "comment_added":
            await self._handle_comment_added(websocket, contract_id, user_id, message)
        elif message_type == "suggestion_applied":
            await self._handle_suggestion_applied(websocket, contract_id, user_id, message)
        else:
            logger.warning(f"Unknown message type: {message_type}")
    
    async def _handle_cursor_update(self, websocket: WebSocket, contract_id: int, user_id: int, message: Dict[str, Any]):
        """Handle cursor position update"""
        await self.broadcast_to_contract(
            contract_id,
            {
                "type": "cursor_update",
                "user_id": user_id,
                "contract_id": contract_id,
                "position": message.get("position"),
                "timestamp": asyncio.get_event_loop().time()
            },
            exclude=websocket
        )
    
    async def _handle_text_change(self, websocket: WebSocket, contract_id: int, user_id: int, message: Dict[str, Any]):
        """Handle text content change"""
        await self.broadcast_to_contract(
            contract_id,
            {
                "type": "text_change",
                "user_id": user_id,
                "contract_id": contract_id,
                "changes": message.get("changes"),
                "version": message.get("version"),
                "timestamp": asyncio.get_event_loop().time()
            },
            exclude=websocket
        )
    
    async def _handle_selection_change(self, websocket: WebSocket, contract_id: int, user_id: int, message: Dict[str, Any]):
        """Handle text selection change"""
        await self.broadcast_to_contract(
            contract_id,
            {
                "type": "selection_change",
                "user_id": user_id,
                "contract_id": contract_id,
                "selection": message.get("selection"),
                "timestamp": asyncio.get_event_loop().time()
            },
            exclude=websocket
        )
    
    async def _handle_typing_start(self, websocket: WebSocket, contract_id: int, user_id: int, message: Dict[str, Any]):
        """Handle typing start indicator"""
        await self.broadcast_to_contract(
            contract_id,
            {
                "type": "typing_start",
                "user_id": user_id,
                "contract_id": contract_id,
                "position": message.get("position"),
                "timestamp": asyncio.get_event_loop().time()
            },
            exclude=websocket
        )
    
    async def _handle_typing_stop(self, websocket: WebSocket, contract_id: int, user_id: int, message: Dict[str, Any]):
        """Handle typing stop indicator"""
        await self.broadcast_to_contract(
            contract_id,
            {
                "type": "typing_stop",
                "user_id": user_id,
                "contract_id": contract_id,
                "timestamp": asyncio.get_event_loop().time()
            },
            exclude=websocket
        )
    
    async def _handle_comment_added(self, websocket: WebSocket, contract_id: int, user_id: int, message: Dict[str, Any]):
        """Handle new comment notification"""
        await self.broadcast_to_contract(
            contract_id,
            {
                "type": "comment_added",
                "user_id": user_id,
                "contract_id": contract_id,
                "comment_id": message.get("comment_id"),
                "position": message.get("position"),
                "timestamp": asyncio.get_event_loop().time()
            },
            exclude=websocket
        )
    
    async def _handle_suggestion_applied(self, websocket: WebSocket, contract_id: int, user_id: int, message: Dict[str, Any]):
        """Handle AI suggestion application"""
        await self.broadcast_to_contract(
            contract_id,
            {
                "type": "suggestion_applied",
                "user_id": user_id,
                "contract_id": contract_id,
                "suggestion_id": message.get("suggestion_id"),
                "changes": message.get("changes"),
                "timestamp": asyncio.get_event_loop().time()
            },
            exclude=websocket
        )
    
    def get_contract_users(self, contract_id: int) -> List[int]:
        """Get list of user IDs currently connected to a contract"""
        if contract_id not in self.contract_connections:
            return []
        
        users = []
        for websocket in self.contract_connections[contract_id]:
            user_id = self.connection_users.get(websocket)
            if user_id and user_id not in users:
                users.append(user_id)
        
        return users
    
    def get_connection_count(self, contract_id: int) -> int:
        """Get number of active connections for a contract"""
        return len(self.contract_connections.get(contract_id, set()))
    
    def get_total_connections(self) -> int:
        """Get total number of active WebSocket connections"""
        return len(self.connection_contracts)