import pandas as pd
import os
import copy
import numpy as np
import pandas as pd
import numpy as np
import glob
import discretizeData as DD
from datetime import datetime
import math
from sklearn.model_selection import ShuffleSplit
from csaps import csaps
import scipy.stats as st

dict_directories = {
    "Pearson": "pearson",
    "Spearman": "spearman",
    "KendallTau": "kendallTau",
    "KMeans": "kmeans",
    "Agglomerative": "aggclustering"
}

dict_discretizationPrefixes = {
    "Mean": "Mean_",
    "Median": "Median_",
    "EFD": "EFD_",
    "TSD": "TSD_",
    "BiKMeans": "BKM_",
    "DSSPD": "DSSPD_"
}

correlationMethods = ['Spearman', 'Pearson', 'KendallTau']
clusteringMethods = ['KMeans', 'Agglomerative']
possibleDiscretizationApproaches = ['Mean', 'Median', 'TSD', 'EFD', 'BiKMeans', 'DSSPD']

class Log:
    def __init__(self, arguments, fileName):
        '''
        Object constructor
        '''
        self.fileName = fileName
        self.arguments = arguments
        self.times = {}

    def register(self, registerType, value='None'):
        '''
        Registers different types of information on the log.
        '''
        now = datetime.now()
        dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
        tempOpen = open(self.fileName, 'a')
        if registerType == 'initial':
            tempOpen.write(dt_string + " - Starting Log for " + self.arguments['problemName'] + " - " + self.arguments['suffix'] + "\n")
        elif registerType == 'time':
            tempOpen.write(dt_string + " - Elapsed time: " + str(value) + "s\n")
        elif registerType == 'message':
            tempOpen.write(dt_string + " - Message: " + str(value) + "\n")
        elif registerType == 'error':
            tempOpen.write(dt_string + " - Error: " + str(value) + "\n")
        elif registerType == 'info':
            tempOpen.write(dt_string + " - Info: " + str(value) + "\n")
        elif registerType == 'timef':
            tempOpen.write(dt_string + " - Total elapsed time: " + str(value) + "s\n")
        elif registerType == 'final':
            tempOpen.write(dt_string + " - End Log for " + self.arguments['problemName'] + " - " + self.arguments['suffix'] + "\n")
        elif registerType == 'warning':
            tempOpen.write(dt_string + " - Warning: " + str(value) + "\n")
        else:
            tempOpen.close()
        tempOpen.close()



