import os
import contextlib
import unittest
import tempfile
import shutil
from path import path	# needs path.py
import urllib
import moodle2edx as m2emod
from moodle2edx.main import Moodle2Edx
from StringIO import StringIO

@contextlib.contextmanager
def make_temp_directory():
    temp_dir = tempfile.mkdtemp('m2etmp')
    yield temp_dir
    # shutil.rmtree(temp_dir)

class TestExamples(unittest.TestCase):

    @unittest.skip("skip example1 - uses moodle mbz file from remote url")
    def test_example1(self):
        url = 'http://moodleshare.org/mod/resource/view.php?id=14410'
        with make_temp_directory() as tmdir:
            edir = path(tmdir)
            print "edir = %s" % edir
            fn = '%s/explore_eng.mbz' % tmdir
            urllib.urlretrieve(url, fn)
        
            print "file %s" % fn
            m2e = Moodle2Edx(fn, edxdir=tmdir)

            xbfn = edir/'course.xml'
            self.assertTrue(os.path.exists(xbfn))

            xbfn = edir / 'html/label_14399__Now_that_you_know_something_about_the_people_of.xml'
            self.assertTrue(os.path.exists(xbfn))
            xb = open(xbfn).read()
            self.assertIn('<html display_name="Now that you know something about the people of ...">', xb)

            xbfn = edir / 'course/2014_Spring.xml'
            self.assertTrue(os.path.exists(xbfn))
            xb = open(xbfn).read()
            self.assertIn('<chapter display_name="Models and Designs Glossary">', xb)

    def test_example2(self):
        fn = path(m2emod.__file__).parent / 'testdat' / 'intro_to_stats.mbz'

        with make_temp_directory() as tmdir:
            edir = path(tmdir)
            print "edir = %s" % edir
            print "file %s" % fn
            m2e = Moodle2Edx(fn, edxdir=tmdir)

            xbfn = edir/'course.xml'
            self.assertTrue(os.path.exists(xbfn))

            xbfn = edir / 'html/page_13441__Steps_to_construct_a_stemplot.xml'
            self.assertTrue(os.path.exists(xbfn))
            xb = open(xbfn).read()
            self.assertIn('<html display_name="Steps to construct a stemplot">', xb)

            xbfn = edir / 'course/2014_Spring.xml'
            self.assertTrue(os.path.exists(xbfn))
            xb = open(xbfn).read()
            self.assertIn('<sequential display_name="Online Calculator" url_name="seq__Online_Calculator">', xb)

if __name__ == '__main__':
    unittest.main()
