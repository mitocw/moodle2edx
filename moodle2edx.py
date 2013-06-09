
#!/usr/bin/python
#
# File:   moodle2edx.py
# Date:   19-July-2012
# Author: I. Chuang <ichuang@mit.edu>
#
# script to convert a moodle class into an edX course

import os, sys, string, re
import codecs
from lxml import etree
from abox import AnswerBox
import xml.sax.saxutils as saxutils

dir = 'moodle-oeit'		# directory with the moodle backup files

#-----------------------------------------------------------------------------
# convert activity to chapter

def activity2chapter(dir,activity,cxml,qdict):

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
        import_page(dir,adir,html)

    elif category=='quiz':
        print "--> problem %s (%s)" % (title,adir)
        chapter = etree.SubElement(cxml,'chapter')
        chapter.set('name',title)
        section = etree.SubElement(chapter,'section')
        section.set('name','E-text')
        import_quiz(dir,adir,section,qdict)

def import_page(dir,adir,html):
    pxml = etree.parse('%s/%s/page.xml' % (dir,adir)).getroot()
    name = pxml.find('.//name').text
    html.set('name',name)
    fn = os.path.basename(adir)+name.replace(' ','_').replace('/','_') + '.html'
    htmlstr = pxml.find('.//content').text
    # htmlstr = saxutils.unescape(htmlstr)
    htmlstr = u'<html>\n' + htmlstr + u'\n</html>'
    codecs.open('html/%s' % fn,'w',encoding='utf8').write(htmlstr)
    html.set('filename','%s' % fn)

def import_quiz(dir,adir,section,qdict):
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
        export_question(question)

#-----------------------------------------------------------------------------
# write out question as an xml file

def fix_math(s):
    '''
    attempt to turn $$xxx$$ into [mathjax]xxx[/mathjax]
    '''
    s = re.sub('\$\$([^\$]*?)\$\$','[mathjax]\\1[/mathjax]',s)
    return s

def export_question(question):
    problem = etree.Element('problem')
    text = etree.SubElement(problem,'text')
    qtext = question.find('questiontext').text
    qtext = fix_math(qtext)
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
    os.popen('xmllint -format -o problems/%s -' % pfn,'w').write(etree.tostring(problem,pretty_print=True))
    print "        wrote %s" % pfn
        

#-----------------------------------------------------------------------------
# load all questions

def load_questions(dir,qfn):
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

#-----------------------------------------------------------------------------
# main

if 1:
    mfn = 'moodle_backup.xml'	# top-level moodle backup xml
    qfn = 'questions.xml'	# moodle questions xml

    qdict = load_questions(dir,qfn)

    moodx = etree.parse('%s/%s' % (dir,mfn))

    info = moodx.find('.//information')
    name = info.find('.//original_course_fullname').text
    contents = moodx.find('.//contents')

    # start course.xml
    cxml = etree.Element('course', graceperiod="1 day 5 hours 59 minutes 59 seconds")
    cxml.set('name','OEITx')

    for activity in contents.findall('.//activity'):
        activity2chapter(dir,activity,cxml,qdict)
        
    chapter = cxml.find('chapter')
    name = name.replace('/',' ')
    chapter.set('name',name)	# use first chapter for course name (FIXME)

    cdir = '..'
    os.popen('xmllint -format -o %s/course.xml -' % cdir,'w').write(etree.tostring(cxml,pretty_print=True))
    
