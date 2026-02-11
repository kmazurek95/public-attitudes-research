
##############################################################################################################################################

#LOAD PACKAGES

##############################################################################################################################################


library(questionr)
library(haven)
library(sandwich)
library(dplyr)
library(tidyverse) 
library(car)
library(zoo)
library(foreign)

##############################################################################################################################################

#  PART I ---------------   SURVEY DATA (SCORE) PREDPARATION

##############################################################################################################################################

# load data from the R Project folder

rm(list=ls()) #clear working directory

score <- read_dta("./Data/score.dta")
score <- as.data.frame(`score`)


#------------------------------------------------------------------------------

#CORRECT BUURTCODES SO INDICATORS CAN BE MERGED ON BUURT, WIJK, and GEMEENTE 



#The issue with the score dataset is that the buurtcodes are not all eight-digits (this is happening because some of the buurtcodes do not have the leading zeros
# and this is necessary in order to create a eight digit buurtcode). To achieve this, we subset the score dataset by the number of digits in the incomplete buurtcodes.
# All the buurtcodes with five digits are NAs so we do not do anything with them. The buurtcodes with five digits get three leading zeros. The buurtcodes with siz digits 
# get two leading zeros. The buurtcodes with seven digits get get one leading zero. The buurtcodes with eight digits get no leading zeros because they are alreeady eight
# digits. Once all buurtcodes have eight digits, we subtract the last two digits from each buurtcode to get the wijk code and we subtract the last four digits to get the 
# gemeente code. Once all leading zeros are added and wijk and gemeente codes are generated, we add four sub data frames back together to re-create a complete dataset with
# all observations.

#Buurtcode (8 digits) = Gemeentecode (4 digits) + wijkcode (2 Digits) + buurtcode (2 Digits)

# WEBSITE THAT EXPLAINS THE INDICATOR LEVELS: https://www.cbs.nl/nl-nl/longread/aanvullende-statistische-diensten/2021/toelichting-wijk-en-buurtkaart-2021?onepage=true 

#------------------------------------------------------------------------------
#Four Digits

score_four_digit_buurtcodes <- score[score$Buurtcode > 1000 & score$Buurtcode < 10000,] #these have four digits but all are NA 

#------------------------------------------------------------------------------
# FIVE DIGITS 

score_five_digit_buurtcodes <- score[score$Buurtcode > 10000 & score$Buurtcode < 100000,] #these have five digits
score_five_digit_buurtcodes$buurt_code_eight_digits <- paste0("000", score_five_digit_buurtcodes$Buurtcode) #put three zeros in front of the code in order for it to be eight digits (buurtcode)

score_five_digit_buurtcodes$wijk_code_six_digits <- substr(score_five_digit_buurtcodes$buurt_code_eight_digits,1,nchar(score_five_digit_buurtcodes$buurt_code_eight_digits)-2)
score_five_digit_buurtcodes$gemeente_code_four_digits <- substr(score_five_digit_buurtcodes$buurt_code_eight_digits,1,nchar(score_five_digit_buurtcodes$buurt_code_eight_digits)-4)

#------------------------------------------------------------------------------
#SIX DIGITS

score_six_digit_buurtcodes <- score[score$Buurtcode > 100000 & score$Buurtcode < 1000000,] #these have six digits
score_six_digit_buurtcodes$buurt_code_eight_digits <- paste0("00", score_six_digit_buurtcodes$Buurtcode) #put two zeros in front of the code in order for it to be eight digits (buurtcode)

score_six_digit_buurtcodes$wijk_code_six_digits <- substr(score_six_digit_buurtcodes$buurt_code_eight_digits,1,nchar(score_six_digit_buurtcodes$buurt_code_eight_digits)-2)
score_six_digit_buurtcodes$gemeente_code_four_digits <- substr(score_six_digit_buurtcodes$buurt_code_eight_digits,1,nchar(score_six_digit_buurtcodes$buurt_code_eight_digits)-4)


#------------------------------------------------------------------------------
#SEVEN DIGITS

