import os
import re
from collections import OrderedDict

# Repository main directory
ROOT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")


#############
# Resources #
#############
RESOURCES_FOLDER = os.path.join(ROOT_DIR, "resources")

RUN_FILES_FOLDER = os.path.join(RESOURCES_FOLDER, "run_files")
RUN_PARAMS_FOLDER = os.path.join(RESOURCES_FOLDER, "run_params")
RUN_TOOLS_FOLDER = os.path.join(RESOURCES_FOLDER, "run_tools")

TEST = "test.yaml"
LOCAL = "local.yaml"
PRODUCTION = "production.yaml"

# Run Files
RUN_FILES = os.path.join(RUN_FILES_FOLDER, PRODUCTION)
RUN_FILES_TEST = os.path.join(RUN_FILES_FOLDER, TEST)
RUN_FILES_LOCAL = os.path.join(RUN_FILES_FOLDER, LOCAL)

# Run Parameters
RUN_PARAMS = os.path.join(RUN_PARAMS_FOLDER, PRODUCTION)
RUN_PARAMS_TEST = os.path.join(RUN_PARAMS_FOLDER, TEST)

# Resource Paths
TOOL_RESOURCES_LOCAL = os.path.join(ROOT_DIR, "resources/run_tools/local.yaml")
TOOL_RESOURCES_PROD = os.path.join(ROOT_DIR, "resources/run_tools/phoenix.yaml")
TOOL_RESOURCES_LUNA = os.path.join(ROOT_DIR, "resources/run_tools/luna.yaml")
ACCESS_VARIANTS_RUN_TOOLS_MANTA = os.path.join(RUN_TOOLS_FOLDER, "SV.yaml")
ACCESS_VARIANTS_RUN_TOOLS_MANTA_JUNO = os.path.join(RUN_TOOLS_FOLDER, "SV_juno.yaml")

# ACCESS-Variants Resources
ACCESS_VARIANTS_RUN_FILES_PATH = os.path.join(
    RUN_FILES_FOLDER, "ACCESS_variants_run_files.yaml"
)
ACCESS_VARIANTS_RUN_PARAMS_PATH = os.path.join(
    RUN_PARAMS_FOLDER, "ACCESS_variants_run_params.yaml"
)
ACCESS_VARIANTS_RUN_TOOLS_PATH = os.path.join(
    RUN_TOOLS_FOLDER, "ACCESS_variants_phoenix.yaml"
)
ACCESS_VARIANTS_RUN_TOOLS_PATH_CMO = os.path.join(
    RUN_TOOLS_FOLDER, "ACCESS_variants_cmo.yaml"
)
ACCESS_VARIANTS_RUN_TOOLS_PATH_JUNO = os.path.join(
    RUN_TOOLS_FOLDER, "ACCESS_variants_luna.yaml"
)
ACCESS_VARIANTS_RUN_PARAMS_DELLY_PATH = os.path.join(
    RUN_PARAMS_FOLDER, "ACCESS_variants_run_params_delly.yaml"
)

# ACCESS-CopyNumber Resources
ACCESS_COPYNUMBER_RUN_FILES_PATH = os.path.join(
    RUN_FILES_FOLDER, "ACCESS_copynumber_run_files.yaml"
)
ACCESS_COPYNUMBER_RUN_PARAMS_PATH = os.path.join(
    RUN_PARAMS_FOLDER, "ACCESS_copynumber_run_params.yaml"
)

RUN_PARAMS__STANDARD_BAM_TO_COLLAPSED_QC = os.path.join(
    RUN_PARAMS_FOLDER, "standard_bams_to_collapsed_qc.yaml"
)

# ACCESS-MSI Resources
ACCESS_MSI_RUN_FILES_PATH = os.path.join(RUN_FILES_FOLDER, "msi_run_files.yaml")
ACCESS_MSI_RUN_PARAMS_PATH = os.path.join(RUN_PARAMS_FOLDER, "msi_run_params.yaml")


##################################
# SampleSheet Column Definitions #
##################################
SAMPLE_SHEET__LANE_COLUMN = "Lane"
SAMPLE_SHEET__SAMPLE_ID_COLUMN = "Sample_ID"
SAMPLE_SHEET__PATIENT_ID_COLUMN = "Sample_Name"
SAMPLE_SHEET__BARCODE_ID1_COLUMN = "I7_Index_ID"
SAMPLE_SHEET__BARCODE_INDEX_1_COLUMN = "index"
SAMPLE_SHEET__BARCODE_ID2_COLUMN = "I5_Index_ID"
SAMPLE_SHEET__BARCODE_INDEX_2_COLUMN = "index2"
SAMPLE_SHEET__CLASS_COLUMN = "Description"
SAMPLE_SHEET__METADATA_COLUMN = "Operator"
SAMPLE_SHEET__PROJECT_ID_COLUMN = "Sample_Project"


