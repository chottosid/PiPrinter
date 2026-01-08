from fastapi import APIRouter, Depends, HTTPException
from ..utils.printer import printer_manager

router = APIRouter(prefix="/printers", tags=["printers"])


@router.get("/")
async def get_printers():
    printers = printer_manager.get_printers()
    return printers


@router.get("/status")
async def get_printer_status():
    if printer_manager.connect():
        return {
            "status": "connected",
            "printers_available": len(printer_manager.get_printers()),
        }
    else:
        return {"status": "disconnected", "printers_available": 0}
