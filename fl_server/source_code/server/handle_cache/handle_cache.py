import os,json,shutil,pathlib,glob

class CacheFile():
  def __init__(self):
    current_path = str(pathlib.Path(__file__).parent.resolve())
    self.local_path = f'{current_path}\\cache\\cache.json'

  def check_file_exist(self,file_name = ""):
    try:
      path_file_name = self.local_path + file_name
      if os.path.exists(path_file_name):
        return True
      else:
        return False
    
    except Exception as inst:
      print("ERROR ====> check_file_exist" , inst)
      return False

  def delete_cache_file(self,path_exact ):

    try:

      if os.path.exists(path_exact):
        os.remove(path_exact)
      else:
        print("The file does not exist!!!!")

    except Exception as inst:
      print("ERROR ====> delete_cache_file" , inst)
      return False

  def create_file_cache(self,file_name , data):
    try:
      print("CacheFile ==> create file cache")
      path_file_name = self.local_path + file_name
      f = open(path_file_name, "w" ,  encoding="utf8")
      f.write(json.dumps(data))
      f.close()

    except Exception as inst:
      print("ERROR ====> create_file_cache" , inst)
      return False
  
  def get_data_file_cache(self):
    try:

      # print("CacheFile ==> get data from file")
      path_file_name = self.local_path

      f = open(path_file_name, "r" ,  encoding="utf8")

      data = json.loads(f.read())
      return data

    except Exception as inst:
      print("ERROR ====> get_data_file_cache" , inst)
      return False

  def delete_all_file_folder(self,folder_name ):
    try:
      print("CacheFile ==> delete_all_file_folder")
      path_file_name = self.local_path + folder_name
      print(path_file_name)
      files = []

      for r, d, f in os.walk(path_file_name):
        for file in f:
          if '.json' in file:
            _path_file = os.path.join(r, file)
            files.append(_path_file)
            print(_path_file)
            self.delete_cache_file(_path_file)

      return files
    except Exception as inst:
      print(inst)

  def created_folder(self,folder_name):
    try:
      path_file_name = self.local_path + folder_name

      if os.path.isdir(path_file_name) :
        pass
        # print(f"Folder exist: {folder_name}!!!")
      else:
        print(f"CacheFile ==> Created folder: {folder_name};")
        os.makedirs(path_file_name)
    except OSError as inst:
      print(inst)
      print ("Creation of the directory %s failed" % folder_name)

  def remove_empty_folder(self, folder_path):
    try:
      os.rmdir(folder_path)
    except:
      print ("Folder not empty")
  
  def remove_folder_and_files_in_it(self, folder_path):
    try:
      shutil.rmtree(folder_path)
      return True
    except:
      print ("Remove Failed")
      return False