################################
# TitleFile Column Definitions #
################################

# Columns explicity provided in sample sheet
TITLE_FILE__POOL_COLUMN = "Pool"
TITLE_FILE__SAMPLE_ID_COLUMN = "Sample"
TITLE_FILE__PATIENT_ID_COLUMN = "Patient_ID"
TITLE_FILE__SAMPLE_CLASS_COLUMN = "Class"
TITLE_FILE__BARCODE_INDEX_1_COLUMN = "Barcode_index_1"
TITLE_FILE__BARCODE_INDEX_2_COLUMN = "Barcode_index_2"
TITLE_FILE__RUN_ID_COLUMN = "Run_ID"
TITLE_FILE__LANE_COLUMN = "Lane"

# Columns inferred from other columns defined above
TITLE_FILE__SAMPLE_TYPE_COLUMN = "Sample_type"
TITLE_FILE__BAIT_VERSION_COLUMN = "Bait_version"

# Columns defined as constants
TITLE_FILE__IGO_ID_COLUMN = "IGO_ID"
TITLE_FILE__COLLAB_ID_COLUMN = "Collab_ID"

# Columns inteferred from samplesheet metadata/operator column
TITLE_FILE__SEX_COLUMN = "Sex"
TITLE_FILE__PATIENT_NAME_COLUMN = "PatientName"
TITLE_FILE__ACCESSION_COLUMN = "AccessionID"
TITLE_FILE__SEQUENCER_COLUMN = "Sequencer"

# TODO:
# Columns currently filled with dummy values until DMS/LIMS figures out a way.
TITLE_FILE__POOL_INPUT_COLUMN = "Pool_input"

# Columns not current used
TITLE_FILE__BARCODE_ID_COLUMN = "Barcode"
TITLE_FILE__INPUT_NG_COLUMN = "Input_ng"
TITLE_FILE__LIBRARY_YIELD_COLUMN = "Library_yield"
TITLE_FILE__DNA_YIELD_COLUMN = "Extracted_DNA_Yield"


##########################
# Map Column Definitions #
##########################

# Map SAMPLESHEET --> TITLE_FILE
# Use OrderedDict to keep ordering for keys() and values()
columns_map_samplesheet = OrderedDict(
    [
        (SAMPLE_SHEET__PROJECT_ID_COLUMN, TITLE_FILE__POOL_COLUMN),
        (SAMPLE_SHEET__SAMPLE_ID_COLUMN, TITLE_FILE__SAMPLE_ID_COLUMN),
        (SAMPLE_SHEET__PATIENT_ID_COLUMN, TITLE_FILE__PATIENT_ID_COLUMN),
        (SAMPLE_SHEET__CLASS_COLUMN, TITLE_FILE__SAMPLE_CLASS_COLUMN),
        (SAMPLE_SHEET__BARCODE_INDEX_1_COLUMN, TITLE_FILE__BARCODE_INDEX_1_COLUMN),
        (SAMPLE_SHEET__BARCODE_INDEX_2_COLUMN, TITLE_FILE__BARCODE_INDEX_2_COLUMN),
        (SAMPLE_SHEET__LANE_COLUMN, TITLE_FILE__LANE_COLUMN),
    ]
)


###################################
# Title file generation constants #
###################################
COLLAB_ID = "DMP"
PLASMA = "Plasma"
BUFFY = "Buffy Coat"
SAMPLE_ID_ALLOWED_DELIMETER = "-"
DISALLOWED_SAMPLE_ID_CHARACTERS = "!\"#$%&'()*+,./:;<=>?@[\\]^_`{|}~"
METADATA_COLUMN_DELIMETER = "|"
METADATA_REQUIRED_COLUMNS = [1, 2, 3, 4]
SELECT_SPLIT_COLUMN = [1]
ALLOWED_SAMPLE_TYPE = re.compile(r"(^TP|^TB|^NP|^NB)")
ALLOWED_SAMPLE_TYPE_LIST = ["TB", "NB", "TP", "NP"]
PLASMA_SAMPLE_TYPE = re.compile(r"(^TP|^NP)")
# PLASMA_SAMPLE_TYPE = ["TP", "NP", "T"]
BUFFY_SAMPLE_TYPE = re.compile(r"(^TB|^NB)")
# BUFFY_SAMPLE_TYPE = ["TB", "NB", "N"]
ALLOWED_SAMPLE_DESCRIPTION = ["Tumor", "Normal", "PoolTumor", "PoolNormal"]
ALLOWED_SAMPLE_TYPE_DESCRIPTION = [PLASMA, BUFFY]
ALLOWED_CONTROLS = ["PoolTumor", "PoolNormal"]
ALLOWED_SEX = ["Male", "Female"]
CONTROL_SAMPLE_SEX = ["Control", "-"]
FEMALE = "Female"
ALLOWED_SEQUENCERS = ["HISEQ", "NOVASEQ"]
EXPECTED_BAIT_VERSION = "v1"
ASSAY_NAME = "ACCESS"
PROJECT_NAME = re.compile("^" + ASSAY_NAME + "v[0-9]-[A-Za-z]+-[0-9]{8}.*")
BAIT_SEARCH = re.compile("^" + ASSAY_NAME + "v[0-9]")
MERGED_LANE_VALUE = "0"

