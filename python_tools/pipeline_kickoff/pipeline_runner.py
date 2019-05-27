import os
import sys
import shutil
import uuid
import argparse
import subprocess
import ruamel.yaml
from tempfile import mkdtemp

import version
from configuration import *

# This script is used to run workflows from the command line using toil-cwl-runner.
#
# It is a simple wrapper that creates the output directory structure,
# and provides some default values for Toil params.
#
# It does not submit jobs to worker nodes,
# as opposed to pipeline_submit, which uses bsub.
#
# Optional, potentially useful Toil arguments:
#    --realTimeLogging \
#    --rotateLogging \
#    --js-console
# Todo: in 3.15 this argument no longer works. Might have been changed to --dontLinkImports
#    --linkImports \
#    --clusterStats FILEPATH \
#    --stats \


def parse_arguments():
    """
    Argparse wrapper

    Many of these arguments are simply passed through to the Toil runner
    :return:
    """
    parser = argparse.ArgumentParser(description="submit toil job")

    parser.add_argument(
        "--output_location",
        action="store",
        dest="output_location",
        help="Path to Project outputs location",
        required=True,
    )

    parser.add_argument(
        "--inputs_file",
        action="store",
        dest="inputs_file",
        help="CWL Inputs file (e.g. inputs.yaml)",
        required=True,
    )

    parser.add_argument(
        "--workflow",
        action="store",
        dest="workflow",
        help="Workflow .cwl Tool file (e.g. innovation_pipeline.cwl)",
        required=True,
    )

    parser.add_argument(
        "--batch_system",
        action="store",
        dest="batch_system",
        choices=["singleMachine", "gridEngine"],
        default="gridEngine",
        help="e.g. lsf, sge or singleMachine",
        required=False,
    )

    parser.add_argument(
        "--user_Rlibs",
        action="store_true",
        dest="user_Rlibs",
        help="set if environment variable R_LIBS is defined and to be used \
                in addition to the R site library",
        required=False,
    )

    parser.add_argument(
        "--restart",
        action="store_true",
        dest="restart",
        help="include this if we are restarting from an existing output directory",
        required=False,
    )

    parser.add_argument(
        "--logLevel",
        action="store",
        dest="logLevel",
        default="INFO",
        help="INFO will just log the cwl filenames, DEBUG will include the actual commands being run (default is INFO)",
        required=False,
    )

    parser.add_argument(
        "--project_name",
        action="store",
        dest="project_name",
        help="Name for the processed data directory",
        required=False,
    )

    parser.add_argument(
        "--include_version",
        action="store_true",
        dest="include_version",
        help="Include pipeline git version in the project directory name",
        required=False,
    )

    parser.add_argument(
        "--queue",
        action="store",
        dest="queue",
        default="test.q",
        help="Name of the queue to which gridEngine or lsf jobs or submitted. Default: test.q",
        required=False,
    )

    return parser.parse_known_args()


def get_input_params(args):
    """
    get the parameters from inputs_yaml
    
    :param file:
    :return:
    """
    with open(args.inputs_file, "r") as stream:
        inputs_yaml = ruamel.yaml.round_trip_load(stream)

    if args.project_name:
        project_name = args.project_name
    else:
        try:
            project_name = inputs_yaml["project_name"]
        except KeyError:
            raise Exception("project_name not defined in the inputs yaml file.")

    if args.include_version:
        try:
            pipeline_version = inputs_yaml["version"]
        except KeyError:
            raise Exception("pipeline_version not defined in the inputs yaml file.")
        project_name = "-".join([project_name, pipeline_version])

    try:
        tmpdir = inputs_yaml["tmp_dir"]
        os.path.exists(tmpdir)        
    except KeyError:
        raise Exception("The variable tmp_dir is not defined in the inputs yaml file.")
    except OSError:
        raise

    return tmpdir, project_name


def run_toil(args, tmpdir, project):
    """
    Inherit from base classes, set variables and submit toil process.
    """
    project_env = Env()

    try:
        tmpdir = mkdtemp(
            prefix=project + "_", suffix="_" + str(os.getpid()), dir=tmpdir
        )
    except OSError:
        raise Exception("Cannot create temp directory {}".format(tmpdir))

    output_directory = os.path.join(args.output_location, project)

    toil = ToilArgs()
    toil_cmd = toil.get_toil_cmd(
        project_env.get_env_vars(tmpdir, args.user_Rlibs, args.batch_system),
        output_directory,
        args.batch_system,
        args.logLevel,
        args.workflow,
        args.inputs_file,
        args.restart)
        
    if not args.batch_system == "singleMachine":
        if args.batch_system == "gridEngine":
            cluster = GridEngine(args.queue)
        elif args.batch_system == "lsf":
            cluster = LSF(args.queue)
        cluster_cmd = cluster.generate_cluster_cmd(os.getpid(), output_directory)
    else:
        cluster_cmd = ""

    try:
        run_cmd = " ".join(filter(lambda x: x, (cluster_cmd , toil_cmd)))
        print("\nRunning job with command: {}\n".format(run_cmd))
        subprocess.check_call(run_cmd, shell=True)
    except subprocess.CalledProcessError:
        raise
    finally:
        shutil.rmtree(tmpdir)


def set_temp_dir_env_vars(tmpdir):
    """
    Set environment variables for temporary directories
    Try to cover all possibilities for every tool

    :param tmpdir:
    :return:
    """
    os.environ['TMPDIR'] = tmpdir
    os.environ['TMP_DIR'] = tmpdir
    os.environ['TEMP'] = tmpdir
    os.environ['TMP'] = tmpdir
    os.environ['_JAVA_OPTIONS'] = '-Djava.io.tmpdir=' + tmpdir


########
# Main #
########
def main():
    args, unknowns = parse_arguments()
    tmpdir, project = get_input_params(args)
    run_toil(args, tmpdir, project)


if __name__ == "__main__":
    main()
