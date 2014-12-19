############################################################################################################
#First part of this program has code to do conversions and draws the curves
############
#To determine the probability of target winning, A, use the law of total probability:
# p(A) = Sum (p(A|B)p(B)) over all B
# Here, B will be all possible target TTC estimates and p(A|B) will be probability distracters
# are all lower than that target TTC estimate, B

# Assume mean estimate of distracter TTC is 0 and mean estimate of target TTC is dprime,
# (even though this is backwards because target will have lower collision time than
# distracter)
# x is TTC estimate of distracter
# Probability that distracter TTC estimate less than target is pnorm(x): area under curve
# less than x.
# m: number of objects, m-1 of which are distracters
# p(A|B)*p(B) = pnorm(x)^(m-1) * dnorm(x-dprime)
# Hacker & Ratcliff, 1979 and Eliot 1964 derive this, and I derived it independently

# Jakel & Wichmann say that "numerous assumptions necessary for mAFC" where m>2 but not clear
# whether talking about bias only or also about d'

makeIntegrandForDprime <- function(dprime,m) {
	
	integrand <- function(x) {
	  pnorm(x)^(m-1) * dnorm(x-dprime) 
	}
	return (integrand)
}

mAFCdprimeToPcorrect <- function(df) {   #proportion correct if d' = dprime
  #probability that target response is greater than distracter strength
  #expecting df$dprime, df$m, df$lapseRate
  integrand= makeIntegrandForDprime(df$dprime,df$m)
  pCorrect= integrate(integrand,lower= -Inf, upper= Inf)
  pCorrect = pCorrect$value #because it's a structure with various values
  #generate percent correct after incorporating lapse rate
  pCorrect = df$lapseRate*(1/df$m) + (1-df$lapseRate)*pCorrect
  df$pCorrect = pCorrect
  return(df)
  #return(data.frame(pCorrect))
}

#test
#mAFCdprimeToPcorrect(data.frame(dprime=1,m=2,lapseRate=0))

#to convert from percent correct to d-prime
#need to do a search which minimizes discrepancy between predicted percent correct from mAFCdprimeToPcorrect and actual
mAFCdprimeToPcorrectForOptim<- function(dprime,targetPctCorr,m,lapseRate) { 
	#generate true percent correct for this dprime, and return discrepancy with target,  squared
	temp=data.frame(m=m,dprime=dprime,lapseRate=lapseRate)
	pctCorr = mAFCdprimeToPcorrect(temp)  #
	pctCorr= pctCorr$pCorrect
	(targetPctCorr-pctCorr)^2    #squared error term
}

mAFCpCorrectToDprime<- function(pCorr,m,lapseRate) {

  #pCorrect = df$lapseRate*(1/df$m) + (1-df$lapseRate)*pCorrect   other direction
  #go from inclusion of lapses to exclusion
  pCorr = ( pCorr - lapseRate*(1.0/m) ) / (1-lapseRate) 
  fit = optimize(function(dprime) mAFCdprimeToPcorrectForOptim(dprime,pCorr,m,lapseRate),     interval=c(.0001,20) )
  dprime= fit$minimum
  dprime
}

#test
#pCorr=.90; lapseRate=.01
#mAFCpCorrectToDprime(pCorr,m=2,lapseRate=lapseRate)

