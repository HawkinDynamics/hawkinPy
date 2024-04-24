from setuptools import setup, find_packages

# read the contents of your README file
from pathlib import Path
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

VERSION = '0.0.1' 
DESCRIPTION = 'Get your data from the Hawkin Dynamics API'


# Setting up
setup(
       # the name must match the folder name 'verysimplemodule'
        name="hawkinPy", 
        version=VERSION,
        author="Lauren Green",
        author_email="<lauren@hawkindynamics.com>",
        description=DESCRIPTION,
        long_description=long_description,
        long_description_content_type='text/markdown',
        packages=find_packages(),
        install_requires=[], # add any additional packages that 
        # needs to be installed along with your package. Eg: 'caer'
        
        keywords=['python', 'first package'],
        classifiers= [
            "Development Status :: 3 - Alpha",
            "Intended Audience :: Education",
            "Programming Language :: Python :: 2",
            "Programming Language :: Python :: 3",
            "Operating System :: MacOS :: MacOS X",
            "Operating System :: Microsoft :: Windows",
        ]
)