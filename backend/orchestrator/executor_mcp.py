"""
Executor MCP - Exécute les plans avec les clients MCP appropriés
"""
from typing import Dict, Any, List, Optional
from backend.orchestrator.clients.files_client import FilesClient
from backend.orchestrator.clients.memory_client import MemoryClient
from backend.orchestrator.clients.rag_client import RagClient
from backend.orchestrator.clients.vision_client import VisionClient
from backend.orchestrator.clients.search_client import SearchClient
from backend.orchestrator.clients.system_client import SystemClient
from backend.orchestrator.clients.control_client import ControlClient


class ExecutorMCP:
    """Exécute les étapes d'un plan avec les bons clients MCP"""
    
    def __init__(
        self,
        files_client: FilesClient,
        memory_client: MemoryClient,
        rag_client: RagClient,
        vision_client: VisionClient,
        search_client: SearchClient,
        system_client: SystemClient,
        control_client: ControlClient
    ):
        self.files = files_client
        self.memory = memory_client
        self.rag = rag_client
        self.vision = vision_client
        self.search = search_client
        self.system = system_client
        self.control = control_client
        
        # Map actions to handlers
        self.action_map = {
            "search_web": self._exec_search_web,
            "file_read": self._exec_file_read,
            "file_write": self._exec_file_write,
            "file_list": self._exec_file_list,
            "file_delete": self._exec_file_delete,
            "system_open": self._exec_system_open,
            "system_run": self._exec_system_run,
            "system_list_processes": self._exec_system_list_processes,
            "system_kill": self._exec_system_kill,
            "vision_analyze": self._exec_vision_analyze,
            "rag_query": self._exec_rag_query,
            "rag_add": self._exec_rag_add,
            "memory_recall": self._exec_memory_recall,
            "memory_search": self._exec_memory_search,
            "mouse_move": self._exec_mouse_move,
            "mouse_click": self._exec_mouse_click,
            "mouse_scroll": self._exec_mouse_scroll,
            "keyboard_type": self._exec_keyboard_type,
            "keyboard_press": self._exec_keyboard_press
        }
    
    async def execute_steps(
        self,
        steps: List[Dict[str, Any]],
        session_id: str = "default"
    ) -> List[Dict[str, Any]]:
        """
        Exécute une liste d'étapes séquentiellement
        
        Args:
            steps: Liste des étapes à exécuter
            session_id: ID de session
            
        Returns:
            Liste des résultats d'exécution
        """
        results = []
        previous_result = None
        
        for i, step in enumerate(steps):
            action = step.get("action", "")
            params = {k: v for k, v in step.items() if k != "action"}
            
            # Injecter résultat précédent si nécessaire
            if "input" in params and params["input"] == "$previous" and previous_result:
                params["data"] = previous_result
            
            # Exécuter l'action
            if action in self.action_map:
                try:
                    result = await self.action_map[action](**params)
                    results.append({
                        "step": i + 1,
                        "action": action,
                        "status": "success",
                        "data": result
                    })
                    previous_result = result
                except Exception as e:
                    results.append({
                        "step": i + 1,
                        "action": action,
                        "status": "error",
                        "error": str(e)
                    })
            else:
                results.append({
                    "step": i + 1,
                    "action": action,
                    "status": "error",
                    "error": f"Unknown action: {action}"
                })
        
        return results
    
    # ============================================================
    # ACTION HANDLERS
    # ============================================================
    
    async def _exec_search_web(self, query: str, max_results: int = 5, **kwargs) -> Dict[str, Any]:
        """Recherche web"""
        return await self.search.search_all(query)
    
    async def _exec_file_read(self, path: str, **kwargs) -> Dict[str, Any]:
        """Lecture fichier"""
        return await self.files.read_file(path)
    
    async def _exec_file_write(self, path: str, content: str, **kwargs) -> Dict[str, Any]:
        """Écriture fichier"""
        return await self.files.write_file(path, content)
    
    async def _exec_file_list(self, path: str = ".", **kwargs) -> Dict[str, Any]:
        """Liste répertoire"""
        return await self.files.list_dir(path)
    
    async def _exec_file_delete(self, path: str, **kwargs) -> Dict[str, Any]:
        """Suppression fichier"""
        return await self.files.delete_file(path)
    
    async def _exec_system_open(self, path: str, **kwargs) -> Dict[str, Any]:
        """Ouvrir fichier/dossier"""
        import os
        if os.path.isfile(path):
            return await self.system.open_file(path)
        else:
            return await self.system.open_folder(path)
    
    async def _exec_system_run(self, path: str, args: List[str] = None, **kwargs) -> Dict[str, Any]:
        """Exécuter programme"""
        return await self.system.run_program(path, args)
    
    async def _exec_system_list_processes(self, **kwargs) -> Dict[str, Any]:
        """Lister processus"""
        return await self.system.list_processes()
    
    async def _exec_system_kill(self, name: str, **kwargs) -> Dict[str, Any]:
        """Tuer processus"""
        try:
            pid = int(name)
            return await self.system.kill_process(pid)
        except ValueError:
            return {"status": "error", "message": "Provide PID, not name"}
    
    async def _exec_vision_analyze(self, image_bytes: bytes, prompt: str = "", **kwargs) -> Dict[str, Any]:
        """Analyse vision"""
        if prompt:
            return await self.vision.analyze_image(image_bytes)
        else:
            return await self.vision.analyze_screenshot(image_bytes)
    
    async def _exec_rag_query(self, dataset: str, question: str, top_k: int = 5, **kwargs) -> Dict[str, Any]:
        """Requête RAG"""
        results = await self.rag.query(dataset, question, top_k)
        return {"status": "success", "results": results}
    
    async def _exec_rag_add(self, dataset: str, filename: str, content: str, metadata: Dict[str, Any] = None, **kwargs) -> Dict[str, Any]:
        """Ajout document RAG"""
        doc_id = await self.rag.add_document(dataset, filename, content, metadata)
        return {"status": "success", "document_id": doc_id}
    
    async def _exec_memory_recall(self, session_id: str = "default", max_messages: int = 10, **kwargs) -> Dict[str, Any]:
        """Rappel mémoire"""
        context = await self.memory.get_context(session_id, max_messages)
        return {"status": "success", "context": context}
    
    async def _exec_memory_search(self, query: str, session_id: str = None, **kwargs) -> Dict[str, Any]:
        """Recherche mémoire"""
        results = await self.memory.search(query, session_id)
        return {"status": "success", "results": results}
    
    async def _exec_mouse_move(self, x: int, y: int, duration: float = 0.5, **kwargs) -> Dict[str, Any]:
        """Déplacer souris"""
        return await self.control.move_mouse(x, y, duration)
    
    async def _exec_mouse_click(self, x: Optional[int] = None, y: Optional[int] = None, button: str = "left", clicks: int = 1, **kwargs) -> Dict[str, Any]:
        """Clic souris"""
        button_map = {"left": 1, "right": 2, "middle": 3}
        button_num = button_map.get(button, 1)
        return await self.control.click_mouse(button=button_num, x=x, y=y, clicks=clicks)
    
    async def _exec_mouse_scroll(self, clicks: int, **kwargs) -> Dict[str, Any]:
        """Scroll souris"""
        return await self.control.scroll(scroll_y=clicks)
    
    async def _exec_keyboard_type(self, text: str, interval: float = 0.05, **kwargs) -> Dict[str, Any]:
        """Taper texte"""
        return await self.control.type(text, interval)
    
    async def _exec_keyboard_press(self, keys: List[str], **kwargs) -> Dict[str, Any]:
        """Presser touches"""
        return await self.control.keypress(keys)