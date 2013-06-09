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

Note that the abox.py file in this repo is a very recent version (the
same file is used by latex2edx; see https://github.com/mitocw/latex2edx).
The moodle2edx.py script may need to be updated to work properly with
this version of abox.py.

Another useful step would be to use xbundle
(https://github.com/mitocw/xbundle), so that instead of creating a bunch
of separate XML files, moodle2edx could create just one large XML file
with the entire set of course content.  
