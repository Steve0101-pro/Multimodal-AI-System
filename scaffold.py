from pathlib import Path


# ============================================================
# PROJECT ROOT
# ============================================================

ROOT = Path(__file__).resolve().parent


# ============================================================
# DIRECTORIES
# ============================================================

DIRECTORIES = [
    # Data
    "app/",
    "app/api",
    "app/services",
    
]


# ============================================================
# FILES
# ============================================================

FILES = [
    # --------------------------------------------------------
    # Root
    # --------------------------------------------------------
    "app/__init__.py",
    "app/main.py",
    "app/config.py",
    "app/database.py",
    "app/schema.py",
    "app/models.py",
    "app/api/__init__.py",
    "app/api/documents.py",
    "app/services/__init__.py",
    "app/services/storage.py",
    "app/services/ocr_services.py",
    "params.yaml",
    "requirements.txt",
    ".gitignore",
    "README.md",

    
  

    ".github/workflows/ci.yml",

   
]


# ============================================================
# CREATE SCAFFOLD
# ============================================================

def create_scaffold():

  

    # --------------------------------------------------------
    # Create directories
    # --------------------------------------------------------

    for directory in DIRECTORIES:

        path = ROOT / directory

        path.mkdir(
            parents=True,
            exist_ok=True
        )

        print(f"[DIR ] {path}")

    # --------------------------------------------------------
    # Create files
    # --------------------------------------------------------

    for file in FILES:

        path = ROOT / file

        # Create parent directory if necessary
        path.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        # Safety check:
        # If a directory already exists where a file should be,
        # report it instead of silently doing the wrong thing.
        if path.exists() and path.is_dir():

            print(
                f"[WARN] Expected FILE but found DIRECTORY: {path}"
            )

            continue

        if not path.exists():

            path.touch()

            print(f"[FILE] {path}")

        else:

            print(f"[SKIP] {path}")

    


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    create_scaffold()