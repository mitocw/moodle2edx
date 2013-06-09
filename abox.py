#!/usr/bin/python
#
# Answer Box class
#
# object representation of abox, used in Tutor2, now generalized to latex and word input formats.

import os, sys, string ,re
import shlex	# for split keeping quoted strings intact
import csv	# for splitting quoted options

from lxml import etree

class AnswerBox(object):
    def __init__(self,aboxstr):
        '''
        Parse a TUT abox and produce edX XML for a problem responsetype.

        Examples:
        -----------------------------------------------------------------------------
        <abox type="option" expect="float" options=" ","noneType","int","float"' />
        
        <optionresponse>
        <optioninput options="('noneType','int','float')"  correct="int">
        </optionresponse>
        
        -----------------------------------------------------------------------------
        <abox type="string" expect="Michigan" options="ci" />
        
        <stringresponse answer="Michigan" type="ci">
        <textline size="20" />
        </stringresponse>
        
        -----------------------------------------------------------------------------
        <abox type="custom" expect="(3 * 5) / (2 + 3)" cfn="eq" />
        
        <customresponse cfn="eq">
        <textline size="40" correct_answer="(3 * 5) / (2 + 3)"/><br/>
        </customresponse>
        
        -----------------------------------------------------------------------------
        <abox type="numerical" expect="3.141" tolerance="5%" />
        
        <numericalresponse answer="5.0">
        <responseparam type="tolerance" default="5%" name="tol" description="Numerical Tolerance" />
        <textline />
        </numericalresponse>
        
        -----------------------------------------------------------------------------
	<abox type="multichoice" expect="Yellow" options="Red","Green","Yellow","Blue" />

        <multiplechoiceresponse direction="vertical" randomize="yes">
         <choicegroup type="MultipleChoice">
            <choice location="random" correct="false" name="red">Red</choice>
            <choice location="random" correct="true" name="green">Green</choice>
            <choice location="random" correct="false" name="yellow">Yellow</choice>
            <choice location="bottom" correct="false" name="blue">Blue</choice>
         </choicegroup>
        </multiplechoiceresponse>
        -----------------------------------------------------------------------------
        '''
        self.xml = self.abox2xml(aboxstr)
        self.xmlstr = etree.tostring(self.xml)
        
    def abox2xml(self,aboxstr):
        if aboxstr.startswith('abox '): aboxstr = aboxstr[5:]
        s = aboxstr
        s = s.replace(' in_check= ',' ')

        # parse answer box arguments into dict
        abargs = self.abox_args(s)

        if 'tests' in abargs:
            abtype = 'externalresponse'
        elif 'type' in abargs and abargs['type']=='numerical':
            abtype = 'numericalresponse'
        elif 'type' in abargs and abargs['type']=='multichoice':
            abtype = 'multiplechoiceresponse'
        elif 'type' not in abargs and 'options' in abargs:
            abtype = 'optionresponse'
        elif 'type' in abargs and abargs['type']=='option':
            abtype = 'optionresponse'
        elif 'cfn' in abargs:
            abtype = 'customresponse'
        elif 'type' in abargs and abargs['type']=='string':
            abtype = 'stringresponse'
        else:
            abtype = 'symbolicresponse'	# default
        
        abxml = etree.Element(abtype)

        if abtype=='optionresponse':
            oi = etree.Element('optioninput')
            optionstr, options = self.get_options(abargs)
            oi.set('options',optionstr)
            oi.set('correct',self.stripquotes(abargs['expect']))
            abxml.append(oi)
            
        if abtype=='multiplechoiceresponse':
            cg = etree.SubElement(abxml,'choicegroup')
            cg.set('direction','vertical')
            optionstr, options = self.get_options(abargs)
            expect = self.stripquotes(abargs['expect'])
            cnt = 1
            for op in options:
                choice = etree.SubElement(cg,'choice')
                choice.set('correct','true' if op==expect else 'false')
                choice.set('name',str(cnt))
                choice.text = op
                cnt += 1
            
        elif abtype=='stringresponse':
            tl = etree.Element('textline')
            if 'size' in abargs: tl.set('size',self.stripquotes(abargs['size']))
            abxml.append(tl)
            abxml.set('answer',self.stripquotes(abargs['expect']))

        elif abtype=='customresponse':
            abxml.set('cfn',self.stripquotes(abargs['cfn']))
            self.copy_attrib(abargs,'expect',abxml)
            tl = etree.Element('textline')
            self.copy_attrib(abargs,'size',tl)
            abxml.append(tl)
            tl.set('correct_answer',self.stripquotes(abargs['expect']))
            
        elif abtype=='externalresponse':
            tb = etree.Element('textbox')
            self.copy_attrib(abargs,'rows',tb)
            self.copy_attrib(abargs,'cols',tb)
            self.copy_attrib(abargs,'tests',abxml)
            abxml.append(tb)
            # turn script to <answer> later

        elif abtype=='symbolicresponse':
            tl = etree.Element('textline')
            self.copy_attrib(abargs,'size',tl)
            tl.set('math','1')
            abxml.append(tl)
            self.copy_attrib(abargs,'options',abxml)
            abxml.set('answer',self.stripquotes(abargs['expect']))

        elif abtype=='numericalresponse':
            tl = etree.Element('textline')
            self.copy_attrib(abargs,'size',tl)
            abxml.append(tl)
            self.copy_attrib(abargs,'options',abxml)
            answer = self.stripquotes(abargs['expect'])
            try:
                x = float(answer)
            except Exception as err:
                print "Error - numericalresponse expects numerical expect value, for %s" % s
                raise
            abxml.set('answer',answer)
            rp = etree.SubElement(tl,"responseparam")
            rp.attrib['description'] = "Numerical Tolerance"
            rp.attrib['type'] = "tolerance"
            rp.attrib['default'] = abargs.get('tolerance') or "0.00001"
            rp.attrib['name'] = "tol"
        
        # has hint function?
        if 'hintfn' in abargs:
            hintfn = self.stripquotes(abargs['hintfn'])
            hintgroup = etree.SubElement(abxml,'hintgroup')
            hintgroup.set('hintfn',hintfn)

        s = etree.tostring(abxml,pretty_print=True)
        s = re.sub('(?ms)<html>(.*)</html>','\\1',s)
        # print s
        return etree.XML(s)

    def get_options(self,abargs):
        optstr = abargs['options']				# should be double quoted strings, comma delimited
        options = [c for c in csv.reader([optstr])][0]	# turn into list of strings
        options = [x.strip() for x in options]		# strip strings
        if "" in options: options.remove("")
        optionstr = ','.join(["'%s'" % x for x in options])	# string of single quoted strings
        optionstr = "(%s)" % optionstr				# enclose in parens
        return optionstr, options
    
    def abox_args(self,s):
        '''
        Parse arguments of abox.  Splits by space delimitation.
        '''
        s = s.replace(u'\u2019',"'")
        s = str(s)
        abargstxt = shlex.split(s)
        try:
            abargs = dict([x.split('=',1) for x in abargstxt])
        except Exception, err:
            print "Error %s" % err
            print "Failed in parsing args = %s" % s
            print "abargstxt = %s" % abargstxt
            raise
        return abargs

    def stripquotes(self,x):
        if x.startswith('"') and x.endswith('"'):
            return x[1:-1]
        return x

    def copy_attrib(self,abargs,aname,xml):
        if aname in abargs:
            xml.set(aname,self.stripquotes(abargs[aname]))

        
