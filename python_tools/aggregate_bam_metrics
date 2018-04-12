#!/opt/common/CentOS_6-dev/python/python-2.7.10/bin/python


import os
import sys
import ntpath
import subprocess
from shutil import copyfile


######################################################
# Aggregate Metrics across Bams from multiple samples
#
# Example Waltz CountReads output files:
#
# MSK-L-007-bc-IGO-05500-DY-5_bc217_5500-DY-1_L000_mrg_cl_aln_srt_MD_IR_FX_BR.bam.covered-regions
# MSK-L-007-bc-IGO-05500-DY-5_bc217_5500-DY-1_L000_mrg_cl_aln_srt_MD_IR_FX_BR.bam.fragment-sizes
# MSK-L-007-bc-IGO-05500-DY-5_bc217_5500-DY-1_L000_mrg_cl_aln_srt_MD_IR_FX_BR.bam.read-counts

# Example Waltz PileupMetrics output files:
#
# MSK-L-007-bc-IGO-05500-DY-5_bc217_5500-DY-1_L000_mrg_cl_aln_srt_MD_IR_FX_BR-pileup.txt
# MSK-L-007-bc-IGO-05500-DY-5_bc217_5500-DY-1_L000_mrg_cl_aln_srt_MD_IR_FX_BR-pileup-without-duplicates.txt
# MSK-L-007-bc-IGO-05500-DY-5_bc217_5500-DY-1_L000_mrg_cl_aln_srt_MD_IR_FX_BR-intervals.txt
# MSK-L-007-bc-IGO-05500-DY-5_bc217_5500-DY-1_L000_mrg_cl_aln_srt_MD_IR_FX_BR-intervals-without-duplicates.txt


INTERVALS_COVERAGE_SUM_FILENAME = 'intervals_coverage_sum.txt'
EPSILON = 10e-6

# todo - use Pandas instead of looping through files

files = sys.argv[1:]

# todo - not clean, upgrade to Toil-0.12 and use Directory Input:
# Copy all waltz output to current dir
for input_file in files:
    copyfile(input_file, ntpath.basename(input_file))


# Define headers for metrics files:
READ_COUNTS_FILE_HEADER = "Bam\tID\tTotalReads\tUnmappedReads\tTotalMapped\tUniqueMapped\tDuplicateFraction\t"
READ_COUNTS_FILE_HEADER += "TotalOnTarget\tUniqueOnTarget\tTotalOnTargetFraction\tUniqueOnTargetFraction\n"

FRAGMENT_SIZES_FILE_HEADER = "FragmentSize\tTotalFrequency\tUniqueFrequency\tSample\n"
WALTZ_COVERAGE_FILE_HEADER = "Sample\tTotalCoverage\tUniqueCoverage\n"
INTERVALS_COVERAGE_SUM_FILE_HEADER = "Chr\tStart\tEnd\tIntervalName\tLength\tGC\tCoverage\tCoverageWithoutDuplicates\n"


def process_read_counts_files():
    """
    read-counts.txt

    Concatenate .read-counts files for each Bam into one file
    """

    print(os.getcwd())
    print(os.listdir('.'))

    cmd = 'cat ' + './*.read-counts > read-counts.txt'
    return_code = subprocess.check_call(cmd, shell=True)
    print("process_read_counts_files() Return code: {}".format(return_code))

    read_counts = open('read-counts.txt')
    temp = open('t', 'w')
    temp.write(READ_COUNTS_FILE_HEADER)

    for line in read_counts:
        line_split = line.strip().split('\t')
        rest = '\t'.join(line_split[1:])
        sample = line_split[0]
        sample_abbrev = sample.split('_bc')[0]
        temp.write(sample + '\t' + sample_abbrev + '\t' + rest + '\n')

    os.unlink('read-counts.txt')
    os.rename('t', 'read-counts.txt')

