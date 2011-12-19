import subprocess
import os.path
from datetime import datetime

from util import get_output

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
