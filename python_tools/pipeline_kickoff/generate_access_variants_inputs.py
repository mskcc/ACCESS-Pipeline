import os
import re
import logging
import time
import subprocess
import argparse
import ruamel.yaml

import pandas as pd

from python_tools.constants import (
    ACCESS_VARIANTS_RUN_FILES_PATH,
    ACCESS_VARIANTS_RUN_PARAMS_PATH,
    ACCESS_VARIANTS_RUN_TOOLS_PATH,
    SAMPLE_SEP_FASTQ_DELIMETER,
    GROUP_BY_ID,
    SAMPLE_PAIR1,
    SAMPLE_PAIR2,
    CLASS_PAIR1,
    CLASS_PAIR2,
    SAMPLE_TYPE_PAIR1,
    SAMPLE_TYPE_PAIR2,
    TUMOR_CLASS,
    NORMAL_CLASS,
    SAMPLE_TYPE_PLASMA,
    SAMPLE_TYPE_NORMAL_NONPLASMA,
    SAMPLE_CLASS,
    TUMOR_ID,
    NORMAL_ID,
    TITLE_FILE_TO_PAIRED_FILE,
    TITLE_FILE_PAIRING_EXPECTED_COLUMNS,
    ACCESS_VARIANTS_RUN_TOOLS_MANTA,
)

from python_tools.util import (
    find_bams_in_directory,
    include_yaml_resources,
    include_version_info,
    create_yaml_file_objects,
    extract_sample_id_from_bam_path,
)


##########
# Pipeline Inputs generation for the ACCESS-Variants pipeline
#
# Todo:
# - better way to ensure proper sort order of samples
# - combine this with create_ scripts
# - singularity
#
# Usage:
#
# generate_access_variants_inputs \
# -pn \
# Variant_Calling_Project \
# -o \
# inputs.yaml \
# -dn /home/patelju1/projects/Juber/HiSeq/5500-FF-new/run-5500-FF/FinalBams/DA-ret-004-pl-T01-IGO-05500-FF-18_bc427_Pool-05500-FF-Tube3-1_L000_mrg_cl_aln_srt_MD_IR_FX_BR.bam \
# -p \
# ./test_pairs.tsv \
# -tb \
# ~/PROJECT_tumor_bams/duplex_bams \
# -nb \
# ~/PROJECT_normal_bams/duplex_bams \
# -sb \
# ~/PROJECT_normal_bams/simplex_bams \
# -cbd \
# ~/ACCESSv1-VAL-20180003_curated_bams \
# -cbs \
# ~/ACCESSv1-VAL-20180003_curated_bams_simplex
# -m


# Regex for finding bam files
BAM_REGEX = re.compile(".*\.bam")
# Delimiter for printing logs
DELIMITER = "\n" + "*" * 20 + "\n"
# Delimiter for inputs file sections
INPUTS_FILE_DELIMITER = "\n\n" + "# " + "--" * 30 + "\n\n"

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%m/%d/%Y %I:%M:%S %p",
    level=logging.DEBUG,
)
logger = logging.getLogger("access_variants_pipeline_kickoff")


