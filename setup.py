from setuptools import setup, find_packages


setup(
    name='innovation-python-tools',
    version='0.0.0',
    description='MSKCC Center for Molecular Oncology, Innovation Lab, cfDNA sequencing pipeline',
    url='http://github.com/mskcc/Innovation-Pipeline',
    author='Ian Johnson',
    author_email='johnsoni1@mskcc.org',
    licence='MIT',
    packages=find_packages(),
    install_requires=[
        'argparse',
        'toil[cwl]==3.15.0',
        'pandas==0.19.0',
        'xlrd==1.1.0',
        'numpy==1.14.2',
        'pybedtools',
        'ruamel.yaml'
    ],
    scripts=[
        'python_tools/aggregate_bam_metrics',
        'python_tools/list2bed',
        'python_tools/reverse_clip',
        'python_tools/map_read_names_to_umis',
    ],
    zip_safe=False
)
