#!/usr/bin/env Rscript

if(!require("plyr")) {
  install.packages("plyr", dependencies = TRUE)
  library(plyr)
}

if(!require("reshape")) {
  install.packages("reshape", dependencies = TRUE)
  library(reshape)
}

if(!require("scales")) {
  install.packages("scales", dependencies = TRUE)
  library(scales)
}

if(!require("gplots")) {
  install.packages("gplots", dependencies = TRUE)
  library(gplots)
}

path.prefix = c("/nfs/scratch/pprof/2015-03-19/")
result.files = list.files(path=path.prefix, pattern="*.result.csv", recursive = TRUE)
heatmap.files = list.files(path=path.prefix, pattern="*.r.csv", recursive = TRUE)

for(i in 1:length(heatmap.files)) {
  heat.file <- heatmap.files[i]
  papi <- read.csv(file.path(path.prefix, heat.file))
  cat(file.path(path.prefix, heat.file), "\n")
  cat(ncol(papi), "\n")
  if (ncol(papi) > 4) {
    papi_matrix <- t(data.matrix(papi[,4:ncol(papi)]))
    my_colors <- colorRampPalette(c("white", "yellow", "red"))(n = 299)
    heatmap.2(papi_matrix, notecol="black", main=opt$name, trace="none",
              col=my_colors, scale= c("none"), dendrogram="none",
              Colv=FALSE)
  }
}
cat("Done.", "\n")