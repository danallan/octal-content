import pymc as mc;
import pylab as pl;
import numpy as np;
#######ALL THESE PARAMETERS ARE ARBITRARY AND SHOULD BE TRAINED OR BETTER CHOSEN OR SOMETHING
#probability of a guess
pG = .2
#probability of a slip
pS = .3
#compensatory probability (p(correct | partial knowledge of reqs), extra arbitrary - should probably be contextual)
pC = .4
#basic probability a student already knows a concept given we know they know all the prereqs.  Coinflip?  
pK = .5 #p(Knowledge)
#probability a student knows a concept given they miss knowledge on one or more prereqs
pU = .1 #p(Understanding)
#probability a student knows a concept given that they DON'T know ANY of the prereq(s)
pM = .05 #p(Magic)


#this is a really hacky solution for now until I can spend more time figuring out how to do this more programatically 
def stopGapDependencies(name, dependencies):
     p = 0;
     if len(dependencies) == 1:
         dep = dependencies[0]
         #for reference, the semantics of this are if dep=1, p=pK, else if dep=0, p=pM
         p = mc.Lambda(name, lambda dep=dep: pl.where(dep, pK, pM))
     elif len(dependencies) == 2:
         dep = dependencies[0]
         dep2 = dependencies[1]
         p = mc.Lambda(name, lambda dep=dep, dep2=dep2: pl.where(dep2, pl.where(dep, pK, pU), pl.where(dep, pU, pM)))
     elif len(dependencies) == 3:
         dep = dependencies[0]
         dep2 = dependencies[1]
         dep3 = dependencies[2]
         p = (mc.Lambda(name, lambda dep=dep, dep2=dep2, dep3=dep3: pl.where(dep3, pl.where(dep2, pl.where(dep, pK, pU),
             pl.where(dep, pU, pU/2)), pl.where(dep2, pl.where(dep, pU, pU/2),
             pl.where(dep, pU/2, pM)))))
     else:
         print "This is hacky and doesnt work for nodes with more than 3 dependencies"
     return p

         

###########hardcoding our graph in for some testing - fix this###############
primitives = mc.Bernoulli('primitives', pK, value=1)

proceduralExecution = mc.Bernoulli('proceduralExecution', pK, value=1)

pOperations = stopGapDependencies('pOperations', [primitives])
operations = mc.Bernoulli('operations', pOperations, value=1)

pVariables = stopGapDependencies('pVariables', [operations])
variables = mc.Bernoulli('variables', pVariables, value=1)

pConditionals = stopGapDependencies('pConditionals', [variables, proceduralExecution])
conditionals = mc.Bernoulli('conditionals', pConditionals, value=1)

pVariableMutation = stopGapDependencies('pVariableMutation',[variables])
variableMutation = mc.Bernoulli('variableMutation', pVariableMutation, value=1)

pTypes = stopGapDependencies('pTypes', [variables])
types = mc.Bernoulli('types', pTypes, value=1)

pIteration = stopGapDependencies('pIteration', [variableMutation, conditionals])
iteration = mc.Bernoulli('iteration', pIteration, value=1)

pFunctions = stopGapDependencies('pFunctions', [types])
functions = mc.Bernoulli('functions', pFunctions, value=1)

pArrays = stopGapDependencies('pArrays', [iteration])
arrays = mc.Bernoulli('arrays', pArrays, value=1)

pHofs = stopGapDependencies('pHofs', [functions])
hofs = mc.Bernoulli('hofs', pHofs, value=1)

pRecursion = stopGapDependencies('pRecursion', [functions])
recursion = mc.Bernoulli('recursion', pRecursion, value=1)

pSorting = stopGapDependencies('pSorting', [hofs, recursion, arrays])
sorting = mc.Bernoulli('sorting', pSorting, value=1)

pDataStructures = stopGapDependencies('pDataStructures', [arrays])
dataStructures = mc.Bernoulli('dataStructures', pDataStructures, value=1)

pAComplexity = stopGapDependencies('pAComplexity', [sorting, dataStructures])
aComplexity = mc.Bernoulli('acomplexity', pAComplexity, value=1)

########################################################################

pQuestion1 = mc.Lambda('pQuestion1', lambda types=types: pl.where(types, 1-pS, pG))
question1 = mc.Bernoulli('question1', pQuestion1, value=1, observed=True)


##################some simple tests##########

model = mc.Model([primitives, operations, variables, proceduralExecution, types, variableMutation, conditionals, functions, iteration, hofs, recursion, arrays, sorting, dataStructures, aComplexity, question1]);


samples = mc.MCMC(model)

samples.sample(10000)



#this needs tweaking till it works  Try constructing the pl.where structure instead maybe?
#def buildDependencies(dependencies, name, idealP, nonIdealP, compensatoryP):
 #   p = 0;
 #   if len(dependencies) == 1:
 #       dep = dependencies[0];
 #       #for reference, the semantics of this are if dep=1, p=idealP, else if dep=0, p=nonIdealP
 #       p = mc.Lambda('', lambda dep=dep: pl.where(dep, idealP, nonIdealP))
 #   else:
 #       previousDep = buildDependencies(dependencies[1:len(dependencies)], name, idealP, nonIdealP, compensatoryP)
 #       dep = dependencies[0];
 #       #likewise with above, just with two variables that vary between 1 and zero, with the 1 case first
 #       p = (mc.Lambda('', lambda previousDep=previousDep, dep=dep: pl.where(dep, pl.where(previousDep,
 #           idealP, compensatoryP), pl.where(previousDep, compensatoryP, nonIdealP))))
 #   return p


         

