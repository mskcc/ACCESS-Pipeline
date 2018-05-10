class: SchemaDefRequirement
types:
 - name: FastqPair
   type: record
   fields:
     - name: fastq1
       type: File
     - name: fastq2
       type: File
     - name: sample_sheet
       type: File

     - name: adapter
       type: string
     - name: adapter2
       type: string

     - name: add_rg_PL
       type: string
     - name: add_rg_CN
       type: string

     - name: add_rg_LB
       type: string
     - name: add_rg_ID
       type: string

     - name: add_rg_PU
       type: string
     - name: add_rg_SM
       type: string
     - name: patient_id
       type: string
     - name: sample_class
       type: string
