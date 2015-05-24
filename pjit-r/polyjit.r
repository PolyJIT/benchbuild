#!/bin/env Rscript

library(coin)
library(Cairo)
library(Hmisc)
library(vioplot)
library(ggplot2)
#library(manipulate)

dvar <- function(x) {n=length(x) ; var(x,use="complete.obs") * (n-1) / n}
dsd  <- function(x) {n=length(x) ; sqrt(var(x, use="complete.obs") * (n-1) / n)}

# Color definitions.
standard_color <- rgb(0,0,0)
jitable_color  <- rgb(0.4,0.4,0.4)
extended_color <- rgb(0.8,0.8,0.8)

cat("\n")

# Read r.merged.csv, it is assumed that we used reorder.awk to process merged.csv
filePath <- "file://results/r.merged.csv"
covData <- read.table(file=url(filePath), header=T, sep=",")

covData$Class = factor(covData$Class,levels = rev(levels(covData$Class)),ordered = TRUE)

vplot <- qplot(data=covData, x=Class, y=ExecCov)
vplot <- vplot + geom_violin(adjust=0.45, trim=TRUE, scale="count", fill="grey80")
vplot <- vplot + geom_boxplot(position="dodge", width=0.08, outlier.size=3, fill="white")
vplot <- vplot + xlab("Class")
vplot <- vplot + theme_bw()
vplot <- vplot + theme(text = element_text(size=20),
                       legend.position = "none")
vplot <- vplot + ylab("ExecCov [%]")
vplot
ggsave("results/pjit-vioplot.pdf")

#merged <- read.csv("../results/merged.csv")

#standard_dyn <- as.numeric(as.character(merged$StdDyn))
#jitable_dyn <- as.numeric(as.character(merged$JitDyn))
#extended_dyn <- as.numeric(as.character(merged$ExtDyn))

#dynamic <- t(matrix(c(standard_dyn,jitable_dyn,extended_dyn),
#                    nrow = length(standard_dyn),
#                    ncol=3,     
#                    byrow=FALSE))

#par(ps=14)
#ox <- vioplot(standard_dyn, jitable_dyn, names=c("Static", "Dynamic"),
#               lty=1, # Outline of the violin, e.g., 1=solid, 2=dashed, 3=dotted
#               h=3,   # Density approximation factor, default is 3.
#               col="lightblue",
#               pchMed=15,
#               lwd=1,
#               ylim=c(0,100),
#               colMed="black",
#               rectCol="snow",
#               horizontal=F)
#title("", ylab="ExecCov [%]")


#box <- vioplot(extended_dyn, jitable_dyn, standard_dyn,insta outline=TRUE,
#               horizontal=F, boxwex = 0.7, notch=T, cex.axis=0.6)

#box <- boxplot(extended_dyn, jitable_dyn, standard_dyn, outline=TRUE,
#               horizontal=F, boxwex = 0.7, notch=T, cex.axis=0.6)
#axis(2, at=c(1,2,3), labels=F)
#text(y=seq(1,3,by=1), par("usr")[1]-2, labels = c("Ext", "Dyn", "Stat"),
#     srt = 45, pos = 2, xpd = TRUE, cex=0.6)

# describe(standard_dyn)

# dvar(standard_dyn)
# dvar(jitable_dyn)
# dvar(extended_dyn)

# tstd <- as.numeric(merged$Tstd)
# tjit <- as.numeric(merged$Tjit)
# text <- as.numeric(merged$Text)

# num_dyn <- length(standard_dyn)
# max_dyn <- max(extended_dyn)

# #par(cex.lab=1, cex.axis=1, mar=c(5,4,1,1))

# ##################################################
# # The plot.
# ##################################################
# # PDF output. DIN A4, Margins: 5b 2l 1t 1r
# #Cairo(type='pdf', file="both-polyjit-dyn.pdf", width=11.6, height = 8.2, units='in')
# #barplot(dynamic, beside=TRUE,
# #        col = c(standard_color, jitable_color, extended_color),
# #        yaxt="n", ylab="Laufzeitanteil in [%]", xlab="Programme",
# #        family="HersheySerif")
# #legend(x="topright", legend=c("Klassisch", "Erreichbar nach Abschluss PJIT-ANW",
# #                              "Erreichbar nach Abschluss PJIT-METH"),
# #       lwd=2,  col=c(standard_color, jitable_color, extended_color))
# #
# #par(family="HersheySerif")

# # Fake-Plot to attach the program names on the X-axis
# #midpoints <- barplot(standard_dyn, plot=FALSE, space=3)
# #text(midpoints, par("usr")[3], labels = merged$Name,
# #     srt = 45, pos = 2, xpd = TRUE, cex=0.8)
# #axis(2, at=0:100, lab=0:100, cex.axis=0.8)

# # Horizontal lines (Mean).
# std_mean <- mean(standard_dyn)
# #abline(h=std_mean, col=standard_color, lwd=1.5)
# #text(4.2*num_dyn, std_mean+0.6, pos=2, labels=c("\\/O"), cex=0.8)

# jit_mean <- mean(jitable_dyn)
# #abline(h=jit_mean, col=jitable_color, lwd=1.5)
# #text(4.2*num_dyn, jit_mean+0.6, pos=2, labels=c("\\/O"), cex=0.8)

# ext_mean <- mean(extended_dyn)
# #abline(h=ext_mean, col=extended_color, lwd=1.5)
# #text(4.2*num_dyn, ext_mean+0.6, pos=2, labels=c("\\/O"), cex=0.8)

# ##################################################
# # Significance & Correlation.
# ##################################################

