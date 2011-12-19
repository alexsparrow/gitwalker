import json, shutil, tempfile, pprint, optparse, inspect
import tools
from datetime import datetime
from util import log, exit_msg, CmdError
from git import git_clone, git_log, git_checkout

def load_cmds(m):
    return [cls for name, cls in inspect.getmembers(m)
            if inspect.isclass(cls) and
            issubclass(cls, tools.Cmd)
            and cls is not tools.Cmd]

def setupCmdLine(cmds):
    parser = optparse.OptionParser(usage="%prog [options] git_repo")
    parser.add_option("--in", action="append", type="str",
                      default = [], metavar="FILES",
                      dest = "in_paths", help="Read JSON file")
    parser.add_option("--out", action="store", type="str",
                      dest="out_path", metavar="FILE",
                      default="out.json", help="Output JSON file")
    parser.add_option("--reload", action="store_true", help="Refetch info")
    parser.add_option("--debug", action="store_true", help="Debug commands")
    parser.add_option("--update", action="store", type="str", default=None,
                      metavar="FILE", help="Update JSON file")

    cmdgroup = optparse.OptionGroup(parser, "Commands", "Command codes")
    for c in cmds:
        options = c.options()
        options[0].kwargs["default"] = None
        options[0].kwargs["dest"] = c.name
        options[0].kwargs["help"] = c.__doc__
        cmdgroup.add_option("--%s" % c.name, *options[0].args, **options[0].kwargs)
        for opt in options[1:]:
            cmdgroup.add_option("--%s-%s" % (c.name, opt.name), *opt.args, **opt.kwargs)
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

    if opts.update:
        in_paths = [opts.update]
        out_path = opts.update
    else:
        in_paths = opt.in_paths
        out_path = opt.out_path

    for in_path in in_paths:
        d = json.load(open(in_path, "r"))
        for commit, vals in d.iteritems():
            if not commit in out: out[commit] = vals
            else: out[commit]["results"].update(vals["results"])

    try:
        git_new = tempfile.mkdtemp()
        log("Temp dir created: %s", git_new)
        log("Cloning repo: %s -> %s", git_repo, git_new)
        git_clone(git_repo, git_new)

        skip = []
        process =[]
        for comm in git_log(git_new):
            if comm["commit"] in out and all([c.name in out[comm["commit"]]["results"] for c in runlist]):
                skip.append(comm)
            else: process.append(comm)

        log("%d commits: processing %d, skipping %d" % (len(skip)+len(process),
                                                        len(process),
                                                        len(skip)))
        for idx, comm in enumerate(process):
            sha1 = comm["commit"]
            rec = {
                "date" : comm["date"].strftime("%d/%m/%Y"),
                "author" : comm["author"]
                }
            if sha1 in out and "results" in out[sha1]: rec["results"] = out[sha1]
            else: rec["results"] = {}

            if opts.reload: schedule = runlist
            else: schedule = [cmd for cmd in runlist if cmd.name not in rec["results"]]

            log("Checking out revision %s [%d/%d]", comm["commit"], idx+1, len(commits))
            git_checkout(git_new, sha1)

            for cmd in schedule:
                rec["results"][cmd.name] = {}
                try: rec["results"][cmd.name] = cmd.run(git_new)
                except CmdError,e:
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
