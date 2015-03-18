#!/usr/bin/env Rscript
library(getopt)

spec = matrix(c(
  'input', 'i', 1, 'character',
  'help', 'h', 0, "logical",
  'output', 'o', 1, 'character',
  'csv', 'c', 2, 'character',
  'name', 'n', 1, 'character',
  'quiet', 'q', 2, 'logical'
), byrow=TRUE, ncol=4)
opt = getopt(spec)

if (!is.null(opt$help)) {
  cat(getopt(spec, usage=TRUE))
  q(status=1)
}

if (is.null(opt$name)) {   opt$name = "UNDEFINED" }
if (is.null(opt$input)) {  opt$input = "~/src/polyjit/install/bin/pprof-calibrate.profile.events.csv" }
if (is.null(opt$output)) { opt$output = "pprof-heatmap.pdf" }
if (is.null(opt$quiet)) { opt$quiet = FALSE }

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

papi <- read.csv(opt$input)

buckets <- 50
bucket_size <- papi[1,3] %/% buckets
papi[,1] <- sapply(papi[,1], function(x) x %/% bucket_size)
papi[1,3] <- 0

papi <- melt(papi, id=1:2)
#> head(papi_molten)
#StartTime Region variable   value
#1         0  START Duration 2357836
#2         0      a Duration     752
#3         0      b Duration     261
#4         0      a Duration     477
#5         0      b Duration     160
#6         0      a Duration     473

papi <- cast(papi, StartTime + variable ~ Region, sum)
#> head(cast(papi_molten, StartTime + variable ~ Region, sum))
#StartTime variable   START     a     b c
#1         0 Duration 2357836 28750 11078 0
#2         1 Duration       0 34014 11727 0
#3         2 Duration       0 36060 12304 0
#4         3 Duration       0 35677 12855 0
#5         4 Duration       0 37503 13328 0
#6         5 Duration       0 38061 13373 0

rownames(papi) <- papi[,1]
papi_matrix <- t(data.matrix(papi[,4:ncol(papi)]))

if(!is.null(opt$csv)) {
  write.csv2(papi_matrix, file = opt$csv)
}

if(!opt$quiet) {
  my_colors <- colorRampPalette(c("white", "yellow", "red"))(n = 299)
  heatmap.2(papi_matrix,
            notecol="black",
            main=opt$name,
            trace="none",
            col=my_colors,
            scale= c("none"),
            dendrogram="none",
            Colv=FALSE)
}