def parse_arguments():
    """
    Parse arguments for Variant calling pipeline inputs generation

    :return: argparse.ArgumentParser object
    """
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "-o",
        "--output_file_name",
        help="Filename for yaml file to be used as pipeline inputs",
        required=True,
    )

    parser.add_argument(
        "-pn", "--project_name", help="Project name for this run", required=True
    )

    parser.add_argument(
        "-m",
        "--matched_mode",
        action="store_true",
        help="Create inputs from matched T/N pairs (True), or use default Normal (False)",
        required=False,
    )

    parser.add_argument(
        '-t',
        '--title_file_path',
        help='title file in tsv format',
        required=True
    )

    parser.add_argument(
        "-pb",
        "--pair_by",
        choices=["class", "type"],
        default="class",
        help="pair samples in title file by sample class (Tumor:Normal) or sample type (Plamsa:Buffcoat)",
        required=False,
    )

    parser.add_argument(
        "-p",
        "--pairing_file_path",
        help="tsv file with tumor sample IDs mapped to normal sample IDs",
        required=False,
    )

    parser.add_argument(
        "-dn",
        "--default_normal_path",
        help="Normal used in unmatched mode, or in matched mode if no matching normal found for tumor sample",
        required=True,
    )

    parser.add_argument(
        "-b",
        "--bam_directory",
        help="Directory that contains all tumor and normal bams to be used in variant calling",
        required=True,
    )

    parser.add_argument(
        "-tb",
        "--tumor_bams_directory",
        help="Directory that contains all tumor bams to be used in variant calling",
        required=True,
    )

    parser.add_argument(
        "-nb",
        "--normal_bams_directory",
        help="Directory that contains all normal bams to be used in variant calling and genotyping "
        "(if using matched mode, otherwise only used for genotyping)",
        required=False,
    )

    parser.add_argument(
        "-sb",
        "--simplex_bams_directory",
        help="Directory that contains additional simplex bams to be used for genotyping",
        required=True,
    )

    # Note: For ACCESS, we will often genotype from the same folders of curated bams
    parser.add_argument(
        "-cbd",
        "--curated_bams_duplex_directory",
        help="Directory that contains additional duplex curated bams to be used for genotyping",
        required=True,
    )

    parser.add_argument(
        "-cbs",
        "--curated_bams_simplex_directory",
        help="Directory that contains additional simplex curated bams to be used for genotyping",
        required=True,
    )

    parser.add_argument(
        "-stdb",
        "--standard_bams_directory",
        help="If you would like SV calling, this is the directory that contains standard bams to be paired with the \
            default normal. Note: This argument is to be paired with the ACCESS_Variants.cwl workflow.",
        required=False,
    )

    parser.add_argument(
        "-dstdn",
        "--default_stdnormal_path",
        help="Normal used in unmatched mode for structural variant calling",
        required=False,
    )

    parser.add_argument(
        "-tri",
        "--traceback_mutations_input",
        help="Mutation data for any relevant prior samples",
        required=False,
    )

    parser.add_argument(
        "-trb",
        "--traceback_bam_files",
        help="Bam file paths for any relevant prior samples",
        required=False,
    )

    args = parser.parse_args()
    return args


