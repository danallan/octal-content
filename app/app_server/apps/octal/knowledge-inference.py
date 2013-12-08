import pymc as mc;
import pylab as pl;
import numpy as np;

pTest= .5;
test = mc.Bernoulli('test', pTest, value = 1) #coinflip

#dependant on test
pTest2 = mc.Lambda('pTest2', lambda test=test: pl.where(test, .5, .1))
test2 = mc.Bernoulli('test2', pTest2, value = 1)

#dependant on test and test2 (direct child of each, not just grandchild of test)
pTest3 = mc.Lambda('pTest3', lambda test2=test2, test=test: pl.where(test2, pl.where(test, .5, .3), pl.where(test, .3, .1)))
test3 = mc.Bernoulli('test3', pTest3, value = 1)

#question depending only on concept "test"
pQuestion1 = mc.Lambda('pQuestion1', lambda test=test: pl.where(test, .8, .2))
question1 = mc.Bernoulli('question1', pQuestion1, value = 1)

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

#this is a really hacky solution for now until I can spend more time figuring out how to do this more programatically
def stopGapDependencies(dependencies, name, idealP, nonIdealP, compensatoryP):
     p = 0;
     if len(dependencies) == 1:
         dep = dependencies[0]
         #for reference, the semantics of this are if dep=1, p=idealP, else if dep=0, p=nonIdealP
         p = mc.Lambda(name, lambda dep=dep: pl.where(dep, idealP, nonIdealP))
     elif len(dependencies) == 2:
         dep = dependencies[0]
         dep2 = dependencies[1]
         p = mc.Lambda(name, lambda dep=dep, dep2=dep2: pl.where(dep2, pl.where(dep, idealP, compensatoryP), pl.where(dep, compensatoryP, nonIdealP)))
     elif len(dependencies) == 3:
         dep = dependencies[0]
         dep2 = dependencies[1]
         dep3 = dependencies[2]
         p = (mc.Lambda(name, lambda dep=dep, dep2=dep2, dep3=dep3: pl.where(dep3, pl.where(dep2, pl.where(dep, idealP, compensatoryP),
             pl.where(dep, compensatoryP, compensatoryP/2)), pl.where(dep2, pl.where(dep, compensatoryP, compensatoryP/2),
             pl.where(dep, compensatoryP/2, nonIdealP)))))
     else:
         print "This is hacky and doesnt work for" + len(dependencies) + " dependencies"
     return p
         

model = mc.Model([pTest, test, pTest2, test2, pTest3, test3]);

samples = mc.MCMC(model)

samples.sample(10000)
