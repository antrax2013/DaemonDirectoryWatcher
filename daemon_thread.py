from xmlrpc.client import DateTime
from ddw_functions import *
from threading import *

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
            results =  DaemonDirectoryWatcher(
                self._watched_path,
                self._save_path,
                self._save_file_name,
                excluded_directories=excluded_directories,
                excluded_files=excluded_files              
            )

            tmp = results["nb_changes"]
            if(tmp>0) :                
                toaster.show_toast("DDW",f"NextCloud - Solaris Nb Changes: {tmp}")
                
                #if option genereate content table is set on and have any changes
                if self._template_content_table_path != "-1":
                    self.generate_content_table()


            time.sleep(timer)
    ## end of run

    ## Methode to generate content table
    def generate_content_table(self) :
        template = read_file(self._template_content_table_path)

        datas = json.loads(read_file(self._save_full_file_name))
        res = generate_content_table(datas)

        write_file(self._content_table_path,template.replace("#Content#",res).replace("#Date#", datetime.now().strftime('%d/%m/%Y %H:%M')))
    ## end of generate_content_table

    ## Git commit
    os.system(f"git commit -am \"ddw - Auto commit {datetime.now().strftime('%d/%m/%Y %H:%M')} \" ")
    os.system(f"git push --set-upstream Origine main")
    ## end of Git commit
## end of class DaemonThread