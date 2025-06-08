# bootstrap.py
import subprocess
import shutil
import sys

def check_node_and_mmdc():
    # Check Node.js
    if not shutil.which("node"):
        print("❌ Node.js is not installed. Please install it from https://nodejs.org/")
        sys.exit(1)

    # Check Mermaid CLI
    if not shutil.which("mmdc"):
        print("🛠 Installing mermaid-cli...")
        subprocess.run(["npm", "install", "-g", "mermaid.cli"])

def start_app():
    from syncapp.main import main
    main()

if __name__ == "__main__":
    check_node_and_mmdc()
    start_app()
