# todo
baseCommand:
- /opt/common/CentOS_6-dev/python/python-2.7.10/bin/python
- /home/johnsoni/Innovation-QC--new/innovation_qc.py

inputs:
  standard_waltz_metrics:
    type: Directory
    inputBinding:
      prefix: -sw

  fulcrum_waltz_metrics:
    type: Directory
    inputBinding:
      prefix: -fw

  title_file:
    type: File
    inputBinding:
      prefix: -t

outputs:
  qc_pdf:
    type: File
    outputBinding:
      glob: ${ return 'results/final-plots/*.pdf' }
