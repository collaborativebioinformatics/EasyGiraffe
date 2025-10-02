#! /bin/bash

git clone --recursive https://github.com/vgteam/vg.git
cd vg
make get-deps
sudo apt-get install build-essential git cmake pkg-config libncurses-dev libbz2-dev  \
                     protobuf-compiler libprotoc-dev libprotobuf-dev libjansson-dev \
                     automake gettext autopoint libtool jq bsdmainutils bc rs parallel \
                     npm curl unzip redland-utils librdf-dev bison flex gawk lzma-dev \
                     liblzma-dev liblz4-dev libffi-dev libcairo-dev libboost-all-dev \
                     libzstd-dev pybind11-dev python3-pybind11

make -j4
sudo make install
