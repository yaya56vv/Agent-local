"""
Script de test pour le module System Actions
"""

from backend.connectors.system.system_actions import (
    SystemActions,
    SystemActionsError,
    PermissionDeniedError
)


def test_permission_denied():
    """Test que les actions sont refusées sans allow=True"""
    print("\n=== Test Permission Denied ===")
    system = SystemActions()

    try:
        system.exists("C:\\", allow=False)
        print("FAILED: Should have raised PermissionDeniedError")
    except PermissionDeniedError as e:
        print(f"PASS: {e}")


def test_exists():
    """Test la vérification d'existence"""
    print("\n=== Test Exists ===")
    system = SystemActions()

    # Test avec un chemin qui existe (C:\\ sur Windows)
    result = system.exists("C:\\", allow=True)
    print(f"Path exists: {result}")

    # Test avec un chemin qui n'existe pas
    result = system.exists("C:\\nonexistent_path_12345", allow=True)
    print(f"Path not exists: {result}")


def test_system_info():
    """Affiche les informations système"""
    print("\n=== System Information ===")
    system = SystemActions()
    print(f"Platform: {system.platform}")
    print(f"Is Windows: {system.is_windows}")

    # Check psutil
    try:
        import psutil
        print("psutil: Available")
        print(f"CPU count: {psutil.cpu_count()}")
        print(f"Memory: {round(psutil.virtual_memory().total / (1024**3), 2)} GB")
    except ImportError:
        print("psutil: Not available (pip install psutil)")


def test_list_processes():
    """Test de listage des processus"""
    print("\n=== Test List Processes ===")
    system = SystemActions()

    try:
        result = system.list_processes()
        print(f"Found {result['count']} processes")
        # Afficher les 5 premiers
        for proc in result['processes'][:5]:
            print(f"  - {proc['name']} (PID: {proc['pid']}, Memory: {proc['memory_mb']} MB)")
    except SystemActionsError as e:
        print(f"ERROR: {e}")


if __name__ == "__main__":
    print("=" * 50)
    print("System Actions Module - Test Suite")
    print("=" * 50)

    test_permission_denied()
    test_exists()
    test_system_info()
    test_list_processes()

    print("\n" + "=" * 50)
    print("Tests completed!")
    print("=" * 50)
