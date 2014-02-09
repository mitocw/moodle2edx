==========
moodle2edx
==========

Python script to convert moodle course content to edX

This script takes a moodle backup file (.mbz) as input, and produces
as output an edX course in XML format (http://data.edx.org).

moodle2edx handles conversion of the following moodle activities:

* url
* label
* resource
* page
* quiz (only partial implementation)

Static content is also converted.  Relative links also mostly work.

Requirements
============

lxml, html2text

Installation
============

    pip install -e git+https://github.com/mitocw/moodle2edx.git#egg=moodle2edx

Usage
=====

Usage: moodle2edx [options] [moodle_backup.mbz | moodle_backup_dir]

Options:
  --version             show program's version number and exit
  -h, --help            show this help message and exit
  -c, --clean-up-html   clean up html to be proper xhtml
  -v, --verbose         verbose error messages
  -d OUTPUT_DIR, --output-directory=OUTPUT_DIR
                        Directory name for output course XML files
  -o ORG, --org=ORG     organization to use in edX course XML
  -s SEMESTER, --semester=SEMESTER
                        semester to use for edX course (no spaces)

Examples
========

* https://github.com/mitocw/content-ocw-explore-engineering
* https://github.com/mitocw/content-ocw-intro-to-stats

As can be seen from these examples, moodle2edx provides a functional way to get
pages from moodle into edX.  The locations of the content are sub-ideal, but
provide a working starting point for editing using edX Studio.  Translation
of moodle assessments into edX problems is mostly incomplete.


History
=======

* v1.0: python package; unit tests; modular code

Acknowledgements
================

The sample moodle backup file used for testing (testdat/intro_to_stats.mbz)
is from http://moodleshare.org/course/view.php?id=213

The abox.py code used for problem converstion is from 

  https://github.com/mitocw/latex2edx
