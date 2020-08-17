#!/bin/bash


# Script to create inputs for and run the following pipelines:
#
# snps_and_indels.cwl
# manta.cwl
# call_cnv.cwl
# msi.cwl
#
# Run in an existing ACCESS project directory of the following structure:
#
# /current_working_directory
#   /small_variants
#   /copy_number_variants
#   /microsatellite_instability
#   /structural_variants

# Arguments:
#
#   project_id                                                        P
#
#   tumor_bams_directory                                              DTB
#   simplex_bams_directory                                            STB
#   tumor_bams_directory                                              UTB
#   standard_bams_directory                                           STDB
#
#   normal_bams_directory                                             UNB
#   default_normal_path                                               DDN
#   default_stdnormal_path                                            DSTDN
#
#   curated_bams_duplex_directory                                     CBD
#   curated_bams_simplex_directory                                    CBS
#
#   pairing_file_path                                                 PF
#   title_file_path                                                   T

# Example Usage:
#
# downstream_analysis_workflows.sh \
# -P 				    Project_10619_B \
# -T 				    ./Project_10619_B.txt \
# -PF 				    ./pairing.txt \
# -DTB 			    ./duplex_tumor_bams \
# -STB 			    ./simplex_tumor_bams \
# -UTB 			    ./unfiltered_tumor_bams \
# -STTB 			  ./all_standard_bams \
# -UNB 			    ./unfiltered_normal_bams \
# -DDN 			    ./novaseq_unmatched_normal_plasma_duplex_bams_dmp/current/DONOR22-TP_cl_aln_srt_MD_IR_FX_BR__aln_srt_IR_FX-duplex.bam \
# -DSTN 			  ./novaseq_unmatched_normal_plasma_standard_bams_dmp/current/DONOR22-TP_cl_aln_srt_MD_IR_FX_BR.bam \
# -CDB 			    ./novaseq_curated_duplex_bams_dmp/current/ \
# -CSB 			    ./novaseq_curated_simplex_bams_dmp/current/


############
# Step 1: Parse arguments

while (( "$#" )); do
    case "$1" in
    -P)
        PROJECT_ID=$2;;
    -DTB)
        DUPLEX_TUMOR_BAMS_DIRECTORY=$2;;
    -STB)
        SIMPLEX_TUMOR_BAMS_DIRECTORY=$2;;
    -UTB)
        UNFILTERED_TUMOR_BAMS_DIRECTORY=$2;;
    -STTB)
        STANDARD_TUMOR_BAMS_DIRECTORY=$2;;

    -UNB)
        UNFILTERED_NORMAL_BAMS_DIRECTORY=$2;;
    -DDN)
        DEFAULT_DUPLEX_NORMAL_PATH=$2;;
    -DSTN)
        DEFAULT_STANDARD_NORMAL_PATH=$2;;

    -CDB)
        CURATED_DUPLEX_BAMS_DIRECTORY=$2;;
    -CSB)
        CURATED_SIMPLEX_BAMS_DIRECTORY=$2;;

    -PF)
        PAIRING_FILE_PATH=$2;;
    -T)
        TITLE_FILE_PATH=$2
    esac
    shift
    shift
done


############
# Step 2. Generate Inputs

small_variants_inputs=small_variants/${PROJECT_ID}_vc_inputs.yaml
cnv_inputs=${PROJECT_ID}_cnv_inputs.yaml
msi_inputs=microsatellite_instability/${PROJECT_ID}_msi_inputs.yaml

generate_access_variants_inputs_cmo \
--output_file_name "${small_variants_inputs}" \
--project_name "${PROJECT_ID}" \
--default_normal_path "${DEFAULT_DUPLEX_NORMAL_PATH}" \
--tumor_bams_directory "${DUPLEX_TUMOR_BAMS_DIRECTORY}" \
--normal_bams_directory "${UNFILTERED_NORMAL_BAMS_DIRECTORY}" \
--simplex_bams_directory "${SIMPLEX_TUMOR_BAMS_DIRECTORY}" \
--curated_bams_duplex_directory "${CURATED_DUPLEX_BAMS_DIRECTORY}" \
--curated_bams_simplex_directory "${CURATED_SIMPLEX_BAMS_DIRECTORY}" \
--pairing_file_path "${PAIRING_FILE_PATH}" \
--default_stdnormal_path "${DEFAULT_STANDARD_NORMAL_PATH}" \
--standard_bams_directory "${STANDARD_TUMOR_BAMS_DIRECTORY}"

cd copy_number_variants
generate_copynumber_inputs \
--project_id "${PROJECT_ID}" \
--output_file_name "${cnv_inputs}" \
--title_file_path "${TITLE_FILE_PATH}" \
--tumor_bams_directory "${UNFILTERED_TUMOR_BAMS_DIRECTORY}" \
--output_directory . \
--tmp_dir /scratch \
-alone
cd ..

generate_msi_inputs \
--project_name "${PROJECT_ID}" \
--output_file_name "${msi_inputs}" \
--standard_bams_directory "${STANDARD_TUMOR_BAMS_DIRECTORY}" \
--output_directory ./microsatellite_instability \
--tmp_dir /scratch \
-alone


############
# Step 3. Submit Runs

small_variants_workflow=/work/access/production/workflows/access_workflows/v1/pipeline_1.3.36/ACCESS-Pipeline/workflows/subworkflows/snps_and_indels.cwl
structural_variants_workflow=/work/access/production/workflows/access_workflows/v1/pipeline_1.3.36/ACCESS-Pipeline/workflows/subworkflows/manta.cwl
cnv_workflow=/work/access/production/workflows/access_workflows/v1/pipeline_1.3.36/ACCESS-Pipeline/workflows/subworkflows/call_cnv.cwl
msi_workflow=/work/access/production/workflows/access_workflows/v1/pipeline_1.3.36/ACCESS-Pipeline/workflows/subworkflows/msi.cwl

pipeline_submit \
--output_location small_variants \
--inputs_file ./"${small_variants_inputs}" \
--workflow ${small_variants_workflow} \
--batch_system lsf \
--leader_queue general \
--log_level INFO

pipeline_submit \
--output_location structural_variants \
--inputs_file ./"${small_variants_inputs}" \
--workflow ${structural_variants_workflow} \
--batch_system lsf \
--leader_queue general \
--log_level INFO

cd copy_number_variants
pipeline_submit \
--output_location copy_number_variants \
--inputs_file ./"${cnv_inputs}" \
--workflow ${cnv_workflow} \
--batch_system lsf \
--leader_queue general \
--log_level INFO
cd ..

pipeline_submit \
--output_location microsatellite_instability \
--inputs_file "${msi_inputs}" \
--workflow ${msi_workflow} \
--batch_system lsf \
--leader_queue general \
--log_level INFO
