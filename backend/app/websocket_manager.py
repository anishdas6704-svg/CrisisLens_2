import logging
from typing import Dict, List
from fastapi import WebSocket

logger = logging.getLogger(__name__)

class ConnectionManager:
    def __init__(self):
        # Map crisis_id -> list of active WebSockets
        self.active_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, crisis_id: str, websocket: WebSocket):
        await websocket.accept()
        if crisis_id not in self.active_connections:
            self.active_connections[crisis_id] = []
        self.active_connections[crisis_id].append(websocket)
        logger.info(f"WebSocket client connected to crisis room: {crisis_id}")

    def disconnect(self, crisis_id: str, websocket: WebSocket):
        if crisis_id in self.active_connections:
            if websocket in self.active_connections[crisis_id]:
                self.active_connections[crisis_id].remove(websocket)
            if not self.active_connections[crisis_id]:
                del self.active_connections[crisis_id]
        logger.info(f"WebSocket client disconnected from crisis room: {crisis_id}")

    async def broadcast_to_crisis(self, crisis_id: str, message: dict):
        if crisis_id in self.active_connections:
            for connection in list(self.active_connections[crisis_id]):
                try:
                    await connection.send_json(message)
                except Exception as e:
                    logger.warning(f"Error sending message over WebSocket: {e}")
                    self.disconnect(crisis_id, connection)

    async def broadcast_all(self, message: dict):
        for crisis_id in list(self.active_connections.keys()):
            await self.broadcast_to_crisis(crisis_id, message)

ws_manager = ConnectionManager()
