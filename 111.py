import os
import pytesseract.pytesseract as py_t
import logging
import logging.config

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
    return {'lat': location.latitude,
            'lon': location.longitude}


def parse_data(filepath):
    def read_from_file(filepath):
        with open(filepath, 'r', encoding='utf-8') as file:
            temp = ''
            data = []
            for line in file.readlines():
                if line != '\n':
                    temp += line.strip('\n') + ' '
                    continue
                data.append(temp)
                temp = ''
        return data

    def delete_redundant():
        start = list(filter(lambda x: x if 'Озірнянський деканат.' in data[x] else None, range(len(data))))[0]
        end = list(filter(lambda x: x if 'Олеський деканат.' in data[x] else None, range(len(data))))[0]
        return data[19:150]
    data = read_from_file(filepath)
    data = delete_redundant()
    print(data)
        



def main():
    data = get_pictures('data')
    result_path = 'result\\result.txt'
    create_dir(result_path.split('\\')[0])
    recognise_text(result_path, data)
    parse_data(result_path)
    

if __name__ == '__main__':
    main()