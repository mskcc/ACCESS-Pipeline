#!/opt/common/CentOS_6-dev/python/python-2.7.10/bin/python
# Todo: supply python as baseCommand instead of using shebang


import sys
import gzip
from itertools import izip


# Script to add UMIs back into reads from paired fastqs.

# We start with R1 and R2 that have been clipped with Marianas, and UMIs have been placed in the read name:

# Clipped R1:
# @K00217:116:HM7N7BBXX:4:1127:11363:23716:ATG+CAC
# ATGGGAAGACATGGGGCCCAGGACACTCACCCTAGGCCAGCCCAGGAGCCCCAGGGGAGGCAGCCCCTCCCACCCAGCAGGGCACAGGCACTCACAGACCCTGGGGCTACTACCCCTGTCTC
# +
# AA---7FAJJJF<<F<A<-FJ7-7FJ<AJJJJFF7-FFJ7<-FAAFAAAAJ-AAAAFF-77F<AAF-AA7AJFJJJ<JFJ<JAFJJJJJJ<-FJAJ-7J-A<AA-AA-FAFFF-7---7F7<

# Clipped R2:
# @K00217:116:HM7N7BBXX:4:1102:22627:48227:CAC+ATG
# ATGGGAAGACATGGGGCCCAGGACACTCACCCTAGGCCAGCCCAGGAGCCCCAGGGGAGGCAGCCCCTCCCACCCAGCAGGGCACAGGCACTCACAGACCCTGGGGCTACTACCCCTGTCTC
# +
# FJFJJA<JFJFFAJJJJJJJJJAFFJAFJJJJJJJ<JAFJFJJFJJFFJJJJFJJFJAAJJAFJJJJJJJJJFFJJJJAJFJFFFFJJJJF7FJJJFFFJF77FJJJJFFFJJFJJJJ7F-F

# We take the UMIs from the read name, split them, and stick them on the beginnings of the R1 and R2 files,
# following IDT loop UMI rules for adding support bases:
# todo - using G for length 2 support bases - correct?

# Output R1:
# @K00217:116:HM7N7BBXX:4:1127:11363:23716 1:N:0:TCGACAAG+CTTGTCGA
# ATGT ATGGGAAGACATGGGGCCCAGGACACTCACCCTAGGCCAGCCCAGGAGCCCCAGGGGAGGCAGCCCCTCCCACCCAGCAGGGCACAGGCACTCACAGACCCTGGGGCTACTACCCCTGTCTC
# +
# AAAA AA---7FAJJJF<<F<A<-FJ7-7FJ<AJJJJFF7-FFJ7<-FAAFAAAAJ-AAAAFF-77F<AAF-AA7AJFJJJ<JFJ<JAFJJJJJJ<-FJAJ-7J-A<AA-AA-FAFFF-7---7F7<

# Output R2:
# @K00217:116:HM7N7BBXX:4:1127:11363:23716 2:N:0:TCGACAAG+CTTGTCGA
# CACT ATGGGAAGACATGGGGCCCAGGACACTCACCCTAGGCCAGCCCAGGAGCCCCAGGGGAGGCAGCCCCTCCCACCCAGCAGGGCACAGGCACTCACAGACCCTGGGGCTACTACCCCTGTCTC
# +
# AAAA FJFJJA<JFJFFAJJJJJJJJJAFFJAFJJJJJJJ<JAFJFJJFJJFFJJJJFJJFJAAJJAFJJJJJJJJJFFJJJJAJFJFFFFJJJJF7FJJJFFFJF77FJJJJFFFJJFJJJJ7F-F

# Todo: Refactor this file:
# Static string constants
# Extract functions
# Argparse

def main():
    '''
    Reads the fastq 1 & fastq 2 in a paired fashion,
    taking read names from RGID & adding them to ends of R1 & R2

    :return:
    '''
    input_r1 = str(sys.argv[1])
    input_r2 = str(sys.argv[2])

    new_r1_name = input_r1.replace('.fastq', '_clipping-reversed.fastq')
    new_r2_name = input_r2.replace('.fastq', '_clipping-reversed.fastq')

    output_r1 = open(new_r1_name, 'w')
    output_r2 = open(new_r2_name, 'w')

    # Iterate through the Read 1 and Read 2 fastqs @ the same time
    for i, tuple in enumerate(izip(open(input_r1), open(input_r2))):
        line_r1 = tuple[0].strip()
        line_r2 = tuple[1].strip()

        if i % 4 == 0:
            # Read Group ID line (with the UMIs)
            read_name = ':'.join(line_r1.split(':')[0:-1])
            umi = line_r1.split(':')[-1]
            umi_1 = umi.split('+')[0]
            umi_2 = umi.split('+')[1]

            umi_1 = add_support_bases(umi_1)
            umi_2 = add_support_bases(umi_2)

            # Todo: We are spoofing the barcode sequences for now
            output_r1.write(read_name + ' 1:N:0:TCGACAAG+CTTGTCGA' + '\n')
            output_r2.write(read_name + ' 2:N:0:TCGACAAG+CTTGTCGA' + '\n')

        elif i % 4 == 1:
            # Base sequence line
            sequence_1 = umi_1 + line_r1
            sequence_2 = umi_2 + line_r2

            output_r1.write(sequence_1 + '\n')
            output_r2.write(sequence_2 + '\n')

            # Todo: Just put R1 on + strand and R2 on - strand for now
            # todo: does this put reads on the correct strands?
            output_r1.write('+\n')
            output_r2.write('-\n')

        elif i % 4 == 3:
            # Base quality line
            # Todo: Use original base qualities
            output_r1.write('A'*len(umi_1) + line_r1 + '\n')
            output_r2.write('A'*len(umi_2) + line_r2 + '\n')

    output_r1.close()
    output_r2.close()


def add_support_bases(umi):
    '''
    If last base of UMI in 'GC' --> return 'T'
    Else if last base of UMI in 'AT' --> return 'GT'

    :param umi:
    :return:
    '''
    if umi[-1] in 'GC':
        umi = umi + 'T'
    elif umi[-1] in 'AT':
        umi = umi + 'GT'
    return umi


if __name__ == "__main__":
    main()