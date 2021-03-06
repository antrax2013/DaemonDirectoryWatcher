from daemon_thread import *

###########
### RUN
###########
log_file = "C:\\Users\\cyril\\OneDrive\\Documents\\Solaris\\nextcloud\\Cyril\ddw.log"
logging.basicConfig(filename=log_file, level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

# creating a thread
processus = DaemonThread(
    "C:\\Users\\cyril\\OneDrive\\Documents\\Solaris\\nextcloud\\Solaris",
    "C:\\Users\\cyril\\OneDrive\\Documents\\Solaris\\nextcloud\\Cyril",
    15,
    "./contentTable_template.md",
    "C:\\Users\\cyril\\OneDrive\\Documents\\Solaris\\nextcloud\\Solaris\Sommaire.md"
) 
 
# starting of Thread T
processus.start()