def process_fragment_sizes_files():
    """
    fragment-sizes.txt
    """
    fragment_sizes_file = open('fragment-sizes.txt', 'w')
    fragment_sizes_file.write(FRAGMENT_SIZES_FILE_HEADER)

    input_files = [f for f in os.listdir('.') if '.fragment-sizes' in f]
    for f in input_files:
        sample = f.replace('.bam.fragment-sizes', '')
        file_path = '.' + '/' + f

        with open(file_path) as input_file:
            for line in input_file:
                fragment_sizes_file.write(line.strip() + '\t' + sample + '\n')


def create_waltz_coverage_file():
    """
    waltz-coverage.txt
    """
    waltz_coverage_file = open('waltz-coverage.txt', 'w')
    waltz_coverage_file.write(WALTZ_COVERAGE_FILE_HEADER)

    input_files = [f for f in os.listdir('.') if '-intervals.txt' in f]

    for f in input_files:
        sample = f.replace('-intervals.txt', '')

        file_path = '.' + '/' + f

        # Total Coverage = the sum of (coverage * fragment length) over all intervals
        with open(file_path) as input_file:
            count = 0
            total_coverage = 0
            for interval in input_file:
                line_split = interval.strip().split('\t')
                count = count + int(line_split[4])
                total_coverage = total_coverage + int(line_split[4]) * float(line_split[6])

            print(total_coverage, count, total_coverage / count)
            total_coverage = total_coverage / count

        # Unique Coverage = the sum of (coverage * fragment length) over all unique intervals
        new_file_path = file_path.replace('-intervals', '-intervals-without-duplicates')
        with open(new_file_path) as input_file:
            count = 0
            unique_coverage = 0
            for interval in input_file:
                line_split = interval.strip().split('\t')
                count = count + int(line_split[4])
                unique_coverage = unique_coverage + int(line_split[4]) * float(line_split[6])

            print(unique_coverage, count, unique_coverage / count)
            unique_coverage = unique_coverage / count

        waltz_coverage_file.write(sample + '\t' + str(total_coverage) + '\t' + str(unique_coverage) + '\n')


def create_sum_of_coverage_temp_file():
    """
    t5
    """
    temp_5 = open('t5', 'w')

    coverage = {}
    gc = {}

    input_files = [f for f in os.listdir('.') if '-intervals.txt' in f]
    for f in input_files:

        file_path = '.' + '/' + f

        with open(file_path) as input_file:
            for line in input_file:
                line_split = line.strip().split('\t')

                key = '\t'.join(line_split[0:5])
                if key in coverage:
                    coverage[key] = float(coverage[key]) + float(line_split[6])
                else:
                    coverage[key] = line_split[6]
                    gc[key] = line_split[7]

        for key in coverage.keys():
            temp_5.write(key + '\t' + str(gc[key]) + '\t' + str(coverage[key]) + '\n')

    temp_5.close()


def create_temp_6_file():
    """
    t6
    """
    temp_6 = open('t6', 'w')

    input_files = [f for f in os.listdir('.') if '-intervals-without-duplicates.txt' in f]

    coverage = {}
    for f in input_files:
        file_path = '.' + '/' + f

        with open(file_path) as input_file:
            for line in input_file:
                line_split = line.strip().split('\t')

                key = line_split[3]
                if key in coverage:
                    coverage[key] = coverage[key] + line_split[6]
                else:
                    coverage[key] = line_split[6]

        for key in coverage.keys():
            temp_6.write(key + '\t' + coverage[key] + '\n')

    temp_6.close()


def create_intervals_coverage_sum_file():
    """
    intervals-coverage-sum.txt
    """
    intervals_coverage_sum_file = open(INTERVALS_COVERAGE_SUM_FILENAME, 'w')
    intervals_coverage_sum_file.write(INTERVALS_COVERAGE_SUM_FILE_HEADER)

    with open('t5', 'rU') as t5:
        with open('t6', 'rU') as t6:
            for line in t5:
                line_2 = t6.readline()

                try:
                    coverage_wo_dup = line_2.strip().split('\t')[1]
                except:
                    coverage_wo_dup = '0'

                intervals_coverage_sum_line = line.strip() + '\t' + coverage_wo_dup + '\n'
                intervals_coverage_sum_file.write(intervals_coverage_sum_line)

    intervals_coverage_sum_file.close()

    os.unlink('t5')
    os.unlink('t6')


