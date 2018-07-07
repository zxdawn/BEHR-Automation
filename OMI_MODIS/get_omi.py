from __future__ import print_function

# This script will also contact GES DISC Web server at
# https://aura.gesdisc.eosdis.nasa.gov
# get OMNO2 and OMPIXCOR files from specific months and retrieve them,
# putting them in the proper directory.
#
# The  directory of OMI should be defined in the env. variable OMNO2DIR and OMPIXCORDIR
#
# Xin Zhang <xinzhang1215@gmail.com> 5 Jul 2018

import os
import time
import argparse
import urllib2
import requests
import numpy as np
import datetime as dt
from bs4 import BeautifulSoup

user = 'USERNAME'
password = 'PASSWORD'
base_url = 'https://aura.gesdisc.eosdis.nasa.gov/data/Aura_OMI_Level2'


def loop_year(products, startTime, endTime):
    htmls = []
    syear = startTime.timetuple()[0]
    eyear = endTime.timetuple()[0]
    sday = startTime.timetuple()[7]
    eday = endTime.timetuple()[7]

    for y in np.arange(syear, eyear+1, 1):
        for m in np.arange(sday, eday+1, 1):
            htmls.append(base_url+'/'+products+'/'+str(y)+'/'+str(m).zfill(3)+'/')

    return htmls


def get_url(products, startTime, endTime):
    names = []
    urls = []

    htmls = loop_year(products, startTime, endTime)

    for html in htmls:
        tmp_names = []
        html_page = urllib2.urlopen(html)
        soup = BeautifulSoup(html_page, "html.parser")
        # Filter links and save to list
        for link in soup.findAll('a'):
            link = link.get('href')
            if link.endswith('he5'):
                tmp_names.append(link)
        tmp_names = list(set(tmp_names))
        names.extend(tmp_names)
        urls += ([html]*len(tmp_names))

    return names, urls


def get_omi(products, startTime, endTime, output_file=None):
    print("Retrieving file URLs")
    attempt=0
    while True:
        try:
            filenames, fileURLs = get_url(products, startTime, endTime)
            print("fileURLs has length", len(fileURLs))
        except Exception as err:
            if attempt > 5:
                print("More than five attempts failed to retrieve file URLs. Aborting.")
                raise
            else:
                print("Retrieving file URLs failed, waiting 30 sec")
                print("Message was:", str(err))
                time.sleep(30)
        else:
            break
        finally:
            attempt += 1

    return filenames, fileURLs


def list_product_urls(product, path, start_date, end_date):
    filenames, file_urls = get_omi(products=product, startTime=start_date, endTime=end_date)
    if file_urls:
        return filenames, file_urls
    else:
        raise RuntimeError('No file URLs obtained')


def download_product(product, path, start_date, end_date, verbose=0):
    names, urls = list_product_urls(product, path, start_date, end_date)

    for counter, name in enumerate (names):
        year_str = name.split("_")[2][:4]
        year_directory = os.path.join(path, year_str)
        if not os.path.isdir(year_directory):
            os.mkdir(year_directory)

        month_str = name.split("_")[2][5:7]
        month_directory = os.path.join(year_directory, month_str)
        if not os.path.isdir(month_directory):
            os.mkdir(month_directory)

        file_fullname = os.path.join(month_directory, name)

        if os.path.isfile(file_fullname) and os.path.getsize(file_fullname) > 0:
            if verbose > 1:
                print('File {} already exists and size is > 0; not re-downloaded'.format(file_fullname))
            continue

        with open(file_fullname, 'wb') as save_obj:
            if verbose > 0:
                print('Downloading {} to {}'.format(name, month_directory))
            resp = requests.get(urls[counter]+name, auth=(user, password))
            save_obj.write(resp.content)


def driver(start_date, end_date, verbose=0):
    omno2_dir = os.getenv('OMNO2DIR')
    ompixcor_dir = os.getenv('OMPIXCORDIR')

    products = [('OMNO2.003', omno2_dir), ('OMPIXCOR.003',ompixcor_dir)]
    for product, path in products:
        if verbose > 0:
            print('Now downloading the {} product'.format(product))
        download_product(product, path, start_date, end_date, verbose=verbose)


def parse_cl_date(datestr):
        return dt.datetime.strptime(datestr, '%Y-%m-%d')


def parse_args():
    parser = argparse.ArgumentParser(description='Driver to download OMNO2 and OMPIX data')
    parser.add_argument('-s', '--start-date', type=parse_cl_date, help='startdate yyyy-mm-dd')
    parser.add_argument('-e', '--end-date', type=parse_cl_date, help='enddate yyyy-mm-dd')
    parser.add_argument('-v', '--verbose', action='count', help='Increase verbosity to the terminal')

    return vars(parser.parse_args())


def main():
    args_dict = parse_args()
    driver(**args_dict)


if __name__ == '__main__':
    main()