def verifyArgs(opts, Log):
    '''
    Verifies the arguments passed through the command prompt.
    Inputs:
    opts - dictionary containing all arguments obtained through the argparse
    Log - Log object
    '''
    Log.register('message', "Start verification of arguments...")
    if opts.problemName == 'None':
        print("You must define the problem name.")
        Log.register('error', "You must define the problem name.")
        Log.register('info', "You set problem name as " + str(opts.problemName))
        exit()
    if opts.suffix == 'None':
        print("You must define a suffix.")
        Log.register('error', "You must define a suffix.")
        Log.register('info', "You set suffix as " + str(opts.suffix))
        exit()
    if opts.clusterMethod in clusteringMethods:
        if opts.n_clusters == 'None':
            print("You must define the number of clusters to be tested. 2 <= nc <= Number of Genes - 1.")
            Log.register('error', "You must define the number of clusters to be tested. 2 <= nc <= Number of Genes - 1.")
            Log.register('info', "You set the number of clusters = " + str(opts.numberOfClusters))
            exit()
    if opts.clusterMethod in correlationMethods:
        if opts.correlation_threshold == 'None':
            print("You must define a correlation threshold. 0 <= t <= 1.")
            Log.register('error', "You must define a correlation threshold. 0 <= t <= 1.")
            Log.register('info', "You set the correlation threshold as " + str(opts.correlation_threshold))
            exit()
        elif float(opts.correlation_threshold) > 1:
            print("The correlation threshold can not be greater than 1. 0 <= t <= 1.")
            Log.register('error', "The correlation threshold can not be greater than 1. 0 <= t <= 1.")
            Log.register('info', "You set the correlation threshold as " + str(opts.correlation_threshold))
            exit()
        elif float(opts.correlation_threshold) < 0:
            print("The correlation threshold must be positive. The correlation threshold value is considered in its absolute value. 0 <= t <= 1.")
            Log.register('error', "The correlation threshold must be positive. The correlation threshold value is considered in its absolute value. 0 <= t <= 1.")
            Log.register('info', "You set the correlation threshold as " + str(opts.correlation_threshold))
            exit() 
    if opts.clusterMethod != 'None' and opts.clusterMethod not in correlationMethods and opts.clusterMethod not in clusteringMethods:
        print("Invalid cluster method.")
        Log.register('error', "Invalid cluster method. Valid values are: " + str(correlationMethods) + " " + str(clusteringMethods))
        Log.register('info', "You set the cluster method as " + str(opts.clusterMethod))
        exit()
    if not(os.path.exists(opts.expressionDataFile)):
        print("Expression Data File not found.")
        Log.register('error', "Expression Data File not found.")
        Log.register('info', "You set the expression data file as " + str(opts.expressionDataFile))
        exit()
    if not(os.path.exists(opts.pseudotimeFile)):
        print("Pseudotime File not found.")
        Log.register('error', "Pseudotime File not found.")
        Log.register('info', "You set the pseudotime file as " + str(opts.pseudotimeFile))
        exit()
    if opts.argSplineFile != 'None':
        if not(os.path.exists(opts.argSplineFile)):
            print("You passed an invalid spline file.")
            Log.register('error', "Spline File not found.")
            Log.register('info', 'You set the Spline File as ' + str(opts.argSplineFile))
            exit()
    if opts.discretizationApproach == 'None':
        print("You must define a discretization approach.")
        Log.register('error', "Invalid discretization approach. Valid values are " + str(possibleDiscretizationApproaches))
        Log.register('info', "You set the discretization approach as " + str(opts.discretizationApproach))
        exit()
    if opts.discretizationApproach not in possibleDiscretizationApproaches:
        print("You have chosen an invalid discretization approach.")
        Log.register('error', "You have chosen an invalid discretization approach. Valid values are " + str(possibleDiscretizationApproaches))
        Log.register('info', "You set the discretization approach as " + str(opts.discretizationApproach))
        exit()
    if int(opts.independentRuns) <= 0:
        print("The number of independent runs must be a positive, greater than 0, integer.")
        Log.register('error', 'The number of independent runs must be a positive, greater than 0, integer. 1 <= r <= inf.')
        Log.register('info', "You set the number of independent runs as " + str(opts.independentRuns))
        exit()
    if (opts.fullTT == True) and ((opts.clusterMethod not in clusteringMethods) and (opts.clusterMethod != 'None')):
        print("You only can use full truth table when using clustering methods or without using a clustering method.")
        Log.register('error', 'You can only use full truth table when using clustering methods or without using a clustering method.')
        Log.register('info', 'You have chosen ' + str(opts.clusterMethod) + ", however only " + str(clusteringMethods) + " or no clustering method are acceptable.")
        exit()
    if opts.cgpNodes != 'None':
        if int(opts.cgpNodes) <= 0:
            print("The number of CGPGRN nodes must be a positive integer.")
            Log.register('error', 'The number of CGPGRN nodes must be a positive integer.')
            Log.register('info', 'You have chosen ' + str(opts.cgpNodes) + " and it is not a positive integer.")
            exit()
    if opts.cgpGens != 'None':
        if int(opts.cgpGens) <= 0:
            print("The number of CGPGRN generations must be a positive integer.")
            Log.register('error', 'The number of CGPGRN generations must be a positive integer.')
            Log.register('info', 'You have chosen ' + str(opts.cgpGens) + " and it is not a positive integer.")
            exit()
    if opts.multipleExecutions != 'None':
        if not(os.path.exists(opts.multipleExecutions)):
            print("You passed an invalid problem list file.")
            Log.register('error', "Problem List File not found.")
            Log.register('info', 'You set the Problem List File as ' + str(opts.multipleExecutions))
            exit()  
        else:
            tempMEFile = open(opts.multipleExecutions, 'r')
            currentLine = -1
            for line in tempMEFile:
                currentLine += 1
                splitFile = line.split('\t')
                tempMEExpressionData = splitFile[0].strip()
                tempMEPseudoTime = splitFile[1].strip()
                if not(os.path.exists(tempMEExpressionData)):
                    print("Invalid Expression Data File found in Problem List File on line: ", currentLine)
                    Log.register('error', "Invalid Expression Data File found in Problem List File")
                    Log.register('info', 'Expression Data File not found ' + str(tempMEExpressionData))
                    exit()
                if not(os.path.exists(tempMEPseudoTime)):
                    print("Invalid PseudoTime File found in Problem List File on line: ", currentLine)
                    Log.register('error', "Invalid PseudoTime File found in Problem List File")
                    Log.register('info', 'PseudoTime File File not found ' + str(tempMEPseudoTime))
                    exit()
                    
        
    Log.register('message', "Verification of arguments sucessfully done.")
        
    
