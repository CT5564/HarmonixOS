import subprocess
import sys

from watchfiles import watch

from services.log import get_log

log = get_log(__name__)


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

        log.info("Python file changed.")
        log.info("Restarting Harmonix...")

        process.terminate()
        process.wait()

        process = run_bot()

except KeyboardInterrupt:

    log.info("Stopping Harmonix...")

    process.terminate()
    process.wait()