def generate_pairing_file(args):
    """
    Create T/N pairs from title file

    1. We allow grouping samples by either sample class (Tumor and Normal, Default) or sample type (Plasma and Buffycoat)
    2. Samples are paired based on common GROUP_BY_ID column in the title file

    :param title_file:
    :param pair_by: str
    :return paired_df: dict
    """
    tf = pd.read_csv(args.title_file_path, sep="\t", comment="#", header="infer")
    tfmerged = pd.merge(tf, tf, on=GROUP_BY_ID, how="left")
    try:
        tfmerged = tfmerged[
            [
                SAMPLE_PAIR1,
                SAMPLE_PAIR2,
                GROUP_BY_ID,
                CLASS_PAIR1,
                CLASS_PAIR2,
                SAMPLE_TYPE_PAIR1,
                SAMPLE_TYPE_PAIR2,
            ]
        ]
        # tfmerged = tfmerged.loc[(tfmerged[SAMPLE_PAIR1] != tfmerged[SAMPLE_PAIR2]) & (~tfmerged[CLASS_PAIR2].isin([TUMOR_CLASS]))]
    except KeyError:
        raise Exception(
            "Missing or unexpected column headers in {}. Title File should contain the following columns for successful pairing: {}".format(
                args.title_file_path, ", ".join(TITLE_FILE_PAIRING_EXPECTED_COLUMNS)
            )
        )
    if args.pair_by == SAMPLE_CLASS:
        paired = tfmerged[
            (tfmerged[CLASS_PAIR1] == TUMOR_CLASS)
            & (tfmerged[CLASS_PAIR2] == NORMAL_CLASS)
        ][[SAMPLE_PAIR1, SAMPLE_PAIR2, GROUP_BY_ID]]
        unpaired = tfmerged[
            (tfmerged[CLASS_PAIR1] == TUMOR_CLASS)
            & (~tfmerged[SAMPLE_PAIR1].isin(paired[SAMPLE_PAIR1].unique().tolist()))
        ][[SAMPLE_PAIR1, SAMPLE_PAIR2, GROUP_BY_ID]]
    else:
        paired = tfmerged[
            (tfmerged[SAMPLE_TYPE_PAIR1] == SAMPLE_TYPE_PLASMA)
            & (tfmerged[SAMPLE_TYPE_PAIR2] == SAMPLE_TYPE_NORMAL_NONPLASMA)
        ][[SAMPLE_PAIR1, SAMPLE_PAIR2, GROUP_BY_ID]]
        unpaired = tfmerged[
            (tfmerged[SAMPLE_TYPE_PAIR1] == SAMPLE_TYPE_PLASMA)
            & (~tfmerged[SAMPLE_PAIR1].isin(paired[SAMPLE_PAIR1].unique().tolist()))
        ][[SAMPLE_PAIR1, SAMPLE_PAIR2, GROUP_BY_ID]]
    unpaired[SAMPLE_PAIR2] = ""
    paired_df = pd.concat([paired, unpaired]).rename(
        index=str,
        columns={
            SAMPLE_PAIR1: TUMOR_ID,
            SAMPLE_PAIR2: NORMAL_ID,
            GROUP_BY_ID: GROUP_BY_ID,
        },
    )
    paired_df.to_csv(
        os.path.join(os.getcwd(), TITLE_FILE_TO_PAIRED_FILE),
        sep="\t",
        header=True,
        mode="w",
        index=False,
    )
    args.pairing_file_path = os.path.join(os.getcwd(), TITLE_FILE_TO_PAIRED_FILE)
    print(
        "Tumor - Normal pairing inferred from the title file. Pairing information is reported here: {}".format(
            os.path.join(os.getcwd(), TITLE_FILE_TO_PAIRED_FILE)
        )
    )
    return paired_df


def validate_pairing_file(pairing_file, tumor_samples, normal_samples):
    """
    Validate T/N pairs

    1. We allow normal_id to be blank in pairing file
    2. If normal_id is not blank, and id is not found in `normal_samples`, raise error
    3. Tumor ID can never be blank
    4. Tumor ID must be found in tumor_samples
    5. If both are found, continue

    :param pairing_file:
    :param tumor_samples: str[] of tumor bam files paths
    :param normal_samples: str[] of normal bam files paths
    :return:
    """
    for i, tn_pair in pairing_file.iterrows():
        tumor_id = tn_pair[TUMOR_ID]
        normal_id = tn_pair[NORMAL_ID]
        assert tumor_id, "Missing tumor sample ID in pairing file"

        # Find the path to the bam that contains this tumor sample ID
        tumor_sample = filter(
            lambda t: os.path.basename(t).startswith(
                tumor_id + SAMPLE_SEP_FASTQ_DELIMETER
            ),
            tumor_samples,
        )
        assert (
            len(tumor_sample) == 1
        ), "Incorrect # of matches for tumor sample {}".format(tumor_id)

        if normal_id and normal_id != "":
            normal_sample = filter(
                lambda n: normal_id + SAMPLE_SEP_FASTQ_DELIMETER in n, normal_samples
            )
            assert (
                len(normal_sample) == 1
            ), "Incorrect # of matches ({}) for paired normal for tumor sample {}".format(
                len(normal_sample), tumor_sample
            )


