from daemon_thread import *

###########
### RUN
###########
root = "C:\\Users\\cyril\\OneDrive\\Documents\\Solaris\\solaris-maurepas.frama.space"
log_file = root + "\\ddw.log"
logging.basicConfig(filename=log_file, level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

# creating a thread
processus = DaemonThread(
    root + "\\Tous les documents de l'alvéole",
    root +"\\workspace",
    15,
    "./contentTable_template.md",
    root +"\\Tous les documents de l'alvéole\Sommaire.md"
) 
 
# starting of Thread T
processus.start()