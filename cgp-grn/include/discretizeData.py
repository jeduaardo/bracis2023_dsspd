import pandas as pd
import numpy as np
from csaps import csaps
from sklearn.model_selection import ShuffleSplit
import matplotlib.pyplot as plt
from os.path import exists
import gc
from time import perf_counter
from scipy import stats
import os
from sklearn.cluster import KMeans
from sklearn import preprocessing
import glob
import utils as Utils
import objects as Objs
import warnings
warnings.filterwarnings("ignore")

def meanDiscretization(geneName, expressionData, timePoints, outFileName):
    mean = np.mean(expressionData)
    currentDiscretization = []
    for ED in expressionData:
        if ED >= mean:
            currentDiscretization.append(1)
        else:
            currentDiscretization.append(0)
    currentDict = {}
    currentDict[geneName] = currentDiscretization
    df = pd.DataFrame(data = currentDict, index=timePoints)
    if os.path.exists(outFileName):
        df.T.to_csv(outFileName, mode='a', header=False)
    else:
        df.T.to_csv(outFileName, mode='a')            


def medianDiscretization(geneName, expressionData, timePoints, outFileName):
    # Funcionando como o GEDPROTOOLS
    median = np.median(expressionData)
    currentDiscretization = []
    for ED in expressionData:
        if ED >= median:
            currentDiscretization.append(1)
        else:
            currentDiscretization.append(0)
    currentDict = {}
    currentDict[geneName] = currentDiscretization
    df = pd.DataFrame(data = currentDict, index=timePoints)
    if os.path.exists(outFileName):
        df.T.to_csv(outFileName, mode='a', header=False)
    else:
        df.T.to_csv(outFileName, mode='a')

def DSSPDDiscretization(geneObject, outFileName):
    geneName = geneObject.geneName
    currentDiscretization = geneObject.splineStates
    currentDict = {}
    currentDict[geneName] = currentDiscretization
    timePoints = geneObject.sortedAllPT
    df = pd.DataFrame(data = currentDict, index=timePoints)
    if os.path.exists(outFileName):
        df.T.to_csv(outFileName, mode='a', header=False)
    else:
        df.T.to_csv(outFileName, mode='a')

def EWDDiscretization(geneName, expressionData, timePoints, LOD, outFileName):
    print("ToDo - EWD Discretization")


def TSDDiscretization(geneName, expressionData, timePoints, outFileName):
    zscored = stats.zscore(list(expressionData))
    discretizedData = []
    for i in range(len(zscored)):
        if i == 0:
            next
        else:
            dif = zscored[i] - zscored[i-1]
            if dif >= 0:
                discretizedData.append(1)
            else:
                discretizedData.append(0)
    discretizedData.insert(0, discretizedData[0])
    currentDict = {}
    currentDict[geneName] = discretizedData
    df = pd.DataFrame(data = currentDict, index=timePoints)
    if os.path.exists(outFileName):
        df.T.to_csv(outFileName, mode='a', header=False)
    else:
        df.T.to_csv(outFileName, mode='a')
    
    
def EFDDiscretization(geneName, expressionData, timePoints, LOD, outFileName):
    # Funcionando como o GEDPROTOOLS
    argsOrderedExpressionData = np.argsort(list(expressionData))
    division = int(len(expressionData)/LOD)
    #print(division)
    initialPoint = 0
    finalPoint = division
    discretizedData = []
    for i in range(len(expressionData)):
        discretizedData.append(-1)
    for divisions in range(LOD):
        if divisions == LOD - 1:
            currentArgs = argsOrderedExpressionData[initialPoint:]
        else:
            currentArgs = argsOrderedExpressionData[initialPoint:finalPoint]

        for index in currentArgs:
            if LOD == 3:
                if divisions == 0:
                    discretizedData[index] = divisions
                elif divisions == 1:
                    discretizedData[index] = -1
                elif divisions == 2:
                    discretizedData[index] = 1
            else:
                discretizedData[index] = divisions
        initialPoint = finalPoint
        finalPoint += division

    currentDict = {}
    currentDict[geneName] = discretizedData
    df = pd.DataFrame(data = currentDict, index=timePoints)
    if os.path.exists(outFileName):
        df.T.to_csv(outFileName, mode='a', header=False)
    else:
        df.T.to_csv(outFileName, mode='a')



