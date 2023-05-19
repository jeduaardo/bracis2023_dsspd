import os
import pandas as pd
import utils as Utils
import preProcessing as PP
import clusterData as CD
import discretizeData as DD
import numpy as np

class Gene:
    def __init__(self, geneName, pseudotime, splineData, firstDerivative, secondDerivative, sortedAllPT):
        self.geneName = geneName
        self.pseudotime = pseudotime
        self.splineData = splineData
        self.firstDerivative = firstDerivative
        self.secondDerivative = secondDerivative
        self.sortedAllPT = sortedAllPT
        self.splineStates = []
        self.firstDerivativeStates = []
        self.secondDerivativeStates = []
        self.splinePoints = []
        self.splinePointsIndex = []
        self.firstDerivativePoints = []
        self.secondDerivativePoints = []
        self.distribution = 'None'
        self.mean = 0

    def getStates(self):


        print("Olhe: ", self.mean)
        print("Olha2: ", (max(self.splineData)-min(self.splineData))/2)
        print("Maior: ", max(self.splineData))
        print("Menor: ", min(self.splineData))
        print("Distribuição: ", self.distribution)

        splineDados = self.splineData


        #plt.plot(splineDados)
        #plt.show()
        
        estadoAtual = 'nulo'
        for i in range(len(splineDados)):
            if i == 0:
                next
            else:
                if self.distribution == 'expon' and self.mean <= 0.02:
                    self.splineStates.append(0)
                else:
                    if splineDados[i] - splineDados[i-1] > 0:
                        if estadoAtual == 'nulo':
                            estadoAtual = 'maior'
                        else:
                            if estadoAtual != 'maior':
                                #self.splinePoints.append(sortedPT[i])
                                self.splinePoints.append(self.sortedAllPT[i])
                                self.splinePointsIndex.append(i)
                                estadoAtual = 'maior'
                        self.splineStates.append(1)
                    else:
                        if estadoAtual == 'nulo':
                            estadoAtual = 'menor'
                        else:
                            if estadoAtual != 'menor':
                                #self.splinePoints.append(sortedPT[i])
                                self.splinePoints.append(self.sortedAllPT[i])
                                self.splinePointsIndex.append(i)
                                estadoAtual = 'menor'
                        self.splineStates.append(0)
        self.splineStates.insert(0, self.splineStates[0])
        #print(self.splineStates)
        self.splinePointsIndex.insert(0, 0)
        self.splinePointsIndex.append(len(splineDados))
        print(self.splinePointsIndex)


        newStates = []
        #Se o tamanho é 2, só tem os pontos de início e fim do spline. Caso contrário, existem pontos de mudança de sinal
        if len(self.splinePointsIndex) != 2:
            previousPoint = -1
            currentPoint = -1
            ultimoEstado = -1
            for i in range(len(self.splinePointsIndex)):
                
                if self.distribution == 'expon' and self.mean <= 0.02:
                    #print("OLHAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA")
                    newStates.append(0)
                else:
                    if i == 0:
                        previousPoint = self.splinePointsIndex[i]
                    else:
                        if currentPoint == -1:
                            currentPoint = self.splinePointsIndex[i]
                        else:
                            previousPoint = currentPoint
                            currentPoint = self.splinePointsIndex[i]
                                        
                                        
                        ####CONTINUAR DAQUI                                
                        print(previousPoint)
                        print(currentPoint)
                        print("Media: ", np.mean(splineDados[previousPoint:currentPoint]))
                        print("Var: ", np.var(splineDados[previousPoint:currentPoint]))
                        print("Std: ", np.std(splineDados[previousPoint:currentPoint]))
                        if previousPoint == 0:
                            print("primeiro intervalo")
                            if np.var(splineDados[previousPoint:currentPoint]) < (0.05 * np.var(splineDados)):#0.02:
                                for j in range(len(splineDados[previousPoint:currentPoint])):
                                    if np.mean(splineDados[previousPoint:currentPoint]) < self.mean:#0.15:
                                        newStates.append(0)
                                    else:
                                        newStates.append(1)
                                ultimoEstado = newStates[len(newStates)-1]
                                
                            else:
                                for j in range(len(splineDados[previousPoint:currentPoint])):
                                    if j == 0:
                                        next
                                    else:
                                        if splineDados[j] - splineDados[j-1] >= 0:
                                            newStates.append(1)
                                        else:
                                            newStates.append(0)
                                newStates.insert(0, newStates[0])
                                ultimoEstado = newStates[len(newStates)-1]
                                    
                        else:
                            print("Demais intervalos")
                            partialStates = []
                            for j in range(len(splineDados[previousPoint:currentPoint])):
                                if np.var(splineDados[previousPoint:currentPoint]) < (0.05 * np.var(splineDados)):#0.02:
                                    partialStates.append(ultimoEstado)
                                else:
                                    if j == 0:
                                        next
                                    else:
                                        if splineDados[previousPoint + j] - splineDados[previousPoint + j - 1] >= 0:
                                            partialStates.append(1)
                                        else:
                                            partialStates.append(0)
                            if np.var(splineDados[previousPoint:currentPoint]) >= (0.05 * np.var(splineDados)):#0.02:
                                partialStates.insert(0, partialStates[0])
                            for pS in partialStates:
                                newStates.append(pS)
                            ultimoEstado = newStates[len(newStates)-1]
        
            


                
            print("Tamanho dos estados originais: ", len(self.splineStates))
            print("Tamanho dos novos estados: ", len(newStates))
            print(self.splineStates)
            print(newStates)
            #plt.plot(self.splineStates)
            #plt.plot(newStates)
            #plt.plot(self.splineData)
            #plt.legend(['splineStates', 'newStates'])
            #plt.show()
            if len(self.splinePointsIndex) != 2:
                print(self.splinePointsIndex)
                #for k in self.splinePointsIndex:
                #    plt.axvline(x = k, color = 'b')
                #plt.plot(self.splineData)
                #plt.show()
                

            if len(newStates) != 0:
                self.splineStates = newStates            

        else:
            print("ENTROU NO ELSE")
            #plt.plot(self.splineStates)
            #plt.plot(self.splineData)
            #plt.title('Entrou no Else')
            #plt.show()


