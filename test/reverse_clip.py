import sys
import gzip
from itertools import izip

# We start with R1 and R2 that have been clipped with Marianas, and UMIs have been placed in the read name.
#
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
# following IDT UMI rules for adding support bases
# todo - randomly using G for length 2 support bases - correct?
#
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


def main():
    input_r1 = str(sys.argv[1])
    input_r2 = str(input_r1.replace('_R1', '_R2'))

    new_r1_name = input_r1.replace('.fastq.gz', '') + '_clipping-reversed.fastq'
    new_r2_name = input_r2.replace('.fastq.gz', '') + '_clipping-reversed.fastq'

    output_r1 = open(new_r1_name, 'w')
    output_r2 = open(new_r2_name, 'w')

    for i, tuple in enumerate(izip(gzip.open(input_r1), gzip.open(input_r2))):
        line_r1 = tuple[0].strip()
        line_r2 = tuple[1].strip()

        if i % 4 == 0:
            read_name = ':'.join(line_r1.split(':')[0:-1])
            umi = line_r1.split(':')[-1]
            umi_1 = umi.split('+')[0]
            umi_2 = umi.split('+')[1]

            umi_1 = add_support_bases(umi_1)
            umi_2 = add_support_bases(umi_2)

            output_r1.write(read_name + ' 1:N:0:TCGACAAG+CTTGTCGA' + '\n')
            output_r2.write(read_name + ' 2:N:0:TCGACAAG+CTTGTCGA' + '\n')

        elif i % 4 == 1:
            sequence_1 = umi_1 + line_r1
            sequence_2 = umi_2 + line_r2

            output_r1.write(sequence_1 + '\n')
            output_r2.write(sequence_2 + '\n')

            output_r1.write('+\n')
            output_r2.write('+\n')

        elif i % 4 == 3:
            output_r1.write('A'*len(umi_1) + line_r1 + '\n')
            output_r2.write('A'*len(umi_2) + line_r2 + '\n')

    output_r1.close()
    output_r2.close()


def add_support_bases(umi):
    if umi[-1] in 'GC':
        umi = umi + 'T'
    elif umi[-1] in 'AT':
        umi = umi + 'GT'
    return umi


if __name__ == "__main__":
    main()