def parse_tumor_normal_pairing(
    pairing_file, tumor_samples, normal_samples, default_normal_path
):
    """
    Build tumor-normal pairs from pairing file and tumor / normal bam directories.

    Default to `default_normal_path` if matched normal not found.

    :param path:
    :return:
    """
    ordered_tumor_samples = []
    ordered_normal_samples = []
    ordered_fillout_samples = []
    # This flag will prevent us from trying to genotype the default normal more than once
    default_added_for_genotyping = False

    for i, tn_pair in pairing_file.iterrows():
        tumor_id = tn_pair["tumor_id"]
        normal_id = tn_pair["normal_id"]

        # Find the path to the bam that contains this tumor sample ID
        # (after pairing file validation this should return exactly 1 result)
        tumor_sample = filter(
            lambda t: os.path.basename(t).startswith(
                tumor_id + SAMPLE_SEP_FASTQ_DELIMETER
            ),
            tumor_samples,
        )
        assert (
            len(tumor_sample) == 1
        ), "Incorrect # of matches (matched = {}) for sammple ID {} in tumor_samples list.".format(
            str(len(tumor_sample)), tumor_id
        )
        tumor_sample = tumor_sample.pop()

        # Leaving the normal ID blank will cause the default normal to be used
        # Only tumor is used for genotyping
        if normal_id == "":
            ordered_tumor_samples.append(tumor_sample)
            ordered_normal_samples.append(default_normal_path)
            ordered_fillout_samples.append(tumor_sample)
            default_added_for_genotyping = True

            # if not default_added_for_genotyping:
            #     ordered_fillout_samples.append(default_normal_path)
            #     default_added_for_genotyping = True

        # Use the matching normal bam that contains this normal sample ID
        # Both samples are added for genotyping
        # TODO: make this else statement more specific
        elif any(normal_id in n for n in normal_samples):
            # matching_normal_samples = filter(lambda n: normal_id in n, normal_samples)
            matching_normal_sample = filter(
                lambda t: os.path.basename(t).startswith(
                    normal_id + SAMPLE_SEP_FASTQ_DELIMETER
                ),
                normal_samples,
            )
            assert (
                len(matching_normal_sample) == 1
            ), "Incorrect # of matches (matched = {}) for sammple ID {} in tumor_samples list.".format(
                str(len(matching_normal_sample)), normal_id
            )

            # if len(matching_normal_samples) > 1:
            # If we have multiple matches for this normal sample ID, make sure that they are exactly the same,
            # to avoid the following case: Sample_1 != Sample_1A
            # assert all([all([x == y for x in matching_normal_samples]) for y in matching_normal_samples])

            normal_sample = matching_normal_sample.pop()
            ordered_tumor_samples.append(tumor_sample)
            ordered_normal_samples.append(normal_sample)
            ordered_fillout_samples.append(tumor_sample)
            # Only genotype each normal once, even if it is paired with multiple tumors
            if not normal_sample in ordered_fillout_samples:
                ordered_fillout_samples.append(normal_sample)

    if default_added_for_genotyping:
        ordered_fillout_samples.append(default_normal_path)

    return ordered_tumor_samples, ordered_normal_samples, ordered_fillout_samples


