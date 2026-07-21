# 00_simulate_data.R — generate a SYNTHETIC neighbourhood-nested survey dataset.
# No real respondents: this mirrors the STRUCTURE of the SCoRE Netherlands
# neighbourhood-effects analysis (individuals nested in neighbourhoods, outcome =
# support for redistribution, 0-100) so the multilevel pipeline can be run and
# checked by anyone, with zero restricted microdata.

set.seed(2023)

n_neighbourhoods <- 300
avg_per_nbhd     <- 16

# ---- neighbourhood level ------------------------------------------------------
nbhd <- data.frame(
  nbhd_id          = sprintf("N%04d", seq_len(n_neighbourhoods)),
  low_income_share = plogis(rnorm(n_neighbourhoods, 0, 0.8)),  # key context predictor (0-1)
  u0               = rnorm(n_neighbourhoods, 0, 3.0)           # nbhd random intercept (small -> low ICC)
)

counts <- rpois(n_neighbourhoods, avg_per_nbhd)
counts[counts < 3] <- 3
d <- nbhd[rep(seq_len(n_neighbourhoods), counts), ]
n <- nrow(d)

# ---- individual level ---------------------------------------------------------
d$ind_income <- rnorm(n, 0, 1)                  # standardised household income
d$education  <- sample(1:4, n, replace = TRUE)  # education level 1..4
d$age        <- round(runif(n, 18, 80))
d$migration  <- rbinom(n, 1, 0.15)              # migration background (0/1)

# ---- outcome: support for redistribution (0-100) ------------------------------
# Planted structure: strong INDIVIDUAL SES gradient and a neighbourhood
# context effect of exactly ZERO. The demo's null is built in, not found,
# and is not evidence about the study.
lin <- 60 +
  -6.0 * d$ind_income +
  -2.5 * (d$education - 2.5) +
   0.05 * (d$age - 50) +
   3.0 * d$migration +
   0.0 * (d$low_income_share - 0.5) +   # contextual effect set to ZERO — mirrors the study's null
   d$u0                                  #   (low ICC still comes from u0; the predictor is non-significant)
d$redistribution <- pmin(100, pmax(0, lin + rnorm(n, 0, 12)))

dir.create("data", showWarnings = FALSE)
out <- d[, c("nbhd_id", "redistribution", "low_income_share",
             "ind_income", "education", "age", "migration")]
write.csv(out, "data/synthetic_survey.csv", row.names = FALSE)
cat(sprintf("Simulated %d respondents in %d neighbourhoods -> data/synthetic_survey.csv\n",
            n, n_neighbourhoods))
