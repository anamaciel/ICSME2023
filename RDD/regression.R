library(readr)
library(ggplot2)
library(stargazer)
library(lme4)
library(MuMIn)
library(lmerTest)
library(rms)
library(sjstats)
library(ggpubr)

# Importing dataset
data <- read.csv("testeData9-agoravai.csv",sep=",")
data['time'] <- lapply(data['time'] , factor)

data$time <- rep((1:24)[1:24 != 0], 91)

data["month_index"] <- NA
data$month_index <- rep((-12:12)[-12:12 != 0], 91)
data$month_index <- factor(data$month_index, levels=c((-12:12)[-12:12 != 0]),ordered=TRUE)

# Fit the model including fixed and random effects

# RDD - Number of new users issues
vif(lm(log(new_users_issues + 1) ~ ageIssues
       + log(total_number_issues_authors)
       + log(issues_total)
       + time 
       + intervention
       + time_after_intervention, data=data))

# RDD - Number of new issues per month
vif(lm(log(issues_per_month + 1) ~ issues_total
       + log(ageIssues)
       + log(total_number_issues_authors)
       + log(issues_total)
       + time 
       + intervention
       + time_after_intervention, data=data))

# RDD - Number of new issues per month
vif(lm(log(pr_per_month + 1) ~ pr_total
       + log(agePulls)
       + log(total_number_pr_authors)
       + time 
       + intervention
       + time_after_intervention, data=data))

# RDD - Number of new users pulls
vif(lm(log(new_users_pulls + 1) ~ agePulls
       + log(total_number_pr_authors)
       + log(pr_total)
       + time 
       + intervention
       + time_after_intervention, data=data))

#se o numero for maior que 5 precisa remover a variável

rdd_issues = lme4::lmer(log(new_users_issues + 1) ~ ageIssues
                           + log(total_number_issues_authors)
                           + log(issues_total)
                           + time 
                           + intervention
                           + time_after_intervention
                           + (1 | name)
                           + (1 | lang), data=data)


r.squaredGLMM(rdd_issues)

anova(rdd_issues)

stargazer(rdd_issues, type="text")

#pulls

rdd_pulls = lme4::lmer(log(new_users_pulls + 1) ~ agePulls
                        + log(total_number_pr_authors)
                        + log(pr_total)
                        + time 
                        + intervention
                        + time_after_intervention
                        + (1 | name)
                        + (1 | lang), data=data)

r.squaredGLMM(rdd_pulls)

anova(rdd_pulls)

stargazer(rdd_pulls, type="text")

#issues_per_month
rdd_issues_per_month = lme4::lmer(log(issues_per_month + 1) ~ issues_total
                                  + log(ageIssues)
                                  + log(total_number_issues_authors)
                                  + time 
                                  + intervention
                                  + time_after_intervention
                                  + (1 | name)
                                  + (1 | lang), data=data)

r.squaredGLMM(rdd_issues_per_month)

anova(rdd_issues_per_month)

stargazer(rdd_issues_per_month, type="text")

#pr_per_month
rdd_pulls_per_month = lme4::lmer(log(pr_per_month + 1) ~ pr_total
                                  + log(agePulls)
                                  + log(total_number_pr_authors)
                                  + time 
                                  + intervention
                                  + time_after_intervention
                                  + (1 | name)
                                  + (1 | lang), data=data)

r.squaredGLMM(rdd_pulls_per_month)

anova(rdd_pulls_per_month)

stargazer(rdd_pulls_per_month, type="text")


# Plot
g1 <- ggplot(data, aes(data$month_index, as.numeric(data$issues_per_month+1))) + 
        geom_boxplot() +
        scale_y_log10(breaks = scales::trans_breaks("log10", function(x) 10^x), 
                      labels = scales::trans_format("log10", scales::math_format(10^.x))) +
        theme(text = element_text(size = 7)) +
        labs(y="Issues Per Month", x="Month index")

g2 <- ggplot(data, aes(data$month_index, as.numeric(data$pr_per_month+1))) + 
        geom_boxplot() +
        scale_y_log10(breaks = scales::trans_breaks("log10", function(x) 10^x), 
                      labels = scales::trans_format("log10", scales::math_format(10^.x))) +
        theme(text = element_text(size = 7)) +
        labs(y="PR per month", x="Month index")

ggarrange(g1, g2, nrow = 2, ncol = 1)

ggsave("issues_pr_per_month.png", width = 4, height = 4, dpi = 300)

# Plot
g3 <- ggplot(data, aes(data$month_index, as.numeric(data$new_users_issues+1))) + 
        geom_boxplot() +
        scale_y_log10(breaks = scales::trans_breaks("log10", function(x) 10^x), 
                      labels = scales::trans_format("log10", scales::math_format(10^.x))) +
        theme(text = element_text(size = 7)) +
        labs(y="New Users Issues", x="Month index")

g4 <- ggplot(data, aes(data$month_index, as.numeric(data$new_users_pulls+1))) + 
        geom_boxplot() +
        scale_y_log10(breaks = scales::trans_breaks("log10", function(x) 10^x), 
                      labels = scales::trans_format("log10", scales::math_format(10^.x))) +
        theme(text = element_text(size = 7)) +
        labs(y="New Users PR", x="Month index")

ggarrange(g3, g4, nrow = 2, ncol = 1)

ggsave("new_users_issues_pr_per_month_v2.png", width = 4, height = 4, dpi = 300)
