library(ggplot2)

papi <- read.csv("~/src/polyjit/pprof-study/results/install/bin/pprof-calibrate.profile.events.csv")

pprof <- papi
st_new <- sapply(papi[,1], FUN= function(x) { return(x %/% 1) })
pprof["StartTime"] <- st_new
pprof[1,3] <- 0
dur_new <- sapply(pprof[,3], FUN= function(x) { return(x %/% 1) })
pprof["Duration"] <- dur_new
lab <- with(pprof, pprof[,3])

plot <- ggplot(data=pprof, aes(x=Region, y= StartTime, fill=Duration)) + geom_tile() + scale_x_discrete(breaks=lab)
plot