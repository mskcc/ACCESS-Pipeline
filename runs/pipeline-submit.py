import os
import uuid
import argparse
import subprocess


##
# This is a script to submit the leader toil-cwl-runner job to
# one of the worker nodes instead of the head node.
# It gets called from scripts such as run-example.sh, or run-DY.sh

##
# Todo: This script relies on bsub
# We would like it to work across batch systems.
# Use pipeline-runner.sh to use other batch systems,
# which runs the leader job on the head node.

# Todo: Move to project root


def bsub(bsubline):
    '''
    Execute lsf bsub

    :param bsubline:
    :return:
    '''
    process = subprocess.Popen(bsubline, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    output = process.stdout.readline()

    # fixme: need better exception handling
    print output
    lsf_job_id = int(output.strip().split()[1].strip('<>'))

    return lsf_job_id


def submit_to_lsf(job_store_uuid, project_name, output_location, inputs_file, workflow, batch_system):
    '''
    Submit roslin-runner to the w node

    :param job_store_uuid:
    :param project_name:
    :param output_location:
    :param inputs_file:
    :param workflow:
    :param batch_system:
    :return:
    '''
    mem = 1
    cpu = 1
    leader_node = "w01"
    queue_name = "control"

    lsf_proj_name = "{}:{}".format(project_name, job_store_uuid)
    job_desc = lsf_proj_name

    cwd = os.path.dirname(__file__)
    pipeline_runner_script = os.path.join(cwd, '../pipeline-runner.sh')

    job_command = "{} {} {} {} {} {} {}".format(
        pipeline_runner_script,
        project_name,
        workflow,
        inputs_file,
        output_location,
        batch_system,
        job_store_uuid
    )

    bsubline = [
        "bsub",
        "-R", "select[hname={}]".format(leader_node),
        "-q", queue_name,
        "-R", "rusage[mem={}]".format(mem),
        "-n", str(cpu),
        "-P", lsf_proj_name,
        "-J", project_name,
        "-Jd", job_desc,
        "-cwd", '.',
        "-oo", "stdout.log",
        "-eo", "stderr.log",
        job_command
    ]

    lsf_job_id = bsub(bsubline)

    return lsf_proj_name, lsf_job_id


def main():
    "main function"

    parser = argparse.ArgumentParser(description='submit')

    parser.add_argument(
        "--project_name",
        action="store",
        dest="project_name",
        help="Name for Project (e.g. pipeline_test)",
        required=True
    )

    parser.add_argument(
        "--output_location",
        action="store",
        dest="output_location",
        help="Path to CMO Project outputs location (e.g. /ifs/work/bergerm1/Innovation/sandbox/ian",
        required=True
    )

    parser.add_argument(
        "--inputs_file",
        action="store",
        dest="inputs_file",
        help="CWL Inputs file (e.g. inputs.yaml)",
        required=True
    )

    parser.add_argument(
        "--workflow",
        action="store",
        dest="workflow",
        help="Workflow .cwl Tool file (e.g. innovation_pipeline.cwl)",
        required=False
    )

    parser.add_argument(
        "--batch_system",
        action="store",
        dest="batch_system",
        help="(e.g. lsf or singleMachine)"
    )

    params = parser.parse_args()

    # Create job-uuid
    job_store_uuid = str(uuid.uuid1())

    # submit
    lsf_proj_name, lsf_job_id = submit_to_lsf(
        job_store_uuid,
        params.project_name,
        params.output_location,
        params.inputs_file,
        params.workflow,
        params.batch_system
    )

    print lsf_proj_name
    print lsf_job_id



if __name__ == "__main__":

    main()
