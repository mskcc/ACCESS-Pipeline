# This file defines parameters to override ResourceRequimenents with smaller values,
# for running tests on smaller machines in singleMachine mode, such as a laptop or in Travis-CI

#cwltool:overrides:
#  # Todo: can use relative path?
#  ProcessLoopUMIFastq.cwl:
#    requirements:
#    - class: ResourceRequirement
#      ramMin: 5000
#      coresMin: 1
#
#  # Todo: can use relative path?
#  abra.cwl:
#    requirements:
#    - class: ResourceRequirement
#      ramMin: 5000
#      coresMin: 1

overrides:
  echo.cwl:
    requirements:
      EnvVarRequirement:
        envDef:
          MESSAGE: override_value


#  file:///Users/johnsoni/Desktop/code/Innovation-Pipeline/cwl_tools/bwa-mem/bwa-mem.cwl:
#    requirements:
#    - class: ResourceRequirement
#      ramMin: 5000
#      coresMin: 1
#
#  file:///Users/johnsoni/Desktop/code/Innovation-Pipeline/cwl_tools/gatk/BaseQualityScoreRecalibration.cwl:
#    requirements:
#    - class: ResourceRequirement
#      ramMin: 5000
#      coresMin: 1
#
#  file:///Users/johnsoni/Desktop/code/Innovation-Pipeline/cwl_tools/gatk/FindCoveredIntervals.cwl:
#    requirements:
#    - class: ResourceRequirement
#      ramMin: 5000
#      coresMin: 1
#
#  file:///Users/johnsoni/Desktop/code/Innovation-Pipeline/cwl_tools/gatk/PrintReads.cwl:
#    requirements:
#    - class: ResourceRequirement
#      ramMin: 5000
#      coresMin: 1
#
#  file:///Users/johnsoni/Desktop/code/Innovation-Pipeline/cwl_tools/picard/AddOrReplaceReadGroups.cwl:
#    requirements:
#    - class: ResourceRequirement
#      ramMin: 5000
#      coresMin: 1
#
#  file:///Users/johnsoni/Desktop/code/Innovation-Pipeline/cwl_tools/picard/FixMateInformation.cwl:
#    requirements:
#    - class: ResourceRequirement
#      ramMin: 5000
#      coresMin: 1
#
#  file:///Users/johnsoni/Desktop/code/Innovation-Pipeline/cwl_tools/picard/MarkDuplicates.cwl:
#    requirements:
#    - class: ResourceRequirement
#      ramMin: 5000
#      coresMin: 1
#
#  file:///Users/johnsoni/Desktop/code/Innovation-Pipeline/cwl_tools/trimgalore/trimgalore.cwl:
#    requirements:
#    - class: ResourceRequirement
#      ramMin: 5000
#      coresMin: 1
