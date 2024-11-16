import logging
import os

formatter = logging.Formatter(
    "[%(levelname)s] %(asctime)s - %(name)s - %(message)s", datefmt="%H:%M:%S"
)

_level = logging.DEBUG if os.environ.get("DEBUG") else logging.INFO

# Create console handler.
console = logging.StreamHandler()
console.setLevel(_level)
console.setFormatter(formatter)

# Create logging handler. Capitalized for implying its static nature.
Log = logging.getLogger("main")
Log.setLevel(_level)
Log.addHandler(console)