class CGPGRN:
    def __init__(self, arguments, Log):
        '''
        Object constructor
        '''
        self.arguments = arguments
        self.Log = Log
        
        self.genesNamesFiles = []
        self.directories = []
        self.additional_discretizedFiles = []
        self.discretizedFiles = []        

    def performSplineStep(self):
        '''
        Performs the spline step. Considers and verifies the given spline files if passed as argument.
        Outputs:
        splineDataNames - all spline data filenames
        '''

        std_messages = {'maxclusters_error': "The maximum number of clusters must be lower than the total number of genes."}

        print("Starting spline step...")
        self.Log.register('message', 'Starting spline step...')
        
        #Verification of spline files, spline list and generation of spline data
        if self.arguments.argSplineFile == 'None':
            if Utils.verifyNumberOfClusters([self.arguments.expressionDataFile], self.arguments.n_clusters) == True:
                print("Generating spline file...")
                self.Log.register('message', "Generating spline file...")
                splineDataNames = PP.preProcessData(self.arguments.pseudotimeFile, self.arguments.expressionDataFile, self.arguments.suffix)
            else:
                print(std_messages['maxclusters_error'])
                self.Log.register('error', std_messages['maxclusters_error'])
                self.Log.register('info', "You set the number of clusters as " + str(self.arguments.n_clusters))
        else:
            if self.arguments.splineList == False:
                verifyClusterConstraint = Utils.verifyNumberOfClusters([self.arguments.argSplineFile], self.arguments.n_clusters)
                if verifyClusterConstraint == True:
                    print("Using spline file passed as an argument...")
                    self.Log.register('message', "Using spline file passed as an argument")
                    splineDataNames = [self.arguments.argSplineFile]
                elif verifyClusterConstraint == 'nf':
                    print("Spline file not found.")
                    self.Log.register('error', "Spline file not found.")
                    exit()
                else:
                    print(std_messages['maxclusters_error'])
                    self.Log.register('error', std_messages['maxclusters_error'])
                    exit()
            else:
                print("Using spline list file passed as an argument...")
                self.Log.register('message', "Using spline list file passed as an argument...")                
                splineDataNames = Utils.getSplineFilesNames(self.arguments.argSplineFile)
                verifyClusterConstraint = Utils.verifyNumberOfClusters(splineDataNames, self.arguments.n_clusters)
                if verifyClusterConstraint == False:
                    print(std_messages['maxclusters_error'])
                    self.Log.register('error', std_messages['maxclusters_error'])
                    exit()
                elif verifyClusterConstraint == 'nf':
                    print("Spline file not found.")
                    self.Log.register('error', "Spline file not found.")
                    exit()

        #Generation of spline list, if -gsl is True
        if self.arguments.generateSplineList == True:
            Utils.generateSplineList(splineDataNames, self.Log, self.arguments.problemName)

        
        return splineDataNames


    def performClusteringStep(self, splineDataName, currentPseudoTime):
        dirName, bestNClusters = CD.main(self.arguments.problemName, self.arguments.correlation_threshold, splineDataName, self.arguments.n_clusters, self.arguments.clusterMethod, currentPseudoTime, self.Log)
        return dirName, bestNClusters


    def performDiscretizationStep(self, dirName, bestNClusters, currentPseudoTime, splineDataName, expressionDataFile, pseudotimeFile):
        print("DISCRETIZATION")

        genesNamesFiles = []
        directories = []
        additional_discretizedFiles = []
        discretizedFiles = []

        if self.arguments.fullDiscretization == True:
            self.Log.register('message', "Using full discretization...")

            if self.arguments.clusterMethod in Utils.clusteringMethods: #Using a clustering method
                localClusterDir = Utils.dict_directories[self.arguments.clusterMethod]

                for cluster in range(bestNClusters):
                    print("Discretizing data for cluster " + str(cluster))
                    self.Log.register('message', "Discretizing data for cluster " + str(cluster))

                    currentDir1 = os.path.join(os.getcwd(), localClusterDir)
                    currentDir = currentDir1 + "/Cluster" + str(cluster)

                    currentFile = currentDir + "/spline_" + self.arguments.problemName + "_" + str(cluster) + "_" + currentPseudoTime + ".csv"
                    currentGenesNamesFiles = currentDir + "/geneNames_" + str(cluster) + "_" + currentPseudoTime + ".txt"

                    genesNamesFiles.append(currentGenesNamesFiles)
                    directories.append(currentDir)

                    currentOutFile = currentDir + Utils.dict_discretizationPrefixes[self.arguments.discretizationApproach] + self.arguments.problemName + "_" + str(cluster) + "_" + currentPseudoTime + ".csv"

                    if self.arguments.discretizationApproach == 'BiKMeans':
                        if Utils.verifyNumberOfClusters([localClusterDir+"/Cluster"+str(cluster) + "/spline_" + self.arguments.problemName + "_" + str(cluster) + "_" + currentPseudoTime + ".csv"], 3) != True:
                            print("The spline data does not contain the minimum number of needed genes (3). Using not full discretization instead.")
                            self.Log.register('warning', "The spline data does not contain the minimum number of needed genes (3). Using not full discretization instead.")
                            self.Log.register('info', "Spline File Name: " + str(currentFile))

                            currentTempFile = splineDataName
                            currentTempOutFile = Utils.dict_discretizationPrefixes[self.arguments.discretizationApproach] + self.arguments.problemName + "_full_" + currentPseudoTime + ".csv"
                            if not os.path.exists(currentTempOutFile):
                                DD.discretizationProcedure(self.arguments.discretizationApproach, currentTempOutFile, currentTempFile, self.arguments.problemName, currentPseudoTime, expressionDataFile, pseudotimeFile)
                                additional_discretizedFiles.append(currentTempOutFile)

                            currentOutFile2 = currentDir + Utils.dict_discretizationPrefixes[self.arguments.discretizationApproach] + self.arguments.problemName + "_" + str(cluster) + "_" + currentPseudoTime + ".csv"

                            DD.generateNotFullDiscretizationData(currentTempOutFile, currentOutFile2, currentGenesNamesFiles)

                            discretizedFiles.append(currentOutFile2)

                        else:

                            DD.discretizationProcedure(self.arguments.discretizationApproach, currentOutFile, currentFile, self.arguments.problemName, currentPseudoTime, expressionDataFile, pseudotimeFile)
                            discretizedFiles.append(currentOutFile)
                    else:
                        DD.discretizationProcedure(self.arguments.discretizationApproach, currentOutFile, currentFile, self.arguments.problemName, currentPseudoTime, expressionDataFile, pseudotimeFile)
                        discretizedFiles.append(currentOutFile)

            elif self.arguments.clusterMethod in Utils.correlationMethods:
                print("eh metodo de correlação")

                currentDir = dirName + "/"

                readSplineData = pd.read_csv(splineDataName, index_col=0)
                allGenes = readSplineData.T.columns

                for gene in allGenes:
                    self.Log.register('message', "Discretizing data for gene " + str(gene))
                    currentFile = currentDir + "spline_" + self.arguments.problemName + "_" + str(gene) + "_" + currentPseudoTime + ".csv"
                    currentGenesNamesFiles = currentDir + "geneNames_" + str(gene) + "_" + currentPseudoTime + ".txt"
                    genesNamesFiles.append(currentGenesNamesFiles)
                    directories.append(currentDir)
                    currentOutFile = currentDir + Utils.dict_discretizationPrefixes[self.arguments.discretizationApproach] + self.arguments.problemName + "_" + str(gene) + "_" + currentPseudoTime + ".csv"
                    DD.discretizationProcedure(self.arguments.discretizationApproach, currentOutFile, currentFile, self.arguments.problemName, currentPseudoTime, expressionDataFile, pseudotimeFile)

                    discretizedFiles.append(currentOutFile)

            else:

                print("nao eh nem clustering nem correlation")

                currentDir = dirName + "/"

                readSplineData = pd.read_csv(splineDataName, index_col=0)
                allGenes = readSplineData.T.columns

                currentFile = currentDir + "spline_" + self.arguments.problemName + "_" + currentPseudoTime + ".csv"
                currentGenesNamesFiles = currentDir + "genesNames_" + self.arguments.problemName + "_" + currentPseudoTime + ".txt"
                genesNamesFiles.append(currentGenesNamesFiles)
                directories.append(currentDir)
                currentOutFile = currentDir + Utils.dict_discretizationPrefixes[self.arguments.discretizationApproach] + self.arguments.problemName + "_" + currentPseudoTime + ".csv"
                DD.discretizationProcedure(self.arguments.discretizationApproach, currentOutFile, currentFile, self.arguments.problemName, currentPseudoTime, expressionDataFile, pseudotimeFile)

                discretizedFiles.append(currentOutFile)

        else:
            print("não eh full Discretization (FD)")

            self.Log.register('message', "Using not full discretization...")
            if self.arguments.clusterMethod in Utils.clusteringMethods:
                localClusterDir = Utils.dict_directories[self.arguments.clusterMethod]

                currentFile = splineDataName
                currentOutFile = Utils.dict_discretizationPrefixes[self.arguments.discretizationApproach] + self.arguments.problemName + "_full_" + currentPseudoTime + ".csv"
                DD.discretizationProcedure(self.arguments.discretizationApproach, currentOutFile, currentFile, self.arguments.problemName, currentPseudoTime, expressionDataFile, pseudotimeFile)

                for cluster in range(bestNClusters):
                    print("Discretizing data for cluster " + str(cluster))
                    self.Log.register('message', "Discretizing data for cluster " + str(cluster))

                    currentDir1 = os.path.join(os.getcwd(), localClusterDir)
                    currentDir = currentDir1 + "/Cluster" + str(cluster)
                    currentGenesNamesFiles = currentDir + "/geneNames_" + str(cluster) + "_" + currentPseudoTime + ".txt"
                    genesNamesFiles.append(currentGenesNamesFiles)
                    directories.append(currentDir)
                    currentOutFile2 = currentDir + Utils.dict_discretizationPrefixes[self.arguments.discretizationApproach] + self.arguments.problemName + "_" + str(cluster) + "_" + currentPseudoTime + ".csv"

                    DD.generateNotFullDiscretizationData(currentOutFile, currentOutFile2, currentGenesNamesFiles)

                    discretizedFiles.append(currentOutFile2)

            elif self.arguments.clusterMethod in Utils.correlationMethods:

                currentFile = splineDataName
                currentOutFile = Utils.dict_discretizationPrefixes[self.arguments.discretizationApproach] + self.arguments.problemName + "_full_" + currentPseudoTime + ".csv"
                DD.discretizationProcedure(self.arguments.discretizationApproach, currentOutFile, currentFile, self.arguments.problemName, currentPseudoTime, expressionDataFile, pseudotimeFile)

                currentDir = dirName + "/"

                readSplineData = pd.read_csv(splineDataName, index_col=0)
                allGenes = readSplineData.T.columns
                for gene in allGenes:
                    self.Log.register('message', "Discretizing data for gene " + str(gene))
                    currentFile = currentDir + "spline_" + self.arguments.problemName + "_" + str(gene) + "_" + currentPseudoTime + ".csv"
                    currentGenesNamesFiles = currentDir + "/geneNames_" + str(gene) + "_" + currentPseudoTime + ".txt"
                    genesNamesFiles.append(currentGenesNamesFiles)
                    directories.append(currentDir)
                    currentOutFile2 = currentDir + Utils.dict_discretizationPrefixes[self.arguments.discretizationApproach] + self.arguments.problemName + "_" + str(gene) + "_" + currentPseudoTime + ".csv"

                    DD.generateNotFullDiscretizationData(currentOutFile, currentOutFile2, currentGenesNamesFiles)

                    discretizedFiles.append(currentOutFile2)

            else:

                currentDir = dirName + "/"

                readSplineData = pd.read_csv(splineDataName, index_col=0)
                allGenes = readSplineData.T.columns

                currentFile = currentDir + "spline_" + self.arguments.problemName + "_" + currentPseudoTime + ".csv"
                currentGenesNamesFiles = currentDir + "geneNames_" + self.arguments.problemName + "_" + currentPseudoTime + ".txt"
                genesNamesFiles.append(currentGenesNamesFiles)
                directories.append(currentDir)
                currentOutFile = currentDir + Utils.dict_discretizationPrefixes[self.arguments.discretizationApproach] + self.arguments.problemName + "_" + currentPseudoTime + ".csv"
                DD.discretizationProcedure(self.arguments.discretizationApproach, currentOutFile, currentFile, self.arguments.problemName, currentPseudoTime, expressionDataFile, pseudotimeFile)

                discretizedFiles.append(currentOutFile)

        return genesNamesFiles, directories, additional_discretizedFiles, discretizedFiles
            
                                

                
                
        
        
