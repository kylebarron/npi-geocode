---
author: Kyle Barron
date: Monday, March 19, 2018
title: Setting up Pelias locally for Geocoding
---

# Overview

This document gives an overview of how to set up [Pelias](https://pelias.io/) locally. Pelias is an open-source
geocoding engine that uses up to four different open mapping sources to form its geocoding results.

This guide will assume that you're installing this onto a Linux/Unix workstation.

# Installation

This guide roughly follows Pelias' [official install guide](https://pelias.io/install.html).

## Dependencies

### Node.js

I'm using Node v8.10.0, which you can install with:

```bash
wget https://nodejs.org/dist/v8.10.0/node-v8.10.0-linux-x64.tar.gz -O /tmp/node-v8.tar.gz

mkdir /tmp/node
tar -xzvf /tmp/node-v8.tar.gz -C /tmp/node/ --strip-components 1

mkdir -p ~/local/bin/
mv /tmp/node/bin/* ~/local/bin/

mkdir -p ~/local/include/
mv /tmp/node/include/* ~/local/include/

mkdir -p ~/local/lib/
mv /tmp/node/lib/* ~/local/lib/

mkdir -p ~/local/share/doc/
mv /tmp/node/share/doc/* ~/local/share/doc/

mkdir -p ~/local/share/man/man1/
mv /tmp/node/share/man/man1/* ~/local/share/man/man1/

npm config set prefix ~/local
```

This assumes that `~/local/bin/` is on your `PATH`, and that `~/local/lib/` is on your `LD_LIBRARY_PATH`.
You can add these to your path with:
```bash
export PATH=$HOME/local/bin:$PATH
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$HOME/local/lib
```

### Elasticsearch

First install the most recent version of Java. Then install Elasticsearch version 2.3.0.

```bash
wget https://download.elasticsearch.org/elasticsearch/release/org/elasticsearch/distribution/tar/elasticsearch/2.3.0/elasticsearch-2.3.0.tar.gz -O /tmp/elasticsearch.tar.gz

mkdir ~/local/elasticsearch
tar -xzvf /tmp/elasticsearch.tar.gz -C ~/local/elasticsearch/ --strip-components 1
```

Then add `~/local/elasticsearch` to your `PATH`:
```bash
export PATH=$HOME/local/elasticsearch/bin:$PATH
```

### Libpostal

From the GitHub repo:

> libpostal is a C library for parsing/normalizing street addresses around the world using statistical NLP and open data.
> The goal of this project is to understand location-based strings in every language, everywhere.

As of now, to install you can do:

```bash
git clone https://github.com/openvenues/libpostal /tmp/libpostal
cd /tmp/libpostal
./bootstrap.sh
./configure --prefix=$HOME/local --datadir={directory to hold 2GB of source data}
make -j4
make install
```

On the configure step, I got an error:
```
libtool: Version mismatch error. This is libtool 2.4.6, but the
libtool: definition of this LT_INIT comes from libtool 2.2.6b
```
To fix this I did:

```bash
autoreconf -i
cat m4/libtool.m4 >> aclocal.m4
cat m4/ltoptions.m4 >> aclocal.m4
cat m4/ltversion.m4 >> aclocal.m4
cat m4/lt\~obsolete.m4 >> aclocal.m4
./configure --prefix=$HOME/local --datadir={directory to hold 2GB of source data}
make -j4
make install
```

Note that as part of the `make -j4` step, it will download about 700 MB worth of files to the data provided as `--datadir` (specifically at `datadir/libpostal/`). If the download fails, follow [these instructions](https://github.com/openvenues/libpostal/issues/330#issuecomment-373478507).

Again, make sure that `~/local/lib` is on your `LD_LIBRARY_PATH`. You can add this with:
```bash
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$HOME/local/lib
```

## Installing Pelias

Now you're ready to actually install Pelias itself.
It's structured into two main Git repositories, plus five others to
assist in importing open geospatial data into the program.

Go to a directory that's convenient for installing these libraries; I install them into the `lib/` folder of my main project directory.
Aka if my project directory is at `/home/kyle/geocoding`, then I'd put these into `/home/kyle/geocoding/lib`. Change to that directory and then run the following.

I'll call the top-level directory `importer_directory`, so for me, I'll make the variable:
```bash
importer_directory=/home/kyle/disk/npi-geocode/lib/
```

```bash
cd $importer_directory
for repository in schema api whosonfirst geonames openaddresses openstreetmap polylines; do
    git clone git@github.com:pelias/${repository}.git
    pushd $repository > /dev/null
    git checkout production
    npm install
    popd > /dev/null
done
```

This didn't work for me on one of the computers I was installing this on because a firewall was blocking the `git://` URI to GitHub. To fix this, change `git://` to `https://` in the `package.json` file in each of those directories.

Additionally, you'll probably receive some error messages regarding `node-postal`, which doesn't build correctly since it can't find the `libpostal` libraries in `~/local/lib/`. After the above commands stop running, run the following:

```bash
cd /api/node_modules/node-postal
sed -i "s@/usr/local/lib@$HOME/local/lib@g" binding.gyp
sed -i "s@/usr/local/include@$HOME/local/include@g" binding.gyp
npm install
cd ../../../
```


# Downloading Data

You have several different options of data to download. To make things easier, store your data directory in a variable:
```bash
datadir="/homes/nber/barronk/bulk/raw/npi-geocode"
```
This should be the same folder you provided in the `libtool` installation step above. It's easiest to put all this data in the same folder.

## Configuring Pelias

The Pelias configuration goes into a `pelias.json` file. By default Pelias looks for the file at `~/pelias.json`, so I put my file there, despite cluttering the home directory.

Note that the `datapath` values for each of the values within `imports` is the _absolute_ path of the place within `datadir` where I'll be storing my data.

I'll explain parts of this configuration file in the next few download sections.

```json
{
  "elasticsearch": {
    "settings": {
      "index": {
        "number_of_replicas": "0",
        "number_of_shards": "5",
        "refresh_interval": "1m"
      }
    }
  },
  "interpolation": {
    "client": {
      "adapter": "null"
    }
  },
  "imports": {
    "adminLookup": {
      "enabled": true
    },
    "geonames": {
      "datapath": "/homes/nber/barronk/bulk/raw/npi-geocode/geonames"
    },
    "openstreetmap": {
      "datapath": "/homes/nber/barronk/bulk/raw/npi-geocode/openstreetmap",
      "import": [{
        "filename": "us-northeast-latest.osm.pbf",
        "filename": "us-midwest-latest.osm.pbf",
        "filename": "us-south-latest.osm.pbf",
        "filename": "us-west-latest.osm.pbf"
      }]
    },
    "openaddresses": {
      "datapath": "/homes/nber/barronk/bulk/raw/npi-geocode/openaddresses/us",
      "files": [
        "all.csv"
      ]
    },
    "polyline": {
      "datapath": "/homes/nber/barronk/bulk/raw/npi-geocode/polyline",
      "files": [
        "road_network.polylines"
      ]
    },
    "whosonfirst": {
      "importPostalcodes": true,
      "importPlace": 85633793,
      "datapath": "/homes/nber/barronk/bulk/raw/npi-geocode/whosonfirst"
    }
  }
}
```

## Who's on First

There is a convenient auto-downloader script in the `whosonfirst` Git repository downloaded into `importer_directory`. You can tell it the `datapath` in the `pelias.json` file and it will automatically download the data into that folder.

You can also provide an `importPlace` key to filter the downloads. For example, I use [`85633793`](https://spelunker.whosonfirst.org/id/85633793/), the ID number for the United States.

All allowable keys are detailed at the `pelias/whosonfirst` [README](https://github.com/pelias/whosonfirst#configuration).

The go to the `whosonfirst` directory, and run the download script
```bash
cd $importer_directory/whosonfirst
npm run download
```

For me, this didn't work because it couldn't find `GLIBCXX_3.4.18`. This was solved by downloading [miniconda](https://conda.io/miniconda.html) to `~/local/miniconda3/`, running `conda install libgcc`, and adding `~/local/miniconda3/lib/` to `LD_LIBRARY_PATH`, with

```bash
wget https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh -O /tmp/miniconda3.sh
bash /tmp/miniconda3.sh -b -p ~/local/miniconda3
~/local/miniconda3/bin/conda update --all
export PATH=$HOME/local/miniconda3/bin:$PATH
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$HOME/local/miniconda3/lib
```


## OpenAddresses

Download these files:

```bash
wget https://s3.amazonaws.com/data.openaddresses.io/openaddr-collected-us_northeast.zip -P $datadir/openaddresses/
wget https://s3.amazonaws.com/data.openaddresses.io/openaddr-collected-us_midwest.zip -P $datadir/openaddresses/
wget https://s3.amazonaws.com/data.openaddresses.io/openaddr-collected-us_south.zip -P $datadir/openaddresses/
wget https://s3.amazonaws.com/data.openaddresses.io/openaddr-collected-us_west.zip -P $datadir/openaddresses/
```

Then change to that directory and unzip all of them:
```bash
cd $datadir/openaddresses
unzip *.zip
```

Now all of the data is held in csv's by state within `us/`. To make this easiest for later, we'll concatenate all these csv's.

```bash
cd us
cat **/*.csv > all.csv
```

## OpenStreetMap

You need to download OpenStreetMap data in `.osm.pdf` format. There are many mirrors; I use `https://download.geofabrik.de`.
To download the entire OpenStreetMap for the United States, you can download the four sub regions that website provides:

```bash
wget https://download.geofabrik.de/north-america/us-midwest-latest.osm.pbf -P $datadir/openstreetmap
wget https://download.geofabrik.de/north-america/us-northeast-latest.osm.pbf -P $datadir/openstreetmap
wget https://download.geofabrik.de/north-america/us-south-latest.osm.pbf -P $datadir/openstreetmap
wget https://download.geofabrik.de/north-america/us-west-latest.osm.pbf -P $datadir/openstreetmap
```

# Importing Data

If you're importing a lot of data (as we're about to), Pelias recommends increasing the "Heap size". I personally set my Heap size to 20GB with
```bash
export ES_HEAP_SIZE=20g
```

It's helpful to have somewhat of a graphic interface to see your data and interact with the database. To install a [simple one](https://mobz.github.io/elasticsearch-head/), run:
```bash
~/local/elasticsearch/bin/plugin install mobz/elasticsearch-head
```
This should allow you to go to `http://localhost:9200/_plugin/head/` and see database information. If you're installing this on a remote server, you first need to forward the port to your local computer, with something like
```bash
ssh user@host -L9200:localhost:9200
```
Then you can go to the above address in your browser.

Now start Elasticsearch with
```bash
~/local/elasticsearch/bin/elasticsearch -d
```

Then create an index with
```bash
cd $importer_directory/schema
node scripts/create_index.js
```

Now go to each helper Git repository and run `npm start` to start loading data into Elasticsearch. For example, to import OpenStreetMap data into Elasticsearch, run
```bash
cd $importer_directory/openstreetmap
npm start
```





