score_seven_digit_buurtcodes <- score[score$Buurtcode > 1000000 & score$Buurtcode < 10000000,] #these have seven digits
score_seven_digit_buurtcodes$buurt_code_eight_digits <- paste0("0", score_seven_digit_buurtcodes$Buurtcode) #put one zero in front of the code in order for it to be eight digits (buurtcode)

score_seven_digit_buurtcodes$wijk_code_six_digits <- substr(score_seven_digit_buurtcodes$buurt_code_eight_digits,1,nchar(score_seven_digit_buurtcodes$buurt_code_eight_digits)-2)
score_seven_digit_buurtcodes$gemeente_code_four_digits <- substr(score_seven_digit_buurtcodes$buurt_code_eight_digits,1,nchar(score_seven_digit_buurtcodes$buurt_code_eight_digits)-4)


#-----------------------------------------------------------------------------------------------------
#EIGHT DIGITS

score_eight_digit_buurtcodes <- score[score$Buurtcode > 10000000 & score$Buurtcode < 100000000,] #eight digits and fine the way they are
score_eight_digit_buurtcodes$buurt_code_eight_digits <- paste0("", score_eight_digit_buurtcodes$Buurtcode) #put one zero in front of the code in order for it to be eight digits (buurtcode)

score_eight_digit_buurtcodes$wijk_code_six_digits <- substr(score_eight_digit_buurtcodes$buurt_code_eight_digits,1,nchar(score_eight_digit_buurtcodes$buurt_code_eight_digits)-2)
score_eight_digit_buurtcodes$gemeente_code_four_digits <- substr(score_eight_digit_buurtcodes$buurt_code_eight_digits,1,nchar(score_eight_digit_buurtcodes$buurt_code_eight_digits)-4)


#------------------------------------------------------------------------------------------------------
# NOW THAT ALL OF THE BUURTCODES ARE EIGHT DIGITS, WE CAN BIND THE SEPERATE DATA FRAMES INTO ONE

total <- rbind(score_five_digit_buurtcodes, score_six_digit_buurtcodes, score_seven_digit_buurtcodes, score_eight_digit_buurtcodes) #why is the total more? (because of NAs)


# RESTRICT THE VARIABLES TO THE ONES WE NEED FOR THE ANALYSIS 

keeps <- c("a27_1","a27_2", "a27_3", "b01", "b02", "b03", "b04", "b05", "b06", "b07", "b08", "b09",
           "b10", "b11", "b12_1", "b13", "b14_1", "b14_2", "b14_3", "b14_4", "b14_5", "b15", "b16", "b17", "b18", "b19", "b20", "b21", "b22",
           "GENDERID", "weegfac", "Buurtcode", "buurt_code_eight_digits", "wijk_code_six_digits", "gemeente_code_four_digits", "respnr")

#SUBSET OF THE ORIGINAL DATASET WITH EIGHT DIGIT BUURTCODEA AND THE VARIABLES OF INTEREST

score_final <- total[keeps]

#---------------------------------------------------------------------------------------------------------
# GET THE NAMES OF OF THE VARIABLES AS THEY APPEAR IN THE ORIGINAL DATASET SO THE CAN BE RENAMED UNDER THEIR ENGLISH TRANSLATIONS

describe(score_final)

#CHANGE THE NAMES OF THE VARIABLES 