def create_inputs_file(args):
    """
    Create the inputs.yaml file for the ACCESS Variant calling pipeline (modules 3 + 4)

    :param args: argparse.ArgumentParser object
    """
    validate_args(args)
    if args.pairing_file_path:
        pairing_df = pd.read_csv(
            args.pairing_file_path, sep="\t", comment="#", header="infer"
        ).fillna("")
    else:
        try:
            pairing_df = generate_pairing_file(args)
        except (KeyError, ValueError, IndexError):
            raise Exception(
                "Cannot create Tumor Normal pairing file from {}".format(
                    args.title_file_path
                )
            )

    tumor_ids, normal_ids, patient_ids = (
        filter(None, pairing_df[TUMOR_ID].tolist()),
        filter(None, pairing_df[NORMAL_ID].tolist()),
        filter(None, pairing_df[GROUP_BY_ID].tolist()),
    )
    tumor_bam_paths = find_bams_in_directory(args.tumor_bams_directory, tumor_ids)
    simplex_bam_paths = find_bams_in_directory(
        args.simplex_bams_directory, tumor_ids
    )
    curated_bam_duplex_paths = find_bams_in_directory(
        args.curated_bams_duplex_directory
    )
    curated_bam_simplex_paths = find_bams_in_directory(
        args.curated_bams_simplex_directory
    )

    # Normal bams paths are either from the bams directory, or repeating the default normal
    # Todo: remove! this logic should be based on the args.matched_mode param
    if args.normal_bams_directory:
        normal_bam_paths = find_bams_in_directory(
            args.normal_bams_directory, normal_ids
        )
    else:
        normal_bam_paths = [args.default_normal_path] * len(tumor_bam_paths)

    fh = open(args.output_file_name, "w")
    write_yaml_bams(
        fh,
        args,
        # tumor_ids,
        # normal_ids,
        patient_ids,
        tumor_bam_paths,
        normal_bam_paths,
        simplex_bam_paths,
        curated_bam_duplex_paths,
        curated_bam_simplex_paths,
    )

    map(
        include_yaml_resources,
        [fh] * 3,
        [
            ACCESS_VARIANTS_RUN_FILES_PATH,
            ACCESS_VARIANTS_RUN_PARAMS_PATH,
            ACCESS_VARIANTS_RUN_TOOLS_PATH,
        ],
    )
    # include_yaml_resources(fh, ACCESS_VARIANTS_RUN_FILES_PATH)
    # include_yaml_resources(fh, ACCESS_VARIANTS_RUN_PARAMS_PATH)
    # include_yaml_resources(fh, ACCESS_VARIANTS_RUN_TOOLS_PATH)

    if args.standard_bams_directory:
        include_sv_inputs(args, tumor_ids, fh)

    fh.write(INPUTS_FILE_DELIMITER)

    create_traceback_inputs(args, fh)

    fh.write('project_name: {}'.format(args.project_name))


    ####### Generate inputs for CNV ########
    cmd = "generate_copynumber_inputs -t {title_file} -tb {bam_dir} -o {output_dir}/inputs_cnv.yaml -od {output_dir}".format(
        title_file=args.title_file_path, 
        bam_dir=args.normal_bams_directory, 
        output_dir=os.path.dirname(args.output_file_name)
    )
    process = subprocess.Popen(cmd, shell=True, close_fds=True)
    process.wait()
    returncode = process.returncode
    if returncode == 0:
        time.sleep(3)
        cnv_yaml = os.path.join(os.path.dirname(args.output_file_name), "inputs_cnv.yaml")
        map(include_yaml_resources, [fh], [cnv_yaml])
    else:
        raise Exception("Unable to generate inputs yaml for cnv")
    ####### End of Generating inputs for CNV ########


    include_version_info(fh)

    fh.write("title_file: {{class: File, path: {}}}\n".format(args.title_file_path))
    fh.write("project_name: {}\n".format(args.project_name))
    include_version_info(fh)
    fh.close()


def create_traceback_inputs(args, fh):
    Traceback_status = (
        True if args.traceback_mutations_input and args.traceback_bam_files else False
    )
    Traceback_inputs = args.traceback_mutations_input
    Traceback_bams = args.traceback_bam_files
    fh.write("Traceback: " + str(Traceback_status) + "\n")
    fh.write("Traceback_inputs: " + str(Traceback_inputs) + "\n")
    fh.write("Traceback_bams: " + str(Traceback_bams) + "\n")
    fh.write(INPUTS_FILE_DELIMITER)


