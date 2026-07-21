# 01_fit_models.R — fit the multilevel sequence with lme4:
#   null (variance decomposition) -> + neighbourhood context -> + individual controls.

suppressPackageStartupMessages(library(lme4))

d <- read.csv("data/synthetic_survey.csv")

icc <- function(m) {
  v <- as.data.frame(VarCorr(m))$vcov   # c(neighbourhood_var, residual_var)
  round(v[1] / sum(v), 4)
}

m0 <- lmer(redistribution ~ 1 + (1 | nbhd_id), data = d, REML = FALSE)
m1 <- lmer(redistribution ~ low_income_share + (1 | nbhd_id), data = d, REML = FALSE)
m2 <- lmer(redistribution ~ low_income_share + ind_income + education + age + migration +
             (1 | nbhd_id), data = d, REML = FALSE)

dir.create("data", showWarnings = FALSE)
saveRDS(list(null = m0, context = m1, full = m2), "data/models.rds")
cat(sprintf("Null-model ICC (between-neighbourhood share of variance): %.4f\n", icc(m0)))
cat("Models saved -> data/models.rds\n")