SAMPLE_SHEET_REQUIRED_COLUMNS = [
    "Lane",
    "Sample_ID",
    "Sample_Name",
    "I7_Index_ID",
    "index",
    "I5_Index_ID",
    "index2",
    "Description",
    "Control",
    "Operator",
    "Sample_Project",
]

SAMPLE_SHEET_OPTIONAL_COLUMNS = [
    "FCID",
    "Sample_Plate",
    "Sample_Well",
    "Sample_Ref",
    "Control",
    "Recipe",
]

TITLE_FILE__COLUMN_ORDER = [
    TITLE_FILE__BARCODE_ID_COLUMN,
    TITLE_FILE__POOL_COLUMN,
    TITLE_FILE__SAMPLE_ID_COLUMN,
    TITLE_FILE__IGO_ID_COLUMN,
    TITLE_FILE__COLLAB_ID_COLUMN,
    TITLE_FILE__PATIENT_ID_COLUMN,
    TITLE_FILE__SAMPLE_CLASS_COLUMN,
    TITLE_FILE__SAMPLE_TYPE_COLUMN,
    TITLE_FILE__POOL_INPUT_COLUMN,
    TITLE_FILE__BAIT_VERSION_COLUMN,
    TITLE_FILE__SEX_COLUMN,
    TITLE_FILE__PATIENT_NAME_COLUMN,
    TITLE_FILE__ACCESSION_COLUMN,
    TITLE_FILE__BARCODE_INDEX_1_COLUMN,
    TITLE_FILE__BARCODE_INDEX_2_COLUMN,
    TITLE_FILE__RUN_ID_COLUMN,
    TITLE_FILE__LANE_COLUMN,
]

##############################
# Pipeline Kickoff Constants #
##############################

NON_REVERSE_COMPLEMENTED = 0
REVERSE_COMPLEMENTED = 1

# Delimiter for printing logs
DELIMITER = "\n" + "*" * 20 + "\n"
# Delimiter for inputs file sections
INPUTS_FILE_DELIMITER = "\n\n" + "# " + "--" * 30 + "\n\n"

# Template identifier string that will get replaced with the project root location
PIPELINE_ROOT_PLACEHOLDER = "$PIPELINE_ROOT"

BAM_REGEX = re.compile(r".*\.bam$")

SAMPLE_SEP_FASTQ_DELIMETER = "_"
SAMPLE_SEP_DIR_DELIMETER = "/"


##########################
# Constants for QC files #
##########################

# Avoid division by zero errors
EPSILON = 1e-9

# Shorter reference to sample ID column, to be used everywhere
SAMPLE_ID_COLUMN = TITLE_FILE__SAMPLE_ID_COLUMN

# WALTZ Metrics Files Constants

# File suffixes
WALTZ_READ_COUNTS_FILENAME_SUFFIX = ".read-counts"
WALTZ_FRAGMENT_SIZES_FILENAME_SUFFIX = ".fragment-sizes"
WALTZ_INTERVALS_FILENAME_SUFFIX = "-intervals.txt"
WALTZ_INTERVALS_WITHOUT_DUPLICATES_FILENAME_SUFFIX = "-intervals-without-duplicates.txt"

TOTAL_OFF_TARGET_FRACTION_COLUMN = "total_off_target_fraction"

WALTZ_CHROMOSOME_COLUMN = "chromosome"
WALTZ_START_COLUMN = "start"
WALTZ_STOP_COLUMN = "stop"
WALTZ_INTERVAL_NAME_COLUMN = "interval_name"
WALTZ_FRAGMENT_SIZE_COLUMN = "fragment_size"
WALTZ_PEAK_COVERAGE_COLUMN = "peak_coverage"
WALTZ_AVERAGE_COVERAGE_COLUMN = "TotalCoverage"
WALTZ_GC_CONTENT_COLUMN = "gc"

