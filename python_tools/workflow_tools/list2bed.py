#!python

import os
import sys
import shutil
import argparse
import pybedtools

# Notes:
# There are two original versions of this file
# 1. /opt/common/CentOS_6-dev/list2bed/1.0.1/list2bed.py (used in CMO wrapper)
# 2. From Impact pipeline Run_FindCoveredIntervals.py
#
# They are very comparable, but this file is adapted from the first


def list_to_bed(inFile, outFile, sort):
    tmp_name = 'listToBed.temp'
    tmp = open(tmp_name, "w")

    if os.stat(inFile).st_size == 0:
        # Todo: What is this magic number?
        tmp.write("1\t963754\t963902\n")
    else:
        with open(inFile, 'r') as filecontent:
            for line in filecontent:
                data = line.rstrip('\n').split(":")
                chr = data[0]
                # Formated as 1:1234567-2345678
                if "-" in data[1]:
                    st, en = data[1].split("-")
                # Formated as 1:1234567:2345678
                else:
                    st = data[1]
                    # Todo: is this supposed to be:
                    # int(data[2])
                    en = int(data[1]) + 1
                tmp.write(str(chr) + "\t" + str(st) + "\t" + str(en) + "\n")
    tmp.close()

    if sort:
        # Todo: Why stderr?
        print >> sys.stderr, "Sorting..."
        bedtool = pybedtools.BedTool(tmp_name)
        stbedtool = bedtool.sort()
        mbedtool = stbedtool.merge(d=50)
        mbedtool.saveas(outFile)
    else:
        shutil.move(tmp_name, outFile)

    return outFile


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input_file", help="picard interval list", required=True)
    parser.add_argument("-o", "--output_file", help="output bed file", required=True)
    parser.add_argument("-s", "--sort", help="sort bed file output", action='store_true')
    args = parser.parse_args()
    print args

    list_to_bed(os.path.abspath(args.input_file), os.path.abspath(args.output_file), args.sort)


if __name__ == '__main__':
    main()
