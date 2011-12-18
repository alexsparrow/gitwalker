from util import log, CmdError, get_output
import os.path

class Func:
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs

class Cmd(object):
    def __init__(self, val): pass

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

    def __init__(self, fname):
        self.fname = fname

    def word_count(self, base, path):
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
        return self.extract_wordcount(self.word_count(path, self.fname)["total"])
