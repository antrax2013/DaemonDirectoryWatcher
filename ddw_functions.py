import os
from os.path import exists
import re
from datetime import datetime
import time
import json
import logging


### Convert float to datetime
def convert_float_date(t):
    tmp = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(t))
    return datetime.strptime(tmp,'%Y-%m-%d %H:%M:%S')

### Nb minutes between 2 date
def mintues_between(d1, d2):
    return abs((d2 - d1)).total_seconds() / 60

## function init structure
def init_stucture() : 
    return {"files":{"path":[]}}

### function to show diff between 2 execution
def diff_content(src, current) :
    src_paths=[]

    # map args
    if(len(src)>1) :
        src_paths = [elmt["path"] for elmt in src["files"]]

    current_paths = [elmt["path"] for elmt in current["files"]]

    # filter values
    added = [elmt for elmt in src_paths + current_paths if elmt not in src_paths]
    deleted = [elmt for elmt in src_paths + current_paths if elmt not in current_paths]
    modified = [elmt["path"] for elmt in current["files"] if elmt["modified"]==True and not elmt["path"] in added]

    return {
        "nb_changes":len(added)+len(deleted)+len(modified),
        "added":added,
        "deleted":deleted,
        "modified":modified
    }
    
### function to write string into filepath
def write_file(filepath, datas):
    fichier = open(filepath, "w", encoding="utf-8")
    fichier.write(datas)
    fichier.close()

### function to read filepath and return datas
def read_file(filepath) :
    datas = ""
    try:
        if(exists(filepath)) :
            fichier = open(filepath, "r", encoding="utf-8")
            datas = fichier.read()
            fichier.close()
    
    except ValueError:
        logging.critical(f"error on readin {filepath}")

    return datas

### Function to crawl directory content
def directory_spider(input_dir, path_pattern="", file_pattern="", max_results=1000, date_ref=datetime.now(), excluded_files=[]):
    
    file_paths = []
    now = datetime.now()
    pivot = mintues_between(date_ref, now)
    
    if not os.path.exists(input_dir):
        raise FileNotFoundError("Could not find path: %s"%(input_dir))
    
    for dirpath, dirnames, filenames in os.walk(input_dir) :
        if re.search(path_pattern, dirpath):
            
            file_list = [item for item in filenames if re.search(file_pattern,item)]
            
            file_path_list=[]

            ### loop in filepath of current folder
            for item in file_list :
                #if file not excluded
                if(item in excluded_files):
                    continue

                current = os.path.join(dirpath, item)
                modif_date = convert_float_date(os.path.getmtime(current))
                diff_time = mintues_between(modif_date, now)
                file_path_list.append({
                    "name": item,
                    "path": current.replace(input_dir,".").replace("\\","/"), 
                    "modif_date": modif_date.strftime('%Y-%m-%d %H:%M:%S'), 
                    "time" : diff_time,
                    "modified": diff_time < pivot
                })
            
            file_paths += file_path_list
            
            if len(file_paths) > max_results:
                break
    
    return file_paths[0:max_results]

### Function to find path from file_path
def get_path(root, file_path, separator="/") :
    current_path = root
    tmp = file_path.split(separator)

    _len = len(tmp)
    if _len >= 1 :
        for i in range(1,_len) :
            current_path += separator+tmp[i]
    
    return current_path

### Function to generate html content table from datas
def generate_content_table(datas, relative_url="../") :
    html=""
    separator ="/"
    if len(datas["files"]) > 0 :

        template_ul=f"## #directoryName# \n #li# \n\n "
        
        template_li=f"- #fileName# \n "
        
        main_path = datas["path"]

        datas = [elmt["path"] for elmt in datas["files"]]

        paths = []

        for path in datas :
            paths.append(get_path(main_path, path))

        directories= list(dict.fromkeys(paths))

        current_directory =""
        li=""        
        for path in directories:
            tmp = path.split(separator)
            root = tmp[0]
            
            filename =""
            if len(tmp) > 2:
             root+=separator+tmp[1]
             for i in range(2,len(tmp)):
                filename+=tmp[i]+separator

            else : filename = tmp[-1]
 
            if current_directory != root : 
                
                if  current_directory != ""  :     
                    html+= template_ul.replace("#pathName#",root).replace("#directoryName#",current_directory).replace("#li#",li)
                    li=""
                current_directory=root 

            li += template_li.replace("#pathName#",path).replace("#fileName#", filename.strip(separator))

        html+= template_ul.replace("#directoryName#",current_directory).replace("#li#",li)

    return html

##
## Function to watched changes into children tree of directory
## watched_folder : the folder watched
## save_path : path where the file populated with informations will be saved for next comparison
## save_file_name
def DaemonDirectoryWatcher(
    watched_folder, 
    save_path="", 
    save_file_name="ddw-informations.json",
    excluded_files=[]) :

    path_from = watched_folder
    save_file = save_file_name
    save_path = (watched_folder if save_path=="" else save_path)
    excluded_files.append(save_file)

    logging.debug("Treatment started")

    date_ref = datetime.now()   

    ## Checks
    if(not exists(watched_folder)) :
        raise Exception(f"Folder {watched_folder} not found")

    if(not exists(save_path)) :
         raise Exception(f"Folder {save_path} not found") 
    
    save_path = os.path.join((watched_folder if save_path=="" else save_path),save_file)

    ## READ
    previous = read_file(save_path)
    infos=init_stucture()

    if(len(previous) > 0) :
        infos = json.loads(previous)
        path = infos["path"]
        d = infos["last_execution"]
        taille = len(infos["files"])
        logging.debug(f"Previous execution  : {path} - Nb files : {taille} at {d}")
        date_ref = datetime.strptime(d,'%Y-%m-%d %H:%M:%S') 

    ## WRITE
    contents = directory_spider(path_from, date_ref=date_ref, excluded_files=excluded_files)

    current = {
        "path": path_from.split("\\")[-1],       
        "last_execution" : datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        "files" : contents
    }

    path = current["path"]
    taille = len(current["files"])
    d = current["last_execution"]
    logging.debug(f"Current execution   : {path} - Nb files : {taille} at {d}")

    write_file(save_path,json.dumps(current, sort_keys=True))

    ## COMPARISON
    comparison = diff_content(infos, current)
    logging.info(comparison)

    logging.debug("Treatment completed")

    return comparison
