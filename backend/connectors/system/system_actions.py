"""
System Actions Module
Permet à l'agent d'interagir avec le système Windows de manière sécurisée.
"""

import os
import subprocess
import platform
from pathlib import Path
from typing import Dict, List, Optional, Any

# Safe mode configuration
ALLOW_UNSAFE = False  # Set to True to allow potentially dangerous operations
CRITICAL_PATHS = [
    "C:/Windows/System32",
    "C:/Windows/SysWOW64",
    "C:/Program Files",
    "C:/Program Files (x86)"
]


# Vérifier si psutil est disponible
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False


class SystemActionsError(Exception):
    """Exception de base pour les erreurs d'actions système."""
    pass


class PermissionDeniedError(SystemActionsError):
    """Exception levée quand allow=True n'est pas fourni."""
    pass


class SystemActions:
    """
    Classe pour effectuer des actions système sur Windows.
    Toutes les actions nécessitent allow=True pour des raisons de sécurité.
    """

    def __init__(self):
        """Initialise SystemActions et vérifie la plateforme."""
        self.platform = platform.system()
        self.is_windows = self.platform == "Windows"

    def _is_safe_path(self, path: str) -> bool:
        """
        Check if a path is safe to access.
        
        Args:
            path: Path to check
            
        Returns:
            bool: True if path is safe, False otherwise
        """
        if ALLOW_UNSAFE:
            return True
        
        path_str = str(Path(path).resolve())
        
        for critical_path in CRITICAL_PATHS:
            if path_str.startswith(critical_path):
                return False
        
        return True

    def _check_permission(self, allow: bool) -> None:
        """
        Vérifie que l'autorisation explicite est donnée.

        Args:
            allow: Doit être True pour autoriser l'action

        Raises:
            PermissionDeniedError: Si allow n'est pas True
        """
        if not allow:
            raise PermissionDeniedError(
                "Action refused: allow=True required for security"
            )

    def open_path(self, path: str) -> Dict[str, Any]:
        """
        Open a file or folder with the default application.
        Automatically detects if path is a file or folder.
        
        Args:
            path: Path to open
            
        Returns:
            Dict with status and message
            
        Raises:
            SystemActionsError: If operation fails
        """
        path_obj = Path(path)
        
        if not path_obj.exists():
            raise SystemActionsError(f"Path not found: {path}")
        
        # Check if path is safe
        if not self._is_safe_path(path):
            raise PermissionDeniedError(f"Access denied to critical system path: {path}")
        
        try:
            if self.is_windows:
                os.startfile(str(path_obj))
            else:
                if platform.system() == "Darwin":  # macOS
                    subprocess.Popen(["open", str(path_obj)])
                else:  # Linux
                    subprocess.Popen(["xdg-open", str(path_obj)])
            
            path_type = "folder" if path_obj.is_dir() else "file"
            return {
                "success": True,
                "message": f"{path_type.capitalize()} opened: {path}",
                "path": str(path_obj),
                "type": path_type
            }
        except Exception as e:
            raise SystemActionsError(f"Failed to open path: {str(e)}")

    def open_file(self, path: str, allow: bool = False) -> Dict[str, Any]:
        """
        Ouvre un fichier avec l'application par défaut.

        Args:
            path: Chemin du fichier à ouvrir
            allow: Doit être True pour autoriser l'action

        Returns:
            Dict avec status et message

        Raises:
            PermissionDeniedError: Si allow n'est pas True
            SystemActionsError: Si l'opération échoue
        """
        self._check_permission(allow)

        path_obj = Path(path)

        if not path_obj.exists():
            raise SystemActionsError(f"File not found: {path}")

        if not path_obj.is_file():
            raise SystemActionsError(f"Path is not a file: {path}")

        try:
            if self.is_windows:
                os.startfile(str(path_obj))
            else:
                # Fallback pour autres plateformes
                if platform.system() == "Darwin":  # macOS
                    subprocess.Popen(["open", str(path_obj)])
                else:  # Linux
                    subprocess.Popen(["xdg-open", str(path_obj)])

            return {
                "success": True,
                "message": f"File opened: {path}",
                "path": str(path_obj)
            }
        except Exception as e:
            raise SystemActionsError(f"Failed to open file: {str(e)}")

    def open_folder(self, path: str, allow: bool = False) -> Dict[str, Any]:
        """
        Ouvre un dossier dans l'explorateur.

        Args:
            path: Chemin du dossier à ouvrir
            allow: Doit être True pour autoriser l'action

        Returns:
            Dict avec status et message

        Raises:
            PermissionDeniedError: Si allow n'est pas True
            SystemActionsError: Si l'opération échoue
        """
        self._check_permission(allow)

        path_obj = Path(path)

        if not path_obj.exists():
            raise SystemActionsError(f"Folder not found: {path}")

        if not path_obj.is_dir():
            raise SystemActionsError(f"Path is not a folder: {path}")

        try:
            if self.is_windows:
                os.startfile(str(path_obj))
            else:
                # Fallback pour autres plateformes
                if platform.system() == "Darwin":  # macOS
                    subprocess.Popen(["open", str(path_obj)])
                else:  # Linux
                    subprocess.Popen(["xdg-open", str(path_obj)])

            return {
                "success": True,
                "message": f"Folder opened: {path}",
                "path": str(path_obj)
            }
        except Exception as e:
            raise SystemActionsError(f"Failed to open folder: {str(e)}")

    def run_program(self, path: str, args: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Lance un programme.

        Args:
            path: Chemin du programme à lancer
            args: Arguments optionnels pour le programme
            allow: Doit être True pour autoriser l'action

        Returns:
            Dict avec status, message et PID

        Raises:
            PermissionDeniedError: Si allow n'est pas True
            SystemActionsError: Si l'opération échoue
        """
        path_obj = Path(path)
        
        # Check if path is safe
        if not self._is_safe_path(path):
            raise PermissionDeniedError(f"Access denied to critical system path: {path}")

        if not path_obj.exists():
            raise SystemActionsError(f"Program not found: {path}")

        try:
            cmd = [str(path_obj)]
            if args:
                cmd.extend(args)

            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                creationflags=subprocess.CREATE_NEW_CONSOLE if self.is_windows else 0
            )

            return {
                "success": True,
                "message": f"Program started: {path}",
                "path": str(path_obj),
                "pid": process.pid
            }
        except Exception as e:
            raise SystemActionsError(f"Failed to run program: {str(e)}")

    def list_processes(self) -> Dict[str, Any]:
        """
        Liste tous les processus en cours.

        Args:
            allow: Doit être True pour autoriser l'action

        Returns:
            Dict avec la liste des processus

        Raises:
            PermissionDeniedError: Si allow n'est pas True
            SystemActionsError: Si psutil n'est pas disponible
        """
        if not PSUTIL_AVAILABLE:
            raise SystemActionsError(
                "psutil module not available. Install with: pip install psutil"
            )

        try:
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'username', 'memory_info']):
                try:
                    info = proc.info
                    processes.append({
                        "pid": info['pid'],
                        "name": info['name'],
                        "username": info.get('username', 'N/A'),
                        "memory_mb": round(info['memory_info'].rss / 1024 / 1024, 2)
                                     if info.get('memory_info') else 0
                    })
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue

            return {
                "success": True,
                "message": f"Found {len(processes)} processes",
                "count": len(processes),
                "processes": processes
            }
        except Exception as e:
            raise SystemActionsError(f"Failed to list processes: {str(e)}")

    def kill_process(self, name: str) -> Dict[str, Any]:
        """
        Termine un processus par son nom.

        Args:
            name: Nom du processus à terminer
            allow: Doit être True pour autoriser l'action

        Returns:
            Dict avec status et nombre de processus terminés

        Raises:
            PermissionDeniedError: Si allow n'est pas True
            SystemActionsError: Si psutil n'est pas disponible
        """
        if not PSUTIL_AVAILABLE:
            raise SystemActionsError(
                "psutil module not available. Install with: pip install psutil"
            )

        try:
            killed_count = 0
            killed_pids = []

            for proc in psutil.process_iter(['pid', 'name']):
                try:
                    if proc.info['name'].lower() == name.lower():
                        pid = proc.info['pid']
                        proc.kill()
                        killed_count += 1
                        killed_pids.append(pid)
                except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
                    continue

            if killed_count == 0:
                return {
                    "success": False,
                    "message": f"No process found with name: {name}",
                    "killed_count": 0
                }

            return {
                "success": True,
                "message": f"Killed {killed_count} process(es) named: {name}",
                "killed_count": killed_count,
                "killed_pids": killed_pids
            }
        except Exception as e:
            raise SystemActionsError(f"Failed to kill process: {str(e)}")

    def exists(self, path: str, allow: bool = False) -> Dict[str, Any]:
        """
        Vérifie si un chemin (fichier ou dossier) existe.

        Args:
            path: Chemin à vérifier
            allow: Doit être True pour autoriser l'action

        Returns:
            Dict avec status et informations sur le chemin

        Raises:
            PermissionDeniedError: Si allow n'est pas True
        """
        self._check_permission(allow)

        path_obj = Path(path)
        exists = path_obj.exists()

        result = {
            "success": True,
            "exists": exists,
            "path": str(path_obj)
        }

        if exists:
            result["is_file"] = path_obj.is_file()
            result["is_dir"] = path_obj.is_dir()

            try:
                stat = path_obj.stat()
                result["size_bytes"] = stat.st_size
                result["modified_timestamp"] = stat.st_mtime
            except Exception:
                pass

        return result
