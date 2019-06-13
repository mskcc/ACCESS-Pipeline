import os
from subprocess import check_output, CalledProcessError


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


def version():
    """
    get a comprehensive git version and report it in
    the package at build-time.

    :param :
    :return str:
    """
    version = (
        get_tag()
        + "+"
        + get_commit_count_after_tag()
        + "."
        + get_commit()
        + (".dirty" if dirty() else "")
    )

    with open(
        os.path.dirname(os.path.abspath(__file__)) + "/python_tools/__init__.py", "w"
    ) as i:
        i.write('__version__ = "{}"\n'.format(version))

    return version
