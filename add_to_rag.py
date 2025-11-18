"""
Script utilitaire pour ajouter des documents au RAG depuis des fichiers
"""

import sys
from pathlib import Path
import argparse

# Ajouter le répertoire parent au path
sys.path.insert(0, str(Path(__file__).parent))

from backend.rag.rag_helper import rag_helper


def add_file_to_rag(file_path: str, dataset: str):
    """
    Ajoute un fichier au RAG.
    
    Args:
        file_path: Chemin vers le fichier
        dataset: Nom du dataset
    """
    path = Path(file_path)
    
    if not path.exists():
        print(f"❌ Fichier non trouvé: {file_path}")
        return False
    
    if not path.is_file():
        print(f"❌ Ce n'est pas un fichier: {file_path}")
        return False
    
    # Lire le contenu
    try:
        content = path.read_text(encoding='utf-8')
    except UnicodeDecodeError:
        print(f"⚠️  Tentative avec encodage latin-1...")
        try:
            content = path.read_text(encoding='latin-1')
        except Exception as e:
            print(f"❌ Impossible de lire le fichier: {e}")
            return False
    
    # Ajouter au RAG
    try:
        doc_id = rag_helper.add_document_sync(
            dataset=dataset,
            filename=path.name,
            content=content,
            metadata={
                "source": "file",
                "path": str(path.absolute()),
                "size": len(content),
                "extension": path.suffix
            }
        )
        print(f"✅ Document ajouté: {path.name}")
        print(f"   Dataset: {dataset}")
        print(f"   ID: {doc_id[:16]}...")
        print(f"   Taille: {len(content)} caractères")
        return True
    except Exception as e:
        print(f"❌ Erreur lors de l'ajout: {e}")
        return False


def add_directory_to_rag(dir_path: str, dataset: str, extensions: list = None):
    """
    Ajoute tous les fichiers d'un répertoire au RAG.
    
    Args:
        dir_path: Chemin vers le répertoire
        dataset: Nom du dataset
        extensions: Liste d'extensions à inclure (ex: ['.txt', '.md'])
    """
    path = Path(dir_path)
    
    if not path.exists():
        print(f"❌ Répertoire non trouvé: {dir_path}")
        return
    
    if not path.is_dir():
        print(f"❌ Ce n'est pas un répertoire: {dir_path}")
        return
    
    # Extensions par défaut
    if extensions is None:
        extensions = ['.txt', '.md', '.py', '.js', '.html', '.css', '.json', '.yaml', '.yml']
    
    # Trouver tous les fichiers
    files = []
    for ext in extensions:
        files.extend(path.rglob(f'*{ext}'))
    
    if not files:
        print(f"⚠️  Aucun fichier trouvé avec les extensions: {extensions}")
        return
    
    print(f"📁 Traitement de {len(files)} fichier(s)...")
    print()
    
    success_count = 0
    fail_count = 0
    
    for file in files:
        if add_file_to_rag(str(file), dataset):
            success_count += 1
        else:
            fail_count += 1
        print()
    
    print("=" * 60)
    print(f"✅ {success_count} fichier(s) ajouté(s)")
    if fail_count > 0:
        print(f"❌ {fail_count} fichier(s) en échec")
    print("=" * 60)


def main():
    parser = argparse.ArgumentParser(
        description="Ajouter des fichiers au système RAG",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples:
  # Ajouter un fichier
  python add_to_rag.py --file README.md --dataset docs

  # Ajouter un répertoire
  python add_to_rag.py --dir ./backend --dataset code

  # Ajouter un répertoire avec extensions spécifiques
  python add_to_rag.py --dir ./docs --dataset documentation --ext .md .txt
        """
    )
    
    parser.add_argument(
        '--file',
        type=str,
        help='Fichier à ajouter'
    )
    
    parser.add_argument(
        '--dir',
        type=str,
        help='Répertoire à ajouter'
    )
    
    parser.add_argument(
        '--dataset',
        type=str,
        required=True,
        help='Nom du dataset (obligatoire)'
    )
    
    parser.add_argument(
        '--ext',
        nargs='+',
        help='Extensions de fichiers à inclure (ex: .txt .md)'
    )
    
    args = parser.parse_args()
    
    print()
    print("=" * 60)
    print("📚 Ajout de documents au RAG")
    print("=" * 60)
    print()
    
    if args.file:
        add_file_to_rag(args.file, args.dataset)
    elif args.dir:
        extensions = args.ext if args.ext else None
        add_directory_to_rag(args.dir, args.dataset, extensions)
    else:
        print("❌ Erreur: Spécifiez --file ou --dir")
        parser.print_help()
        return
    
    print()
    print("💡 Pour voir vos documents:")
    print("   http://localhost:8000/ui/rag.html")
    print()


if __name__ == "__main__":
    main()
