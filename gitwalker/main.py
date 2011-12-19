import sys, json, shutil, tempfile, pprint, optparse, inspect
import tools
from datetime import datetime
from util import log, exit_msg
from git import git_clone, git_log, git_checkout

def load_cmds(m):
    return [cls for name, cls in inspect.getmembers(m)
            if inspect.isclass(cls) and
            issubclass(cls, tools.Cmd)
            and cls is not tools.Cmd]

def setupCmdLine(cmds):
    parser = optparse.OptionParser()
    parser.add_option("--in", action="append", type="str",
                      default = [],
                      dest = "in_paths", help="Read JSON file")
    parser.add_option("--out", action="store", type="str",
                      dest="out_path",
                      default="out.json", help="Output JSON file")
    parser.add_option("--reload", action="store_true", help="Refetch info")
    parser.add_option("--debug", action="store_true", help="Debug commands")
    cmdgroup = optparse.OptionGroup(parser, "Commands", "Command codes")
    for c in cmds:
        opt = c.primary_opt()
        opt.kwargs["default"] = None
        opt.kwargs["dest"] = c.name
        cmdgroup.add_option("--%s" % c.name, *opt.args, **opt.kwargs)
    parser.add_option_group(cmdgroup)
    return parser

def main():
    cmds = load_cmds(tools)
    parser = setupCmdLine(cmds)
    opts, args = parser.parse_args()
    try: git_repo = args[0]
    except: exit_msg(parser.get_usage())

    runlist = [cmd(primary_opt, debug=opts.debug)
               for cmd, primary_opt in zip(cmds, map(lambda x: getattr(opts, x.name, None), cmds))
               if primary_opt]

    if len(runlist) == 0: exit_msg("Must specify a command to be run")

    out = {}
    for in_path in opts.in_paths:
        d = json.load(open(in_path, "r"))
        for commit, vals in d.iteritems():
            if not commit in out: out[commit] = vals
            else: out[commit]["results"].update(vals["results"])

    try:
        git_new = tempfile.mkdtemp()
        log("Temp dir created: %s", git_new)
        log("Cloning repo: %s -> %s", git_repo, git_new)
        git_clone(git_repo, git_new)
        commits = list(git_log(git_new))
        log("%d commits found" % len(commits))
        for idx, comm in enumerate(commits):
            sha1 = comm["commit"]
            if sha1 in out:
                rec = out[sha1]
            else:
                rec = {
                    "date" : comm["date"].strftime("%d/%m/%Y"),
                    "author" : comm["author"],
                    "results" : {}
                }
            if opts.reload: schedule = runlist
            else: schedule = [cmd for cmd in runlist if cmd.name not in rec["results"]]
            if len(schedule) == 0:
                log("Skipping revision %s [%d/%d]", comm["commit"], idx+1, len(commits))
                continue
            log("Checking out revision %s [%d/%d]", comm["commit"], idx+1, len(commits))
            git_checkout(git_new, sha1)

            for cmd in schedule:
                rec["results"][cmd.name] = {}
                try: rec["results"][cmd.name] = cmd.run(git_new)
                except tools.CmdError,e:
                    log("Command '%r' failed with %d", e.cmd, e.ret)
                    log("Output: %s", e.out)
                except Exception, e:
                    log("Failed to get output of command: %r",e)
                log("[%s] %s", cmd.name, pprint.pformat(rec["results"][cmd.name]))
            out[sha1] = rec

        log("Writing output file: %s", opts.out_path)
        json.dump(out, open(opts.out_path, "w"), indent=1)
    finally:
        log("Tidying temp dir: %s", git_new)
        shutil.rmtree(git_new)

if __name__ == "__main__":
    main()
