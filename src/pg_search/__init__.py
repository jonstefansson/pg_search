import logging
import sys

logging.basicConfig(
    level=logging.NOTSET,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stderr
)