def write_yaml_bams(
    fh,
    args,
    # tumor_ids,
    # normal_ids,
    patient_ids,
    tumor_bam_paths,
    normal_bam_paths,
    simplex_bam_paths,
    curated_bam_duplex_paths,
    curated_bam_simplex_paths,
):
    """
    Write the lists of tumor, normal, and genotyping bams to the inputs file, along with their sample IDs
    Todo: clean this up a bit

    :param fh: inputs file file handle
    :param args: argparse.ArgumentParser object with bam directory attribute
    :return:
    """

    # 1. Build lists of bams
    if args.pairing_file_path:
        pairing_file = pd.read_csv(
            args.pairing_file_path, sep="\t", comment="#", header="infer"
        ).fillna("")
        validate_pairing_file(pairing_file, tumor_bam_paths, normal_bam_paths)

        ordered_tumor_bams, ordered_normal_bams, ordered_tn_genotyping_bams = parse_tumor_normal_pairing(
            pairing_file, tumor_bam_paths, normal_bam_paths, args.default_normal_path
        )

        if not args.matched_mode:
            # If we aren't in matched mode, do variant calling with default normal
            # (pairing file is only used for genotyping)
            ordered_normal_bams = [args.default_normal_path] * len(tumor_bam_paths)
            # Todo: Need to genotype default normal?
            # ordered_tn_genotyping_bams = ordered_tn_genotyping_bams + [args.default_normal_path]

        matched_normal_ids = [n for n in pairing_file["normal_id"]]
        matched_normal_ids = [
            correct_sample_id(n, normal_bam_paths) if n else ""
            for n in matched_normal_ids
        ]
    else:
        # In unmatched mode, the sample pairing is much simpler (just use the supplied default normal)
        ordered_tumor_bams = tumor_bam_paths
        ordered_normal_bams = [args.default_normal_path] * len(tumor_bam_paths)
        # Only add the default normal once
        ordered_tn_genotyping_bams = ordered_tumor_bams + [args.default_normal_path]
        matched_normal_ids = [""] * len(ordered_tumor_bams)

    # 2. Build lists of Sample IDs
    if args.matched_mode:
        # Use pairing file in matched mode
        tumor_sample_ids = [
            correct_sample_id(t, ordered_tumor_bams) for t in pairing_file["tumor_id"]
        ]
        normal_sample_ids = [
            n if n else extract_sample_id_from_bam_path(args.default_normal_path)
            for n in pairing_file["normal_id"]
        ]
    elif args.pairing_file_path:
        # Use pairing file in matched mode
        tumor_sample_ids = [
            correct_sample_id(t, ordered_tumor_bams) for t in pairing_file["tumor_id"]
        ]
        normal_sample_ids = [
            extract_sample_id_from_bam_path(args.default_normal_path)
        ] * len(tumor_sample_ids)
    else:
        # Otherwise use default normal
        tumor_sample_ids = [extract_sample_id_from_bam_path(b) for b in tumor_bam_paths]
        normal_sample_ids = [
            extract_sample_id_from_bam_path(args.default_normal_path)
        ] * len(tumor_sample_ids)

    # 3. Convert bam paths to CWL File objects
    tumor_bams, normal_bams, tn_genotyping_bams, simplex_genotyping_bams, curated_duplex_genotyping_bams, curated_simplex_genotyping_bams = map(
        create_yaml_file_objects,
        [
            ordered_tumor_bams,
            ordered_normal_bams,
            ordered_tn_genotyping_bams,
            simplex_bam_paths,
            curated_bam_duplex_paths,
            curated_bam_simplex_paths,
        ],
    )

    # 4. Genotyping sample IDs must be extracted from the bams themselves
    merged_tn_sample_ids = [
        extract_sample_id_from_bam_path(b["path"]) for b in tn_genotyping_bams
    ]
    simplex_genotyping_ids = [
        extract_sample_id_from_bam_path(b["path"]) + "-SIMPLEX"
        for b in simplex_genotyping_bams
    ]
    curated_duplex_genotyping_ids = [
        extract_sample_id_from_bam_path(b["path"]) + "-CURATED-DUPLEX"
        for b in curated_duplex_genotyping_bams
    ]
    curated_simplex_genotyping_ids = [
        extract_sample_id_from_bam_path(b["path"]) + "-CURATED-SIMPLEX"
        for b in curated_simplex_genotyping_bams
    ]

    genotyping_bams = (
        tn_genotyping_bams
        + simplex_genotyping_bams
        + curated_duplex_genotyping_bams
        + curated_simplex_genotyping_bams
    )
    genotyping_bams_ids = (
        merged_tn_sample_ids
        + simplex_genotyping_ids
        + curated_duplex_genotyping_ids
        + curated_simplex_genotyping_ids
    )

    genotyping_bams_ids = {"genotyping_bams_ids": genotyping_bams_ids}
    tumor_bam_paths = {"tumor_bams": tumor_bams}
    normal_bam_paths = {"normal_bams": normal_bams}
    tumor_sample_ids = {"tumor_sample_names": tumor_sample_ids}
    normal_sample_ids = {"normal_sample_names": normal_sample_ids}
    matched_normal_ids = {"matched_normal_ids": matched_normal_ids}
    patient_ids = {"patient_ids": patient_ids}
    genotyping_bams_paths = {"genotyping_bams": genotyping_bams}

    # 5. Write them to the inputs yaml file
    fh.write(ruamel.yaml.dump(tumor_bam_paths))
    fh.write(ruamel.yaml.dump(normal_bam_paths))
    fh.write(ruamel.yaml.dump(tumor_sample_ids))
    fh.write(ruamel.yaml.dump(normal_sample_ids))
    fh.write(ruamel.yaml.dump(matched_normal_ids))
    fh.write(ruamel.yaml.dump(patient_ids))
    fh.write(ruamel.yaml.dump(genotyping_bams_paths))
    fh.write(ruamel.yaml.dump(genotyping_bams_ids))


