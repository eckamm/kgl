
from init import init
from leveleditor import LevelEditor



def main(dirnm):
    g = init()
    level_editor = LevelEditor(g, dirnm)
    level_editor.run()

    level_editor.dump()


if __name__=="__main__":
    main(".")