def partialKMeans(data, nc):
    maxValue = max(data)
    minValue = min(data)
    step = abs(maxValue - minValue) / nc
    centroids = []
    centroid = minValue + step/2
    for i in range(nc):
        centroids.append([centroid])
        centroid += step
    model = KMeans(n_clusters=nc, init=centroids, random_state=0)

    result = model.fit_predict(np.array(data).reshape(-1, 1))

    return list(result)


def BiKMeans(splineFileName, outFileName):
    splineFile = pd.read_csv(splineFileName, index_col=0)
    allGenes = splineFile.T.columns
    allTimes = splineFile.columns

    kmeansrows = []
    for gene in allGenes:
        kmeansrows.append(partialKMeans(splineFile.T[gene], 3))

    allData = []
    for gene in allGenes:
        allData.append(list(splineFile.T[gene]))

    tmp = Utils.transposeDataset(allData)
    tmp_kmeanscolumns = []
    for data in tmp:
        tmp_kmeanscolumns.append(partialKMeans(data, 3))

    tmp = Utils.transposeDataset(tmp_kmeanscolumns)

    kmeanscolumns = tmp

    BKM_G_Matrix = []

    for i in range(len(allData)):
        BKM_G_Matrix.append([])
        for j in range(len(allData[0])):
            BKM_G_Matrix[i].append(0)


    nc = 2
    for i in range(len(kmeansrows)):
        for j in range(len(kmeansrows[0])):
            k_d = 1
            while ((k_d)*(k_d) <= (kmeansrows[i][j]+1) * (kmeanscolumns[i][j]+1)):
                k_d += 1

            if ( (kmeansrows[i][j]+1) == (nc+1) and (kmeanscolumns[i][j]+1) == (nc+1) ):
                BKM_G_Matrix[i][j] = k_d - 2
            else:
                BKM_G_Matrix[i][j] = k_d - 1

    dfBKM = pd.DataFrame(BKM_G_Matrix, index=allGenes, columns=list(allTimes))

    for gene in allGenes:
        currentDict = {}
        currentDict[gene] = dfBKM.T[gene]
        df = pd.DataFrame(data = currentDict, index=list(allTimes))
        if os.path.exists(outFileName):
            df.T.to_csv(outFileName, mode='a', header=False)
        else:
            df.T.to_csv(outFileName, mode='a')

    print("BiKMeans sucessfully performed.")    

    


def BiKMeans_Old(splineFileName, outFileName):
    print("Initializing BiKMeans")
    splineFile = pd.read_csv(splineFileName, index_col=0)
    allGenes = splineFile.T.columns


    allExpressionUniform = []
    for gene in allGenes:
        allExpressionUniform.append(list(splineFile.T[gene]))
    #minmax_scaler = preprocessing.MinMaxScaler()
    #allExpressionUniform = minmax_scaler.fit_transform(allExpressionUniform)

    UniformData = pd.DataFrame(allExpressionUniform, index=allGenes, columns=list(splineFile.columns))

    kmeansModel = KMeans(n_clusters=3, random_state=0)
    kmeansrows = []
    kmeanscolumns2 = []
    kmeanscolumns = []

    for gene in allGenes:
        kmeansrows.append(list(kmeansModel.fit_predict(np.array(UniformData.T[gene]).reshape(-1, 1))))
        

    for time in UniformData.columns:
        kmeanscolumns2.append(list(kmeansModel.fit_predict(np.array(UniformData[time]).reshape(-1, 1))))

    dfColumns = pd.DataFrame(kmeanscolumns2, index=list(UniformData.columns), columns=allGenes)

    for gene in allGenes:
        kmeanscolumns.append(dfColumns[gene])


    BKM_Matrix = []
    for i in range(len(kmeansrows)):
        localRow = []
        for j in range(len(kmeansrows[0])):
            k_d = 1
            while ( ((k_d)*(k_d)) <= ((kmeansrows[i][j]+1)*(kmeanscolumns[i][j]+1))):
                k_d += 1

            if (((kmeansrows[i][j]+1) == 3) and ((kmeanscolumns[i][j]+1) == 3)):
                localRow.append(k_d - 2)
            else:
                localRow.append(k_d - 1)
        BKM_Matrix.append(localRow)
            
    dfBKM = pd.DataFrame(BKM_Matrix, index=allGenes, columns=list(UniformData.columns))

    for gene in allGenes:
        currentDict = {}
        currentDict[gene] = dfBKM.T[gene]
        df = pd.DataFrame(data = currentDict, index=list(UniformData.columns))
        if os.path.exists(outFileName):
            df.T.to_csv(outFileName, mode='a', header=False)
        else:
            df.T.to_csv(outFileName, mode='a')

    print("BiKMeans sucessfully performed.")