names(score_final)[1] <- "a27_1_government_intervention_into_the_economy" # 1-fully disagree  7-fully agree
names(score_final)[2] <- "a27_2_reduce_differences_in_income_levels" # 1-fully disagree  7-fully agree
names(score_final)[3] <- "a27_3_Employees_need_strong_trade_unions" # 1-fully disagree  7-fully agree
names(score_final)[4] <- "b01_sex"
names(score_final)[5] <- "b02_birth_year"
names(score_final)[6] <- "b03_highest_level_of_education "
names(score_final)[7] <- "b04_years_of_education"
names(score_final)[8] <- "b05_vote_in_the_last_parliamentary_elections_2017?"
names(score_final)[9] <- "b06_party_voted_for"
names(score_final)[10] <- "b07_employment_status"
names(score_final)[11] <- "b08_completed_paid_work_ever"
names(score_final)[12] <- "b09_salaried_or_self_employed_or_family_business"
names(score_final)[13] <- "b10_type_of_organization"
names(score_final)[14] <- "b11_leadership_responsability"
names(score_final)[15] <- "b12_1_how_many_people_responsible_for"
names(score_final)[16] <- "b13_description_current_previous_job?"
names(score_final)[17] <- "b14_1_home_ownership"
names(score_final)[18] <- "b14_2_other_realestate_ownership"
names(score_final)[19] <- "b14_3_savings_account_ownership"
names(score_final)[20] <- "b14_4_stock_or_bonds_ownership"
names(score_final)[21] <- "b14_5_no_ownership"
names(score_final)[22] <- "b15_member_of_a_faith_denomination"
names(score_final)[23] <- "b16_type_of_faith_denomination"
names(score_final)[24] <- "b17_religiosity"
names(score_final)[25] <- "b18_frequency_of_attendance_religious_service"
names(score_final)[26] <- "b19_apart_religious_services_frequency_of_prayer"
names(score_final)[27] <- "b20_born_in_netherlands"
names(score_final)[28] <- "b21_father_born_in_netherlands"
names(score_final)[29] <- "b22_mother_born_in_netherlands"
names(score_final)[30] <- "GENDERID"
names(score_final)[31] <- "Weegfactor"
names(score_final)[32] <- "Buurtcode"
names(score_final)[33] <- "buurt_code_eight_digits"
names(score_final)[34] <- "wijk_code_six_digits"
names(score_final)[35] <- "gemeente_code_four_digits"
names(score_final)[36] <- "respondent_number"

#----------------------------------------------------------------------------------------------------
#CONVERT THE CODES THAT THE INDICATORS WILL BE MATCHED ON INTO NUMERIC (IN THE CASES THEY ARE NOT ALREADY)

score_final$gemeente_code_four_digits <- sprintf(score_final$gemeente_code_four_digits)
describe(score_final$gemeente_code_four_digits)


#-----------------------------------------------------------------------------------------------------------
#SAVE THE PREPARED SCORE DATA IN csv FORMAT 

write.csv(score_final,"./Data/processed_score_data/score_prepped.csv")

#-----------------------------------------------------------------------------------------------------------










##############################################################################################################################################


#  PART II ---------------   PREPARE THE THREE LEVELS OF INDICATORS (I.E., BUURT, WIJK, AND GEMEENTE)


##############################################################################################################################################


#------------------------------------------------------------------------
# LOAD INDICATORS INTO WORKING ENVIRONMENT AND TRANSFORM TO DATAFRAME


indicators_beert_wijk_gemeente <- read_csv("./Data/indicators_buurt_wijk_gemeente.csv")
indicators_beert_wijk_gemeente <- as.data.frame(`indicators_beert_wijk_gemeente`)


#-------------------------------------------------------------------------------
#translate the variables into english 

names(indicators_beert_wijk_gemeente)[1] <- "id"
names(indicators_beert_wijk_gemeente)[2] <- "district_and_neighborhood"
names(indicators_beert_wijk_gemeente)[3] <- "municipality"
names(indicators_beert_wijk_gemeente)[4] <- "type_region"
names(indicators_beert_wijk_gemeente)[5] <- "code"
names(indicators_beert_wijk_gemeente)[6] <- "buurt_change_in_layout"
names(indicators_beert_wijk_gemeente)[7] <- "buurt_number_of_inhabitants"
names(indicators_beert_wijk_gemeente)[8] <- "buurt_n_Sixty_Five_Years_Or_Older"
names(indicators_beert_wijk_gemeente)[9] <- "buurt_WesternTotal"
names(indicators_beert_wijk_gemeente)[10] <- "Non_Western_Total"
names(indicators_beert_wijk_gemeente)[11] <- "Morocco"
names(indicators_beert_wijk_gemeente)[12] <- "Turkey"
names(indicators_beert_wijk_gemeente)[13] <- "Population_Density"
names(indicators_beert_wijk_gemeente)[14] <- "Average_Home_Value"
names(indicators_beert_wijk_gemeente)[15] <- "Average_Income_Per_Income_Recipient"
names(indicators_beert_wijk_gemeente)[16] <- "_Average_Income_Per_Inhabitant"
names(indicators_beert_wijk_gemeente)[17] <- "40_Lowest_Income_People"
names(indicators_beert_wijk_gemeente)[18] <- "_20_Persons_With_Highest_Income"
names(indicators_beert_wijk_gemeente)[19] <- "40_Lowest_Income_Households"
names(indicators_beert_wijk_gemeente)[20] <- "20_House_holds_With_Highest_Income"
names(indicators_beert_wijk_gemeente)[21] <- "low_income_households" 
names(indicators_beert_wijk_gemeente)[22] <- "House_hold_Under_Or_Around_Social_Minimum"
#---------------------------------------------------------------------------------------

