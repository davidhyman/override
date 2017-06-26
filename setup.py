from setuptools import setup

with open('requirements.txt') as fh:
    requirements = fh.readlines()

setup(
    name='pyoverride',
    packages=['override'],
    version='0.9.2',
    license='MIT',
    description='Python project configuration',
    author='David Hyman',
    author_email='david.hyman...@gmail.com',
    url='https://github.com/davidhyman/override',
    download_url='https://github.com/davidhyman/override/archive/0.9.tar.gz',
    keywords=[
        'settings',
        'configuration',
        'override',
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
    ],
    python_requires='>=3',
    install_requires=requirements,
)
