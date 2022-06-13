from ddw_functions import *
from threading import *

#pip install win10toast
from win10toast import ToastNotifier


# class defining Daemon Thread
class DaemonThread(Thread):
    _frequency=1
    _watched_path=""
    _save_path=""

    # Daemon Thread constructor
    def __init__(self, watched_path, save_path, frequency=1):
        Thread.__init__(self)
        self._watched_path = watched_path
        self._save_path = save_path
        self._frequency = frequency

    # Daemon Thread run method
    def run(self):
        toaster = ToastNotifier()
        toaster.show_toast("DDW started")

        # for i in range(1,2):
        while(True):
            results =  DaemonDirectoryWatcher(
                self._watched_path,
                self._save_path              
            )

            tmp = results["nb_changes"]
            if(tmp>0) :                
                toaster.show_toast(f"NextCloud - Solaris Nb Changes: {tmp}")

            time.sleep(self._frequency*60)
        
        print("End")
        return
