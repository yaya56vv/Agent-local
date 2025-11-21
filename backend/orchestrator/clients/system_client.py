"""
System MCP Client
Handles communication with the System MCP server for system operations.
"""


class SystemClient:
    def __init__(self, base_url: str):
        self.base_url = base_url

    async def list_processes(self) -> dict:
        """
        TODO: Liste les processus système.
        Enverra une requête HTTP asynchrone au service MCP System pour obtenir
        la liste des processus en cours d'exécution.
        
        Returns:
            dict: List of running processes from System MCP server
        """
        pass

    async def kill_process(self, pid: int) -> dict:
        """
        TODO: Termine un processus par son PID.
        Enverra une requête HTTP asynchrone au service MCP System pour terminer
        un processus spécifique.
        
        Args:
            pid: Process ID to terminate
            
        Returns:
            dict: Result of process termination from System MCP server
        """
        pass

    async def open_file(self, file_path: str) -> dict:
        """
        TODO: Ouvre un fichier avec l'application par défaut.
        Enverra une requête HTTP asynchrone au service MCP System pour ouvrir
        un fichier avec l'application système par défaut.
        
        Args:
            file_path: Path to the file to open
            
        Returns:
            dict: Result of file opening operation from System MCP server
        """
        pass

    async def open_folder(self, folder_path: str) -> dict:
        """
        TODO: Ouvre un dossier dans l'explorateur de fichiers.
        Enverra une requête HTTP asynchrone au service MCP System pour ouvrir
        un dossier dans l'explorateur de fichiers système.
        
        Args:
            folder_path: Path to the folder to open
            
        Returns:
            dict: Result of folder opening operation from System MCP server
        """
        pass

    async def run_program(self, program_path: str, args: list = None) -> dict:
        """
        TODO: Exécute un programme avec des arguments optionnels.
        Enverra une requête HTTP asynchrone au service MCP System pour exécuter
        un programme avec des arguments optionnels.
        
        Args:
            program_path: Path to the program to execute
            args: Optional list of command-line arguments
            
        Returns:
            dict: Result of program execution from System MCP server
        """
        pass
