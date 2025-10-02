#! /bin/bash
wget https://www.niehs.nih.gov/sites/default/files/2024-02/artbinmountrainier2016.06.05linux64.tgz

tar -xzf artbinmountrainier2016.06.05linux64.tgz 
cd art_bin_MountRainier/
chmod -x art_illumina
export PATH=$PATH:$PWD