import argparse
import importlib

from override.project import Project
from override.updates import RuntimeUpdates


def init_from_command():
    parser = argparse.ArgumentParser()
    parser.add_argument('module_name')
    args = parser.parse_known_args()[0]
    my_module, my_package = args.module_name.rsplit(':', 1)
    my_module = importlib.import_module(my_module, my_package)
    project = getattr(my_module, my_package)
    if not isinstance(project, Project):
        raise TypeError('%r ought to be an instance of %r' % (project, Project))
    RuntimeUpdates().apply_all(project)
    project.apply_config()
