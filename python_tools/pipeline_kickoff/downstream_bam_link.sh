#!/usr/bin/env bash


# Usage:
# downstream_bam_link.sh <bam_qc folder> <output folder>
#
# bam_qc subdirectory with sample directories
BAM_QC_FOLDER=$1
# Output location for folders with symlinks
OUTPUT_FOLDER=$2


echo "Creating subdirectories for linked bam files"
mkdir -p ${OUTPUT_FOLDER}/standard_tumor_bams
mkdir -p ${OUTPUT_FOLDER}/unfiltered_tumor_bams
mkdir -p ${OUTPUT_FOLDER}/simplex_tumor_bams
mkdir -p ${OUTPUT_FOLDER}/duplex_tumor_bams

mkdir -p ${OUTPUT_FOLDER}/standard_normal_bams
mkdir -p ${OUTPUT_FOLDER}/unfiltered_normal_bams
mkdir -p ${OUTPUT_FOLDER}/simplex_normal_bams
mkdir -p ${OUTPUT_FOLDER}/duplex_normal_bams

echo "Linking Tumor Bams"
for d in `ls -d ${BAM_QC_FOLDER}/*L0*/`; do
    echo $d;

    standard_bam=`readlink -f ${d}/*_cl_aln_srt_MD_IR_FX_BR.bam`
    unfiltered_bam=`readlink -f ${d}/*_cl_aln_srt_MD_IR_FX_BR__aln_srt_IR_FX.bam`
    simplex_bam=`readlink -f ${d}/*-simplex.bam`
    duplex_bam=`readlink -f ${d}/*-duplex.bam`

    standard_bam_base=`basename ${standard_bam}`
    unfiltered_bam_base=`basename ${unfiltered_bam}`
    simplex_bam_base=`basename ${simplex_bam}`
    duplex_bam_base=`basename ${duplex_bam}`

    ln -s ${standard_bam} ${OUTPUT_FOLDER}/standard_tumor_bams/${standard_bam_base}
    ln -s ${unfiltered_bam} ${OUTPUT_FOLDER}/unfiltered_tumor_bams/${unfiltered_bam_base}
    ln -s ${simplex_bam} ${OUTPUT_FOLDER}/simplex_tumor_bams/${simplex_bam_base}
    ln -s ${duplex_bam} ${OUTPUT_FOLDER}/duplex_tumor_bams/${duplex_bam_base}

    ln -s ${standard_bam%.bam}.bai ${OUTPUT_FOLDER}/standard_tumor_bams/${standard_bam_base%.bam}.bai
    ln -s ${unfiltered_bam%.bam}.bai ${OUTPUT_FOLDER}/unfiltered_tumor_bams/${unfiltered_bam_base%.bam}.bai
    ln -s ${simplex_bam%.bam}.bai ${OUTPUT_FOLDER}/simplex_tumor_bams/${simplex_bam_base%.bam}.bai
    ln -s ${duplex_bam%.bam}.bai ${OUTPUT_FOLDER}/duplex_tumor_bams/${duplex_bam_base%.bam}.bai
done

echo "Linking Normal Bams"
for d in `ls -d ${BAM_QC_FOLDER}/*N0*/`; do
    echo $d;

    standard_bam=`readlink -f ${d}/*_cl_aln_srt_MD_IR_FX_BR.bam`
    unfiltered_bam=`readlink -f ${d}/*_cl_aln_srt_MD_IR_FX_BR__aln_srt_IR_FX.bam`
    simplex_bam=`readlink -f ${d}/*-simplex.bam`
    duplex_bam=`readlink -f ${d}/*-duplex.bam`

    standard_bam_base=`basename ${standard_bam}`
    unfiltered_bam_base=`basename ${unfiltered_bam}`
    simplex_bam_base=`basename ${simplex_bam}`
    duplex_bam_base=`basename ${duplex_bam}`

    ln -s ${standard_bam} ${OUTPUT_FOLDER}/standard_normal_bams/${standard_bam_base}
    ln -s ${unfiltered_bam} ${OUTPUT_FOLDER}/unfiltered_normal_bams/${unfiltered_bam_base}
    ln -s ${simplex_bam} ${OUTPUT_FOLDER}/simplex_normal_bams/${simplex_bam_base}
    ln -s ${duplex_bam} ${OUTPUT_FOLDER}/duplex_normal_bams/${duplex_bam_base}

    ln -s ${standard_bam%.bam}.bai ${OUTPUT_FOLDER}/standard_normal_bams/${standard_bam_base%.bam}.bai
    ln -s ${unfiltered_bam%.bam}.bai ${OUTPUT_FOLDER}/unfiltered_normal_bams/${unfiltered_bam_base%.bam}.bai
    ln -s ${simplex_bam%.bam}.bai ${OUTPUT_FOLDER}/simplex_normal_bams/${simplex_bam_base%.bam}.bai
    ln -s ${duplex_bam%.bam}.bai ${OUTPUT_FOLDER}/duplex_normal_bams/${duplex_bam_base%.bam}.bai
done
