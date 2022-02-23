import os
import pytesseract.pytesseract as py_t
import logging
import logging.config
import re
import json

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
        logger.info('Location found!')
        return {'lat': location.latitude,
                'lng': location.longitude}
    except AttributeError:
        logger.info('Not found!')
        return None


def parse_data(filepath):
    def read_from_file(filepath):
        with open(filepath, 'r', encoding='utf-8') as file:
            temp = ''
            return [line.strip('\n') for line in file.readlines()]

    def serialize(data):
        with open('result.json', 'w', encoding='utf-8') as result:
            json.dump(data, result, ensure_ascii=False)

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

        for i in towns:
            decanat_data.append({
                "протопресвітерат": protopres_name,
                "деканат": decanat_name,
                "населений пункт": {
                    "назва": towns[i],
                },
            })
            loc = get_location(towns[i])
            if loc:
                decanat_data[-1]["населений пункт"]["location"] = loc
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
                    elif word.strip(',') in ['віз.', 'зруйн.', 'відб.', 'відбуд.']:
                        year = re.findall(word + ' ([0-9]+)', data[i])
                        if year:
                            current_church[word.strip(',')] = year[0]
                    elif 'Дн.' in word:
                        current_church['Дн.'] = 'Дн.'
                town_churches.append(current_church)
            decanat_data[-1]['церкви'] = town_churches
        return decanat_data

    data = read_from_file(filepath)
    data = retrieve_fields(data)
    serialize(data)


def main():
    data = get_pictures('data')
    result_path = 'деканати\\Галицький.txt'
    create_dir(result_path.split('\\')[0])
    # recognise_text(result_path, data)
    parse_data(result_path)


if __name__ == '__main__':
    main()
