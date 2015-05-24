#!/bin/env Rscript

library(ggplot2)
library(scales)
library(plyr)
library(gridExtra)
library(getopt)

spec = matrix(c(
    'verbose', 'v', 2, "integer",
    'help', 'h', 0, "logical",
    'std', 's', 1, 'character',
    'jit', 'j', 1, 'character',
    'output', 'o', 2, 'character'
  ), byrow=TRUE, ncol=4)

opt = getopt(spec)

if (!is.null(opt$help)) {
  cat(getopt(spec, usage=TRUE))
  q(status=1)
}

if (is.null(opt$verbose)) { opt$verbose = FALSE }
if (is.null(opt$output)) { opt$output = 'regions-barplot.pdf'}

get_runtime_data <- function(raw, metric) {
  colnames(raw) = c("Project", "Domain", "Region", "Metric", "Core", "Value")
  #colnames(raw) = c("Project", "Region", "Metric", "Core", "Value")
  rt <- raw[raw$Metric == metric,]
  rt <- aggregate(as.numeric(as.character(rt$Value)), by=list(rt$Project, rt$Region, rt$Domain), FUN=sum)
  #rt <- aggregate(as.numeric(as.character(rt$Value)), by=list(rt$Project, rt$Region), FUN=sum)

  print(head(rt))
  
  colnames(rt) = c("Project", "Region", "Domain", "Value")
  #colnames(rt) = c("Project", "Region", "Value")

  return(rt)
}

group_stages <- function(raw) {
  rt <- raw

  print ("================================")
  comp.regions.noncrit <- c("ExtractScops", "PreoptMain", "OptMain")
  comp.regions.crit <- c("CodeGenMain")
  comp.regions <- c(comp.regions.noncrit, comp.regions.crit)

  main.regions <- c("RunMain")

  # Construct JIT regions:
  all.regions <- unique(rt$Region)
  jit.regions <- setdiff(all.regions, comp.regions)

  rt.comp.noncrit <- rt[rt$Region == comp.regions.noncrit,]
  rt.comp.crit <- rt[rt$Region == comp.regions.crit,]
  rt.comp <- rt[rt$Region == comp.regions,]
  rt.jit <- rt[rt$Region == jit.regions,]
  print ("JIT")
  print(rt.jit)
  print(rt.jit[rt.jit$Project == "3mm",])

  rt.comp.noncrit$Stage <- rep(c("Compilation (non-critical)"), nrow(rt.comp.noncrit))
  rt.comp.crit$Stage <- rep(c("Compilation (critical)"), nrow(rt.comp.crit))
  rt.jit$Stage <- rep(c("Run Time"), nrow(rt.jit))

  rt <- rbind(rt.comp.noncrit, rt.comp.crit)
  rt <- rbind(rt, rt.jit)

  return(rt)
}

add_plot <- function (rtdata, title, log = FALSE) {
  print(head(rtdata))
  bp <-
    #ggplot(data=rtdata, aes(x=Region, y=Value, fill=Region, group=Project)) +
    ggplot(data=rtdata, aes(x=Stage, y=Value, fill=Region, group=Project)) +
    #facet_wrap(~ Project, ncol=6, scales="free") +
    facet_grid(~ Project, scales="free_y") +
    geom_bar(stat="identity", position=position_dodge())
  if (!log) {
    bp <- bp + scale_y_continuous()
  }
  else {
    bp <- bp + scale_y_log10(breaks = trans_breaks("log10", function(x) 10^x),
                             labels = trans_format("log10", math_format(10^.x)))
  }
  bp <- bp +
    theme(axis.text.x=element_text(angle=45, hjust = 1),
          legend.position="bottom",
          legend.text = element_text(size=8)) +
    ggtitle(title)
  return(bp)
}

print_plot <- function (plot, rows, cols) {
  #plots = dlply(std.rt, "Project", `%+%`, e1 = plot)
  #ml = do.call(marrangeGrob, c(plots, list(nrow=rows, ncol=cols)))
  #print(ml)
  print(plot)
}

std.likwid <- read.csv(opt$std, header=FALSE)
jit.likwid <- read.csv(opt$jit, header=FALSE)

std.rt <- group_stages(get_runtime_data(std.likwid, "Runtime (RDTSC) [s]"))
jit.rt <- group_stages(get_runtime_data(jit.likwid, "Runtime (RDTSC) [s]"))

#std.pwr <- get_runtime_data(std.likwid, "Power [W]")
#jit.pwr <- get_runtime_data(jit.likwid, "Power [W]")

#std.energy <- get_runtime_data(std.likwid, "Energy [J]")
#jit.energy <- get_runtime_data(jit.likwid, "Energy [J]")

#std.calls <- get_runtime_data(std.likwid, "call count")
#jit.calls <- get_runtime_data(jit.likwid, "call count")

#std.cpi <- get_runtime_data(std.likwid, "CPI")
#jit.cpi <- get_runtime_data(jit.likwid, "CPI")

# DIN A0?
#pdf(file=paste(opt$output,sep=""), width=11.6,height=20,onefile=TRUE,paper="special")

# Wiiiiiide
pdf(file=paste(opt$output,sep=""), width=50,height=5,onefile=TRUE,paper="special")

# DIN A4
#pdf(file=paste(opt$output,sep=""), width=11.6,height=8.2,onefile=TRUE,paper="special")

print_plot(add_plot(std.rt, "Run-Time profile (std)"), 2, 4)
print_plot(add_plot(std.rt, "Run-Time profile (std)", TRUE), 2, 4)

print_plot(add_plot(jit.rt, "Run-Time profile (jit)"), 2, 4)
print_plot(add_plot(jit.rt, "Run-Time profile (jit)", TRUE), 2, 4)

#print_plot(add_plot(std.pwr, "Power consumption [W] (std)"), 8, 4)
#print_plot(add_plot(jit.pwr, "Power consumption [W] (jit)"), 8, 4)

#print_plot(add_plot(std.energy, "Energy [J] (std)"), 8, 4)
#print_plot(add_plot(jit.energy, "Energy [J] (jit)"), 8, 4)

#print_plot(add_plot(std.calls, "Calls (std)"), 8, 4)
#print_plot(add_plot(jit.calls, "Calls (jit)"), 8, 4)

#print_plot(add_plot(std.cpi, "Cycles per instruction (std)"), 8, 4)
#print_plot(add_plot(jit.cpi, "Cycles per instruction (jit)"), 8, 4)

warnings()
dev.off()
