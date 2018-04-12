from setuptools import setup


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
        'toil[cwl]==3.15.0',
        'pandas==0.19.0',
        'xlrd==1.1.0',
        'numpy==1.14.2',
        'pybedtools',
    ],
    # setup_requires=[
    #     # Setuptools 18.0 properly handles Cython extensions.
    #     'setuptools>=18.0',
    #     'cython',
    # ],
    packages = ['python_tools', 'python_tools.pipeline_kickoff'],
    entry_points = {
        'console_scripts': [
            'create_inputs_from_title_file = python_tools.pipeline_kickoff.create_inputs_from_title_file:main',
            'create_title_file_from_manifest = python_tools.pipeline_kickoff.create_title_file_from_manifest:main',
            'aggregate_bam_metrics = python_tools.aggregate_bam_metrics:main',
            'list2bed = python_tools.list2bed:main',
            'map_read_names_to_umis = python_tools.map_read_names_to_umis:main',
            'reverse_clip = python_tools.reverse_clip:main'
        ]
    },
    zip_safe=False
)
