import os
from subprocess import check_output, CalledProcessError

# User-defined version. This will be used as the package/build
#  version, in case version cannot be retrived using git methods.
__version__ = "1.1.0"


def get_tag():
    return str(
        check_output(["git", "describe", "--tags"])
        .decode("utf-8")
        .strip()
        .split("-")
        .pop(0)
    )


def get_commit(shorten=True):
    return str(
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
        .pop(0)
    )[: 7 if shorten else None]


def dirty():
    try:
        check_output(["git", "diff", "--exit-code"])
        check_output(["git", "diff", "--cached", "--exit-code"])
    except CalledProcessError as e:
        if e.returncode == 1:
            return True
        else:
            raise Exception("Not a git directory")
    return False


def get_commit_count_after_tag(tag=get_tag()):
    return str(
        check_output(["git", "rev-list", tag + "..HEAD", "--count"])
        .decode("utf-8")
        .strip()
    )


def get_version():
    """
    get a comprehensive git version and report it in
    the package at build-time.

    :param :
    :return str:
    """
    return (
        get_tag()
        + "+"
        + get_commit_count_after_tag()
        + "."
        + get_commit()
        #+ (".dirty" if dirty() else "")
    )


def get_and_write_version():
    version = get_version()

    with open(
        os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "../resources/run_params/version.yaml",
        ),
        "w",
    ) as i:
        i.write("# Pipeline Run Version:\nversion : {}\n".format(version))
    return version
