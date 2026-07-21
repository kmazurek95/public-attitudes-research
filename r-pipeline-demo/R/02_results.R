# 02_results.R — plain-text summary of the fitted models.

suppressPackageStartupMessages(library(lme4))

models <- readRDS("data/models.rds")
icc <- function(m) { v <- as.data.frame(VarCorr(m))$vcov; round(v[1] / sum(v), 4) }

dir.create("results", showWarnings = FALSE)
sink("results/summary.txt")
cat("Multilevel models of redistribution support — SYNTHETIC data\n")
cat("============================================================\n\n")
cat(sprintf("Null-model ICC (between-neighbourhood variance share): %.4f\n\n", icc(models$null)))
cat("Full-model fixed effects:\n")
print(round(summary(models$full)$coefficients, 3))
cat("\nModel comparison (lower AIC = better):\n")
print(round(sapply(models, AIC), 1))
sink()

cat("Wrote results/summary.txt\n")
cat(readLines("results/summary.txt"), sep = "\n")
cat("\n")
