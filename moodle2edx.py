
#!/usr/bin/python
#
# File:   moodle2edx.py
# Date:   19-July-2012
# Author: I. Chuang <ichuang@mit.edu>
#
# script to convert a moodle class into an edX course
#
# Usage: python moodle2edx.py [ backup-file.mbz | backup-directory ]

import os, sys, string, re
import codecs
from lxml import etree
from abox import AnswerBox
from path import path
import xml.sax.saxutils as saxutils

#-----------------------------------------------------------------------------

class Moodle2Edx(object):
    '''
    Python class for converting moodle backup files to edX XML course format
    '''

    def __init__(self, infn, edxdir='.'):
        if infn.endswith('.mbz'):
            # import gzip, tarfile
            # dir = tarfile.TarFile(fileobj=gzip.open(infn))
            dir = tempfile.mkdtemp(prefix="moodle2edx")
            curdir = os.path.abspath('.')
            os.chdir(dir)
            os.system('tar xzf %s' % infn)
            os.chdir(curdir)
        else:
            dir = infn
    
        if not os.path.isdir(dir):
            print "Input argument should be directory name or moodle *.mbz backup file"
            sys.exit(0)
    
        self.edxdir = path(edxdir)
        if not os.path.exists('%s/html' % self.edxdir):
            os.mkdir(self.edxdir / 'html')
        if not os.path.exists('%s/problem' % self.edxdir):
            os.mkdir(self.edxdir / 'problem')

        mfn = 'moodle_backup.xml'	# top-level moodle backup xml
        qfn = 'questions.xml'	# moodle questions xml
    
        qdict = self.load_questions(dir,qfn)
    
        moodx = etree.parse('%s/%s' % (dir,mfn))
    
        info = moodx.find('.//information')
        name = info.find('.//original_course_fullname').text
        contents = moodx.find('.//contents')
    
        # start course.xml
        cxml = etree.Element('course', graceperiod="1 day 5 hours 59 minutes 59 seconds")
        cxml.set('name','OEITx')
    
        for activity in contents.findall('.//activity'):
            self.activity2chapter(dir,activity,cxml,qdict)
            
        chapter = cxml.find('chapter')
        name = name.replace('/',' ')
        chapter.set('name',name)	# use first chapter for course name (FIXME)
    
        cdir = self.edxdir
        os.popen('xmllint -format -o %s/course.xml -' % cdir,'w').write(etree.tostring(cxml,pretty_print=True))
            
    # convert activity to chapter
    
    def activity2chapter(self, dir,activity,cxml,qdict):
    
        adir = activity.find('directory').text
        title = activity.find('title').text
        category = activity.find('modulename').text
    
        if category=='url':
            print "--> URL %s (%s)" % (title,adir)
            print "*** skipping"
        elif category=='page':
            print "--> etext %s (%s)" % (title,adir)
    
            chapter = etree.SubElement(cxml,'chapter')
            chapter.set('name',title)
            section = etree.SubElement(chapter,'section')
            section.set('name','E-text')
            seq = etree.SubElement(section,'sequential')
            html = etree.SubElement(seq,'html')
            self.import_page(dir,adir,html)
    
        elif category=='quiz':
            print "--> problem %s (%s)" % (title,adir)
            chapter = etree.SubElement(cxml,'chapter')
            chapter.set('name',title)
            section = etree.SubElement(chapter,'section')
            section.set('name','E-text')
            self.import_quiz(dir,adir,section,qdict)
    
    def import_page(self, dir,adir,html):
        pxml = etree.parse('%s/%s/page.xml' % (dir,adir)).getroot()
        name = pxml.find('.//name').text
        html.set('name',name)
        fn = os.path.basename(adir)+name.replace(' ','_').replace('/','_') + '.html'
        htmlstr = pxml.find('.//content').text
        # htmlstr = saxutils.unescape(htmlstr)
        htmlstr = u'<html>\n' + htmlstr + u'\n</html>'
        codecs.open('%s/html/%s' % (self.edxdir, fn),'w',encoding='utf8').write(htmlstr)
        html.set('filename','%s' % fn)
    
    def import_quiz(self, dir,adir,section,qdict):
        qxml = etree.parse('%s/%s/quiz.xml' % (dir,adir)).getroot()
        name = qxml.find('.//name').text
        section.set('name',name)
        # TODO: import intro, do points
        seq = etree.SubElement(section,'sequential')
        for qinst in qxml.findall('.//question_instance'):
            qnum = qinst.find('question').text
            question = qdict[qnum]
            problem = etree.SubElement(seq,'problem')
            problem.set('rerandomize',"never")
            problem.set('showanswer','attempted')
            qname = question.find('name').text
            problem.set('name',qname)
            problem.set('filename',question.get('filename').replace('.xml',''))
            print "    --> question: %s" % qname
            self.export_question(question)
    
    #-----------------------------------------------------------------------------
    # write out question as an xml file
    
    @staticmethod
    def fix_math(s):
        '''
        attempt to turn $$xxx$$ into [mathjax]xxx[/mathjax]
        '''
        s = re.sub('\$\$([^\$]*?)\$\$','[mathjax]\\1[/mathjax]',s)
        return s
    
    def export_question(self, question):
        problem = etree.Element('problem')
        text = etree.SubElement(problem,'text')
        qtext = question.find('questiontext').text
        qtext = self.fix_math(qtext)
        qtext = '<html>%s</html>' % qtext
        # qtext = saxutils.unescape(qtext)
        text.append(etree.XML(qtext))
        qtype = question.find('.//qtype').text
    
        if qtype=='truefalse':
            options = []
            expect = ""
            for answer in question.findall('.//answer'):
                op = answer.find('answertext').text
                options.append(op)
                if float(answer.find('fraction').text)==1.0:
                    expect = str(op)
            optionstr = ','.join(['"%s"' % x.replace('"',"'") for x in options])
            abox = AnswerBox("type='option' expect='%s' options=%s" % (expect,optionstr))
            problem.append(abox.xml)
    
        elif qtype=='multichoice':
            options = []
            expect = ""
            for answer in question.findall('.//answer'):
                op = answer.find('answertext').text
                op = op.replace(u'\xa0',' ')
                options.append(op)
                if float(answer.find('fraction').text)==1.0:
                    expect = str(op)
            optionstr = ','.join(['"%s"' % x.replace('"',"'") for x in options])
            abox = AnswerBox("type='multichoice' expect='%s' options=%s" % (expect,optionstr))
            problem.append(abox.xml)
    
        pfn = question.get('filename')
        os.popen('xmllint -format -o %s/problem/%s -' % (self.edxdir, pfn),'w').write(etree.tostring(problem,pretty_print=True))
        print "        wrote %s" % pfn
            
    
    #-----------------------------------------------------------------------------
    # load all questions
    
    def load_questions(self, dir,qfn):
        qdict = {}
        moodq = etree.parse('%s/%s' % (dir,qfn))
        for question in moodq.findall('.//question'):
            id = question.get('id')
            if id is None: continue
            qdict[id] = question
            try:
                name = question.find('.//name').text
                question.set('filename',name.replace(' ','_').replace('.','_') + '.xml')
            except Exception as err:
                print "** Error: can't get name for question id=%s" % question.get('id')
        return qdict
    
#--------------------------------------------------------------------------
# main

if __name__=='__main__':
    if len(sys.argv)<2:
        print "Usage: python moodle2edx.py [ backup-file.mbz | backup-directory ]"
        sys.exit(0)
    infn = sys.argv[1]
    sys.argv.pop(1)
    edxdir = '.'
    if len(sys.argv)>1:
        edxdir = sys.argv[1]

    print "importing %s to %s" % (infn, edxdir)

    m2e = Moodle2Edx(infn, edxdir)
    
