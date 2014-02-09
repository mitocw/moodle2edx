import glob
from setuptools import setup

def findfiles(pat):
    #return [x[10:] for x in glob.glob('latex2edx/' + pat)]
    return [x for x in glob.glob('share/' + pat)]

data_files = [
    ('share/render', findfiles('render/*')),
    ('share/testtex', findfiles('testtex/*')),
    ('share/plastexpy', findfiles('plastexpy/*.py')),
    ]

# print "data_files = %s" % data_files

setup(
    name='moodle2edx',
    version='0.1.0',
    author='I. Chuang',
    author_email='ichuang@mit.edu',
    packages=['moodle2edx', 'moodle2edx.test'],
    scripts=[],
    url='http://pypi.python.org/pypi/moodle2edx/',
    license='LICENSE.txt',
    description='Converter from latex to edX XML format course content files.',
    long_description=open('README.txt').read(),
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'moodle2edx = moodle2edx.main:CommandLine',
            ],
        },
    install_requires=['lxml',
                      'path.py',
                      'html2text',
                      ],
    package_dir={'moodle2edx': 'moodle2edx'},
    package_data={ 'moodle2edx': ['testdat/*'] },
    # data_files = data_files,
    test_suite = "moodle2edx.test",
)

