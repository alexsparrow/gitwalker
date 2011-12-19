import subprocess

def log(msg, *args):
    print ">>> " + msg % args

# Annoyingly need to be compatible with old Pythons so can't use
# subprocess.check_output
def get_output(cmds, *args, **kwargs):
    kwargs["stdout"] = subprocess.PIPE
    process = subprocess.Popen( cmds, *args, **kwargs)
    output, unused_err = process.communicate()
    retcode = process.poll()
    if retcode: raise CmdError(retcode, cmds, output)
    return output
