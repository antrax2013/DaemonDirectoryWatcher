from xmlrpc.client import DateTime
from ddw_functions import *
from threading import *
import subprocess

#pip install win10toast
from win10toast import ToastNotifier


# class defining Daemon Thread
class DaemonThread(Thread):
    _frequency=1
    _watched_path=""
    _save_path=""
    _save_file_name="ddw-informations.json"
    _save_full_file_name=""
    _template_content_table_path=""
    _content_table_path=""

    # Daemon Thread constructor
    def __init__(self, watched_path, save_path, frequency=1, template_content_table_path="-1", content_table_path="-1"):
        Thread.__init__(self)

        if not os.path.exists(watched_path):
            raise FileNotFoundError("Could not find path: %s"%(watched_path))

        self._watched_path = watched_path
        
        if not os.path.exists(save_path):
            raise FileNotFoundError("Could not find path: %s"%(save_path))

        self._save_path = save_path
        self._save_full_file_name=os.path.join(save_path,self._save_file_name)
        self._frequency = frequency

        if template_content_table_path!="-1" and not os.path.exists(template_content_table_path):
            raise FileNotFoundError("Could not find path: %s"%(template_content_table_path))

        self._template_content_table_path = template_content_table_path

        self._content_table_path = content_table_path
    ## end of __init__

    # Daemon Thread run method
    def run(self):
        timer = self._frequency*60
        toaster = ToastNotifier()
        toaster.show_toast("DDW", f"Started - frequency : {timer}")

        #eclude content table file of watching
        excluded_files =[self._content_table_path.replace("\\","/").replace("//","/").split("/")[-1]]
        excluded_directories=[".git"]

        # for i in range(1,2):
        while(True):
            DaemonThread.core_process(self._watched_path, self._save_path, self._save_file_name, excluded_directories, excluded_files, self._template_content_table_path, self._save_full_file_name, self._content_table_path, toaster)
            time.sleep(timer)
    ## end of run

    @staticmethod
    def core_process(watched_path, save_path, save_file_name, excluded_directories, excluded_files, template_content_table_path, save_full_file_name, content_table_path, toaster=None, force=False) :
        results =  DaemonDirectoryWatcher(
            watched_path,
            save_path,
            save_file_name,
            excluded_directories,
            excluded_files              
        )

        tmp = results["nb_changes"]
        if(tmp>0 or force) :                
            if not toaster is None :
                toaster.show_toast("DDW",f"NextCloud - Solaris Nb Changes: {tmp}")
            
            #if option genereate content table is set on and have any changes
            if template_content_table_path != "-1":
                DaemonThread.generate_content_table(template_content_table_path, save_full_file_name, content_table_path)
                DaemonThread.git_update_remote_repository(watched_path)


    ## Methode to generate content table
    @staticmethod
    def generate_content_table(template_content_table_path, save_full_file_name, content_table_path) :
        template = read_file(template_content_table_path)

        datas = json.loads(read_file(save_full_file_name))
        res = generate_content_table(datas)

        write_file(content_table_path,template.replace("#Content#",res).replace("#Date#", datetime.now().strftime('%d/%m/%Y %H:%M')))
    ## end of generate_content_table

    ## Git commit : use local git account
    @staticmethod
    def git_update_remote_repository(watched_path):
        ## change working directory
        os.chdir(watched_path)
        ## stage changes, commit and push
        subprocess.call(["git", "add", "-A", "."], shell=True)
        subprocess.call(["git", "commit", "-aqm", f"ddw - Auto commit {datetime.now().strftime('%d/%m/%Y %H:%M')} \" "], shell=True) 
        subprocess.call(["git", "push", "-q", "--set-upstream", "origin", "main"], shell=True) 
    ## end of Git commit
## end of class DaemonThread