def performMeanDiscretization(splineFileName, outFileName):
    splineFile = pd.read_csv(splineFileName, index_col=0)
    allGenes = splineFile.T.columns
    timePoints = splineFile.columns
    for gene in allGenes:
        meanDiscretization(gene, splineFile.T[gene], timePoints, outFileName)

def performMedianDiscretization(splineFileName, outFileName):
    splineFile = pd.read_csv(splineFileName, index_col=0)
    allGenes = splineFile.T.columns
    timePoints = splineFile.columns
    for gene in allGenes:
        medianDiscretization(gene, splineFile.T[gene], timePoints, outFileName)

def performEFDDiscretization(splineFileName, outFileName):
    splineFile = pd.read_csv(splineFileName, index_col=0)
    allGenes = splineFile.T.columns
    timePoints = splineFile.columns
    for gene in allGenes:
        EFDDiscretization(gene, splineFile.T[gene], timePoints, 2, outFileName)

def performTSDDiscretization(splineFileName, outFileName):
    splineFile = pd.read_csv(splineFileName, index_col=0)
    #print(splineFile)
    allGenes = splineFile.T.columns
    timePoints = splineFile.columns
    for gene in allGenes:
        TSDDiscretization(gene, splineFile.T[gene], timePoints, outFileName)


def performDSSPDDiscretization(allGeneObjects, outFileName):
    print("DSSPD discretization")
    for gene in allGeneObjects:
        DSSPDDiscretization(gene, outFileName)


def generateNotFullDiscretizationData(splineFileName, outFileName, genesNames):
    allGenes = []
    localFileGenesNames = open(genesNames, "r")
    for line in localFileGenesNames:
        allGenes.append(line.strip())
    localFileGenesNames.close()
    splineFile = pd.read_csv(splineFileName, index_col=0)
    timePoints = list(splineFile.columns)
    for geneName in allGenes:
        currentDict = {}
        currentDict[geneName] = list(splineFile.T[geneName])
        df = pd.DataFrame(data = currentDict, index=timePoints)
        if os.path.exists(outFileName):
            df.T.to_csv(outFileName, mode='a', header=False)
        else:
            df.T.to_csv(outFileName, mode='a')


