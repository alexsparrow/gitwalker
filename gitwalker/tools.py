from util import log, get_output
import os.path

script_dir = os.path.dirname(os.path.realpath(__file__))
tex_count_path = os.path.normpath(os.path.join(script_dir, "bin/texcount.pl"))

class Func:
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs

class Cmd(object):
    def __init__(self, val): pass

class CmdError(Exception):
    def __init__(self, ret, cmd, out): self.ret, self.cmd, self.out = ret, cmd, out


class du(Cmd):
    name = "du"
    @staticmethod
    def primary_opt():
        return Func(action="store_true", help="Disk Usage")
    def run(self, path):
        out = get_output(["du", "-chs", "--exclude=.git", path])
        return out.splitlines()[-1].split()[0]

class word_count(Cmd):
    name = "wordcount"

    @staticmethod
    def primary_opt():
        return Func(action="store", type="str", metavar="TEXFILE",
                    help="Word count a TeX file")

    def __init__(self, fname, debug=False, *args,  **kwargs):
        self.fname = fname
        self.debug = debug
    def word_count(self, base, path):
        out = get_output(["perl", tex_count_path, "-inc", path], cwd=base)
        if self.debug: log("TeXCount: %s", out)
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
        return (out, results)

    def extract_wordcount(self, d):
        fields = [
            ("wordcount", "Words in text"),
            ("wordsinheaders" ,"Words in headers"),
            ("wordsincaptions" ,"Words in float captions"),
            ("nheaders" ,"Number of headers"),
            ("nfloats" ,"Number of floats"),
            ("nmathinlines" ,"Number of math inlines"),
            ("nmathdisplays" ,"Number of math displayed"),
            ("filecount", "Files")
            ]
        out = {}
        for x, y in fields:
            try: out[x] = int(d[y])
            except: out[x] = -1
        return out

    def run(self, path):
        if not os.path.exists(os.path.join(path, self.fname)): raise IOError("Couldn't find TeX file: %s" % self.fname)
        (out, wc) = self.word_count(path, self.fname)
        if not "total" in wc: raise ValueError("Error parsing output: %s" % out)
        else: return self.extract_wordcount(wc["total"])
