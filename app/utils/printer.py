from typing import List, Dict, Optional

try:
    import cups

    CUPS_AVAILABLE = True
except ImportError:
    CUPS_AVAILABLE = False
    print("Warning: pycups not installed. Printer functionality will not be available.")
    print("Install with: sudo apt install libcups2-dev && pip install pycups")


class PrinterManager:
    def __init__(self):
        self.conn = None

    def connect(self):
        if not CUPS_AVAILABLE:
            return False
        try:
            self.conn = cups.Connection()
            return True
        except Exception as e:
            print(f"Failed to connect to CUPS: {e}")
            return False

    def get_printers(self) -> List[Dict]:
        if not CUPS_AVAILABLE or not self.connect():
            return []

        printers_dict = self.conn.getPrinters()
        printers = []

        for name, printer in printers_dict.items():
            printers.append(
                {
                    "name": name,
                    "info": printer.get("printer-info", ""),
                    "location": printer.get("printer-location", ""),
                    "state": self._get_state_text(printer.get("printer-state", 3)),
                }
            )

        return printers

    def _get_state_text(self, state: int) -> str:
        state_map = {3: "idle", 4: "printing", 5: "stopped"}
        return state_map.get(state, "unknown")

    def is_printer_available(self, printer_name: str) -> bool:
        if not CUPS_AVAILABLE or not self.connect():
            return False

        try:
            printers = self.get_printers()
            return any(p["name"] == printer_name for p in printers)
        except:
            return False

    def print_document(
        self, printer_name: str, file_path: str, title: str = "Document"
    ) -> bool:
        if not CUPS_AVAILABLE or not self.connect():
            return False

        try:
            self.conn.printFile(printer_name, file_path, title, {})
            return True
        except Exception as e:
            print(f"Print failed: {e}")
            return False

    def get_default_printer(self) -> Optional[str]:
        if not CUPS_AVAILABLE or not self.connect():
            return None

        try:
            return self.conn.getDefault()
        except:
            return None

        try:
            return self.conn.getDefault()
        except:
            return None


printer_manager = PrinterManager()