# todo
WALTZ_INTERVALS_FILE_HEADER = [
    WALTZ_CHROMOSOME_COLUMN,
    WALTZ_START_COLUMN,
    WALTZ_STOP_COLUMN,
    WALTZ_INTERVAL_NAME_COLUMN,
    WALTZ_FRAGMENT_SIZE_COLUMN,
    WALTZ_PEAK_COVERAGE_COLUMN,
    WALTZ_AVERAGE_COVERAGE_COLUMN,
    WALTZ_GC_CONTENT_COLUMN,
]

WALTZ_COVERAGE_FILE_HEADER = ["TotalCoverage", "UniqueCoverage"]


# AGBM Metrics Files Constants
#
# Column names
AGBM_COVERAGE_FILENAME = "waltz-coverage.txt"
AGBM_READ_COUNTS_FILENAME = "read-counts.txt"
AGBM_FRAGMENT_SIZES_FILENAME = "fragment-sizes.txt"
AGBM_INTERVALS_COVERAGE_SUM_FILENAME = "intervals_coverage_sum.txt"


# fragment-sizes.txt
FRAGMENT_SIZE_COLUMN = "FragmentSize"
TOTAL_FREQUENCY_COLUMN = "TotalFrequency"
UNIQUE_FREQUENCY_COLUMN = "UniqueFrequency"

# read-counts.txt
TOTAL_MAPPED_COLUMN = "TotalMapped"
UNIQUE_MAPPED_COLUMN = "UniqueMapped"
TOTAL_READS_COLUMN = "TotalReads"
UNMAPPED_READS_COLUMN = "UnmappedReads"
DUPLICATE_FRACTION_COLUMN = "DuplicateFraction"
TOTAL_ON_TARGET_COLUMN = "TotalOnTarget"
UNIQUE_ON_TARGET_COLUMN = "UniqueOnTarget"
TOTAL_ON_TARGET_FRACTION_COLUMN = "TotalOnTargetFraction"
UNIQUE_ON_TARGET_FRACTION_COLUMN = "UniqueOnTargetFraction"

# File Headers
AGBM_READ_COUNTS_HEADER = [
    SAMPLE_ID_COLUMN,
    "bam",
    TOTAL_READS_COLUMN,
    UNMAPPED_READS_COLUMN,
    TOTAL_MAPPED_COLUMN,
    UNIQUE_MAPPED_COLUMN,
    DUPLICATE_FRACTION_COLUMN,
    TOTAL_ON_TARGET_COLUMN,
    UNIQUE_ON_TARGET_COLUMN,
    TOTAL_ON_TARGET_FRACTION_COLUMN,
    UNIQUE_ON_TARGET_FRACTION_COLUMN,
]

AGBM_FRAGMENT_SIZES_FILE_HEADER = [
    SAMPLE_ID_COLUMN,
    FRAGMENT_SIZE_COLUMN,
    TOTAL_FREQUENCY_COLUMN,
    UNIQUE_FREQUENCY_COLUMN,
]

# Chr\tStart\tEnd\tIntervalName\tLength\tGC\tCoverage\tCoverageWithoutDuplicates
# intervals-coverage-sum.txt
CHROMOSOME_COLUMN = "Chr"
START_COLUMN = "Start"
END_COLUMN = "End"
INTERVAL_NAME_COLUMN = "IntervalName"
LENGTH_COLUMN = "Length"
GC_COLUMN = "GC"
COVERAGE_COLUMN = "Coverage"
COVERAGE_WITH_DUPLICATES_COLUMN = "CoverageWithoutDuplicates"

AGBM_INTERVALS_COVERAGE_SUM_FILE_HEADER = [
    SAMPLE_ID_COLUMN,
    CHROMOSOME_COLUMN,
    START_COLUMN,
    END_COLUMN,
    INTERVAL_NAME_COLUMN,
    LENGTH_COLUMN,
    GC_COLUMN,
    COVERAGE_COLUMN,
    COVERAGE_WITH_DUPLICATES_COLUMN,
]

AGBM_TOTAL_AVERAGE_COVERAGE_COLUMN = "TotalCoverage"
AGBM_UNIQUE_AVERAGE_COVERAGE_COLUMN = "UniqueCoverage"

AGBM_COVERAGE_HEADER = [
    SAMPLE_ID_COLUMN,
    AGBM_TOTAL_AVERAGE_COVERAGE_COLUMN,
    AGBM_UNIQUE_AVERAGE_COVERAGE_COLUMN,
]


# TABLES MODULE Files Constants
#
# Labels for collapsing methods
TOTAL_LABEL = "TotalCoverage"
PICARD_LABEL = "Picard Unique"
MAPPED_LABEL = "Mapped"

