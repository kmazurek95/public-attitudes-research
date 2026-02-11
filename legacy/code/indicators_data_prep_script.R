
require(haven)
require(stargazer)
require(ivreg)
require(plm)
require(sandwich)
require(lmtest)    
require(dplyr)
require(questionr)
require(ggplot2)
library(tidyverse) 
library(backports)
library(broom)
library(car)
library(zoo)
library(lmtest)
library(foreign)
library(readxl)


#rm(list=ls()) # Clears working environment
#rm(merged_buurt)

setwd("C:/Users/kaleb/OneDrive/Documents")

indicators_beert_wijk_gemeente <- read_csv("C:/Users/kaleb/OneDrive/Documents/indicators_beert_wijk_gemeente.csv")

indicators_beert_wijk_gemeente <- as.data.frame(`indicators_beert_wijk_gemeente`)

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


# indicators_buurt$buurt_code_eight <- gsub("^.{0,2}", "", indicators_buurt$buurt_code_eight) ##this is how we can create a buurt code without the letters in r

#---------------------------------------------------------------------------------------

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



#SAVE THE THREE LEVELS OF INDICATORS TO STATA, CSV, &  R DATA FORMATS

#BUURT INDICATORS
save(indicators_buurt, file = "C:/Users/kaleb/OneDrive/Desktop/attitudes-toward-income-inequality/processed_indicators/prepped_indicators_buurt.RData")
write.dta(indicators_buurt, "C:/Users/kaleb/OneDrive/Desktop/attitudes-toward-income-inequality/processed_indicators/prepped_indicators_buurt.dta")
write.csv(indicators_buurt,"C:/Users/kaleb/OneDrive/Desktop/attitudes-toward-income-inequality/processed_indicators/prepped_indicators_buurt.csv")


#WIJK INDICATORS

save(indicators_wijk, file = "C:/Users/kaleb/OneDrive/Desktop/attitudes-toward-income-inequality/processed_indicators/prepped_indicators_wijk.RData")
write.dta(indicators_wijk, "C:/Users/kaleb/OneDrive/Desktop/attitudes-toward-income-inequality/processed_indicators/prepped_indicators_wijk.dta")
write.csv(indicators_wijk,"C:/Users/kaleb/OneDrive/Desktop/attitudes-toward-income-inequality/processed_indicators/prepped_indicators_wijk.csv")


#GEMEENTE INDICATORS
save(indicators_gemeente, file = "C:/Users/kaleb/OneDrive/Desktop/attitudes-toward-income-inequality/processed_indicators/prepped_indicators_gemeente.RData")
write.dta(indicators_gemeente, "C:/Users/kaleb/OneDrive/Desktop/attitudes-toward-income-inequality/processed_indicators/prepped_indicators_gemeente.dta")
write.csv(indicators_gemeente,"C:/Users/kaleb/OneDrive/Desktop/attitudes-toward-income-inequality/processed_indicators/prepped_indicators_gemeente.csv")





