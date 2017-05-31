"""
for example, this file can be invoked from the command line to apply config `one`:
python -m override example.example2:P --set=selected=one
or by exec'ing the Project system itself:
python -c "from example.example2 import P; P.apply_config('one')"
"""

from override.tools import Project

P = Project(
    config_module='my_configs',
    config_path='built_config.py',
    relative_root=__file__,
    runtime_override_key='fizz',
    post_import_handler='post_import'
)