#subset the indicators into their three levels (Buurt, Wijk, and Gemeente)

indicators_buurt <- indicators_beert_wijk_gemeente[indicators_beert_wijk_gemeente$type_region=="Buurt",]
indicators_wijk <- indicators_beert_wijk_gemeente[indicators_beert_wijk_gemeente$type_region=="Wijk",]
indicators_gemeente <- indicators_beert_wijk_gemeente[indicators_beert_wijk_gemeente$type_region=="Gemeente",]

#the buurt, wijk, and gemeente codes all have two characters in front of them that specifiy the type of region: Buurt= BU & Wijk=WK & Gemeente = GM
#We remove these to get the codes just with their numeric indentifiers

indicators_buurt$buurt_code_eight_digits <- substr(indicators_buurt$code,3, 10) #remove the first two characters of the code to get the eight digit buurtcode
indicators_wijk$wijk_code_six_digits <- substr(indicators_wijk$code,3, 8) #remove the first two characters of the code to get the six digit wijk code
indicators_gemeente$gemeente_code_four_digits <- substr(indicators_gemeente$code,3, 6) #remove the first two characters of the code to get the six digit wijk code


#---------------------------------------------------------------------------------------
#NAME THE INDICATORS SO WE KNOW THEY ARE AT THE LEVEL OF BUURT

names(indicators_buurt)[1] <- "buurt_id"
names(indicators_buurt)[2] <- "burt_district_and_neighborhood"
names(indicators_buurt)[3] <- "buurt_municipality"
names(indicators_buurt)[4] <- "buurt_type_region"
names(indicators_buurt)[5] <- "buurt_code"
names(indicators_buurt)[6] <- "buurt_change_in_layout"
names(indicators_buurt)[7] <- "buurt_number_of_inhabitants"
names(indicators_buurt)[8] <- "buurt_n_Sixty_Five_Years_Or_Older"
names(indicators_buurt)[9] <- "buurt_WesternTotal"
names(indicators_buurt)[10] <- "buurt_Non_Western_Total"
names(indicators_buurt)[11] <- "buurt_Morocco"
names(indicators_buurt)[12] <- "buurt_Turkey"
names(indicators_buurt)[13] <- "buurt_Population_Density"
names(indicators_buurt)[14] <- "buurt_Average_Home_Value"
names(indicators_buurt)[15] <- "buurt_Average_Income_Per_Income_Recipient"
names(indicators_buurt)[16] <- "buurt_Average_Income_Per_Inhabitant"
names(indicators_buurt)[17] <- "buurt_40_Lowest_Income_People"
names(indicators_buurt)[18] <- "buurt_20_Persons_With_Highest_Income"
names(indicators_buurt)[19] <- "buurt_40_Lowest_Income_Households"
names(indicators_buurt)[20] <- "buurt_20_House_holds_With_Highest_Income"
names(indicators_buurt)[21] <- "buurt_low_income_households" 
names(indicators_buurt)[22] <- "buurt_House_hold_Under_Or_Around_Social_Minimum"
names(indicators_buurt)[23] <- "buurt_code_eight_digits"


#---------------------------------------------------------------------------------------------------------------------------------------------------------------
#NAME THE INDICATORS SO WE KNOW THEY ARE AT THE LEVEL OF WIJK


