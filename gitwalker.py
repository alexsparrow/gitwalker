#!/usr/bin/env python2
import subprocess, sys, os.path, json, copy, shutil, tempfile
from datetime import datetime

class CmdError(Exception):
    def __init__(self, ret, cmd, out): self.ret, self.cmd, self.out = ret, cmd, out

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

def git_cmd(path, *args, **kwargs):
    repo = os.path.join(path, ".git")
    return get_output(["git", "--git-dir", repo, "--work-tree", path]+list(args), **kwargs)

def git_clone(path, target):
    get_output(["git", "clone", path, target])

def git_log(path):
    outp = git_cmd(path, "rev-list", "--date=iso", "--all", "--pretty=medium")
    out = {}
    for l in outp.splitlines():
        if l.startswith("commit"): out["commit"] = l.split()[1]
        elif l.startswith("Author"): out["author"] = l.split(":")[1].strip().rstrip()
        elif l.startswith("Date"):
            out["date"] = datetime.strptime(l.split(":",1)[1].split("+")[0].strip().rstrip(), "%Y-%m-%d %H:%M:%S")
        if "commit" in out and "author" in out and "date" in out:
            yield out
            out = {}

def git_checkout(path, commit):
    git_cmd(path, "checkout", commit, stderr=subprocess.PIPE)

def word_count(base, path):
    script_dir = os.path.dirname(os.path.realpath(__file__))
    tex_count_path = os.path.join(script_dir, "texcount.pl")
    out = get_output([tex_count_path, "-inc", path], cwd=base)
    results = {}
    name = None
    for l in out.splitlines():
        if not ":" in l: continue
        k, v = l.split(":")[0].strip().rstrip(), l.split(":")[1].strip().rstrip()
        if k in ["File", "Included file"]:
            name = v
            results[name] = {}
        elif k == "File(s) total":
            name = "total"
            results[name] = {}
        elif name is not None: results[name][k] = v
    return results

def my_func(path, fname):
    try: return word_count(path, fname)["total"]["Words in text"]
    except CmdError,e:
        log("Command '%r' failed with %d", e.cmd, e.ret)
        log("Output: %s", e.out)
        return {}

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print "Usage: %s <git repository> <TeX path> <output file>" % os.path.basename(__file__)
        sys.exit(-1)
    git_repo = sys.argv[1]
    tex_path = sys.argv[2]
    out_path = sys.argv[3]
    git_new = tempfile.mkdtemp()
    log("Temp dir created: %s", git_new)
    try:
        log("Cloning repo: %s -> %s", git_repo, git_new)
        git_clone(git_repo, git_new)
        outs = []
        commits = list(git_log(git_new))
        log("%d commits found" % len(commits))
        for idx, x in enumerate(commits):
            log("Checking out revision %s [%d/%d]", x["commit"], idx+1, len(commits))
            git_checkout(git_new, x["commit"])
            out = copy.deepcopy(x)
            out["date"] = out["date"].strftime("%d/%m/%Y")
            out["result"] = my_func(git_new, tex_path)
            outs.append(out)
            log("Result: %r", out["result"])
        json.dump(outs, open(out_path, "w"), indent=1)
    except CmdError, e:
        print "Command '%r' failed with %d" % (e.cmd, e.ret)
    finally:
        log("Tidying temp dir: %s", git_new)
        shutil.rmtree(git_new)