def discretizationProcedure(discretizationApproach, currentOutFile, currentFile, problemName, currentPseudoTime, expressionDataFile, pseudotimeFile):
    
    if discretizationApproach == 'BiKMeans':
        BiKMeans(currentFile, currentOutFile)
    elif discretizationApproach == 'Mean':
        performMeanDiscretization(currentFile, currentOutFile)
    elif discretizationApproach == 'Median':
        performMedianDiscretization(currentFile, currentOutFile)
    elif discretizationApproach == 'EFD':
        performEFDDiscretization(currentFile, currentOutFile)
    elif discretizationApproach == 'TSD':
        performTSDDiscretization(currentFile, currentOutFile)
    elif discretizationApproach == 'DSSPD':
        ########
        #Get gene names
        desiredGenes = list(pd.read_csv(currentFile, index_col=0).T.columns)
        #Get desired genes expression data
        localOpenExpressionData = pd.read_csv(expressionDataFile, index_col=0)
        copyDF = localOpenExpressionData.T[desiredGenes].copy()
        currentUseExpressionData = copyDF.T
        #create pseudotime dictionary
        localOpenPseudoTime = pd.read_csv(pseudotimeFile, index_col=0)
        dictPseudoTimes = {}
        for pt in range(len(localOpenPseudoTime.columns)):
            dictPseudoTimes[pt] = []
        for cell in localOpenPseudoTime.T.columns:
            for pt in range(len(localOpenPseudoTime.columns)):
                if str(localOpenPseudoTime.T[cell][pt]) != 'nan':
                    dictPseudoTimes[pt].append(cell)
        #create pseudotime dataframes
        pseudotimeDataFrames = []
        bestDistributions = []
        for pt in range(len(localOpenPseudoTime.columns)):
            pseudotimeDataFrames.append(localOpenExpressionData[dictPseudoTimes[pt]].copy())
            bestDistributions.append([])
        #create dictTimes for currentPseudotime
        localCurrentPseudoTime = int(currentPseudoTime.replace('pt', ''))
        dictTimes = {}
        for cell in pseudotimeDataFrames[localCurrentPseudoTime].columns:
            ptValue = localOpenPseudoTime.T[cell][localCurrentPseudoTime]
            if ptValue not in dictTimes.keys():
                dictTimes[ptValue] = [cell]
            else:
                dictTimes[ptValue].append(cell)
        #process expressionData
        allGeneObjects = []
        for cellN in range(len(pseudotimeDataFrames[localCurrentPseudoTime].T.columns)):
            dictExpressionPT = {}
            for key in dictTimes.keys():
                if len(dictTimes[key]) == 1:
                    if pseudotimeDataFrames[localCurrentPseudoTime][dictTimes[key][0]][cellN] == 0:
                        #dropout
                        next
                    else:
                        dictExpressionPT[key] = pseudotimeDataFrames[localCurrentPseudoTime][dictTimes[key][0]][cellN]
                else:
                    count = 0
                    accumValue = 0
                    for cell in range(len(dictTimes[key])):
                        if pseudotimeDataFrames[localCurrentPseudoTime][dictTimes[key][cell]][cellN] == 0:
                            next
                        else:
                            accumValue += pseudotimeDataFrames[localCurrentPseudoTime][dictTimes[key][cell]][cellN]
                            count += 1
                    if count != 0:
                        accumValue /= count
                    if accumValue != 0:
                        dictExpressionPT[key] = accumValue

            sortedPT = list(dictExpressionPT.keys())
            sortedPT.sort()

            sortedAllPT = list(dictTimes.keys())
            sortedAllPT.sort()

            expressionDataPT = []
            for key in sortedPT:
                expressionDataPT.append(dictExpressionPT[key])

            
            bestSmooth = Utils.calculateSmooth(expressionDataPT, sortedPT)

            s = csaps(sortedPT, expressionDataPT, smooth=bestSmooth).spline
            ds1 = s.derivative(nu=1)
            ds2 = s.derivative(nu=2)
            currentGeneObject = Objs.Gene(str(pseudotimeDataFrames[localCurrentPseudoTime].T.columns[cellN]), localCurrentPseudoTime, list(s(sortedAllPT)), list(ds1(sortedAllPT)), list(ds2(sortedAllPT)), sortedAllPT)
            best_dist = Utils.fitDistribution(pseudotimeDataFrames[localCurrentPseudoTime].T[str(pseudotimeDataFrames[localCurrentPseudoTime].T.columns[cellN])])
            currentGeneObject.distribution = best_dist
            currentGeneObject.mean = np.mean(expressionDataPT)

            currentGeneObject.getStates()
            allGeneObjects.append(currentGeneObject)

            print("CHEGOU ATE AQUI")            
        
        for geneObject in allGeneObjects:
            print(geneObject.geneName)
            print(geneObject.splineStates)
        #Utils.getAllStates(allGeneObjects, localCurrentPseudoTime) 
        performDSSPDDiscretization(allGeneObjects, currentOutFile)


        #exit()