names(indicators_wijk)[1] <- "wijk_id"
names(indicators_wijk)[2] <- "wijk_district_and_neighborhood"
names(indicators_wijk)[3] <- "wijk_municipality"
names(indicators_wijk)[4] <- "wijk_type_region"
names(indicators_wijk)[5] <- "wijk_code"
names(indicators_wijk)[6] <- "wijk_change_in_layout"
names(indicators_wijk)[7] <- "wijk_number_of_inhabitants"
names(indicators_wijk)[8] <- "wijk_n_Sixty_Five_Years_Or_Older"
names(indicators_wijk)[9] <- "wijk_WesternTotal"
names(indicators_wijk)[10] <- "wijk_Non_Western_Total"
names(indicators_wijk)[11] <- "wijk_Morocco"
names(indicators_wijk)[12] <- "wijk_Turkey"
names(indicators_wijk)[13] <- "wijk_Population_Density"
names(indicators_wijk)[14] <- "wijk_Average_Home_Value"
names(indicators_wijk)[15] <- "wijk_Average_Income_Per_Income_Recipient"
names(indicators_wijk)[16] <- "wijk_Average_Income_Per_Inhabitant"
names(indicators_wijk)[17] <- "wijk_40_Lowest_Income_People"
names(indicators_wijk)[18] <- "wijk_20_Persons_With_Highest_Income"
names(indicators_wijk)[19] <- "wijk_40_Lowest_Income_Households"
names(indicators_wijk)[20] <- "wijk_20_House_holds_With_Highest_Income"
names(indicators_wijk)[21] <- "wijk_low_income_households" 
names(indicators_wijk)[22] <- "wijk_House_hold_Under_Or_Around_Social_Minimum"
names(indicators_wijk)[23] <- "wijk_code_six_digits"


#-------------------------------------------------------------------------------------------------------------------------------------------------------------------
#NAME THE INDICATORS SO WE KNOW THEY ARE AT THE LEVEL OF gEMEENTE


names(indicators_gemeente)[1] <- "gemeente_id"
names(indicators_gemeente)[2] <- "gemeente_district_and_neighborhood"
names(indicators_gemeente)[3] <- "gemeente_municipality"
names(indicators_gemeente)[4] <- "gemeente_type_region"
names(indicators_gemeente)[5] <- "gemeente_code"
names(indicators_gemeente)[6] <- "gemeente_change_in_layout"
names(indicators_gemeente)[7] <- "gemeente_number_of_inhabitants"
names(indicators_gemeente)[8] <- "gemeente_n_Sixty_Five_Years_Or_Older"
names(indicators_gemeente)[9] <- "gemeente_WesternTotal"
names(indicators_gemeente)[10] <- "gemeente_Non_Western_Total"
names(indicators_gemeente)[11] <- "gemeente_Morocco"
names(indicators_gemeente)[12] <- "gemeente_Turkey"
names(indicators_gemeente)[13] <- "gemeente_Population_Density"
names(indicators_gemeente)[14] <- "gemeente_Average_Home_Value"
names(indicators_gemeente)[15] <- "gemeente_Average_Income_Per_Income_Recipient"
names(indicators_gemeente)[16] <- "gemeente_Average_Income_Per_Inhabitant"
names(indicators_gemeente)[17] <- "gemeente_40_Lowest_Income_People"
names(indicators_gemeente)[18] <- "gemeente_20_Persons_With_Highest_Income"
names(indicators_gemeente)[19] <- "gemeente_40_Lowest_Income_Households"
names(indicators_gemeente)[20] <- "gemeente_20_House_holds_With_Highest_Income"
names(indicators_gemeente)[21] <- "gemeente_low_income_households" 
names(indicators_gemeente)[22] <- "gemeente_House_hold_Under_Or_Around_Social_Minimum"
names(indicators_gemeente)[23] <- "gemeente_code_four_digits"

describe(indicators_gemeente$gemeente_code_four_digits)
#-------------------------------------------------------------------------------------------------------------------------------------------------------------------
#SAVE THE THREE LEVELS OF INDICATORS TO CSV FORMAT

#BUURT INDICATORS
write.csv(indicators_buurt,"./Data/processed_indicators/prepped_indicators_buurt.csv")
write.dta(indicators_buurt, "./Data/processed_indicators/prepped_indicators_buurt.dta")