def create_sample_per_interval_coverage_files():
    """
    t5, t6 again
    """
    temp_5 = open('t5', 'w')
    temp_6 = open('t6', 'w')

    input_files = [f for f in os.listdir('.') if '-intervals.txt' in f]

    for f in input_files:

        file_path = '.' + '/' + f

        with open(file_path) as input_file:

            sample = f.replace('-intervals.txt', '')
            sample = sample.split('_bc')[0]
            for line in input_file:
                line_split = line.strip().split('\t')


                intervals_line_output = line_split[3] + '\t' + sample + '\t' + line_split[6] + '\t' + line_split[7]
                temp_5.write(intervals_line_output + '\n')


    input_files = [f for f in os.listdir('.') if '-intervals-without-duplicates.txt' in f]

    for f in input_files:

        file_path = '.' + '/' + f

        with open(file_path) as input_file:

            sample = f.replace('-intervals-without-duplicates.txt', '')
            sample = sample.split('_bc')[0]
            for line in input_file:
                line_split = line.strip().split('\t')

                ivals_wo_dups_path = file_path.replace('-intervals', '-intervals-without-duplicates')

                intervals_wo_dups_output = line_split[3] + '\t' + sample + '\t' + line_split[6] + '\t' + line_split[7]
                temp_6.write(str(intervals_wo_dups_output + '\n'))

    temp_5.close()
    temp_6.close()


def make_normalized_coverage_files():
    """
    t7, t8
    todo - not well tested (manually or automatically...)
    """
    t7 = open('t7', 'w')
    t8 = open('t8', 'w')

    t7.write("Interval\tGene\tSample\tTotalCoverage\n")
    t8.write("Interval\tGene\tSample\tUniqueCoverage\n")

    input_files = [f for f in os.listdir('.') if '-intervals.txt' in f]

    for sample_intervals_filename in input_files:
        file_path = '.' + '/' + sample_intervals_filename

        sample = sample_intervals_filename.replace('-intervals.txt', '')
        sample = sample.split('_bc')[0]

        # Sample mean as normalizing factor
        norm_factor = compute_coverage_mean(file_path)

        for line in open(file_path):
            line_split = line.strip().split('\t')
            normalized_coverage = str( float(line_split[6]) / norm_factor )
            t7.write(str(line_split[3] + '\t' + sample + '\t' + normalized_coverage + '\n'))

        sample_intervals_wo_dups_file_path = file_path.replace('-intervals', '-intervals-without-duplicates')
        norm_factor_wo_dups = compute_coverage_mean(sample_intervals_wo_dups_file_path)

        for line in open(sample_intervals_wo_dups_file_path):
            line_split = line.strip().split('\t')
            normalized_coverage = str( float(line_split[6]) / norm_factor_wo_dups )
            t8.write(str(line_split[3] + '\t' + sample + normalized_coverage + '\n'))

    t7.close()
    t8.close()


def compute_coverage_mean(filename):
    interval_count = 0
    coverage_total = 0
    for line in open(filename):
        interval_count = interval_count + 1
        coverage_total = coverage_total + float(line.split('\t')[6])

    interval_count += EPSILON

    norm_factor = coverage_total * 1.0 / interval_count
    return norm_factor



"""
Would be better to pass filenames in expliticly
todo - obviously some cleanup left in this code
"""
if __name__ == '__main__':
    process_read_counts_files()
    process_fragment_sizes_files()
    create_waltz_coverage_file()
    create_sum_of_coverage_temp_file()
    create_temp_6_file()
    create_intervals_coverage_sum_file()
    create_sample_per_interval_coverage_files()
    # make_normalized_coverage_files()
