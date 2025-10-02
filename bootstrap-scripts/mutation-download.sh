#! /bin/bash
# Download a small region of the human genome (chr1:12345-12500) in FASTA format
# using the UCSC Genome Browser's API.
# This file is intended to be run as part of the bootstrap process.
# The downloaded FASTA file will be used for testing and demonstration purposes.    


wget https://togows.org/api/ucsc/hg38/chr1:12,345-12,500.fasta