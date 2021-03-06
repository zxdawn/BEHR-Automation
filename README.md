# Automated script

Download MCD43D07, MCD43D08, MCD43D09, MCD43D31, MYD06, OMNO2 ans OMPIXCOR

## Requirements

1. LAADS app key; 

   You can generate [here](https://ladsweb.modaps.eosdis.nasa.gov/tools-and-services/data-download-scripts/#appkeys) and save it as `~/.earthdata-app-key`

2. SOAPpy; 

   `pip install SOAPpy`

3. requests

   `conda install -c anaconda requests`

4. beautifulsoup4

   `conda install -c anaconda beautifulsoup4`

## Directory structure

```
export MODDIR='xxxxxxxxxxx/MODIS/'
export OMNO2DIR='xxxxxxxxxxx/OMNO2/version_3_3_0'
export OMPIXCORDIR='xxxxxxxxxxx/OMPIXCOR/version_003'
```

```
├── MODIS
│   ├── Land_Water_Mask_7Classes_UMD.hdf
│   ├── MCD43D
│   │   └── yyyy_1
│   │   └── yyyy_2
│   └── MYD06_L2
│       └── yyyy_1
│       └── yyyy_2
├── OMI
│   ├── OMNO2
│   │   └── version_3_3_0
│   │       ├── yyyy_1
│   │       │   └── mm_1
│   └── OMPIXCOR
│       └── version_003
│           ├── yyyy_1
│           │   └── mm_1
```
## Usage

**Arguments:**

```
-s|--startdate

	yyyy-mm-dd;

-e|--enddate

	yyyy-mm-dd;

```

You need to change `USERNAME` and `PASSWORD ` in `get_omi.py`

**Example:**

```
python get_modis.py -s 2014-04-01 -e 2014-04-30 -v
python get_omi.py -s 2014-04-01 -e 2014-04-30 -v
```
