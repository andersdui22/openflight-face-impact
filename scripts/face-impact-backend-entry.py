"""PyInstaller entry point for the development-only Windows mock backend.

Do not infer physical camera validation from the health endpoint.
"""
from openflight.server import main

if __name__ == "__main__":
    main()
