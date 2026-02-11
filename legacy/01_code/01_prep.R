# Load packages
library(haven)
library(tidyverse) 

# clear working environment
rm(list=ls())

#-------------------------------------------------------------------------------
# PART 1 - SURVEY DATA (SCORE) PREPARATION
#-------------------------------------------------------------------------------

# Load data from the R Project folder

score <- read_dta("./02_data_orig/score.dta")
score <- as.data.frame(`score`)

# We add leading zeros to the existing neighborhood code variable ("Buurtcode")
# so it can be merged with administrative data (see below). We truncate the
# resulting variable to create codes for the district ("wijk") and municipality
# ("gemeente"), again to facilitate merging.

score <- score %>%
  mutate(buurt_id = case_when(
  Buurtcode > 9999 & Buurtcode < 100000 ~ paste0("000", Buurtcode),
  Buurtcode > 99999 & Buurtcode < 1000000 ~ paste0("00", Buurtcode),
  Buurtcode > 999999 & Buurtcode < 10000000 ~ paste0("0", Buurtcode),
  Buurtcode > 9999999 ~ paste0(Buurtcode)))

score$wijk_id <- substr(score$buurt_id, 1, 6)
score$gemeente_id <- substr(score$buurt_id, 1, 4)

# We only keep the variables we need for the analysis

score_final <- score %>%
  select(a27_1,a27_2, a27_3, b01, b02, b03, b04, b05, b06, b07, b08, b09, b10,
         b11, b12_1, b13, b14_1, b14_2, b14_3, b14_4, b14_5, b15, b16, b17, b18,
         b20, b21, b22, weegfac, Buurtcode, buurt_id,
         wijk_id, gemeente_id, respnr)

# Change the names of the variables

names(score_final)[1] <- "gov_int" # 1-fully disagree  7-fully agree
names(score_final)[2] <- "red_inc_diff" # 1-fully disagree  7-fully agree
names(score_final)[3] <- "union_pref" # 1-fully disagree  7-fully agree
names(score_final)[4] <- "sex"
names(score_final)[5] <- "birth_year"
names(score_final)[6] <- "educlvl "
names(score_final)[7] <- "educyrs"
names(score_final)[8] <- "voted"
names(score_final)[9] <- "vote_choice"
names(score_final)[10] <- "work_status"
names(score_final)[11] <- "has_worked"
names(score_final)[12] <- "work_type"
names(score_final)[13] <- "org_type"
names(score_final)[14] <- "leader_resp"
names(score_final)[15] <- "leader_resp_n"
names(score_final)[16] <- "job_desc"
names(score_final)[17] <- "home_owner"
names(score_final)[18] <- "other_real_estate"
names(score_final)[19] <- "savings"
names(score_final)[20] <- "stocks"
names(score_final)[21] <- "no_owner"
names(score_final)[22] <- "relig_yn"
names(score_final)[23] <- "relig_type"
names(score_final)[24] <- "religiosity"
names(score_final)[25] <- "relig_attend"
names(score_final)[26] <- "born_in_nl"
names(score_final)[27] <- "father_dutch"
names(score_final)[28] <- "mother_dutch"
names(score_final)[29] <- "weight"
names(score_final)[30] <- "geocode"
names(score_final)[31] <- "buurt_id"
names(score_final)[32] <- "wijk_id"
names(score_final)[33] <- "gemeente_id"
names(score_final)[34] <- "respondent_id"

#-------------------------------------------------------------------------------
# PART 2 - ADMINISTRATIVE DATA PREPARATION
#-------------------------------------------------------------------------------

# Load data

ind_bwg <- read_csv("./02_data_orig/indicators_buurt_wijk_gemeente.csv",
                    na = ".")

# Dropping unneeded variables

ind_bwg = subset(ind_bwg, select = -c(Codering_3,
                                      IndelingswijzigingWijkenEnBuurten_4,
                                      Marokko_19,
                                      Turkije_22))

# Translate the variable names into English

names(ind_bwg)[1] <- "id"
names(ind_bwg)[2] <- "code"
names(ind_bwg)[3] <- "municipality"
names(ind_bwg)[4] <- "region_type"
names(ind_bwg)[5] <- "pop_total"
names(ind_bwg)[6] <- "pop_over_65"
names(ind_bwg)[7] <- "pop_west"
names(ind_bwg)[8] <- "pop_nonwest"
names(ind_bwg)[9] <- "pop_dens"
names(ind_bwg)[10] <- "avg_home_value"
names(ind_bwg)[11] <- "avg_inc_recip"
names(ind_bwg)[12] <- "avg_inc_pers"
names(ind_bwg)[13] <- "perc_low40_pers"
names(ind_bwg)[14] <- "perc_high20_pers"
names(ind_bwg)[15] <- "perc_low40_hh"
names(ind_bwg)[16] <- "perc_high20_hh"
names(ind_bwg)[17] <- "perc_low_inc_hh" 
names(ind_bwg)[18] <- "perc_soc_min_hh"

# Subset the indicators into their three levels (Buurt, Wijk, and Gemeente)

ind_bu <- ind_bwg[ind_bwg$region_type == "Buurt",]
ind_wi <- ind_bwg[ind_bwg$region_type == "Wijk",]
ind_ge <- ind_bwg[ind_bwg$region_type == "Gemeente",]

# Name the indicators so we know which region they are measured at

colnames(ind_bu) <- paste0("b_", colnames(ind_bu))
colnames(ind_wi) <- paste0("w_", colnames(ind_wi))
colnames(ind_ge) <- paste0("g_", colnames(ind_ge))

# The buurt, wijk, and gemeente codes all start with two letters, which we
# remove to match them with the survey data

ind_bu$buurt_id <- substr(ind_bu$b_code, 3, 10)
ind_wi$wijk_id <- substr(ind_wi$w_code, 3, 8)
ind_ge$gemeente_id <- substr(ind_ge$g_code, 3, 6)

#-------------------------------------------------------------------------------
# PART 3 - MERGING SURVEY AND ADMINISTRATIVE DATA
#-------------------------------------------------------------------------------

# Adding in neighborhood data
merge_temp1 <- merge(x = score_final, y = ind_bu,
                    by = "buurt_id", all.x = TRUE)

# Adding in district data
merge_temp2 <- merge(x = merge_temp1, y = ind_wi,
                    by = "wijk_id", all.x = TRUE)

# Adding in municipality data
complete_merge <- merge(x = merge_temp2, y = ind_ge,
                        by = "gemeente_id", all.x = TRUE)

# Removing temporary data frames
rm(list=ls()[! ls() %in% c("complete_merge")])

write.csv(complete_merge,"./03_data_final/complete_merge1.csv")
