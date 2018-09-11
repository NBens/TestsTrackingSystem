import os
import sys
import json
import urllib.request, urllib.error
from datetime import datetime


def pull(url, json_path, platforms_list):
    
    with open(json_path, "r") as file:
        data_dictionary = json.load(file)
    for platform in platforms_list:

        last_modified_json = data_dictionary[platform].get("last-modified")
        last_test_json = data_dictionary[platform].get("last-xml")

        try:
            path = url + platform
            file = urllib.request.urlopen(path + "/files.dat")
            last_modified = file.getheader("Last-Modified")
        except urllib.error.HTTPError as e:
            print("Couldn't fetch {}".format(path))
            print(e)
        
        last_modified_date = datetime.strptime(last_modified, "%a, %d %b %Y %H:%M:%S %Z")
        if str(last_modified_date) == last_modified_json:
            break

        lines = reversed(file.readlines())
        tests_to_download = list()
        last_test = ""
        
        for line in lines:
            line = line.decode("utf-8")
            if str(line[-13:-1]) == "/test.xml.gz" and str(line[:-4]) != last_test_json:
                tests_to_download.append(str(line[:-4]))
                last_test = str(line[:-4])
            elif str(line[:-4]) == last_test_json:
                break
        print("Tests to be downloaded for {}: {}".format(platform, len(tests_to_download)))
        
        for test_file in tests_to_download:

            try:
                file_name = "test-" + str(round(datetime.timestamp(datetime.now()))) + ".xml"
                urllib.request.urlretrieve(path + "/" + test_file, file_name)
                os.popen("python ./push.py -f " + file_name)
                os.remove(file_name)
            except OSError as e:
                print("Couldn't run process")
                print(e)
            except urllib.error.HTTPError as e:
                print("Couldn't retreive xml file")
                print(e)
                
        
        data = {
            platform: {
                "last-modified": str(last_modified_date),
                "last-xml": last_test
            }
        }
        
        data_dictionary.update(data)
    with open(json_path, "w") as file:
        json.dump(data_dictionary, file)


def json_keys(json_file_path):
    with open(json_file_path, "r") as json_file:
        json_data = json.load(json_file)
        json_keys = [*json_data]
        return json_keys

if __name__ == "__main__":

    gson_url = "http://www.gson.org/netbsd/bugs/build/"
    gson_builds = json_keys("gson.json")

    b5_url = "http://releng.netbsd.org/b5reports/"
    b5_builds = json_keys("babylon5.json")

    
    pull(gson_url, "gson.json", gson_builds)
    pull(b5_url, "babylon5.json", b5_builds)


