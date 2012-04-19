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
baseLeft = 100
baseTop = 200

outputScale = 0.5

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
        
def log(string):
    #print '#%s'%string
    pass
    
def output(string):
    print string
    
def outputAddImage(left,top,width,height,filename,parentName):
    viewName = 'imageView'
    if filename[-7:]=='@2x.png':
        filename = filename[:-7]+'.png'
    
    print '    UIImageView *%s = [[UIImageView alloc] init];'%viewName
    print '    %s.frame = CGRectMake(%.1ff, %.1ff, %.1ff, %.1ff)];'%(viewName,left,top,width,height)
    print '    %s.image = [UIImage imageNamed:@"%s"];'%(viewName,filename)
    print '    [%s addSubview:%s];'%(parentName,viewName)
    print '    [%s release];'%viewName
    print ''

def outputAddLabel(left,top,width,height,text,parentName,styleNames):
    viewName = 'label'
    styles = {}
    for styleName in styleNames:
        log(styleName)
        tempStyle = {}
        if styleName in styleVar.keys():
            tempStyle = styleVar[styleName]
            for key in tempStyle.keys():
                styles[key] = tempStyle[key]
    
    print '    UILabel *%s = [[UILabel alloc] init'%viewName
    print '    %s.frame = CGRectMake(%.1ff, %.1ff, %.1ff, %.1ff)];'%(viewName,left,top,width,height)
    print '    %s.text = @"%s";'%(viewName,text)
    if 'fontName' in styles.keys():
        print '    //fontName:%s'%styles['fontName']
    if 'fontSize' in styles.keys():
        print '    %s.font = [UIFont systemFontOfSize:%.1ff];'%(viewName,float(styles['fontSize'])*outputScale)
    if 'fontColor' in styles.keys():
        color = styles['fontColor'];
        print '    %s.textColor = [UIColor colorWithRed:%.2f green:%.2f blue:%.2f alpha:%.2f];'%(viewName,float(color['R']),float(color['G']),float(color['B']),float(color['A']))
    #print '    statusLabel.shadowColor = [UIColor darkGrayColor];'
    #print '    statusLabel.shadowOffset = CGSizeMake(0.0f, -1.0f);'
    print '    %s.backgroundColor = [UIColor clearColor];'%viewName
    print '    [%s addSubview:%s];'%(parentName,viewName)
    print '    [%s release];'%viewName
    print ''


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
    log( ' position:%s,%s'%(position.getAttribute('sfa:x'),
                            position.getAttribute('sfa:y')))
    log( ' size:%s,%s'%(size.getAttribute('sfa:w'),
                         size.getAttribute('sfa:h')))
    return (float(position.getAttribute('sfa:x'))*outputScale,
            float(position.getAttribute('sfa:y'))*outputScale,
            float(size.getAttribute('sfa:w'))*outputScale,
            float(size.getAttribute('sfa:h'))*outputScale)

def parseStyleRefId(drawObj):
    style = getElm(drawObj,'sf:style')
    graphicStyleRef = getElm(style,'sf:graphic-style-ref')
    if graphicStyleRef:
        graphicStyleRefID = graphicStyleRef.getAttribute('sfa:IDREF')
        log( ' styleRefID:%s'%graphicStyleRefID )
        if (graphicStyleRefID in styleVar.keys()):
            log( styleVar[graphicStyleRefID] )
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
        
