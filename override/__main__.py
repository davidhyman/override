import argparse

if __name__ == '__main__':
    from override.tools import Project
    from override.tools import RuntimeUpdates
    P = Project()
    RuntimeUpdates('override').apply_all(P)
    P.apply_config()

