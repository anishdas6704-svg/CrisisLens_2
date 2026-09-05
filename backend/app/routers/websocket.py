import logging
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.websocket_manager import ws_manager

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ws", tags=["WebSocket"])

@router.websocket("/{crisis_id}")
async def crisis_websocket_endpoint(websocket: WebSocket, crisis_id: str):
    await ws_manager.connect(crisis_id, websocket)
    try:
        while True:
            # Keep listening for client messages/heartbeats
            data = await websocket.receive_text()
            # Echo or acknowledge if client sends ping
            if data == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        ws_manager.disconnect(crisis_id, websocket)
    except Exception as e:
        logger.warning(f"WebSocket error in crisis room {crisis_id}: {e}")
        ws_manager.disconnect(crisis_id, websocket)
