#!/usr/bin/env python

#-------------------------------------------------------------------------------
# Copyright (c) 2010 Patrick Mueller
# Licensed under the MIT license: 
# http://www.opensource.org/licenses/mit-license.php
#-------------------------------------------------------------------------------

import os
import re
import sys
import urllib2
import urlparse
import datetime

PROGRAM = os.path.basename(sys.argv[0])
VERSION = "1.0.0"

ARTICLES_URL  = "http://developer.android.com/resources/articles/index.html"
ARTICLES_BASE = "http://developer.android.com/resources/articles/"

#-------------------------------------------------------------------------------
def main(): 

    if False:
        if os.path.exists("out"):
            if not os.path.isdir("out"):
                error("file 'out' exists but is not a directory")
        
        else:
            os.mkdir("out")

    log("reading: %s" % ARTICLES_URL)
    iFile = urllib2.urlopen(ARTICLES_URL)
    contents = iFile.read()
    iFile.close()
    
    pattern = r'.*?<dt><a href="(.*?)">(.*?)</a></dt>\s*<dd>(.*?)</dd>(.*)'
    pattern = re.compile(pattern, re.DOTALL)
    
    articles = []
        
    while contents != "":
        match = pattern.match(contents)
        if not match:
            break
            
        url    = match.group(1)
        title  = toHTML(match.group(2))
        descr  = toHTML(match.group(3))
        after  = match.group(4)

        url = urlparse.urljoin(ARTICLES_URL, url)

        article = Article(url, title, descr)
        articles.append(article)
        
        contents = after

    oFileName = "Android-Articles-for-Kindle.html"
    oFile = file(oFileName, "w")
    
    date = datetime.datetime.now().isoformat(" ")
    
    print >>oFile, getHtmlHead()
    print >>oFile
    print >>oFile, '<mbp:section>'
    print >>oFile, '<a name="TOC"/><a name="start"/>'
    print >>oFile, "<h1>Android Articles</h1>"
    print >>oFile, "<p>Generated on %s" % (date)
    print >>oFile, "<p>Generated by %s %s" % (PROGRAM, VERSION)
    print >>oFile

    for article in articles:
        url   = article.url
        title = article.titleHTML()
        descr = article.descrHTML()
        frag  = article.fragment()
        
        print >>oFile, '<p>'
        print >>oFile, '<h2><a href="#%s">%s</a></h2>' % (frag, title)
        print >>oFile, '<p>%s' % descr
        print >>oFile
            
    for article in articles:
        title = article.titleHTML()
        frag  = article.fragment()
        print >>oFile, '<guide><reference type="toc" title="%s" href="#%s"/></guide>' % (title, frag)

    print >>oFile
    
    
    print >>oFile, '</mbp:section>'
    print >>oFile
        
    for article in articles:
        url   = article.url
        title = article.titleHTML()
        frag  = article.fragment()
        
        contents = article.content()
        
        print >>oFile, '<div class="page-break"> </div>'
        print >>oFile, '<mbp:pagebreak/>'
        print >>oFile, '<mbp:section>'
        print >>oFile, '<a id="%s"></a>' % frag
        print >>oFile
        print >>oFile, '<!-- ============================================= -->'
        print >>oFile, contents
        print >>oFile, '<!-- ============================================= -->'
        print >>oFile
        print >>oFile, '<p>Content originally from: <a href="%s">%s</a>' % (url, url)
        print >>oFile, '</mbp:section>'
        print >>oFile
        
    print >>oFile, '</body>'
    print >>oFile, '</html>'

    log("writing: %s" % oFileName)

    oFile.close()

#-------------------------------------------------------------------------------
class Article:

    #---------------------------------------------------------------------------
    def __init__(self, url, title, descr):
        self.url     = url
        self.title   = title
        self.descr   = descr
        self._content = None

    #---------------------------------------------------------------------------
    def content(self):
        if self._content: return self._content
        
        log("reading: %s" % self.url)
        
        iFile = urllib2.urlopen(self.url)
        contents = iFile.read()
        iFile.close()
        
        patternStart = r'<div class="g-unit" id="doc-content"><a name="top"></a>'
        patternEnd   = r'</div><!-- end doc-content -->'
        patternFull  = ".*" + patternStart + "(.*)" + patternEnd + ".*"    
        
        pattern = re.compile(patternFull, re.DOTALL)
        
        contents = pattern.sub(r"\1", contents)
        
#        patternImg = r'(<img.*?\ssrc=")(.*?)"(.*?)>'
#        pattern = re.compile(patternImg, re.DOTALL)
        
#        contents = pattern.sub(r"\1%s\2" % ARTICLES_BASE, contents)

        self._contents = contents        
    
        return self._contents        

    #---------------------------------------------------------------------------
    def fragment(self):
        return os.path.basename(urlparse.urlparse(self.url)[2])

    #---------------------------------------------------------------------------
    def titleHTML(self):
        return toHTML(self.title)

    #---------------------------------------------------------------------------
    def descrHTML(self):
        return toHTML(self.descr)


#-------------------------------------------------------------------------------
def toHTML(string):
    string = string.replace("&", "&amp;")
    string = string.replace("<", "&lt;")
    string = string.replace(">", "&gt;")
    return string


#-------------------------------------------------------------------------------
def log(message):
    print "%s: %s" % (PROGRAM, message)

#-------------------------------------------------------------------------------
def error(message):
    log(message)
    exit(1)

#-------------------------------------------------------------------------------
def errorException(message):
    eType  = str(sys.exc_info()[0])
    eValue = str(sys.exc_info()[1])
    
    error("%s; exception: %s: %s" % (message, eType, eValue))

#-------------------------------------------------------------------------------
def getHtmlHead():
    return """
<html>
<head>
<title>Android Articles</title>
<style>
@media print {
    body {
        font-size:      150%;
    }
}

h1 {
    background-color:   #DDD;
    padding:            5px 0px;
    border-radius:      0.5em;
    -moz-border-radius: 0.5em;
}

pre {
    margin-top:         5px;
    background-color:   #EEE;
    padding:            5px 10px;
    border-radius:      1.0em;
    -moz-border-radius: 1.0em;
    overflow:           hidden;
    font-size:          75%;
}

p {
    margin-top:         5px;
    text-indent:        0px;
}

.title-toc {
    font-size:          120%;
    font-weight:        bold;
}

.toc li {
    list-style-type:    none;
}

.page-break {
    page-break-after:   always;
}
</style>
</head>
<body>
""".strip()

#-------------------------------------------------------------------------------
def getHelp():
    return """
downloads and formats Technical Articles from the 
developer.android.com site
    """.strip()

#-------------------------------------------------------------------------------
if __name__ == '__main__':
    main()

