"""
System MCP Client
Handles communication with the System MCP server for system operations.
"""
import httpx


class SystemClient:
    def __init__(self, base_url: str):
        self.base_url = base_url

    async def list_processes(self) -> dict:
        """
        Liste les processus système.
        
        Returns:
            dict: List of running processes from System MCP server
        """
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(f"{self.base_url}/system/list_processes")
                response.raise_for_status()
                return response.json()
        except Exception as e:
            return {"status": "error", "error": str(e)}

    async def kill_process(self, pid: int) -> dict:
        """
        Termine un processus par son PID.
        
        Args:
            pid: Process ID to terminate
            
        Returns:
            dict: Result of process termination from System MCP server
        """
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.base_url}/system/kill",
                    json={"pid": pid}
                )
                response.raise_for_status()
                return response.json()
        except Exception as e:
            return {"status": "error", "error": str(e)}

    async def open_file(self, file_path: str) -> dict:
        """
        Ouvre un fichier avec l'application par défaut.
        
        Args:
            file_path: Path to the file to open
            
        Returns:
            dict: Result of file opening operation from System MCP server
        """
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.base_url}/system/open/file",
                    json={"path": file_path}
                )
                response.raise_for_status()
                return response.json()
        except Exception as e:
            return {"status": "error", "error": str(e)}

    async def open_folder(self, folder_path: str) -> dict:
        """
        Ouvre un dossier dans l'explorateur de fichiers.
        
        Args:
            folder_path: Path to the folder to open
            
        Returns:
            dict: Result of folder opening operation from System MCP server
        """
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.base_url}/system/open/folder",
                    json={"path": folder_path}
                )
                response.raise_for_status()
                return response.json()
        except Exception as e:
            return {"status": "error", "error": str(e)}

    async def run_program(self, program_path: str, args: list = None) -> dict:
        """
        Exécute un programme avec des arguments optionnels.
        
        Args:
            program_path: Path to the program to execute
            args: Optional list of command-line arguments
            
        Returns:
            dict: Result of program execution from System MCP server
        """
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.base_url}/system/run",
                    json={"path": program_path, "args": args or []}
                )
                response.raise_for_status()
                return response.json()
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    async def snapshot(self) -> dict:
        """
        Récupère un snapshot de l'état système actuel
        
        Returns:
            dict: System state snapshot
        """
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(f"{self.base_url}/system/snapshot")
                response.raise_for_status()
                return response.json()
        except Exception as e:
            # Fallback: retourne un snapshot basique si le serveur ne répond pas
            return {
                "status": "partial",
                "error": str(e),
                "basic_info": {
                    "timestamp": "unknown",
                    "processes_count": 0
                }
            }

