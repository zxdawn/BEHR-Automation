from __future__ import print_function

import automodis as am

import argparse
import datetime as dt
from glob import glob
import os
import re
import shutil
import sys
import pdb

modis_date_re = re.compile('(?<=A)\d{7}')
max_download_attempts = 10
USERAGENT = 'tis/download.py_1.0--' + sys.version.replace('\n','').replace('\r','')


def list_product_urls(product, collection, path, start_date, end_date, verbose=0):
    file_urls = am.get_modis(products=product, collection=collection, startTime=start_date.strftime('%Y-%m-%d %H:%M:%S'),
                             endTime=end_date.strftime('%Y-%m-%d %H:%M:%S'), dayNightBoth='DB')
    if file_urls is None:
        raise RuntimeError('No file URLs obtained')
    else:
        return file_urls


def get_earthdata_token():
    with open(os.path.join(os.path.expanduser('~'), '.earthdata-app-key'), 'r') as fobj:
        for line in fobj:
            if line.startswith('#'):
                continue
            else:
                return line.strip()


def geturl(url, token=None, out=None, verbose=0):
    """
    Retrieves a file from the MODIS LAADS server. Modified from
    https://ladsweb.modaps.eosdis.nasa.gov/tools-and-services/data-download-scripts/#python
    """
    headers = { 'user-agent' : USERAGENT }
    if not token is None:
        headers['Authorization'] = 'Bearer ' + token
    safety = 0
    while safety < max_download_attempts:
        safety += 1
        if safety > 1 and verbose > 0:
            print('   Retrying download for {}'.format(url))

        try:
            import ssl
            CTX = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
            if sys.version_info.major == 2:
                import urllib2
                try:
                    fh = urllib2.urlopen(urllib2.Request(url, headers=headers), context=CTX)
                    if out is None:
                        return fh.read()
                    else:
                        shutil.copyfileobj(fh, out)
                except urllib2.HTTPError as e:
                    print('HTTP GET error code: %d' % e.code, file=sys.stderr)
                    print('HTTP GET error message: %s' % e.message, file=sys.stderr)
                except urllib2.URLError as e:
                    print('Failed to make request: %s' % e.reason, file=sys.stderr)
                else:
                    return None

            else:
                from urllib.request import urlopen, Request, URLError, HTTPError
                try:
                    fh = urlopen(Request(url, headers=headers), context=CTX)
                    if out is None:
                        return fh.read().decode('utf-8')
                    else:
                        shutil.copyfileobj(fh, out)
                except HTTPError as e:
                    print('HTTP GET error code: %d' % e.code(), file=sys.stderr)
                    print('HTTP GET error message: %s' % e.message, file=sys.stderr)
                except URLError as e:
                    print('Failed to make request: %s' % e.reason, file=sys.stderr)
                else:
                    return None

        except AttributeError:
            # OS X Python 2 and 3 don't support tlsv1.1+ therefore... curl
            # Not modified to try to redownload a failed file (JLL 22 May 2018)
            import subprocess
            try:
                args = ['curl', '--fail', '-sS', '-L', '--get', url]
                for (k,v) in headers.items():
                    args.extend(['-H', ': '.join([k, v])])
                if out is None:
                    # python3's subprocess.check_output returns stdout as a byte string
                    result = subprocess.check_output(args)
                    return result.decode('utf-8') if isinstance(result, bytes) else result
                else:
                    subprocess.call(args, stdout=out)
            except subprocess.CalledProcessError as e:
                print('curl GET error message: %' + (e.message if hasattr(e, 'message') else e.output), file=sys.stderr)
            return None

    # If we get here, the download never completed successfully
    raise RuntimeError('Number of download attempts for {} exceeded the maximum allowed {}'.format(
        url, max_download_attempts
    ))


def download_product(product, collection, path, start_date, end_date, verbose=0):
    token = get_earthdata_token()
    if not os.path.isdir(path):
        os.mkdir(path)
    urls = list_product_urls(product, collection, path, start_date, end_date, verbose=verbose)
    for link in urls:
        file_datestr = modis_date_re.search(link).group()
        file_date = dt.datetime.strptime(file_datestr, '%Y%j')
        year_str = file_date.strftime('%Y')
        year_directory = os.path.join(path, year_str)

        if not os.path.isdir(year_directory):
            os.mkdir(year_directory)

        file_basename = os.path.basename(link)
        file_fullname = os.path.join(year_directory, file_basename)
        if os.path.isfile(file_fullname) and os.path.getsize(file_fullname) > 0:
            if verbose > 1:
                print('File {} already exists and size is > 0; not re-downloaded'.format(file_fullname))
            continue

        with open(file_fullname, 'wb') as save_obj:
            if verbose > 0:
                print('Downloading {} to {}'.format(link, os.path.join(year_directory, file_basename)))
            geturl(link, token, save_obj, verbose=verbose)


def driver(start_date, end_date, verbose=0):
    modis_path = os.getenv('MODDIR')
    modis_alb_dir = os.path.join(modis_path, 'MCD43D')
    modis_cloud_dir = os.path.join(modis_path, 'MYD06_L2')
    modis_alb_collection = '6'
    modis_cloud_collection = '61'
    products = [('MCD43D07', modis_alb_collection, modis_alb_dir),
                ('MCD43D08', modis_alb_collection, modis_alb_dir),
                ('MCD43D09', modis_alb_collection, modis_alb_dir),
                ('MCD43D31', modis_alb_collection, modis_alb_dir),
                ('MYD06_L2', modis_cloud_collection, modis_cloud_dir)]
    for product, collection, path in products:
        if verbose > 0:
            print('Now downloading the {} (collection {}) product'.format(product, collection))
        download_product(product, collection, path, start_date, end_date, verbose=verbose)


def parse_cl_sdate(datestr):
        return dt.datetime.strptime(datestr + "000000", '%Y-%m-%d%H%M%S')
def parse_cl_edate(datestr):
        return dt.datetime.strptime(datestr + "235959", '%Y-%m-%d%H%M%S')

def parse_args():
    parser = argparse.ArgumentParser(description='Driver to download MODIS albedo and cloud data')
    parser.add_argument('-s', '--start-date', type=parse_cl_sdate, help='startdate yyyy-mm-dd')
    parser.add_argument('-e', '--end-date', type=parse_cl_edate, help='enddate yyyy-mm-dd')
    parser.add_argument('-v', '--verbose', action='count', help='Increase verbosity to the terminal')

    return vars(parser.parse_args())


def main():
    args_dict = parse_args()
    driver(**args_dict)


if __name__ == '__main__':
    main()