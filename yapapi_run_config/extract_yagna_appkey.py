import os
import subprocess
from sys import platform
import json

def init_payments_debug():
    if platform == "win32":
        command = "yagna payment init --sender --network mumbai"
        print("Running: " + command)
        os.system(command)



def gather_info():
    if platform == "win32":
        proc = subprocess.Popen(["where.exe", "yagna.exe"], stdout=subprocess.PIPE, shell=True)
        (out, err) = proc.communicate()
        yagna_output_path = out
        yagna_path = yagna_output_path.decode('utf-8').strip()

        if yagna_path.find(" ") != -1:
            print("Found space in the path. This can cause problems.")
            return


        print("Your yagna path: " + yagna_path)

        proc = subprocess.Popen(["yagna.exe", "--version"], stdout=subprocess.PIPE, shell=True)
        (out, err) = proc.communicate()
        yagna_version = out.decode('utf-8').strip()
        print("Your yagna version: " + yagna_version)

        proc = subprocess.Popen(["yagna.exe", "app-key", "list", "--json"], stdout=subprocess.PIPE, shell=True)
        (out, err) = proc.communicate()
        yagna_response = out.decode('utf-8').strip()
        #print(yagna_response)

        obj = json.loads(yagna_response)

        #print(obj["headers"])
        #print(obj["values"])

        key_idx = obj["headers"].index("key")

        if len(obj["values"]) == 0:
            print("NO KEYS FOUND")
            return

        if len(obj["values"]) > 1:
            print("MULTIPLE KEYS FOUND, RETURNING FIRST")

        yagna_appkey = obj["values"][0][key_idx]
        print("Your yagna appkey: " + yagna_appkey)



if __name__ == "__main__":
    gather_info()
    init_payments_debug()





