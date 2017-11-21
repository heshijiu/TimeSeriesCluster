#!/usr/bin/Python
# -*- coding: utf-8 -*-

#Get a matrin with size is  count * count and all element's value .
def Initial(count = 1, value = -1):
    w = []
    for i in range(0, count):
        a = []
        for j in range(0, count):
            a.append(value)
        w.append(a)
    return w
###################################################
#AffinityMatrx: affintyMatrx constructor.#######
class AffinityMatrx:
    w = []
    size = 0
    def __init__(self, size = 0, initialValue = -1):
        self.w = Initial(size, initialValue)
        self.size = len(self.w)
        return
    def GetMatrx(self):
        newMatrx = []
        for i in range(0,self.size):
            a = []
            for j in range(0, self.size):
                a.append(self.w[i][j])
            newMatrx.append(a)
        return newMatrx
    def WriteToFile(self,fileName = None):
        if fileName == None or isinstance(fileName, str) == False:
            print("Wrong File Name")
            return
        try:
            fo = open(fileName, "w+")
        except IOError:
            print("Read File Error")
        else:
            for i in range(0, self.size):
                for j in range(0, self.size):
                    fo.write(str(self.w[i][j]))
                    fo.write("#")
                fo.write("\n")
            fo.close()
        return
    def ClearMatrx(self):
        self.w[:] = []
        self.size = 0

class AffinityMatrxFromFile(AffinityMatrx):
    def __init__(self):
        self.ClearMatrx()
        return
    def ReadFile(self, fileName):
        if fileName == None or isinstance(fileName, str) == False:
            print("Wrong File Name")
            return
        self.ClearMatrx()
        try:
            fo = open(fileName)
        except IOError:
            print("Read File Error")
        else:
            for line in fo:
                fea = []
                content = line.split("#")
                for i in range(0, len(content) - 1):
                    fea.append(float(content[i]))
                self.w.append(fea)
            fo.close()
        self.size = len(self.w)
        return
class AffinityMatrxFromSingleSets(AffinityMatrx):
    def __init__(self):
        self.ClearMatrx()
        return
    def InitialMatrxWithSingleSets(self, singleSets = None, func = None):
        if singleSets == None or func == None:
            return
        self.ClearMatrx()
        self.size = len(singleSets)
        self.w = Initial(self.size)
        for i in range(0, self.size):
            for j in range(i, self.size):
                self.w[i][j] = self.w[j][i] = func(singleSets[i],singleSets[j])
        return
###################################################
class SortObject:
    __object = None
    __key = None
    def __init__(self, object = None, key = None):
        self.__object = object
        self.__key = key
        return
    def GetKey(self):
        return self.__key
    def GetObject(self):
        return self.__object

def GetKey(sobject):
    return sobject.GetKey()

class TemplateCluster:
    __templateSingles = None
    __labelList = None
    def __init__(self):
        self.__templateSingles = {}
        self.__templateSingles.clear()
        self.__labelList = []
        self.__labelList[:] = []
        return
    def FitByOneSingle(self, single = None, label = None):
        if single == None or label == None:
            return
        if self.__templateSingles.__contains__(label):
            self.__templateSingles[label].append(single)
        else:
            target = []
            target[:] = []
            self.__labelList.append(label)
            self.__templateSingles[label] = target
            self.__templateSingles[label].append(single)
        return
    def Fit(self, singles = None, labels = None):
        if singles == None or labels == None:
            return
        singleCount = len(singles)
        labelsCount = len(labels)
        if singleCount != labelsCount:
            print("Wrong input data")
            return
        for i in range(0, singleCount):
            self.FitByOneSingle(singles[i], labels[i])
        return
    def Predict(self, single = None, fun = None):
        if single == None or fun == None:
            return
        if len(self.__labelList) == 0:
            print("Please fit data first!")
            return
        resultInx = None
        minDist = float("inf")
        for label in self.__labelList:
            dist = 0.0
            templateSinges = self.__templateSingles[label]
            count = len(templateSinges)
            if count == 0:
                print("error")
                return
            for i in range(0, count):
                dist += fun(single, templateSinges[i])
            dist /= float(count)
            if dist < minDist:
                minDist = dist
                resultInx = label
        if resultInx == None:
            print("error")
            return None
        #self.RefitOneLable([single], resultInx,fun)
        return resultInx
    def RefitOneLable(self, singles = None, label = None, fun = None):
        if singles == None or fun == None or len(singles) == 0:
            return
        singleInTemp = self.__templateSingles[label]
        originalCount = len(singleInTemp)
        singleInTemp.extend(singles)
        count = len(singleInTemp)
        w = [[0 for i in range(count)] for j in range(count)]
        for i in range(0, count):
            for j in range(i, count):
                if i != j:
                    w[i][j] = fun(singleInTemp[i], singleInTemp[j])
                    w[j][i] = w[i][j]
        for i in range(count):
            w[i] = SortObject(i,sum(w[i]))
        w.sort(key = GetKey)
        newTemplateSingles = []
        for i in range(originalCount):
            print(w[i].GetObject())
            print(w[i].GetKey())
            newTemplateSingles.append(singleInTemp[w[i].GetObject()])
        self.__templateSingles[label] = newTemplateSingles
        return

if __name__ == "__main__":
    print("TimeSerisCluster")