def parseDrawables(drawables,baseLeft,baseTop):
    for drawObj in drawables.childNodes:
        if drawObj.tagName == 'sf:media':
            imageMedia = getElm(getElm(drawObj,'sf:content'),'sf:image-media')
            log( imageMedia.tagName )
            if imageMedia.tagName=='sf:image-media':
                left,top,width,height=parseGeometory(drawObj)
                parseStyleRefId(drawObj)
                
                unfiltered = getElm(getElm(imageMedia,'sf:filtered-image'),'sf:unfiltered')
                unfilteredRef = getElm(getElm(imageMedia,'sf:filtered-image'),'sf:unfiltered-ref')
                if unfiltered!=None:
                    id = unfiltered.getAttribute('sfa:ID')
                    data = getElm(unfiltered,'sf:data')
                    path = data.getAttribute('sf:path')
                    log( ' filePath:%s'%(path) )
                    
                    if path[-4:]=='.jpg':
                        baseLeft = left
                        baseTop = top
                    else:
                        outputAddImage(left-baseLeft,top-baseTop,width,height,path,'self')
                    
                    unfilteredImages[id]=path
                    
                    tracedPath = getElm(imageMedia,'sf:traced-path')
                    if tracedPath:
                        log( ' tracedPath:%s'%(tracedPath.getAttribute('sfa:path')) )
                elif unfilteredRef:
                    id = unfilteredRef.getAttribute('sfa:ID')
                    if id in unfilteredImages.keys():
                        path = unfilteredImages[id]
                        log( ' filePath:%s'%(path) )
                        
                    pass
                #mediaType = drawObj.getElementsByTagName('st:content')[0].childNodes #[0].tagName
                #print 
        elif drawObj.tagName == 'sf:shape':
            log( "shape")
            left,top,width,height=parseGeometory(drawObj)
            styleRefId=parseStyleRefId(drawObj)
            
            path = getElm(drawObj,'sf:path')
            if path:
                bezierPath =getElm(path,'sf:bezier-path')
                if bezierPath:
                    bezier = getElm(bezierPath,'sf:bezier')
                    id = bezier.getAttribute('sfa:ID')
                    log ( ' bezier:%s'%(bezier.getAttribute('sfa:path')) )
                    #outputDraws = []
                    outputDraws = createSrcOfBezier(id,bezier,styleRefId,left,top)
                    for line in outputDraws:
                        log( line )
                pointPath = getElm(path,'sf:point-path')
                if pointPath:
                    log (' point-path:%s'%(pointPath.getAttribute('sf:type')) )
                    point = getElm(pointPath,'sf:point')
                    size = getElm(pointPath,'sf:size')
                    log( '  point:%s,%s'%(point.getAttribute('sfa:x'),
                                            point.getAttribute('sfa:y')))
                    log( '  size:%s,%s'%(size.getAttribute('sfa:w'),
                                         size.getAttribute('sfa:h')))
            text = getElm(drawObj,'sf:text')
            if text:
                textStorage = getElm(drawObj,'sf:text-storage')
                textBody = getElm(textStorage,'sf:text-body')
                pList = getElmList(textBody,'sf:p')
                log( ' pList:%s'%(pList) )
                # UnicodeDecodeError: 'ascii' codec can't decode byte 0xc2 in position 0: ordinal not in range(128)
                for p in pList:
                    text = getText(p)
                    pStyleName = p.getAttribute('sf:style')
                    if len(text)>0:
                        outputAddLabel(left-baseLeft,top-baseTop,width,height,text,'self',[pStyleName])
                    spanList = getElmList(p,'sf:span')
                    for span in spanList:
                        text = getText(span)
                        if len(text)>0:
                            spanStyleName = span.getAttribute('sf:style')
                            outputAddLabel(left-baseLeft,top-baseTop,width,height,text,'self',[pStyleName,spanStyleName])
                    

                text = '¥n'.join(getText(p) for p in pList)
                log( ' text:%s'%(text) )
                 
                
            
        elif drawObj.tagName == 'sf:group':
            log( 'group' )
            parseGeometory(drawObj)
            parseDrawables(drawObj,baseLeft,baseTop)
                
    #print 'hoge'
def parseColor(color):
    colorVar = {}
    #if color.hasAttributeAttributeAttribute('sfa:r'):
    colorVar['R'] = color.getAttribute('sfa:r')
    colorVar['G'] = color.getAttribute('sfa:g')
    colorVar['B'] = color.getAttribute('sfa:b')
    colorVar['A'] = color.getAttribute('sfa:a')
    return colorVar

def parseStyles(style):
    propertyVar = {}
    styleId = style.getAttribute('sfa:ID')
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
    elif style.tagName=='sf:paragraphstyle' or style.tagName=='sf:characterstyle':
        if len(propertyMap.childNodes)>0:
            fontColor = getElm(propertyMap,'sf:fontColor')
            if fontColor:
                color = getElm(fontColor,'sf:color')
                if color:
                    propertyVar['fontColor'] = parseColor(color)
            fontSize = getElm(propertyMap,'sf:fontSize')
            if fontSize:
                propertyVar['fontSize'] = getElm(fontSize,'sf:number').getAttribute('sfa:number')
            fontName = getElm(propertyMap,'sf:fontName')
            if fontName:
                propertyVar['fontName'] = getElm(fontName,'sf:string').getAttribute('sfa:string')
    
    styleVar[styleId] = propertyVar    


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

def pageCount(folderpath):
    dom1 = xml.dom.minidom.parse(os.path.join(folderpath,'index.apxl'))
    slides = getElmList(getElm(dom1,'key:slide-list'),'key:slide')
    c = len(slides)
    dom1.unlink
    return c