POOL_A_LABEL = "A Targets"
POOL_B_LABEL = "B Targets"

UNFILTERED_COLLAPSING_METHOD = "All Unique"
SIMPLEX_COLLAPSING_METHOD = "Simplex"
DUPLEX_COLLAPSING_METHOD = "Duplex"
SIMPLEX_DUPLEX_COMBINED = "SimplexDuplex"

# Headers for tables
DUPLICATION_RATES_HEADER = [SAMPLE_ID_COLUMN, "method", "duplication_rate", "pool"]

GC_BIN_COLUMN = "gc_bin"
METHOD_COLUMN = "method"
GC_BIAS_HEADER = [
    SAMPLE_ID_COLUMN,
    "interval_name",
    WALTZ_PEAK_COVERAGE_COLUMN,
    "gc",
    "method",
]
GC_BIAS_AVERAGE_COVERAGE_ALL_SAMPLES_HEADER = [METHOD_COLUMN, GC_BIN_COLUMN, "coverage"]
GC_BIAS_AVERAGE_COVERAGE_EACH_SAMPLE_HEADER = [
    METHOD_COLUMN,
    SAMPLE_ID_COLUMN,
    GC_BIN_COLUMN,
    "coverage",
]

# Output file names
read_counts_filename = "read_counts_agg.txt"
coverage_agg_filename = "coverage_agg.txt"
gc_avg_each_sample_coverage_filename = (
    "GC_bias_with_coverage_averages_over_each_sample.txt"
)
gc_bias_with_coverage_filename = "GC_bias_with_coverage.txt"
read_counts_total_filename = "read_counts_total.txt"
coverage_per_interval_filename = "coverage_per_interval.txt"
read_counts_table_exon_level_filename = "read_counts_agg_exon_level.txt"
coverage_table_exon_level_filename = "coverage_agg_exon_level.txt"
gc_cov_int_table_exon_level_filename = "GC_bias_with_coverage_exon_level.txt"
gc_avg_each_sample_coverage_exon_level_filename = (
    "GC_bias_with_coverage_averages_over_each_sample_exon_level.txt"
)
average_coverage_across_exon_targets_filename = (
    "average_coverage_across_exon_targets_duplex_A.txt"
)

INSERT_SIZE_PREFIX = "insert_sizes_"
INSERT_SIZE_OUTPUT_FILE_NAMES = [
    "standard_A_targets.txt",
    "unfiltered_A_targets.txt",
    "simplex_A_targets.txt",
    "duplex_A_targets.txt",
    "standard_B_targets.txt",
    "unfiltered_B_targets.txt",
    "simplex_B_targets.txt",
    "duplex_B_targets.txt",
]

EXON_COVERAGE_OUTPUT_FILE_NAMES = [
    "coverage_per_interval_A_targets_All_Unique.txt",
    "coverage_per_interval_A_targets_Duplex.txt",
    "coverage_per_interval_A_targets_Simplex.txt",
    "coverage_per_interval_A_targets_TotalCoverage.txt",
]

INSERT_SIZE_OUTPUT_FILE_NAMES = [
    INSERT_SIZE_PREFIX + o for o in INSERT_SIZE_OUTPUT_FILE_NAMES
]

ALL_TABLES_MODULE_OUTPUT_FILES = (
    [
        read_counts_filename,
        coverage_agg_filename,
        gc_avg_each_sample_coverage_filename,
        gc_bias_with_coverage_filename,
        read_counts_total_filename,
        coverage_per_interval_filename,
        read_counts_table_exon_level_filename,
        coverage_table_exon_level_filename,
        gc_cov_int_table_exon_level_filename,
        gc_avg_each_sample_coverage_exon_level_filename,
        average_coverage_across_exon_targets_filename,
    ]
    + EXON_COVERAGE_OUTPUT_FILE_NAMES
    + INSERT_SIZE_OUTPUT_FILE_NAMES
    + ["qc_sample_coverage_A_targets.txt", "qc_sample_coverage_B_targets.txt"]
)


####################
# Constants for VC #
####################

# SampleSheet to TitleFile #
TITLE_FILE_PAIRING_EXPECTED_COLUMNS = ["Sample", "Class", "Patient_ID", "Sample_type"]
TUMOR_ID = "tumor_id"
NORMAL_ID = "normal_id"
SAMPLE_CLASS = "class"
GROUP_BY_ID = "Patient_ID"
SAMPLE_PAIR1 = "Sample_x"
SAMPLE_PAIR2 = "Sample_y"
CLASS_PAIR1 = "Class_x"
CLASS_PAIR2 = "Class_y"
SAMPLE_TYPE_PAIR1 = "Sample_type_x"
SAMPLE_TYPE_PAIR2 = "Sample_type_y"
TUMOR_CLASS = "Tumor"
NORMAL_CLASS = "Normal"
SAMPLE_TYPE_PLASMA = "Plasma"
SAMPLE_TYPE_NORMAL_NONPLASMA = "Buffycoat"
TITLE_FILE_TO_PAIRED_FILE = "Title_file_to_paired.csv"

