#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
Created on 2009/09/30

@author: hirobe
'''
import sys, zipfile, os, os.path
import xml.dom.minidom


#parseでmaximum recursion depthが起きないように
sys.setrecursionlimit(100000)

headerHight = 20
frameX = 100
frameY = 200

styleVar = {}
outputDraws = []
unfilteredImages = {}

class MyClass(object):
    '''
    classdocs
    '''


    def __init__(self,params):
        '''
        Constructor
        '''
def getText(node):
    ret = []
    for n in node.childNodes:
        if n.nodeType in [node.TEXT_NODE, node.COMMENT_NODE]:
            if n.data !=None:
                ret.append(n.data)
    return ''.join(ret)

#entries = []
#for n = doc.getElementsByTagName('entry')
#    link = n.getElementByTagName('link').item(0).getAttribute('href')
#    title = getText(n.getElementByTagName('title').item(0))
#    updated = getText(n.getElementByTagName('updated').item(0))
#    entries.append(dict(link=link, title=title, updated=updated))

def getElm(parentElement,tagName):
    elms = parentElement.getElementsByTagName(tagName)
#    elms = parentElement[tagName]
    if len(elms):
        return elms[0]
    return None

def getElmList(parentElement,tagName):
    elms = parentElement.getElementsByTagName(tagName)
    return elms

def parseGeometory(drawObj):
    geometry = getElm(drawObj,'sf:geometry')
    position = getElm(geometry,'sf:position')
    size = getElm(geometry,'sf:size')
    naturalSize = getElm(geometry,'sf:naturalSize')
    print ' position:%s,%s'%(position.getAttribute('sfa:x'),
                            position.getAttribute('sfa:y'))
    print ' size:%s,%s'%(size.getAttribute('sfa:w'),
                         size.getAttribute('sfa:h'))
    return (position.getAttribute('sfa:x'),
                            position.getAttribute('sfa:y'))

def parseStyleRefId(drawObj):
    style = getElm(drawObj,'sf:style')
    graphicStyleRef = getElm(style,'sf:graphic-style-ref')
    if graphicStyleRef:
        graphicStyleRefID = graphicStyleRef.getAttribute('sfa:IDREF')
        print ' styleRefID:%s'%graphicStyleRefID
        if (graphicStyleRefID in styleVar.keys()):
            print styleVar[graphicStyleRefID]
    return graphicStyleRefID
            

def createSrcOfBezier(id,bezier,styleRef,posX,posY):
    ret = []
    bs = bezier.getAttribute('sfa:path').split(' ')
    if len(bs)==0:
        return ret
    ret.append('// path id:%s'%id);
    while len(bs)>0:
        type = bs.pop(0)
        if type == 'M':
            x = bs.pop(0)
            y = bs.pop(0)
            ret.append('CGContextMoveToPoint(context,%s+%s,%s+%s);'%(posX,x,posY,y))
        elif type == 'L':
            x = bs.pop(0)
            y = bs.pop(0)
            ret.append('CGContextAddLineToPoint(context,%s+%s,%s+%s);'%(posX,x,posY,y))
        elif type == 'C':
            x = bs.pop(0)
            y = bs.pop(0)
            x2 = bs.pop(0)
            y2 = bs.pop(0)
            x3 = bs.pop(0)
            y3 = bs.pop(0)
            ret.append('CGContextAddCurveToPoint(context,%s+%s,%s+%s,%s+%s,%s+%s,%s+%s,%s+%s);'%(posX,x,posY,y,posX,x2,posY,y2,posX,x3,posY,y3))
        elif type == 'Z':
            ret.append('CGContextClosePath(context);')
            break
    ret.append('CGContextStrokePath(context);')
    return ret
        
def parseDrawables(drawables):
    for drawObj in drawables.childNodes:
        if drawObj.tagName == 'sf:media':
            imageMedia = getElm(getElm(drawObj,'sf:content'),'sf:image-media')
            print imageMedia.tagName
            if imageMedia.tagName=='sf:image-media':
                parseGeometory(drawObj)
                parseStyleRefId(drawObj)
                
                unfiltered = getElm(getElm(imageMedia,'sf:filtered-image'),'sf:unfiltered')
                unfilteredRef = getElm(getElm(imageMedia,'sf:filtered-image'),'sf:unfiltered-ref')
                if unfiltered!=None:
                    id = unfiltered.getAttribute('sfa:ID')
                    data = getElm(unfiltered,'sf:data')
                    path = data.getAttribute('sf:path')
                    print ' filePath:%s'%(path)
                    unfilteredImages[id]=path
                    
                    tracedPath = getElm(imageMedia,'sf:traced-path')
                    if tracedPath:
                        print ' tracedPath:%s'%(tracedPath.getAttribute('sfa:path'))
                elif unfilteredRef:
                    id = unfilteredRef.getAttribute('sfa:ID')
                    if id in unfilteredImages.keys():
                        path = unfilteredImages[id]
                        print ' filePath:%s'%(path)
                        
                    pass
                #mediaType = drawObj.getElementsByTagName('st:content')[0].childNodes #[0].tagName
                print 
        elif drawObj.tagName == 'sf:shape':
            print "shape"
            posX,posY=parseGeometory(drawObj)
            styleRefId=parseStyleRefId(drawObj)
            
            path = getElm(drawObj,'sf:path')
            if path:
                bezierPath =getElm(path,'sf:bezier-path')
                if bezierPath:
                    bezier = getElm(bezierPath,'sf:bezier')
                    id = bezier.getAttribute('sfa:ID')
                    print ' bezier:%s'%(bezier.getAttribute('sfa:path'))
                    #outputDraws = []
                    outputDraws = createSrcOfBezier(id,bezier,styleRefId,posX,posY)
                    for line in outputDraws:
                        print line
                pointPath = getElm(path,'sf:point-path')
                if pointPath:
                    print ' point-path:%s'%(pointPath.getAttribute('sf:type'))
                    point = getElm(pointPath,'sf:point')
                    size = getElm(pointPath,'sf:size')
                    print '  point:%s,%s'%(point.getAttribute('sfa:x'),
                                            point.getAttribute('sfa:y'))
                    print '  size:%s,%s'%(size.getAttribute('sfa:w'),
                                         size.getAttribute('sfa:h'))
            text = getElm(drawObj,'sf:text')
            if text:
                textStorage = getElm(drawObj,'sf:text-storage')
                textBody = getElm(textStorage,'sf:text-body')
                pList = getElmList(textBody,'sf:p')
                print ' pList:%s'%(pList)
                # UnicodeDecodeError: 'ascii' codec can't decode byte 0xc2 in position 0: ordinal not in range(128)
                text = '¥n'.join(getText(p) for p in pList)
                print ' text:%s'%(text)
            print
        elif drawObj.tagName == 'sf:group':
            print 'group'
            parseGeometory(drawObj)
            parseDrawables(drawObj)
            print
                
    #print 'hoge'
def parseColor(color):
    colorVar = {}
    #if color.hasAttribute('sfa:r'):
    colorVar['R'] = color.getAttribute('sfa:r')
    colorVar['G'] = color.getAttribute('sfa:g')
    colorVar['B'] = color.getAttribute('sfa:b')
    colorVar['A'] = color.getAttribute('sfa:a')
    return colorVar

def parseStyles(style):
    styleId = style.getAttribute('sfa:ID')
    propertyVar = {}
    propertyMap = getElm(style,'sf:property-map')
    if style.tagName == 'sf:graphic-style':
        for property in propertyMap.childNodes:
            if property.tagName == 'sf:opacity':
                propertyVar['opacity'] = True
                propertyVar['opacityValue'] = getElm(property,'sf:number').getAttribute('sfa:number')
                propertyVar['opacityType'] = getElm(property,'sf:number').getAttribute('sfa:type')
            elif property.tagName == 'sf:fill':
                color = getElm(property,'sf:color')
                if color:
                    propertyVar['fillColor'] = parseColor(color)
                angleGradient = getElm(property,'sf:angle-gradient')
                if angleGradient:
                    propertyVar['angleGradientOpacity'] = angleGradient.getAttribute('sf:opacity')
                    propertyVar['angleGradientAngle'] = angleGradient.getAttribute('sf:angle')
                    propertyVar['angleGradientType'] = angleGradient.getAttribute('sf:type')
                    stopsVar = []
                    stops = getElm(property,'sf:stops')
                    for stop in stops.childNodes:
                        stopVar = {}
                        stopVar['fraction'] = stop.getAttribute('sf:fraction')
                        stopVar['inflection'] = stop.getAttribute('sf:inflection')
                        stopsVar.append(stopVar)
                    propertyVar['angleGradientStops'] = stopsVar
            
                    #propertyVar['fillColorType'] = getElm(property,'xsi:type').getAttribute('sfa:number')
            elif property.tagName == 'sf:stroke':
                stroke = getElm(property,'sf:stroke')
                propertyVar['stroke'] = True
                propertyVar['strokeWidth'] = stroke.getAttribute('sf:width')
                propertyVar['strokeCap'] = stroke.getAttribute('sf:cap')
                propertyVar['strokeJoin'] = stroke.getAttribute('sf:join')
                strokeColor = getElm(stroke,'sf:color')
                if strokeColor:
                    propertyVar['strokeColor'] = parseColor(strokeColor)
                #strokePattern = getElm(stroke,'sf:pattern')
        styleVar[styleId] = propertyVar
    elif style.tagName=='sf:paragraphstyle':
        if len(propertyMap.childNodes)>0:
            fontColor = getElm(propertyMap,'sf:fontColor')
            if fontColor:
                color = getElm(fontColor,'sf:color')
                if color:
                    propertyVar['fontColor'] = parseColor(color)
            fontSize = getElm(propertyMap,'sf:fontSize')
            propertyVar['fontSize'] = getElm(fontSize,'sf:number').getAttribute('sfa:number')
    
    styleVar[styleId] = propertyVar    


def parseApxm(dir,pageNum):
    #parseする。forgraundLayerまでたどり着き、あとはdrawablesをparseDrawablesに任せる
    
    #page番号はを0からはじめる
    pageNum-=1
    #print sys.getrecursionlimit()
    print 'parsing'
    print os.path.join(dir,'index.apxl')
    dom1 = xml.dom.minidom.parse(os.path.join(dir,'index.apxl'))
    print dom1.documentElement.tagName        
    slides = getElmList(getElm(dom1,'key:slide-list'),'key:slide')
    if (pageNum >= len(slides)):
        print 'Error:slides do not have page %d'%pageNum
        dom1.unlink()
        return 
    slide = slides[pageNum]
    
    stylesheet = getElm(slide,'key:stylesheet')
    styles = getElm(stylesheet,'sf:styles')
    anonStyles = getElm(stylesheet,'sf:anon-styles')
    for anonStyle in anonStyles.childNodes:
        parseStyles(anonStyle)
    
    
    layers = getElm(getElm(slide,'key:page'),'sf:layers')
    # key:page->sf:layers->sf;layer[sf:type->sf:string.sfa:string='BGSlideForegroundLayer']
    # ->sf:drawables->sf:media
    for layer in layers.childNodes:
        typeString = getElm(getElm(layer,'sf:type'),'sf:string').getAttribute('sfa:string')
        #print typeString
        if typeString=='BGSlideForegroundLayer':
            drawables = getElm(layer,'sf:drawables')
            parseDrawables(drawables)

#    n = slide
#    print getText(n)
#    print n.getAttribute('sfa:ID')
#    print n.getAttribute('key:depth')
    dom1.unlink()
    print 'end parsing'

def unarchive(zipFilePath):
    ## translate to absolate path
    #if os.path.exists(filePath)==False:
    #    filePath = os.path.join(os.getcwdu(),filePath)

    dir,ext = os.path.splitext(zipFilePath)
    
    if os.path.exists(zipFilePath)==False:
        return False,'%s is not exist'%zipFilePath,dir
    if ext != '.key':
        return False,'%s is not KeyNote09 file'%zipFilePath,dir
    if os.path.exists(dir):
        if os.path.isdir(dir):
            print '%s is already exist.' %dir
            print 'overwriting %s ...' %dir
        else:
            return False,'%s is already exist as file. remove it! '%dir,dir
    else:
        os.mkdir(dir, 0777)


    
    print 'unarchiving %s ...'%zipFilePath
    
    zfobj = zipfile.ZipFile(zipFilePath)
    for name in zfobj.namelist():
        file = os.path.join(dir, name)
        if name.endswith('/'):
            if (os.path.exists(file)==False):
                os.makedirs(file,0777)
        else:
            if os.path.dirname(name) != '':
                subdir = os.path.join(dir, os.path.dirname(name))
                #print subdir
                if (os.path.exists(subdir)==False):
                    os.makedirs(subdir,0777)
            
            outfile = open(file, 'wb')
            outfile.write(zfobj.read(name))
            outfile.close()

    print 'unarchive end.',None,dir
    return dir


def main():
    if len(sys.argv) <2:
        print 'Usage : # python Keynote2iOS.py filename'
        quit()
    path = os.path.abspath(sys.argv[1])
    folderpath = unarchive(path)
    parseApxm(folderpath,2)

if __name__ == '__main__': main()
