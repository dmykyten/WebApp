import json
from geopy.geocoders import Nominatim
geolocator = Nominatim(user_agent="test.py")
def read_file(path):
    with open(path, mode="r", encoding='utf-8') as file:
        data=file.read().split(')')
    for i in range(len(data)):
        data[i]=data[i].split('\n')
    for i in range(len(data[:-1])):
        if len(data[i])>1:
            data[i].pop(-1)
    return data

def create_dict(data,i):
    dct={}
    dct['протопресвітерат']=data[0][0]
    dct['деканат']=data[0][1]
    lst=data[i]
    for j in range(0,len(lst),2):
        dct[lst[j]]={}
    return dct

def create_list(data):
    res=[]
    for i in range(1,19):
        res.append(create_dict(data,i))
    return res

def append_information(previous, data):
    previous=previous[1:]
    for j in range(len(data)):
        data[j].get('населений пункт')['назва']=previous[j][1]
        location=geolocator.geocode(previous[j][1])
        print(location)
        data[j].get('населений пункт')['lat']=location.latitude
        data[j].get('населений пункт')['lng']=location.longitude
    return data
        
def write_file(dictionary,path):
    """
    Write a json file
    """
    with open(path, mode="w", encoding='utf-8') as f:
        json.dump(dictionary,f,ensure_ascii=False,indent=2)

data=append_information(read_file('test.txt'),create_list(read_file('test.txt')))
write_file(data,'Naraivskyi.json')