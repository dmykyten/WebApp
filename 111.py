import os
import pytesseract.pytesseract as py_t
import logging
import logging.config
import re

logging.config.fileConfig('logging.conf')
logger = logging.getLogger('ocr_logger')


def get_pictures(local_path):
    full_path = f'{os.getcwd()}\\{local_path}\\'
    filelist = list(os.walk(local_path)).pop()[2]
    logger.info('Read files from directory')
    return [{'path': full_path,
             'filename': file} for file in filelist]


def create_dir(path):
    if os.path.exists(path):

        if os.path.isdir(path):
            logger.info(f'Directory on path already exists.')
            return True
    else:
        logger.info(f'Directory {path} not found. Creating new directory.')
        os.mkdir(path)
        return True
    logger.info('Selected path already exists and is not directory.')
    return False


def recognise_text(result_path, data):
    logger.info('Processing images...')
    with open(result_path, 'w', encoding='utf-8') as file:
        for image in data:
            path = image['path'] + image['filename']
            logger.info(f'Current image: {path}')
            temp = py_t.image_to_string(image=path, lang="ukr")
            file.write(temp)


def get_location(location_name):
    from geopy.geocoders import Nominatim
    geolocator = Nominatim(user_agent="ocr_webapp")
    location = geolocator.geocode(location_name)
    try:
        return {'lat': location.latitude,
                'lng': location.longitude}
    except AttributeError:
        return None


def parse_data(filepath):
    def read_from_file(filepath):
        with open(filepath, 'r', encoding='utf-8') as file:
            temp = ''
            return [line.strip('\n') for line in file.readlines()]

    def retrieve_fields(data):
        decanat_name = data[0].split(' ')[1]
        protopres_name = data[1].split(' ')[0].strip('(')
        decanat_data = []
        towns = {}
        churches = {}
        for i, line in enumerate(data):
            temp = re.findall('ц\. (.*?),', line)
            temp += re.findall('(капличка\. .*?)\.', line)
            if temp:
                churches[i] = temp
            temp = re.findall('^[0-9]+\) (.*?),', line)
            if temp:
                towns[i] = temp
        print()
        print(churches)
        print()
        print(towns)
        print()
        for i in towns:
            decanat_data.append({
                "протопресвітерат": protopres_name,
                "деканат": decanat_name,
                "населений пункт": {
                    "назва": towns[i],
                    #"location": get_location(towns[i])
                },
            })
            town_churches = []
            for church in churches[i]:
                current_church = {
                    'назва': church
                }
                temp = data[i].split(church)[1].split(' ')
                for j, word in enumerate(temp):
                    if word.strip(',') in ['мур.', 'дер.', 'М. дер.', 'відмур. на стар. фунд.']:
                        current_church['тип'] = word.strip(',')
                        year = re.findall(word + ' ([0-9]+)', data[i])
                        if year:
                            current_church['рік'] = year[0]
                town_churches.append(current_church)
            print(town_churches)


    data = read_from_file(filepath)
    print(data)
    retrieve_fields(data)


def main():
    data = get_pictures('data')
    result_path = 'деканати\\Галицький.txt'
    create_dir(result_path.split('\\')[0])
    #recognise_text(result_path, data)
    parse_data(result_path)
    

if __name__ == '__main__':
    main()