# Final maf to text #
MAF_COLUMNS_SELECT = [
    "Hugo_Symbol",
    "Chromosome",
    # "Start_Position",
    "VCF_POS",
    "Variant_Classification",
    # "Reference_Allele",
    "VCF_REF",
    # "Tumor_Seq_Allele2",
    "VCF_ALT",
    "dbSNP_RS",
    "Tumor_Sample_Barcode",
    "caller_Norm_Sample_Barcode",
    "HGVSc",
    "HGVSp_Short",
    "Transcript_ID",
    "EXON",
    "INTRON",
    "GMAF",
    "D_t_alt_count_fragment",
    "D_t_ref_count_fragment",
    "D_t_vaf_fragment",
    "SD_t_alt_count_fragment",
    "SD_t_ref_count_fragment",
    "SD_t_vaf_fragment",
    "n_alt_count_fragment",
    "n_ref_count_fragment",
    "n_vaf_fragment",
    "CURATED_SIMPLEX_DUPLEX_median_VAF",
    "CURATED_SIMPLEX_DUPLEX_n_fillout_sample_alt_detect",
    "CURATED_SIMPLEX_DUPLEX_n_fillout_sample",
    "NORMAL_median_VAF",
    "NORMAL_n_fillout_sample_alt_detect",
    "NORMAL_n_fillout_sample",
    "CURATED_DUPLEX_median_VAF",
    "CURATED_DUPLEX_n_fillout_sample_alt_detect",
    "CURATED_DUPLEX_n_fillout_sample",
    "gnomAD_AF",
    "gnomAD_AF_AFR",
    "gnomAD_AF_AMR",
    "gnomAD_AF_ASJ",
    "gnomAD_AF_EAS",
    "gnomAD_AF_FIN",
    "gnomAD_AF_NFE",
    "gnomAD_AF_OTH",
    "gnomAD_AF_SAS",
    "CallMethod",
    "Mutation_Class",
    "Status",
    "Cosmic_ID",
]