# # Significance
# kruskal_data <- c(standard_dyn, jitable_dyn, extended_dyn)
# standard_vec <- c(1:num_dyn)
# standard_vec <- replace(standard_vec, c(1:num_dyn), "standard")
# jitable_vec <- c(1:num_dyn)
# jitable_vec <- replace(jitable_vec, c(1:num_dyn), "jitable")
# extended_vec <- c(1:num_dyn)
# extended_vec <- replace(extended_vec, c(1:num_dyn), "extended")
# kruskal_data <- cbind(as.numeric(kruskal_data), as.factor(c(standard_vec, jitable_vec, extended_vec)))
# colnames(kruskal_data) <- c("Dynamic", "Approach")

# wilcox.test(standard_dyn, jitable_dyn, paired=FALSE)
# wilcox.test(jitable_dyn, extended_dyn, paired=FALSE)

# cat("\n")
# cat("Kruskal-Wallis test (Are the data sets (standard, jitable, extended) significantly different?):\n\n")
# cat("  dynamic coverage ~ approach (p value):\t", kruskal.test(Dynamic ~ Approach, data=kruskal_data)$p.value, "\n")
# cat("\n")
# cat("  dynamic coverage (mean):", "\n")
# cat("    standard:\t", mean(standard_dyn), "\n")
# cat("    jitable:\t", mean(jitable_dyn), "\n")
# cat("    extended:\t", mean(extended_dyn), "\n")
# cat("\n")

# cat(" standard std-dev", sd(standard_dyn), "\n")
# cat(" jitable std-dev", sd(jitable_dyn), "\n")
# cat(" extended std-dev", sd(extended_dyn), "\n")
# cat("\n")
# cat(" standard variance",var(standard_dyn), "\n")
# cat(" jitable variance", var(jitable_dyn), "\n")
# cat(" extended variance",var(extended_dyn), "\n")

# # ======== Benefit(Jitable) vs. Domain =========================================
# jit_benefit_vec <- jitable_dyn - standard_dyn
# jit_domain_data <- matrix(c(jit_benefit_vec,
#                             as.factor(as.character(merged$Domain))),
#                           ncol=2, nrow=length(jit_benefit_vec))
# colnames(jit_domain_data) <- c("JitBenefit", "Domain")
# jitbenefit_domain <- kruskal.test(JitBenefit ~ Domain, data=jit_domain_data)
# cat("Kruskal-Wallis test (Are there significant differences between domains: \
#      standard vs. jitable?):\n\n")
# cat("  JitBenefit ~ Domain (p value):\t", jitbenefit_domain$p.value, "\n")

# # ======== Benefit(Extended) vs Domain =========================================
# dyn_benefit_vec <- extended_dyn - jitable_dyn
# dyn_domain_data <- matrix(c(dyn_benefit_vec,
#                             as.factor(as.character(merged$Domain))),
#                           ncol=2, nrow=length(dyn_benefit_vec))
# colnames(dyn_domain_data) <- c("DynBenefit", "Domain")
# extbenefit_domain <- kruskal.test(DynBenefit ~ Domain, data=dyn_domain_data)
# cat("Kruskal-Wallis test (Are there significant differences between domains: \
#      jitable vs. extended?):\n\n")
# cat("  ExtBenefit ~ Domain (p value):\t", extbenefit_domain$p.value, "\n")


# cat("\n\nIs there a significant difference between run-time and standard coverage?:\n")
# std_time_data <- matrix(c(standard_dyn, tstd), ncol=2, nrow=length(standard_dyn))
# colnames(std_time_data) <- c("StdBenefit", "Time")
# rcorr(   std_time_data, type="spearman")
# rcorr(   std_time_data, type="pearson")

# shapiro.test(standard_dyn)
# shapiro.test(jitable_dyn)
# shapiro.test(extended_dyn)

# shapiro.test(tstd)
# shapiro.test(tjit)
# shapiro.test(text)

# # Check: Daten sind nicht normalverteilt. (shapiro)

# cat(" Wilcoxon Test: StdDyn vs. Tstd (p-value): ")
# cat(wilcox.test(standard_dyn, tstd, paired=T)$p.value)

# cat("\n Wilcoxon Test: JitDyn vs. Tjit (p-value): ")
# cat(wilcox.test(jitable_dyn, tjit, paired=T)$p.value)

# cat("\n Wilcoxon Test: ExtDyn vs. Text (p-value): ")
# cat(wilcox.test(extended_dyn, text, paired=T)$p.value)

# cat("\n\n Benefit per domain: \n\n")
# domains       <- c()
# mean_extended <- c()
# mean_jitable  <- c()
# for(f in levels(as.factor(as.character(merged$Domain)))) {
#   ext_per_domain <- as.numeric(as.character(merged[f==merged$Domain,]$ExtDyn))
#   std_per_domain <- as.numeric(as.character(merged[f==merged$Domain,]$StdDyn))
#   jit_per_domain <- as.numeric(as.character(merged[f==merged$Domain,]$JitDyn))
  
#   ext <- mean(ext_per_domain)
#   std <- mean(std_per_domain)
#   jit <- mean(jit_per_domain)
  
#   mean_extended <- c(mean_extended, ext - std)
#   mean_jitable  <- c(mean_jitable, jit - std)
#   domains       <- c(domains, f)

#   cat (" Std:", std, " Jit:", jit, " Ext:", ext,
#        " Benefit: ", jit - std, ", ", ext - std, ", ", ext - jit, " - ", f,
#        "\n")
# }

# cat("\n")
