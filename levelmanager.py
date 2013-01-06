import os
import glob

"""

levels/
    set1/
        a-1.kgl
        a-2.kgl
    set2/
        b-1.kgl
        a-2.kgl

-> LevelManager.levels == 
    [ 
        [
        "levels/set1/a-1.kgl",
        "levels/set1/a-2.kgl"
        ],
        [
        "levels/set2/a-2.kgl",
        "levels/set2/b-1.kgl"
        ]
    ]
"""

class LevelSection:
    """
    LevelSection.level_filenms -> list of .kgl file names
    LevelSection.section_filenm -> .kgs file name or None
    """
    def __init__(self, dirnm):
        # Collect the level file names.
        self.level_filenms = glob.glob(os.path.join(dirnm, "*.kgl"))
        # Determine the .kgs file name.
        t = sorted(glob.glob(os.path.join(dirnm, "*.kgs")))
        if len(t) > 0:
            self.section_filenm = t[0] 
        else:
            self.section_filenm = None
        if len(t) > 1:
            print >>sys.stderr, "NOTE: using first .kgs file found"

    def __repr__(self):
        return "<%s: %s>" % (self.section_filenm, ", ".join(self.level_filenms))


class LevelManager:
    def __init__(self, basedir="levels"):
        self.basedir = basedir
        self.current = 0
        self.refresh()

    def refresh(self): 
        self.level_sections = []
        # Get the names of the level section directories.
        dirnms = []
        for nm in sorted(os.listdir(self.basedir)):
            fullnm = os.path.join(self.basedir, nm)
            if os.path.isdir(fullnm):
                dirnms.append(fullnm)
        # Create the LevelSections for the section directories.
        for dirnm in dirnms:
            ls = LevelSection(dirnm)
            if len(ls.level_filenms) > 0:
                # Only store if there are levels in the level section.
                self.level_sections.append(ls)
            else:
                print >>sys.stderr, "NOTE: ignoring empty level section %r" % dirnm


if __name__=="__main__":
    lm = LevelManager()
    for ls in lm.level_sections:
        print ls
