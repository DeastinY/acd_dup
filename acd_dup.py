# Amazon Cloud Drive Directory Uploader
import os
import subprocess
try:
    from os import scandir
except ImportError:
    from scandir import scandir

def scantree(path):
    for entry in scandir(path):
        if entry.is_dir(follow_symlinks=False):
            yield from scantree(entry.path)
        else:
            yield entry

if __name__ == "__main__":
    base_directory = "/run/user/1000/gvfs/smb-share:server=192.168.1.12,share=titanic/Richard/Photography"
    acd_base_directory = "/pictures"
    valid_extensions = [".jpg", ".nef"]
    upload_filters = ["personal", "private"]
    acd_paths = set()

    for entry in scantree(base_directory):
        name, extension = os.path.splitext(entry.name)
        if extension.lower() in valid_extensions:
            path = os.path.dirname(entry.path)
            path = path.replace(base_directory, '')
            path = acd_base_directory + path
            if any(f in entry.path.lower() for f in upload_filters):
                print("Skipping "+entry.path)
                continue
            try:
                if not path in acd_paths:
                    parts = path.split("/")
                    combined_p = ""
                    for p in parts[1:]:  # path starts with / so first element will be ''
                        combined_p = combined_p + "/" + p
                        if not combined_p in acd_paths:
                            cmd = "acdcli mkdir \"{}\"".format(combined_p)
                            print(cmd)
                            subprocess.run(cmd, shell=True)
                            acd_paths.add(combined_p)
                cmd = "acdcli upload -d {} \"{}\"".format(entry.path, path)  # -d : deduplicate, excludes duplicates from upload
                print(cmd)
                subprocess.run(cmd, shell=True)
            except Exception as e:
                print(e)
                exit()
