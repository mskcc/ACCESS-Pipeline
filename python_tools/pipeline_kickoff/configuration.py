#!/usr/bin/env python

######################################
# Pipeline environment configuration #
######################################
import os
import uuid
import errno


class Env(object):
    """
    A base class to represent the key environment variables that are
    used by toil.
    """

    def __init__(self):
        self.__ENV_VARS = ["PATH", "PYTHONPATH"]

    def get_env_vars(self, tmpdir, user_Rlibs, batchsystem, queue="test.q", pe="smp"):
        for x in ["TMPDIR", "TMP_DIR", "TEMP", "TMP"]:
            os.environ[x] = tmpdir
            self.__ENV_VARS.append(x)
        os.environ["_JAVA_OPTIONS"] = "-Djava.io.tmpdir=" + tmpdir
        self.__ENV_VARS.append("_JAVA_OPTIONS")

        if not user_Rlibs:
            os.environ["R_LIBS"] = ""
            self.__ENV_VARS.append("R_LIBS")

        if batchsystem == "gridEngine":
            os.environ["TOIL_GRIDENGINE_ARGS"] = " ".join(["-q", queue])
            os.environ["TOIL_GRIDENGINE_PE"] = pe
            self.__ENV_VARS.append("TOIL_GRIDENGINE_ARGS")
            self.__ENV_VARS.append("TOIL_GRIDENGINE_PE")
        elif batchsystem == "lsf":
            self.__ENV_VARS.append("TOIL_LSF_ARGS")
            # TODO: Add additional logic for lsf

        return " ".join(self.__ENV_VARS)


class ToilArgs(object):
    """
    A base class to represent the toil parameters and the support methods.
    """

    def __init__(self):
        self.__BASE_TOIL_RUNNER = "toil-cwl-runner"
        self.__LOG_DIR = "log"
        self.__LOG_FILE = "cwltoil.log"
        self.__TOIL_TMPDIR = "tmp"

    def set_default_toil_args(self, env_args):
        """
        Adopt environment variables to toil.
        """
        self.__DEFAULT_TOIL_ARGS = {
            "--preserve-environment": env_args,
            "--defaultDisk": "10G",
            "--defaultMem": "10G",
            "--no-container": "",
            "--disableCaching": "",
            "--stats": "",
            "--cleanWorkDir": "onSuccess",
            "--maxLogFileSize": "20000000000",
            "--retryCount": 2,
        }
        return self.__DEFAULT_TOIL_ARGS

    def get_toil_cmd(
        self,
        env_args,
        output_directory,
        batch_system,
        logLevel,
        workflow,
        inputs_file,
        restart,
    ):
        """
        Generate a comprehensive toil command to run a CWL workflow.
        """
        self.__OUTDIR = output_directory
        self.__BATCH_SYSTEM = batch_system
        self.__LOG_LEVEL = logLevel
        self.__TOIL_TMPDIR = os.path.join(self.__OUTDIR, self.__TOIL_TMPDIR)
        self.__LOG_DIR = os.path.join(self.__OUTDIR, self.__LOG_DIR)
        self.__LOG_FILE = os.path.join(self.__LOG_DIR, self.__LOG_FILE)
        self.__JOBSTORE = "file://{}/jobstore-{}".format(
            self.__TOIL_TMPDIR, str(uuid.uuid1())
        )
        if restart:
            job_store_dirs = filter(
                lambda x: x.startswith("jobstore"), os.listdir(self.__TOIL_TMPDIR)
            )
            if len(job_store_dirs) > 1:
                raise Exception(
                    "Multiple jobstore directories exist in {}".format(
                        self.__TOIL_TMPDIR
                    )
                )
            try:
                self.__JOBSTORE = "file://{}/{}".format(
                    self.__TOIL_TMPDIR, job_store_dirs.pop()
                )
            except IndexError:
                raise Exception(
                    "No jobstore directory found in {}".format(self.__TOIL_TMPDIR)
                )
        else:
            if os.path.exists(self.__OUTDIR):
                raise Exception(
                    "The specified output location already exist: {}.".format(
                        self.__OUTDIR
                    )
                )

        self.__TOIL_CMD = " ".join(
            [
                self.__BASE_TOIL_RUNNER,
                "--logFile",
                self.__LOG_FILE,
                "--jobStore",
                self.__JOBSTORE,
                "--batchSystem",
                self.__BATCH_SYSTEM,
                "--workDir",
                self.__TOIL_TMPDIR,
                "--outdir",
                self.__OUTDIR,
                "--writeLogs",
                self.__LOG_DIR,
                "--logLevel=" +
                self.__LOG_LEVEL,
            ]
        )

        # Include Default arguments
        for arg, value in self.set_default_toil_args(env_args).items():
            self.__TOIL_CMD += " {} {}".format(arg, value)

        # Include restart argument
        if restart:
            self.__TOIL_CMD += " --restart "

        # End with the workflow and inputs.yaml file
        self.__TOIL_CMD += " {} {}".format(workflow, inputs_file)

        # Make run directories
        for run_dir in (self.__OUTDIR, self.__LOG_DIR, self.__TOIL_TMPDIR):
            try:
                os.makedirs(run_dir)
            except OSError as e:
                if e.errno != os.errno.EEXIST:
                    print("Exception when creating directory: {}".format(run_dir))
                    raise

        return self.__TOIL_CMD