MAF_TSV_COL_MAP = OrderedDict(
    [
        ("Tumor_Sample_Barcode", "Sample"),
        ("caller_Norm_Sample_Barcode", "NormalUsed"),
        ("Chromosome", "Chrom"),
        # ("Start_Position", "Start"),
        # ("Reference_Allele", "Ref"),
        # ("Tumor_Seq_Allele2", "Alt"),
        ("VCF_POS", "Start"),
        ("VCF_REF", "Ref"),
        ("VCF_ALT", "Alt"),
        ("Variant_Classification", "VariantClass"),
        ("Hugo_Symbol", "Gene"),
        ("Call_Confidence", "Call_Confidence"),
        ("EXON", "Exon"),
        ("Transcript_ID", "TranscriptID"),
        ("Comments", "Comments"),
        ("HGVSc", "cDNAchange"),
        ("HGVSp_Short", "AAchange"),
        ("dbSNP_RS", "dbSNP_ID"),
        ("Cosmic_ID", "Cosmic_ID"),
        ("GMAF", "1000G_MAF"),
        ("FailureReason", "FailureReason"),
        ("CallMethod", "CallMethod"),
        ("COSMIC_site", "COSMIC_site"),
        ("n_count_fragment", "N_TotalDepth"),
        ("n_ref_count_fragment", "N_RefCount"),
        ("n_alt_count_fragment", "N_AltCount"),
        ("n_vaf_fragment", "N_AltFreq"),
        ("T_TotalDepth", "T_TotalDepth"),
        ("T_RefCount", "T_RefCount"),
        ("T_AltCount", "T_AltCount"),
        ("T_AltFreq", "T_AltFreq"),
        ("T_Ref_Pos", "T_Ref+"),
        ("T_Ref_Neg", "T_Ref-"),
        ("T_Alt_Pos", "T_Alt+"),
        ("T_Alt_Neg", "T_Alt-"),
        ("Strand_Bias", "Strand_Bias"),
        ("NORMAL_n_fillout_sample_alt_detect", "All_N_Aggregate_AlleleDepth"),
        ("NORMAL_median_VAF", "All_N_Median_AlleleFreq"),
        ("SD_t_vaf_fragment_over_n_vaf_fragment", "T_freq/All_N_Freq"),
        ("NORMAL_n_fillout_sample", "Occurence_in_Normals"),
        ("gnomAD_Max_AF", "gnomAD_Max_AF"),
        ("gnomAD_AF", "gnomAD_ALL"),
        ("gnomAD_AF_AFR", "gnomAD_AFR"),
        ("gnomAD_AF_AMR", "gnomAD_AMR"),
        ("gnomAD_AF_ASJ", "gnomAD_ASJ"),
        ("gnomAD_AF_EAS", "gnomAD_EAS"),
        ("gnomAD_AF_FIN", "gnomAD_FIN"),
        ("gnomAD_AF_NFE", "gnomAD_NFE"),
        ("gnomAD_AF_OTH", "gnomAD_OTH"),
        ("gnomAD_AF_SAS", "gnomAD_SAS"),
        ("Mutation_Class", "Mutation_Class"),
        ("Status", "Mutation_Status"),
        ("D_t_count_fragment", "D_T_TotalDepth"),
        ("D_t_ref_count_fragment", "D_T_RefCount"),
        ("D_t_alt_count_fragment", "D_T_AltCount"),
        ("D_t_vaf_fragment", "D_T_AltFreq"),
        ("S_t_count_fragment", "S_T_TotalDepth"),
        ("S_t_ref_count_fragment", "S_T_RefCount"),
        ("S_t_alt_count_fragment", "S_T_AltCount"),
        ("S_t_vaf_fragment", "S_T_AltFreq"),
        ("SD_t_count_fragment", "SD_T_TotalDepth"),
        ("SD_t_ref_count_fragment", "SD_T_RefCount"),
        ("SD_t_alt_count_fragment", "SD_T_AltCount"),
        ("SD_t_vaf_fragment", "SD_T_AltFreq"),
        (
            "CURATED_DUPLEX_n_fillout_sample_alt_detect",
            "D_All_curatedN_Aggregate_AlleleDepth",
        ),
        ("CURATED_DUPLEX_median_VAF", "D_All_curatedN_Median_AlleleFreq"),
        ("CURATED_DUPLEX_n_fillout_sample", "D_Occurrence_in_Curated_Normals"),
        (
            "CURATED_SIMPLEX_DUPLEX_n_fillout_sample_alt_detect",
            "SD_All_curatedN_Aggregate_AlleleDepth",
        ),
        ("CURATED_SIMPLEX_DUPLEX_median_VAF", "SD_All_curatedN_Median_AlleleFreq"),
        ("CURATED_SIMPLEX_DUPLEX_n_fillout_sample", "SD_Occurrence_in_Curated_Normals"),
    ]
)

MAF_DUMMY_COLUMNS = [
    "Call_Confidence",
    "Comments",
    "Strand_Bias",
    "COSMIC_site",
    "FailureReason",
    "T_TotalDepth",
    "T_RefCount",
    "T_AltCount",
    "T_AltFreq",
    "T_Ref_Pos",
    "T_Ref_Neg",
    "T_Alt_Pos",
    "T_Alt_Neg",
]

GNOMAD_COLUMNS = [
    "gnomAD_AF",
    "gnomAD_AF_AFR",
    "gnomAD_AF_AMR",
    "gnomAD_AF_ASJ",
    "gnomAD_AF_EAS",
    "gnomAD_AF_FIN",
    "gnomAD_AF_NFE",
    "gnomAD_AF_OTH",
    "gnomAD_AF_SAS",
]

MAF_DUMMY_COLUMNS2 = [
    "cosmic_ID",
    "cosmic_OCCURENCE",
    "GMAF",
    "Mutation_Class",
    "gnomAD_AF",
    "gnomAD_AF_AFR",
    "gnomAD_AF_AMR",
    "gnomAD_AF_ASJ",
    "gnomAD_AF_EAS",
    "gnomAD_AF_FIN",
    "gnomAD_AF_NFE",
    "gnomAD_AF_OTH",
    "gnomAD_AF_SAS",
    "CURATED_DUPLEX_median_VAF",
    "CURATED_DUPLEX_n_fillout_sample",
    "CURATED_DUPLEX_n_fillout_sample_alt_detect",
    "CURATED_SIMPLEX_DUPLEX_median_VAF",
    "CURATED_SIMPLEX_DUPLEX_n_fillout_sample",
    "CURATED_SIMPLEX_DUPLEX_n_fillout_sample_alt_detect",
]

