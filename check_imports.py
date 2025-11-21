import os
import sys
import importlib.util

def check_imports(start_dir):
    print(f"Checking imports in {start_dir}...")
    error_count = 0
    for root, dirs, files in os.walk(start_dir):
        for file in files:
            if file.endswith(".py") and not file.startswith("test_"):
                file_path = os.path.join(root, file)
                module_name = os.path.splitext(file)[0]
                
                # Skip __init__.py for now as they might be empty or complex to load in isolation
                if file == "__init__.py":
                    continue

                try:
                    spec = importlib.util.spec_from_file_location(module_name, file_path)
                    if spec and spec.loader:
                        module = importlib.util.module_from_spec(spec)
                        sys.modules[module_name] = module
                        spec.loader.exec_module(module)
                        # print(f"✅ {file_path}")
                except ImportError as e:
                    print(f"❌ ImportError in {file_path}: {e}")
                    error_count += 1
                except Exception as e:
                    # Some files might fail to run (e.g. if they have code at module level)
                    # We are mostly interested in ImportErrors
                    # print(f"⚠️  Error executing {file_path}: {e}")
                    pass
    
    if error_count == 0:
        print("\nNo ImportErrors found!")
    else:
        print(f"\nFound {error_count} ImportErrors.")

if __name__ == "__main__":
    # Add project root to sys.path
    sys.path.append(os.getcwd())
    check_imports("backend")
