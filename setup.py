import os
import sys
from setuptools import setup, find_packages
from subprocess import check_output


def req_file(filename):
    """
    We're using a requirements.txt file so that pyup.io can use this for security checks

    :param filename:
    :return:
    """
    with open(filename) as f:
        content = f.readlines()
        content = filter(lambda x: not x.startswith("#"), content)
    return [x.strip() for x in content]


def most_recent_tag():
    """
    Helper function to get the recent tag and commit

    :param :
    :return:
    """
    tag = (
        check_output(["git", "describe", "--tags"])
        .decode("utf-8")
        .strip()
        .split("-")
        .pop(0)
    )
    commit = (
        check_output(
            [
                "git",
                "log",
                "--pretty=oneline",
                "-n",
                "1",
                "--",
                os.path.dirname(os.path.abspath(__file__)),
            ]
        )
        .decode("utf-8")
        .strip()
        .split(" ")
        .pop(0)[:7]
    )
    return "-".join([tag, commit])


ENTRY_POINTS = """
        [console_scripts]
        create_inputs_from_title_file = python_tools.pipeline_kickoff.create_inputs_from_title_file:main
        create_standard_bam_to_collapsed_qc_inputs = python_tools.pipeline_kickoff.create_standard_bam_to_collapsed_qc_inputs:main
        create_title_file_from_manifest = python_tools.pipeline_kickoff.create_title_file_from_manifest:main
        create_title_file_from_samplesheet = python_tools.pipeline_kickoff.create_title_file_from_samplesheet:main
        create_title_file_from_samplesheet_legacy = python_tools.pipeline_kickoff.create_title_file_from_samplesheet_legacy:main
        pipeline_submit = python_tools.pipeline_kickoff.pipeline_submit:main
        pipeline_runner = python_tools.pipeline_kickoff.pipeline_runner:main
        list2bed = python_tools.workflow_tools.list2bed:main
        qc_wrapper = python_tools.workflow_tools.qc.qc_wrapper:main
        tables_module = python_tools.workflow_tools.qc.tables_module:main
        plot_noise = python_tools.workflow_tools.qc.plot_noise:main
        fingerprinting = python_tools.workflow_tools.qc.fingerprinting:main
        combine_qc_pdfs = python_tools.workflow_tools.qc.combine_qc_pdfs:main
        gender_check = python_tools.workflow_tools.qc.gender_check:main
        pipeline_postprocessing = python_tools.workflow_tools.pipeline_postprocessing:main
        test_outputs = python_tools.test.test_pipeline_outputs:main
        """

SUPPORT_SCRIPTS = [
    "python_tools/workflow_tools/qc/r_tools/plots_module.r",
    "python_tools/workflow_tools/qc/r_tools/plots.r",
    "python_tools/workflow_tools/qc/r_tools/util.r",
    "python_tools/workflow_tools/qc/r_tools/constants.r",
    "python_tools/workflow_tools/qc/calculate_noise.sh",
    "python_tools/workflow_tools/qc/make_umi_qc_tables.sh",
    "python_tools/workflow_tools/qc/aggregate_bam_metrics.sh",
]


setup(
    name="access_pipeline",
    version=most_recent_tag(),
    description="MSKCC Center for Molecular Oncology, Innovation Lab, cfDNA sequencing pipeline",
    url="http://github.com/mskcc/ACCESS-Pipeline",
    author="Ian Johnson, Gowtham Jayakumaran",
    author_email="johnsoni@mskcc.org",
    license="MIT",
    install_requires=req_file("requirements.txt"),
    python_requires=">=2.7",
    classifiers=[
        "Topic :: Scientific/Engineering :: Bio-Informatics",
        "Programming Language :: Python :: 2.7",
    ],
    packages=find_packages(exclude=["test"]),
    package_data={"": ["**/*.r", "**/*.R", "**/**/*.r", "**/**/*.R"]},
    include_package_data=True,
    entry_points=ENTRY_POINTS,
    scripts=SUPPORT_SCRIPTS,
    zip_safe=False,
)
