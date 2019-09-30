#!/usr/bin/env python

import os, re, sys, argparse
import pandas as pd
from glob import glob
from datetime import datetime


def summarize_log_files(log_dir, title_file, outdir, coverage=None, tag=None):
    """
    Core function that consumes all the module level log
    files in the toil log directory and compiles the metrics
    for each module and sample in the project.
    """
    tf_df = pd.read_csv(title_file, header="infer", sep="\t")
    project = tf_df["Pool"].unique().tolist().pop()
    if tag:
        project += "_" + tag
    files = glob(
        log_dir + "/file:*" + "*.cwl" + "*job" + ("[0-9A-Za-z_]" * 6) + "000.log"
    )
    jobs = map(lambda x: re.search("job.{6}", x).group(0), files)
    modules = map(
        lambda x: re.sub(r"(.*.cwl).*", r"\1", x)
        .replace("--", "~")
        .split("-")[-1]
        .replace("~", "-"),
        files,
    )
    samples = [",".join(extract_sampleID(log_file, tf_df)) for log_file in files]
    run_times = [extract_run_time(log_file) for log_file in files]
    time_stamps = [
        datetime.utcfromtimestamp(os.path.getmtime(log_file)).strftime(
            "%Y-%m-%d %H:%M:%S"
        )
        for log_file in files
    ]
    log_df = {
        "samples": samples,
        "run_times": run_times,
        "module": modules,
        "jobID": jobs,
        "Last_modified": time_stamps,
    }
    log_df = pd.DataFrame(data=log_df)
    log_df = log_df.sort_values(by=["module", "run_times"])
    if coverage:
        cov_df = pd.read_csv(coverage, header="infer", sep="\t").replace(
            " ", "_", regex=True
        )
        cov_df = cov_df[(cov_df["pool"] == "A_Targets")]
        cov_df_reshape = cov_df.pivot_table(
            index="Sample", columns="method", values="average_coverage"
        )[["TotalCoverage", "All_Unique", "Duplex", "Simplex"]].reset_index()
        log_df = (
            pd.merge(
                log_df, cov_df_reshape, how="left", left_on="samples", right_on="Sample"
            )
            .drop(["Sample"], axis=1)
            .replace(pd.np.nan, "")
        )
    log_df.to_csv(os.path.join(outdir, project + "_run_stats.txt"), header=True, sep="\t", index=False)


def extract_sampleID(log_file, tf_df):
    """
    helper function to extract any available sample ID
    in a log file.
    """
    samples = tf_df["Sample"].values.tolist()
    with open(log_file, "r") as f:
        lines = f.read().replace("\n", "")
    sample_match = list(
        filter(lambda x: re.search(r"[_|\s+|/]" + x + r"[_|\s+|/]", lines), samples)
    )
    return sample_match


def extract_run_time(log_file):
    """
    helper function to extract run time in a log file.
    """
    with open(log_file, "r") as f:
        lines = f.read().replace("\n", "")
    match = re.match(r".* ([0-9.]+) seconds$", lines).group(1)
    return float(match)


def main():
    """
    Parse arguments

    :return:
    """
    parser = argparse.ArgumentParser(
        prog="orkflow_runtime_stats.py",
        description="compile run time for all modules using log files",
        usage="%(prog)s [options]",
    )
    parser.add_argument(
        "-t",
        "--title_file",
        action="store",
        dest="title_file",
        required=True,
        help="Title file for a given project",
    )
    parser.add_argument(
        "-l",
        "--log_directory",
        action="store",
        dest="log_directory",
        required=True,
        help="Toil log directory that contains module level logs for all the workflows",
    )
    parser.add_argument(
        "-c",
        "--coverage",
        action="store",
        dest="coverage",
        required=False,
        help="Aggregate coverage file for all samples in the project",
    )
    parser.add_argument(
        "-o",
        "--outdir",
        action="store",
        dest="outdir",
        default=os.getcwd(),
        required=False,
        help="Output directory for the usage stats file",
    )
    args = parser.parse_args()
    summarize_log_files(args.log_directory, args.title_file, args.outdir, args.coverage)


if __name__ == "__main__":
    main()
