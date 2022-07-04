"""Script which builds the /dist folder containing the static UI files."""
import subprocess
from pathlib import Path


def build_and_add():
    """
    Build the static files

    """
    client_path = Path(__file__).parent

    # rimraf dist folder
    subprocess.call(["rimraf", "/dist"], cwd=client_path)
    # run npm build
    subprocess.call(["npm", "run", "build"], cwd=client_path)


if __name__ == "__main__":
    build_and_add()
