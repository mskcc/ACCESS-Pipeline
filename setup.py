import os
from setuptools import setup, Command


class CleanCommand(Command):
    """
    Custom clean command to tidy up the project root
    """
    user_options = []

    def initialize_options(self):
        pass
    def finalize_options(self):
        pass
    def run(self):
        os.system('rm -vrf ./build ./dist ./*.pyc ./*.tgz ./*.egg-info')


setup(
    name='innovation-pipeline-tools',
    version='0.0.0',
    description='MSKCC Center for Molecular Oncology, Innovation Lab, cfDNA sequencing pipeline',
    url='http://github.com/mskcc/Innovation-Pipeline',
    author='Ian Johnson',
    author_email='johnsoni@mskcc.org',
    licence='MIT',
    install_requires=[
        'argparse',
        'toil[cwl]',
        # These dependencies may need to be explicitly specified,
        # if PyPi gives us ResourceConflict issues
        # 'cwltool==3.15.0',
        # 'cwltest==1.0.20180209171722',
        # 'cwltest==1.0.20180129111038',
        # 'cwltool==1.0.20180403145700',
        'pandas==0.19.0',
        'xlrd==1.1.0',
        'numpy==1.14.2',
        'pybedtools',
        'PyPDF2==1.26.0',
        'matplotlib==2.2.2'
    ],
    # These links are for referencing a particular commit / branch of Toil
    dependency_links=[
        'git@github.com:BD2KGenomics/toil.git@toilpy23',
        # 'http://github.com/BD2KGenomics/toil/tarball/cwl_safe_followon'
        # 'git+ssh://git@github.com/ionox0/toil.git#egg=toil-0.0.7'
    ],
    packages = ['python_tools', 'python_tools.pipeline_kickoff', 'python_tools.workflow_tools', 'python_tools.workflow_tools.qc'],
    package_data = {'': ['**/*.r', '**/*.R', '**/**/*.r', '**/**/*.R']},
    entry_points = {
        'console_scripts': [
            # Pipeline Kickoff
            'create_inputs_from_title_file = python_tools.pipeline_kickoff.create_inputs_from_title_file:main',
            'create_title_file_from_manifest = python_tools.pipeline_kickoff.create_title_file_from_manifest:main',
            'pipeline_submit = python_tools.pipeline_kickoff.pipeline_submit:main',
            'pipeline_runner = python_tools.pipeline_kickoff.pipeline_runner:main',
            # Workflow Tools
            'list2bed = python_tools.workflow_tools.list2bed:main',
            'map_read_names_to_umis = python_tools.workflow_tools.map_read_names_to_umis:main',
            'reverse_clip = python_tools.workflow_tools.reverse_clip:main',
            'fingerprinting = python_tools.workflow_tools.fingerprinting:main',
            # QC
            'aggregate_bam_metrics = python_tools.workflow_tools.qc.aggregate_bam_metrics:main',
            'qc_wrapper = python_tools.workflow_tools.qc.qc_wrapper:main',
            'qc = python_tools.workflow_tools.qc.qc:main',
        ]
    },
    scripts=[
        'python_tools/workflow_tools/qc/plotting-collapsed-bams.r'
    ],
    include_package_data = True,
    zip_safe=False,
    cmdclass={
        'clean': CleanCommand,
    }
)
