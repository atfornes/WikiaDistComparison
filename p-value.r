#!/usr/bin/env Rscript
require('poweRlaw')

require('stringi')

args = commandArgs(trailingOnly=TRUE)

if (length(args)==0) {
  stop("An argument must be supplied (input file).n", call.=FALSE)
}

fc <- file(args[1])
userContribs <- readLines(fc)
userContribs <- stri_sub(userContribs,3,-3)
userContribs <- strsplit(userContribs, ',')
print ('foo')
close(fc)

pvalues <- 1

numPlausible <- 0
for (i in 1:length(userContribs)){
  contribs <- as.integer(unlist(userContribs[i]))

  pl = displ$new(contribs)

  est = estimate_xmin(pl)

  pl$setXmin(1)

  bs <- bootstrap_p(pl, no_of_sims=100)
  print(bs$p)
  if (bs$p > 0.1) {
     numPlausible <- numPlausible + 1
     pvalues[[i]] <- 1
     dput(pvalues, file = paste(args[1], 'out', sep='.'))
  } else {
     pvalues[[i]] <- 0
  }
}

print (numPlausible)
