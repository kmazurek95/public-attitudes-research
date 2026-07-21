# run_all.R — run the whole synthetic pipeline end-to-end.
# Usage:  Rscript run_all.R   (from the r-pipeline-demo/ directory)

source("R/00_simulate_data.R")
source("R/01_fit_models.R")
source("R/02_results.R")
cat("\nDone. Synthetic pipeline ran end-to-end. See results/summary.txt\n")
