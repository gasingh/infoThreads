"""
genearate x random points on a surface
create a random set of connections

15:06 16/08/2023
"""

import Rhino.Geometry as rg
import rhinoscriptsyntax as rs
import scriptcontext
import math
import random
import itertools

# ==============================================================================
def averagePointRC(vLst):
    
    xTotal = map(lambda v: v.X,vLst)
    xAvg = sum(xTotal)/len(xTotal)
    yTotal = map(lambda v: v.Y,vLst)
    yAvg = sum(yTotal)/len(yTotal)
    zTotal = map(lambda v: v.Z,vLst)
    zAvg = sum(zTotal)/len(zTotal)
    
    ptCentroid = rg.Point3d(xAvg,yAvg,zAvg)
    return ptCentroid

def lineBundleToCurvedBundleRC(lnRCLst):
    lnRCLst = map(lambda v: v.ToNurbsCurve(),lnRCLst)
    for i,j in enumerate(lnRCLst):
        j.Domain = rg.Interval(0,1)
    
    #queryParam1 = 0.25 #from 0 to 1
    #queryParam2 = 0.75 #from 0 to 1
    
    #shiftParam = 0.25
    #queryParam1 = random.uniform(0.0,shiftParam)
    #queryParam2 = random.uniform(shiftParam-0.01,0.99)
    
    uBound = 0.95
    lBound = 0.75
    queryParam1 = random.uniform(lBound,uBound)
    queryParam2 = queryParam1-0.25
    
    ptMid1 = map(lambda v: v.PointAt(queryParam1),lnRCLst)
    ptMidA = averagePointRC(ptMid1)
    ptMid11 = [ptMidA]*len(lnRCLst)
    ptMid2 = map(lambda v: v.PointAt(queryParam2),lnRCLst)
    ptMidB = averagePointRC(ptMid2)
    ptMid22 = [ptMidB]*len(lnRCLst)
    ptA = map(lambda v: v.PointAtStart,lnRCLst)
    ptB = map(lambda v: v.PointAtEnd,lnRCLst)
    ptLst = zip(ptA,ptMid11,ptMid22,ptB)
    crvBundleRC = map(lambda v: rg.Curve.CreateControlPointCurve(v),ptLst)
    #map(scriptcontext.doc.ActiveDoc.Objects.AddCurve,crvBundleRC)
    
    return crvBundleRC

# ==============================================================================

strID = rs.GetObject("sel srf", rs.filter.surface)
strRC = rs.coercesurface(strID)

numOfPts = 45
connectionLength = 15

rs.EnableRedraw(False)

# GENERATE RANDOM POINTS ON A SURFACE

strRC.SetDomain(0,rg.Interval(0,1))
strRC.SetDomain(1,rg.Interval(0,1))

#numOfPts = 200
rndNum = lambda : random.random()
ptLst = [strRC.PointAt(rndNum(),rndNum()) for i in range(numOfPts)]
#ptLstID = map(scriptcontext.doc.ActiveDoc.Objects.AddPoint,ptLst)
#rs.AddObjectsToGroup(ptLstID,rs.AddGroup())

# LET EVERY POINT CONNECT RANDOMLY TO 5 OTHER POINTS WITH A LINE
#connectionLength = 50
lnColl = []
###print(len(ptLst))
indexLst = [i for i in range(len(ptLst))]
randomIndexFromRange = lambda vIndexLstLocal: random.choice(vIndexLstLocal)
for i,j in enumerate(ptLst):
    ###print i
    indexLstLocal = indexLst[:]
    del indexLstLocal[i]
    ###print indexLstLocal
    lnLstLocal = []
    localPts = []
    for m,n in enumerate(range(connectionLength)):
        ###print("...",m)
        randomIndex = randomIndexFromRange(indexLstLocal)
        ###print randomIndex
        #localPts.append(ptLst[randomIndex])
        lnLstLocal.append(rg.Line(ptLst[i],ptLst[randomIndex]))
    lnColl.append(lnLstLocal)

lnIDColl = []
for i,j in enumerate(lnColl):
    collCrvsLocal = lineBundleToCurvedBundleRC(j)
    lnID = map(scriptcontext.doc.ActiveDoc.Objects.AddCurve,collCrvsLocal)
    rs.AddObjectsToGroup(lnID,rs.AddGroup())
    lnIDColl.append(lnID)

#rs.LastCreatedObjects(True)

lnIDCollFlat = sum(lnIDColl,[])
###print len(lnIDCollFlat)
rs.SelectObjects(lnIDCollFlat)
rs.Command("_ColRandomByGroup enter",True)
rs.UnselectAllObjects()
# CREATE A MASTER ADMIN GROUP
#rs.AddObjectsToGroup(sum(lnIDColl,[]),rs.AddGroup())
# HIDE INPUT SPHERE
#rs.HideObject(strID)

# ==============================================================================
#for i,j in enumerate(lnColl):
#    lineBundleToCurvedBundleRC(j)

print("just generated:", str(len(sum(lnIDColl,[]))), " curves!")

rs.EnableRedraw(True)

