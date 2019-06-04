# (Taken from Toil version.py)


def version():
    """
    A version identifier that includes the full-length commit SHA1 and an optional suffix to
    indicate that the working copy is dirty.
    """
    return _version()


def short_version():
    """
    A version identifier that includes the abbreviated commit SHA1 and an optional suffix to
    indicate that the working copy is dirty.
    """
    return _version(shorten=True)


def _version(shorten=False):
    return '-'.join(filter(None, [current_commit()[:7 if shorten else None],
                                  ('dirty' if dirty() else None)]))


def most_recent_tag():
    import subprocess
    return subprocess.check_output(["git", "describe", "--tags"]).strip()


def current_commit():
    from subprocess import check_output
    try:
        output = check_output('git log --pretty=oneline -n 1 -- $(pwd)', shell=True).split()[0]
    except:
        # Return this if we are not in a git environment.
        return 'no_git_dir'
    return output


def dirty():
    from subprocess import call
    try:
        return 0 != call('(git diff --exit-code '
                         '&& git diff --cached --exit-code) > /dev/null', shell=True)
    except:
        return False # In case the git call fails.


def expand_(name=None):
    variables = {k: v for k, v in globals().items()
                 if not k.startswith('_') and not k.endswith('_')}

    def resolve(k):
        v = variables[k]
        if callable(v):
            v = v()
        return v

    if name is None:
        return ''.join("%s = %s\n" % (k, repr(resolve(k))) for k, v in variables.items())
    else:
        return resolve(name)


def _main():
    import sys
    sys.stdout.write(expand_(*sys.argv[1:]))


if __name__ == '__main__':
    _main()