def correct_sample_id(query_sample_id, bam_paths):
    """
    Compare `query_sample_id` to each element in bam_paths, and extract the actual sample ID from that bam's path

    :param query_sample_id: str - sample ID to be found in exactly one entry from `bam_paths`
    :param bam_paths: str[] - bam file paths to search through
    :return:
    """
    matches = filter(
        lambda b: os.path.basename(b).startswith(
            query_sample_id + SAMPLE_SEP_FASTQ_DELIMETER
        ),
        bam_paths,
    )
    assert len(matches) == 1, "Incorrect # of matches for sample ID {}".format(
        query_sample_id
    )

    matching_bam_path = matches.pop()
    return extract_sample_id_from_bam_path(matching_bam_path)


def validate_args(args):
    """Arguments sanity check"""

    # Either one of title file or pairing file is required for this process
    if not (args.title_file_path):
        raise Exception('--title_file_path is required for CNV')

    if not (args.title_file_path or args.pairing_file_path):
        raise Exception(
            "Either --title_file_path or --pairing_file_path is required to determine tumor samples for variant calling."
        )

    # Pairing file is required in matched mode
    if args.matched_mode and args.pairing_file_path is None:
        raise Exception("--matched_mode requires --pairing_file_path")

    # Normal bams folder is required in matched mode
    if args.matched_mode and args.normal_bams_directory is None:
        raise Exception("--matched_mode requires --normal_bams_directory")

    # If structural varint calling is enabled, a control standard bam is required, for unmatched variant calling.
    if args.standard_bams_directory and not args.default_stdnormal_path:
        raise Exception(
            "--default_stdnormal_path should be also provided when --standard_bams_directory is defined."
        )


def include_sv_inputs(args, tumor_ids, fh):
    """
    Write standard_bams files to inputs file, as well as SV parameters and tool paths from SV config files

    :param args: argparse.ArgumentsParser with parsed args
    :param fh: file handle for inputs file to write to
    :return:
    """

    standard_bams = find_bams_in_directory(args.standard_bams_directory, tumor_ids)
    standard_bams_yaml = create_yaml_file_objects(standard_bams)
    default_normal_yaml = {"class": "File", "path": args.default_stdnormal_path}
    sv_sample_id = [extract_sample_id_from_bam_path(b) for b in standard_bams]

    fh.write(INPUTS_FILE_DELIMITER)
    fh.write(ruamel.yaml.dump({"sv_sample_id": sv_sample_id}))
    fh.write(ruamel.yaml.dump({"sv_tumor_bams": standard_bams_yaml}))
    fh.write(ruamel.yaml.dump({"sv_normal_bam": default_normal_yaml}))

    include_yaml_resources(fh, ACCESS_VARIANTS_RUN_TOOLS_MANTA)


def main():
    """ Main """
    args = parse_arguments()
    create_inputs_file(args)


if __name__ == "__main__":
    main()