class GridEngine(object):
    """
    A base class to represent the interface that gridEngine batch
    system must provide to Toil.
    """

    def __init__(self, queue):
        self.__CONTROL_QUEUE = queue
        self.__GRIDENGINE = "/common/sge/bin/lx-amd64/qsub"
        self.__QUEUE_PARAM = "-q"
        self.__TOIL_GRIDENGINE_ARGS = " ".join(
            [self.__QUEUE_PARAM, self.__CONTROL_QUEUE]
        )
        self.__TOIL_GRIDENGINE_PE = "smp"
        self.__PRESERVE_ENV_PARAM = "-V"
        self.__DEFAULT_MEM = 40
        self.__DEFAULT_VMEM = 40
        self.__DEFAULT_CPU = 1
        self.__JOB_NAME_PARAM = "-N"
        self.__WDIR_PARAM = "-wd"
        self.__RESOURCE_PARAM = "-l"
        self.__HVMEM_PARAM = "h_vmem="
        self.__VMEM_PARAM = "virtual_free="
        self.__UNIT = "G"
        self.__PARALLEL_ENV_PARAM = "-pe"
        self.__COMMAND_TYPE_PARAM = "-b y"
        self.__SYNC_PARAM = "-sync y"
        self.__ASSAY = "ACCESS"

    def alter_parellel_env(self, pe):
        """
        Change parallel environment.
        """
        self.__TOIL_GRIDENGINE_PE = pe

    def alter_path(self, path):
        """
        Change path to gridEngine binary.
        """
        self.__GRIDENGINE = path

    def alter_resources(self, mem, vmem, cpu):
        """
        Customize memory and cpu usage.
        """
        self.__DEFAULT_MEM, self.__DEFAULT_VMEM, self.__DEFAULT_CPU = mem, vmem, cpu

    def alter_assay(self, assayname):
        """
        Generic assay label.
        """
        self.__ASSAY = assayname

    def no_sync(self):
        """
        Do not wait for submitted job to complete. Default setting is to wait
        for the submitted job to complete and carry over the exit status.
        """
        self.__SYNC_PARAM = "-sync n"

    def generate_cluster_cmd(self, jobid, wdir):
        """
        Generate a comprehensive gridengine wrapper command.
        """
        return " ".join(
            [
                self.__GRIDENGINE,
                self.__TOIL_GRIDENGINE_ARGS,
                self.__PRESERVE_ENV_PARAM,
                self.__WDIR_PARAM,
                wdir,
                self.__JOB_NAME_PARAM,
                self.__ASSAY + "_pid_" + str(jobid),
                self.__RESOURCE_PARAM,
                self.__HVMEM_PARAM
                + str(self.__DEFAULT_MEM)
                + self.__UNIT
                + ","
                + str(self.__VMEM_PARAM)
                + str(self.__DEFAULT_VMEM)
                + self.__UNIT,
                self.__PARALLEL_ENV_PARAM,
                self.__TOIL_GRIDENGINE_PE,
                str(self.__DEFAULT_CPU),
                self.__COMMAND_TYPE_PARAM,
                self.__SYNC_PARAM,
            ]
        )


class LSF(object):
    """
    A base class to represent the interface that lsf batch
    system must provide to Toil.
    """

    def __init__(self, queue):
        pass
