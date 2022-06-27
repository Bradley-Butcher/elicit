"""Main script, includes CLI, and ability to run the UI."""
import subprocess
from pathlib import Path
import click
import os
import signal


def launch_ui(db_path: Path):
    """
    Launch the User Interface.

    :param db_name: Name of database to use.

    """
    ui_path = Path(__file__).parent.parent / "user_interface"
    # run two commands in parallel to launch the UI
    try:
        client = subprocess.Popen(
            ["python", ui_path / "client" / "client.py"],
            stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
        server = subprocess.Popen(["python", ui_path / "server" /
                                   "app.py", "--db_path", db_path],
                                  stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
    except:
        print("Failed to launch UI")
        return
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
@click.option("--db_path", default="test_db.sqlite", help="Name of the database.")
def gui(db_path: str):
    """
    Launch the User Interface.

    :param db_path: path of database to use.

    """
    launch_ui(db_path)


@main.command(name="kill_ui")
def kill_ui_cmd():
    """
    Kill the User Interface. Kills proocess on ports 8080 and 5000.

    """
    _kill_ui()


if __name__ == "__main__":
    main()