def generateSplineList(splineDataNames, Log, problemName):
    '''
    Generates Spline List file for a given spline data files.
    Inputs:
    splineDataNames - a matrix with all spline data file names
    Log - Log Object
    problemName - the name of the problem
    Output:
    Creates a splineList_problemName file with all given spline data files, one per line.
    '''
    outSplineListFilename = 'splineList_' + str(problemName) + '.txt'
    if os.path.exists(outSplineListFilename):
        outSplineListFilename = 'splineList_' + str(problemName) + '_0.txt'
        while os.path.exists(outSplineListFilename):
            currentIndex = (outSplineListFilename.split("_")[2]).replace('.txt', '')
            print(currentIndex)
            outSplineListFilename = outSplineListFilename.replace(currentIndex, str(int(currentIndex) + 1))
    outSplineListFile = open(outSplineListFilename, 'w')
    for splineDataName in splineDataNames:
        outSplineListFile.write(str(splineDataName))
        outSplineListFile.write("\n")
    outSplineListFile.close()
    print("Spline File List generated.")
    Log.register('message', 'Spline File List generated.')
    Log.register('info', 'Spline List Filename: ' + str(outSplineListFilename))


def verifyNumberOfClusters(data, nc):
    '''
    Verifies if the number of genes present in data is greater than the desired number of clusters.
    Inputs:
    data - a dataset typical file with genes as rows and cell IDs as columns
    nc - the desired number of clusters
    Outputs:
    False if the desired number of clusters is greater than the number of genes - 1
    'nf' if the data file is not found, and
    True is the desired number of clusters is lower than the number of genes
    '''
    if nc == 'None':
        return True
    else:
        for i in range(len(data)):
            if os.path.exists(data[i]):
                tempOpen = pd.read_csv(data[i], index_col=0)
                nGenes = len(tempOpen.T.columns)
                if int(nc) > nGenes - 1:
                    del tempOpen
                    return False
            else:
                return 'nf'
        return True
        
            
def getSplineFilesNames(argSplineFile):
    '''
    Read and append to an array the spline files names for a given spline list file.
    Input:
    argSplineFile - spline list filename
    Output:
    splineDataNames - an array with the file names present in argSplineFile
    '''
    splineDataNames = []
    currentSplineListFile = open(argSplineFile, "r")
    for line in currentSplineListFile:
        splineDataNames.append(line.strip())
    return splineDataNames
    

def mkdir(directory):
    '''
    Verifies the existence of a directory and if it does not exist, create it.
    Input:
    directory - path and name of the new directory
    '''
    if os.path.exists(directory) == False:
        os.mkdir(directory)
    
def transposeDataset(allData):
    '''
    Transpose a given matrix.
    Input:
    allData - matrix
    Output:
    tVector - transposed allData matrix
    '''
    tVector = []
    for i in range(len(allData[0])):
        tVector.append([])
        for j in range(len(allData)):
            tVector[i].append(0)

    for i in range(len(allData)):
        for j in range(len(allData[0])):
            tVector[j][i] = allData[i][j]

    return tVector

def calculateMaxInputs(allGeneFiles):
    '''
    Calculate the maximum number of inputs present in all geneNames files generated during the pipeline.
    Input:
    allGeneFiles - matrix with all geneNames files
    Output:
    maxCount - the maximum value of genes present in all geneNames files
    '''
    maxCount = 0
    for geneFile in allGeneFiles:
        currentCount = 0
        currentOpen = open(geneFile, "r")
        for line in currentOpen:
            currentCount += 1
        currentOpen.close()
        if currentCount > maxCount:
            maxCount = currentCount
    return maxCount