# Filename variables
EXONIC_FILTERED = "_ExonicFiltered.pre_traceback.txt"
EXONIC_DROPPED = "_ExonicDropped.pre_traceback.txt"
SILENT_FILTERED = "_SilentFiltered.pre_traceback.txt"
SILENT_DROPPED = "_SilentDropped.pre_traceback.txt"
NONPANEL_EXONIC_FILTERED = "_NonPanelExonicFiltered.txt"
NONPANEL_EXONIC_DROPPED = "_NonPanelExonicDropped.txt"
NONPANEL_SILENT_FILTERED = "_NonPanelSilentFiltered.txt"
NONPANEL_SILENT_DROPPED = "_NonPanelSilentDropped.txt"


# Filtering functions and variables
ALLOWED_EXONIC_VARIANT_CLASS = [
    "Frame_Shift_Del",
    "Frame_Shift_Ins",
    "In_Frame_Del",
    "In_Frame_Ins",
    "Missense_Mutation",
    "Nonsense_Mutation",
    "Nonstop_Mutation",
    "Splice_Site",
    "Translation_Start_Site",
]


def IS_EXONIC_CLASS(Gene, VariantClass, Coordinate):
    """
    Determine whether a variant can be considered as exonic
    based on user-defined conditions. Multiple user-defined 
    conditions can be added to the conditional block.
    """
    if any(
        [
            VariantClass in ALLOWED_EXONIC_VARIANT_CLASS,
            Gene == "TERT" and VariantClass == "5'Flank",
        ]
    ):
        return (Gene, VariantClass, Coordinate)
    elif any(
        [
            Gene == "MET"
            and VariantClass == "Intron"
            and Coordinate >= 116411708
            and Coordinate <= 116414935
        ]
    ):
        return (Gene, "Splice_Site", Coordinate)
    else:
        return None


#########
# Noise #
#########

NOISE_HEADER = [
    SAMPLE_ID_COLUMN,
    "GenotypeCount",
    "AltCount",
    "AltPercent",
    "ContributingSites",
    "Method",
]


########################
# Cleanup Outputs Step #
########################

TMPDIR_SEARCH = re.compile(r"(^tmp$|^tmp......$)")
OUT_TMPDIR_SEARCH = re.compile(r"^out_tmpdir......$")
TOIL_LOG = re.compile(r"(^toil_job_[0-9]+.[o|e][0-9]+$)")

STANDARD_BAM_DIR = "standard"
UNFILTERED_BAM_DIR = "unfiltered"
SIMPLEX_BAM_DIR = "simplex"
DUPLEX_BAM_DIR = "duplex"
TRIM_FILES_DIR = "trimming_results"
MARK_DUPLICATES_FILES_DIR = "mark_duplicates_results"
COVERED_INTERVALS_DIR = "covered_intervals_results"

BAM_FILE_REGEX = re.compile(r"\.bam$")
STANDARD_BAM_SEARCH = re.compile(r"^.*_cl_aln_srt_MD_IR_FX_BR.bam$")
UNFILTERED_BAM_SEARCH = re.compile(r"^.*_cl_aln_srt_MD_IR_FX_BR__aln_srt_IR_FX.bam$")
SIMPLEX_BAM_SEARCH = re.compile(
    r"^.*_cl_aln_srt_MD_IR_FX_BR__aln_srt_IR_FX-simplex.bam$"
)
DUPLEX_BAM_SEARCH = re.compile(r"^.*_cl_aln_srt_MD_IR_FX_BR__aln_srt_IR_FX-duplex.bam$")
STANDARD_BAI_SEARCH = re.compile(r"^.*_cl_aln_srt_MD_IR_FX_BR.bai$")
UNFILTERED_BAI_SEARCH = re.compile(r"^.*_cl_aln_srt_MD_IR_FX_BR__aln_srt_IR_FX.bai$")
SIMPLEX_BAI_SEARCH = re.compile(
    r"^.*_cl_aln_srt_MD_IR_FX_BR__aln_srt_IR_FX-simplex.bai$"
)
DUPLEX_BAI_SEARCH = re.compile(r"^.*_cl_aln_srt_MD_IR_FX_BR__aln_srt_IR_FX-duplex.bai$")

TRIM_FILE_SEARCH = re.compile(r"^.*_cl\.stats$")
MARK_DUPLICATES_FILE_SEARCH = re.compile(r"^.*\.md_metrics$")
COVERED_INTERVALS_FILE_SEARCH = re.compile(r"^.*(\.fci\.bed\.srt|\.fci\.list)$")

BAM_DIRS = [STANDARD_BAM_DIR, UNFILTERED_BAM_DIR, SIMPLEX_BAM_DIR, DUPLEX_BAM_DIR]

BAM_SEARCHES = [
    STANDARD_BAM_SEARCH,
    UNFILTERED_BAM_SEARCH,
    SIMPLEX_BAM_SEARCH,
    DUPLEX_BAM_SEARCH,
]