#WIJK INDICATORS
write.csv(indicators_wijk,"./Data/processed_indicators/prepped_indicators_wijk.csv")
write.dta(indicators_wijk, "./Data/processed_indicators/prepped_indicators_wijk.dta")


#GEMEENTE INDICATORS
toString(indicators_gemeente$gemeente_code_four_digits)
write.csv(indicators_gemeente,"./Data/processed_indicators/prepped_indicators_gemeente.csv")
write.dta(indicators_gemeente, "./Data/processed_indicators/prepped_indicators_gemeente.dta")

#---------------------------------------------------------------------------------------------------------------------------------------------------------







##############################################################################################################################################


#  PART III  ---------------   MERGE THE THREE LEVELS OF INDICATORS WITH THE SURVEY DATA


##############################################################################################################################################


#--------------------------------------------------------------------------------------------------------------------------------------------------------
# CALL INDICATORS INTO ENVIRONMENT 
prepped_indicators_buurt <- read_csv("./Data/processed_indicators/prepped_indicators_buurt.csv")
prepped_indicators_buurt <- as.data.frame(`prepped_indicators_buurt`)

prepped_indicators_wijk <- read_csv("./Data/processed_indicators/prepped_indicators_wijk.csv")
prepped_indicators_wijk <- as.data.frame(`prepped_indicators_wijk`)

prepped_indicators_gemeente <- read_csv("./Data/processed_indicators/prepped_indicators_gemeente.csv")
prepped_indicators_gemeente <- as.data.frame(`prepped_indicators_gemeente`)

#--------------------------------------------------------------------------------------------------------------------------------------------------------
# CALL SCORE DATASET INTO ENVIRONMENT 
score_prepped <- read_csv("./Data/processed_score_data/score_prepped.csv")
score_prepped <- as.data.frame(`score_prepped`)

#--------------------------------------------------------------------------------------------------------------------------------------------------------
# MERGE THE SCORE DATA SET WITH EACH LEVEL OF INDICATOR TO CREATE THREE DATA SETS (ONE FOR EACH LEVEL OF INDICATOR)

#MERGE SERVEY DATA AND LEVEL 2 INDICATORS (BUURT)
merged_score_with__buurt_indicators_only <- merge(x = score_prepped, y = prepped_indicators_buurt, by = "buurt_code_eight_digits")

write.csv(merged_score_with__buurt_indicators_only,"./Data/merged_data/merged_buurt_only.csv")


#MERGE SERVEY DATA AND LEVEL 3 INDICATORS (WIJK)
merged_score_with_wijk_indicators_only <- merge(x = score_prepped, y = prepped_indicators_wijk, by= "wijk_code_six_digits") #merged wijk indicators with original data set 

write.csv(merged_score_with_wijk_indicators_only,"./Data/merged_data/merged_wijk_only.csv")


#MERGE SERVEY DATA AND LEVEL 4 INDICATORS (GEMEENTE)
merged_score_with_gemeente_indicators_only <- merge(x = score_prepped, y = prepped_indicators_gemeente, by= "gemeente_code_four_digits") #merged wijk indicators with original data set 

write.csv(merged_score_with_gemeente_indicators_only,"./Data/merged_data/merged_gemeente_only.csv")

#--------------------------------------------------------------------------------------------------------------------------------------------------------


#MERGE WIJK INDICATORS (LEVEL 3) WITH SCORE DATA CONTAINING LEVEL 2 INDICATORS (BUURT)
incomplete_merge <- merge(x = merged_score_with__buurt_indicators_only, y = prepped_indicators_wijk, by= "wijk_code_six_digits") #merge wijk indicators with the previous merge between score and buurt indicators

#MERGE GEMEENTE INDICATORS (LEVEL 4) WITH SCORE DATA CONTAINING LEVEL 2 & 3 INDICATORS (BUURT & WIJK) 
complete_merge <- merge(x = incomplete_merge, y = prepped_indicators_gemeente, by= "gemeente_code_four_digits", all.x = TRUE) #merge wijk indicators with the previous merge between score and buurt indicators

write.csv(complete_merge,"./Data/merged_data/complete_merge.csv")





##############################################################################################################################################


#  PART IV  ---------------   CLEAN THE MERGED DATASET AND GET IT INTO ITS FINAL FORM BEFORE THE ANALYSIS


