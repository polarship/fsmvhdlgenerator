import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

topic = ("Topic :: Scientific/Engineering :: "
         "Electronic Design Automation (EDA)")

setuptools.setup(
    name="fsmvhdlgenerator",
    version="1.0.0rc1",
    author="David Indictor",
    author_email="david.indictor.dev@gmail.com",
    description=("A small GUI tool to generate VHDL code of "
                 "Finite State Machines"),
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/polarship/fsmvhdlgenerator",
    install_requires=[
        'boolean.py>=3.8,<4', 'jinja2>=2.11.2,<2.12.0',
        'pygments>=2.6.1,<2.7',
    ],
    setup_requires=['pytest-runner'],
    tests_require=['pytest'],
    package_dir={'': 'src'},
    packages=setuptools.find_packages(where='src'),
    package_data={
        'fsmvhdlgenerator.templates': ['*.vhd.j2'],
        'fsmvhdlgenerator.static': ['*'],
    },
    entry_points={
        'gui_scripts': [
            'fsmvhdlgenerator=fsmvhdlgenerator.main:gui_entry',
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta"
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: POSIX :: Linux",
        topic,
    ],
    keywords='fsm vhdl development',
    project_urls={
        'Source': 'https://github.com/pypa/sampleproject/',
        'Tracker': 'https://github.com/pypa/sampleproject/issues',
    },
    python_requires='>=3.6'
)
