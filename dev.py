import subprocess
import sys

from watchfiles import watch


def run_bot():
    return subprocess.Popen(
        [sys.executable, "main.py"]
    )


process = run_bot()

try:

    for changes in watch(
        ".",
        watch_filter=lambda change, path:
            path.endswith(".py")
    ):

        print("\n🔄 Python file changed.")
        print("♻️ Restarting Harmonix...\n")

        process.terminate()
        process.wait()

        process = run_bot()

except KeyboardInterrupt:

    print("\n🛑 Stopping Harmonix...")

    process.terminate()
    process.wait()