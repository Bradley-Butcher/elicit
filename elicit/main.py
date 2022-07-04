"""Main script, includes CLI, and ability to run the UI."""
import subprocess
from pathlib import Path
import click

from elicit.extractor import Extractor


def launch_ui(*, db_path: Path = None, extractor: Extractor = None, test: bool = False, output: bool = False):
    """
    Launch the User Interface.

    :param db_name: Name of database to use.

    """
    # Setup logging
    log_folder = Path(__file__).parent.parent / ".logs"
    log_folder.mkdir(exist_ok=True)
    (log_folder / "client.log").unlink()
    (log_folder / "server.log").unlink()

    ui_path = Path(__file__).parent.parent / "user_interface"
    # run two commands in parallel to launch the UI
    if extractor is not None:
        db_path = extractor.logger.db_path
    if not test:
        with open(log_folder / "client.log", "w") as f:
            client = subprocess.Popen(
                ["python", ui_path / "client" / "client.py"],
                stdout=f,
                stderr=f,
            )
    else:
        client = subprocess.Popen(
            ["npm", "run", "serve"], cwd=ui_path / "client")
    with open(log_folder / "server.log", "w") as f:
        server = subprocess.Popen(["python", ui_path / "server" /
                                   "app.py", "--db_path", db_path],
                                  stdout=f,
                                  stderr=f)
    try:
        get_ipython
        from IPython.core.display import display, HTML
        display(HTML(
            """Launched UI at: <a href="http://localhost:8080">http://localhost:8080</a>"""))
    except:
        print("Launched UI at: http://localhost:8080")
    try:
        client.wait()
        server.wait()
        print("Failed to launch UI - Processes probably already running on ports 8080 and 5000. Kill them using elicit.main._kill_ui, or just on the CMD.")
    except:
        client.terminate()
        server.terminate()
        print("UI Killed")


def _kill_ui():
    """
    Kill the User Interface. Kills proocess on ports 8080 and 5000. Used for testing.

    """
    subprocess.call(["npx", "kill-port", "8080"])
    subprocess.call(["npx", "kill-port", "5000"])
    print("Killed UI")


@click.group()
def main():
    """Main CLI."""
    pass


@main.command(name="GUI")
@click.option("--db_path", default="database/test_db.sqlite", help="Name of the database.")
@click.option("--test", is_flag=True, help="Run UI in test mode.", default=False)
def gui(db_path: str, test: bool):
    """
    Launch the User Interface.

    :param db_path: path of database to use.

    """
    launch_ui(db_path=db_path, test=test)


@main.command(name="kill_ui")
def kill_ui_cmd():
    """
    Kill the User Interface. Kills proocess on ports 8080 and 5000.

    """
    _kill_ui()


if __name__ == "__main__":
    main()