##############################################################################################################################################




# TRANSFORM COMPLETE MERGE TO DATAFRAME 
complete_merge <- as.data.frame(`complete_merge`)

# DETERMINE VARIABLE TYPES AND SEE WHICH ONES NEED TO BE CONVERTED TO NUMERIC AND VICE VERSA
describe(complete_merge) 

#BUURT LEVEL INDICATORS THAT NEED TO BE CONVERTED TO NUMERIC
complete_merge$buurt_Population_Density <- as.numeric(complete_merge$buurt_Population_Density)
complete_merge$buurt_Average_Home_Value <- as.numeric(complete_merge$buurt_Average_Home_Value)
complete_merge$buurt_Average_Income_Per_Income_Recipient <- as.numeric(complete_merge$buurt_Average_Income_Per_Income_Recipient)
complete_merge$buurt_Average_Income_Per_Inhabitant <- as.numeric(complete_merge$buurt_Average_Income_Per_Inhabitant)
complete_merge$buurt_40_Lowest_Income_People <- as.numeric(complete_merge$buurt_40_Lowest_Income_People)
complete_merge$buurt_20_Persons_With_Highest_Income <- as.numeric(complete_merge$buurt_20_Persons_With_Highest_Income)
complete_merge$buurt_40_Lowest_Income_Households <- as.numeric(complete_merge$buurt_40_Lowest_Income_Households)
complete_merge$buurt_20_House_holds_With_Highest_Income <- as.numeric(complete_merge$buurt_20_House_holds_With_Highest_Income)
complete_merge$buurt_low_income_households <- as.numeric(complete_merge$buurt_low_income_households)
complete_merge$buurt_House_hold_Under_Or_Around_Social_Minimum <- as.numeric(complete_merge$buurt_House_hold_Under_Or_Around_Social_Minimum)

#WIJK LEVEL INDICATORS THAT NEED TO BE CONVERTED TO NUMERIC
complete_merge$wijk_Population_Density <- as.numeric(complete_merge$wijk_Population_Density)
complete_merge$wijk_Average_Home_Value <- as.numeric(complete_merge$wijk_Average_Home_Value)
complete_merge$wijk_Average_Income_Per_Income_Recipient <- as.numeric(complete_merge$wijk_Average_Income_Per_Income_Recipient)
complete_merge$wijk_Average_Income_Per_Inhabitant <- as.numeric(complete_merge$wijk_Average_Income_Per_Inhabitant)
complete_merge$wijk_40_Lowest_Income_People <- as.numeric(complete_merge$wijk_40_Lowest_Income_People)
complete_merge$wijk_20_Persons_With_Highest_Income <- as.numeric(complete_merge$wijk_20_Persons_With_Highest_Income)
complete_merge$wijk_40_Lowest_Income_Households <- as.numeric(complete_merge$wijk_40_Lowest_Income_Households)
complete_merge$wijk_20_House_holds_With_Highest_Income <- as.numeric(complete_merge$wijk_20_House_holds_With_Highest_Income)
complete_merge$wijk_low_income_households <- as.numeric(complete_merge$wijk_low_income_households)
complete_merge$wijk_House_hold_Under_Or_Around_Social_Minimum <- as.numeric(complete_merge$wijk_House_hold_Under_Or_Around_Social_Minimum)


#WIJK LEVEL INDICATORS THAT NEED TO BE CONVERTED TO NUMERIC
complete_merge$gemeente_Average_Home_Value <- as.numeric(complete_merge$gemeente_Average_Home_Value)


#REEVALUATE THE VARIABLE TYPES
describe(complete_merge)


# DELETE THE IRRELEVANT COLUMNS CREATED FROM THE MERGE
drop <- c("...1.y.1","...1.x.1", "...1.y", "...1.x")
complete_merge = complete_merge[,!(names(complete_merge) %in% drop)]


#DROP THE ROWS THAT CONTAIN NAs IN EVERY COLUMN
complete_merge <- complete_merge[rowSums(is.na(complete_merge)) != ncol(complete_merge), ]



#---------------------------------------------------------------------------------------------------------------------------------------------------------------



























