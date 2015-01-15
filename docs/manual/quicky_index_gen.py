# Apache License, Version 2.0

"""
Script to create a partial contents, for generating partial chapters.

Called from conf.py
"""

# Note, keep Python2 & 3 Compatible
import os

CURRENT_DIR = os.path.abspath(os.path.dirname(__file__))

def from_chapters():
    """
    Return conf.py: (master_doc, exclude_patterns) values.
    """

    master_doc = "contents"
    exclude_patterns = []

    quicky_chapters = [c for c in os.environ.get('QUICKY_CHAPTERS', "").strip(":").split(":") if c]
    if not quicky_chapters:
        return master_doc, exclude_patterns

    master_doc = "contents_quicky"

    fn_src = os.path.join(CURRENT_DIR, "contents.rst")
    fn_dst = os.path.join(CURRENT_DIR, "contents_quicky.rst")

    f = open(fn_src, 'r')
    data = f.read()
    f.close()
    del f

    lines = data.split("\n")

    lines_new = []
    for l in lines:
        l_orig = l

        # Extract the identifier
        # world/index.rst --> world
        # world.rst       --> world

        l = l.strip()
        if l.endswith(".rst"):
            l = l[:-4]
            if l.endswith("/index"):
                l = l.rsplit("/", 1)[0]
            # Now we have an identifier
            if l not in quicky_chapters:
                # print("  skipping:", l_orig.strip())
                continue
            # print("  using:", l_orig.strip())
        lines_new.append(l_orig)

    data = "\n".join(lines_new)

    f = open(fn_dst, 'w')
    f.write(data)
    f.close()
    del f

    # now exclude all dirs not in chapters
    exclude_patterns.append("contents.rst")
    for fn in os.listdir(CURRENT_DIR):
        if os.path.isdir(os.path.join(CURRENT_DIR, fn)):
            if fn not in quicky_chapters:
                # print("  exclude:", fn)
                exclude_patterns.append(fn)
        else:
            if fn in ("contents_quicky.rst",):
                continue

            if fn.endswith(".rst"):
                if fn[:-4] not in quicky_chapters:
                    exclude_patterns.append(fn)


    return master_doc, exclude_patterns
