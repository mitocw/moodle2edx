moodle2edx
==========

Python script to convert moodle course content to edX

This script has been used to successfully convert a Moodle course into
edX format.  The basic idea is to start from a Moodle backup dump,
then traverse the XML and other files to construct corresponding edX
content.

The key tool used in this construction is abox.py -- a generic object
for "answer boxes", which abstracts away the capa problem types used
in the edX system.
