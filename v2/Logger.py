import logging
import coloredlogs
import os
from datetime import datetime

logs = logging.getLogger(__name__)
coloredlogs.install(level=logging.DEBUG, logger=logs)
logs.setLevel(logging.DEBUG)

os.makedirs("logs", exist_ok=True)
log_name = datetime.now().strftime("%Y%m%d-%H%M%S")
file = logging.FileHandler("logs/" + log_name + ".log", "w", 'utf-8')
fileformat = logging.Formatter("%(asctime)s:%(levelname)s:%(message)s")
file.setLevel(logging.DEBUG)
file.setFormatter(fileformat)

stream = logging.StreamHandler()
streamformat = logging.Formatter("%(levelname)s:%(module)s:%(message)s")
stream.setLevel(logging.DEBUG)
stream.setFormatter(streamformat)

logs.addHandler(file)
# logs.addHandler(stream)