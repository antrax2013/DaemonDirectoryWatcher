from ddw_functions import *
from daemon_thread import *

###########
### RUN
###########
root = "C:\\Users\\cyril\\OneDrive\\Documents\\Solaris\\solaris-maurepas.frama.space"
log_file = root + "\\workspace\\ddw.log"
logging.basicConfig(filename=log_file, level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

excluded_directories=[".git"]
watched_folder = root + "\\Tous les documents de l'alvéole"
save_path = root +"\\workspace"
save_file_name="ddw-informations.json"
excluded_files=[]
template_content_table_path="./contentTable_template.md"
save_full_file_name=os.path.join(save_path,save_file_name)
content_table_path=root +"\\Tous les documents de l'alvéole\Sommaire.md"


DaemonThread.core_process(
  watched_folder, 
  save_path, 
  save_file_name, 
  excluded_directories, 
  excluded_files, 
  template_content_table_path, 
  save_full_file_name, 
  content_table_path,
  force=True
)
