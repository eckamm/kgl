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
    organizes a collection of level definitions

    LevelSection.level_filenms -> list of .kgl file names
    LevelSection.section_filenm -> .kgs file name or None
    """
    def __init__(self, dirnm):
        self.dirnm = dirnm
        self.refresh()

    def refresh(self):
        # Collect the level file names (.kgl).
        self.level_filenms = glob.glob(os.path.join(self.dirnm, "*.kgl"))
        # Determine the section file name (.kgs).
        t = sorted(glob.glob(os.path.join(self.dirnm, "*.kgs")))
        if len(t) > 0:
            self.section_filenm = t[0] 
        else:
            self.section_filenm = None
        if len(t) > 1:
            print >>sys.stderr, "NOTE: using first .kgs file found"

    def __repr__(self):
        return "<%s: %s>" % (self.section_filenm, ", ".join(self.level_filenms))


class LevelManager:
    """
    organizes the collections (sections) of level definitions

    LevelManager.level_sections -> list of LevelSections
    """
    def __init__(self, basedir="levels"):
        self.basedir = basedir
        self.current = 0
        self.refresh()
        self.section_idx = 0
        self.level_idx = 0

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

    def next(self):
        lidx = self.level_idx + 1
        sidx = self.section_idx
        if lidx >= len(self.level_sections[sidx].level_filenms):
            sidx += 1
            lidx = 0
        if sidx >= len(self.level_sections):
            return None, None
        self.level_idx = lidx 
        self.section_idx = sidx
        s = self.level_sections[self.section_idx]
        return s, s.level_filenms[self.level_idx]

    def prev(self):
        lidx = self.level_idx - 1
        sidx = self.section_idx
        if lidx < 0:
            sidx -= 1
            lidx = 0
        if sidx < 0:
            return None, None
        self.level_idx = lidx 
        self.section_idx = sidx
        s = self.level_sections[self.section_idx]
        return s, s.level_filenms[self.level_idx]


if __name__=="__main__":
    lm = LevelManager()
    for ls in lm.level_sections:
        print ls