def getNodesAndGenerations(fullTT, cgpNodes, cgpGens, currentMaxOutputs):
    '''
    Calculates the number of CGPGRN inference algorithm genotype nodes and the maximum number of CGPGRN inference algorithm generations for evolutionary search
    Inputs:
    fullTT - bool, given in arguments
    cgpNodes - value of cgpNodes passed as argument
    cgpGens - value of cgpGens passed as argument
    currentMaxOutputs - the calculated number of outputs/inputs for each run
    Outputs:
    currentMaxNodes - the number of CGPGRN inference algorithm genotype nodes
    currentMaxGens - the maximum number of CGPGRN inference algorithm generations for evolutionary search
    '''
    if cgpNodes != 'None' and cgpGens != 'None':
        currentMaxNodes = cgpNodes
        currentMaxGens = cgpGens
    else:
        if cgpNodes == 'None':
            if fullTT == False:
                if currentMaxOutputs < 200:
                    currentMaxNodes = 500
                else:
                    currentMaxNodes = 500 + math.ceil(currentMaxOutputs // 200) * 500
            else:
                if currentMaxOutputs < 200:
                    currentMaxNodes = 500
                else:
                    currentMaxNodes = 500 + math.ceil(currentMaxOutputs // 200) * 500
        else:
            currentMaxNodes = cgpNodes
                    
        if cgpGens == 'None':
            if fullTT == False:
                currentMaxGens = 50000 + math.ceil(currentMaxOutputs // 20) * 50000
            else:
                currentMaxGens = 1500000 + math.ceil(currentMaxOutputs // 400) * 1500000
        else:
            currentMaxGens = cgpGens

    return currentMaxNodes, currentMaxGens

def generateFullBashScript(allShellScriptsFileName, fullTT, bashScripts, allCounts, allMaxInputs, arguments):
    '''
    Generates the full Bash script file of CGPGRN framework
    Inputs:
    allShellScriptsFileName - the name of the file for all shell scripts
    fullTT - bool, given in arguments
    bashScripts - a list containing the bash scripts names per independent run and clustering step
    allCounts - a list containing the counting of the number of inputs/outputs for each generated truth table/discretizated/spline files when fullTT = True
    allMaxInputs - a list containing the number of the number of inputs/outputs for each generated truth table/discretizated/spline files when fullTT = False
    arguments - the command prompt given arguments when starting CGPGRN framework
    '''
    
    outputFullShellScripts = open(allShellScriptsFileName, 'a')
    if fullTT == False:
        currentMaxOutputs = allMaxInputs
        currentMaxNodes, currentMaxEval = getNodesAndGenerations(fullTT, arguments.cgpNodes, arguments.cgpGens, currentMaxOutputs)

        currentString = "python include/makeFile.py -o " + "1" + " -n " + str(currentMaxNodes) + " -e " + str(currentMaxEval) + "\n" #p windows

        if os.name != 'nt':
            currentString = currentString.replace('python', 'python3')
            
        outputFullShellScripts.write(currentString)                
        for script in bashScripts:
            currentString = 'bash ' + script + ";\n"
            outputFullShellScripts.write(currentString)

    else:
        previousCurrentMaxOutputs = -1
        previousCurrentMaxNodes = -1
        previousCurrentMaxEval = -1
        for scriptNumber in range(len(bashScripts)):
            script = bashScripts[scriptNumber]
            currentMaxOutputs = allCounts[scriptNumber]
            currentMaxNodes, currentMaxEval = getNodesAndGenerations(fullTT, arguments.cgpNodes, arguments.cgpGens, currentMaxOutputs)

            if ((previousCurrentMaxOutputs == currentMaxOutputs) and (previousCurrentMaxNodes == currentMaxNodes) and (previousCurrentMaxEval == currentMaxEval)):
                pass
            else:

                currentString = "python include/makeFile.py -o " + str(currentMaxOutputs) + " -n " + str(currentMaxNodes) + " -e " + str(currentMaxEval) + "\n"

                if os.name != 'nt':
                    currentString = currentString.replace('python', 'python3')
                outputFullShellScripts.write(currentString)
                previousCurrentMaxOutputs = currentMaxOutputs
                previousCurrentMaxNodes = currentMaxNodes
                previousCurrentMaxEval = currentMaxEval


            
            currentString = 'bash ' + script + ";\n"
            outputFullShellScripts.write(currentString)
    outputFullShellScripts.close()


def calculateSmooth(expressionData, timePoints):
    rs = ShuffleSplit(n_splits = 10, train_size = 0.1, test_size = 0.9, random_state=1345540) ##0.1/0.9
    smooth_errors = {}
    for train, test in rs.split(expressionData):
        train.sort()
        test.sort()
        vector_train = [[],[]]
        vector_test = [[],[]]
        for element in train:
            vector_train[0].append(timePoints[element])
            vector_train[1].append(expressionData[element])
        for element in test:
            vector_test[0].append(timePoints[element])
            vector_test[1].append(expressionData[element])



        smooth_values = [0, 0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4, 0.45, 0.5, 0.55, 0.6, 0.65, 0.7, 0.75, 0.8, 0.85, 0.9, 0.95, 0.99]

        if len(vector_train[0]) > 1 and len(vector_train[1]) > 1:

            #print("entrou")
            for smooths in smooth_values:
                ys = csaps(vector_train[0], vector_train[1], timePoints, smooth=smooths)
                dif_total = 0
                for element in range(len(vector_test[0])):
                    calculated = ys[element]
                    real = vector_test[1][element]
                    dif_total += pow(real - calculated, 2)
                if smooths not in smooth_errors.keys():
                    smooth_errors[smooths] = dif_total
                else:
                    smooth_errors[smooths] += dif_total


            best_smooth = list(smooth_errors.keys())[np.argmin(list(smooth_errors.values()))]

        else:

            best_smooth = 0.99

    return best_smooth    
        
def fitDistribution(data):
    #dist_names = ["alpha","arcsine","beta","betaprime","cauchy","chi","chi2","cosine","dgamma","dweibull","expon","exponnorm","exponweib","exponpow","f","genlogistic","gennorm","genpareto","genexpon","genextreme","gamma","gengamma","halfcauchy","halflogistic","halfnorm","halfgennorm","invgamma","invgauss","invweibull","laplace","laplace_asymmetric","logistic","loggamma","loglaplace","lognorm","loguniform","maxwell","norm","norminvgauss","pareto","pearson3","powerlaw","powerlognorm","powernorm","rayleigh","t","uniform","weibull_min","weibull_max","wrapcauchy"]
    #dist_names = ["alpha","anglit","arcsine","beta","betaprime","cauchy","chi","chi2","cosine","expon","f","fatiguelife","genlogistic","genpareto","genexpon","genextreme","gamma","gengamma","halfcauchy","halflogistic","halfnorm","halfgennorm","logistic","norm","pareto","rayleigh","t","weibull_min","weibull_max"]
    #"dgamma","dweibull",
    dist_names = ["expon", "norm"]
    dist_results = []
    params = {}

    for dist_name in dist_names:
        dist = getattr(st, dist_name)
        param = dist.fit(data)
        params[dist_name] = param
        # Applying the Kolmogorov-Smirnov test
        D, p = st.kstest(data, dist_name, args=param)
        dist_results.append((dist_name, p))

    best_dist, best_p = (max(dist_results, key=lambda item: item[1]))
    x = np.linspace(np.min(data), np.max(data))
    dist = getattr(st, best_dist)
    temp_args = dist.fit(data)
    currentArgs = list(temp_args)
    #print("BINS CALCULADO: ", math.ceil(math.sqrt(len(data))))
    #histogram = plt.hist(data, bins=math.ceil(math.sqrt(len(data))), density=True)
    #print(histogram[0])
    #print(histogram[1])
    #plt.plot(x, dist.pdf(x, *currentArgs))
    #plt.title(best_dist)
    #plt.show()
    return best_dist    
    

def getAllStates(allGeneObjects, pt):
    allSplineStates = []
    allFirstDerivativeStates = []
    allSecondDerivativeStates = []
    #for i in range(len(allGeneObjects[0].firstDerivativeStates)):
    for i in range(len(allGeneObjects[0].splineStates)):
        currentSplineState = ''
        currentFirstDerivativeState = ''
        currentSecondDerivativeState = ''
        for gene in allGeneObjects:
            currentSplineState += str(gene.splineStates[i])
            #currentFirstDerivativeState += str(gene.firstDerivativeStates[i])
            #currentSecondDerivativeState += str(gene.secondDerivativeStates[i])
        allSplineStates.append(currentSplineState)
        #allFirstDerivativeStates.append(currentFirstDerivativeState)
        #allSecondDerivativeStates.append(currentSecondDerivativeState)

    print(allSplineStates)
    
    
    #getTransitions(allSplineStates, 'spline', pt)
    
    