def parseDrawablesForBaseLeftTop(dom,drawables):
    baseLeft = 0;
    baseTop = 0;
    
    for drawObj in drawables.childNodes:
        if drawObj.tagName != 'sf:media':
            continue
        imageMedia = getElm(getElm(drawObj,'sf:content'),'sf:image-media')
        log( imageMedia.tagName )
        if imageMedia.tagName!='sf:image-media':
            continue
        
        left,top,width,height=parseGeometory(drawObj)
                
        unfiltered = getElm(getElm(imageMedia,'sf:filtered-image'),'sf:unfiltered')
        unfilteredRef = getElm(getElm(imageMedia,'sf:filtered-image'),'sf:unfiltered-ref')
        if unfilteredRef!=None:
            refId = unfilteredRef.getAttribute('sfa:IDREF')
            elmList = [node for node in dom.getElementsByTagName("sf:unfiltered") 
                             if node.getAttribute('sfa:ID') == refId]
            if len(elmList)>0:
                unfiltered = elmList[0]
                             
        if unfiltered!=None:
            id = unfiltered.getAttribute('sfa:ID')
            log ("id:%s"%id)
            data = getElm(unfiltered,'sf:data')
            path = data.getAttribute('sf:path')
            if path=='__base.png':
                log("@@left:%d,top:%d"%(left,top))
                return left,top  # find !!
        
    return baseLeft,baseTop
                   

def getBaseLeftTopFromSlide(dom,slide):
    left = 0
    top = 0
    #key:master-slide/key:page/sf:layers/sf:layer/sf:drawables/sf:media:/(sf:geometory/sf:position,sf:content/sf:image-media/sf:filtered-image/sf:unfiltered:/sf:data[sf_path="__base.png"])
    
    layers = getElm(getElm(slide,'key:page'),'sf:layers')
    log(layers.childNodes)
    for layer in layers.childNodes:
        typeString = getElm(getElm(layer,'sf:type'),'sf:string').getAttribute('sfa:string')
        if typeString!='BGMasterSlideLayer':
            continue
            
        drawables = getElm(layer,'sf:drawables')
        log(drawables)
        left,top = parseDrawablesForBaseLeftTop(dom,drawables)
    
    return left,top

def parseApxm(dir,pageNum):
    #parseする。forgraundLayerまでたどり着き、あとはdrawablesをparseDrawablesに任せる
    
    #page番号はを0からはじめる
    #print sys.getrecursionlimit()
    print '===== page %d ====='%pageNum
    pageNum-=1
    log( os.path.join(dir,'index.apxl') )
    parsedDom = xml.dom.minidom.parse(os.path.join(dir,'index.apxl'))
    log( parsedDom.documentElement.tagName )     
    themes = getElmList(getElm(parsedDom,'key:theme-list'),'key:theme') # key:master-slides / key:master-slide sfa:ID="BGMasterSlide-3" / key:page
    slides = getElmList(getElm(parsedDom,'key:slide-list'),'key:slide')
    if (pageNum >= len(slides)):
        print 'Error:slides do not have page %d'%pageNum
        parsedDom.unlink()
        return 
    slide = slides[pageNum]
    
    stylesheet = getElm(slide,'key:stylesheet')
    styles = getElm(stylesheet,'sf:styles')
    anonStyles = getElm(stylesheet,'sf:anon-styles')
    for anonStyle in anonStyles.childNodes:
        parseStyles(anonStyle)
    
    baseLeft,baseTop = 0,0
    masterRefId = getElm(slide,'key:master-ref').getAttribute('sfa:IDREF')
    log ( 'masterRefId:%s'%masterRefId )
    for theme in themes:
        masterSlides = getElmList(getElm(theme, 'key:master-slides'),'key:master-slide')
        for masterSlide in masterSlides:
            masterId = masterSlide.getAttribute('sfa:ID')
            if masterId == masterRefId:
                baseLeft,baseTop = getBaseLeftTopFromSlide(parsedDom,masterSlide)
                log ( 'x:%d,y%d'%(baseTop,baseLeft) )
                break
    
    layers = getElm(getElm(slide,'key:page'),'sf:layers')
    # key:page->sf:layers->sf;layer[sf:type->sf:string.sfa:string='BGSlideForegroundLayer']
    # ->sf:drawables->sf:media
    for layer in layers.childNodes:
        typeString = getElm(getElm(layer,'sf:type'),'sf:string').getAttribute('sfa:string')
        if typeString!='BGSlideForegroundLayer':
            continue
        drawables = getElm(layer,'sf:drawables')
        parseDrawables(drawables,baseLeft,baseTop)

#    n = slide
#    print getText(n)
#    print n.getAttribute('sfa:ID')
#    print n.getAttribute('key:depth')
    parsedDom.unlink()

def main():
    if len(sys.argv) <2:
        print 'Usage :'
        print '  $ python Keynote2iOS.py filename'
        quit()
    path = os.path.abspath(sys.argv[1])
    folderpath = unarchive(path)
    pages = pageCount(folderpath)
    for i in range(1,pages+1):
        parseApxm(folderpath,i)

if __name__ == '__main__': main()
