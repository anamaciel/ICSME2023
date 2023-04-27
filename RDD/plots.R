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
data <- read.csv("testeData9-SemZeros.csv",sep=";")
data['time'] <- lapply(data['time'] , factor)

data["month_index"] <- NA
data$month_index <- rep((-12:12)[-12:12 != 0], 91)
data$month_index <- factor(data$month_index, levels=c((-12:12)[-12:12 != 0]),ordered=TRUE)

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


# Plot
g5 <- ggplot(data, aes(data$month_index, as.numeric(data$merged+1))) + 
  geom_boxplot() +
  scale_y_log10(breaks = scales::trans_breaks("log10", function(x) 10^x), 
                labels = scales::trans_format("log10", scales::math_format(10^.x))) +
  theme(text = element_text(size = 7)) +
  labs(y="Num. merged PRs", x="Month index")

g6 <- ggplot(data, aes(data$month_index, as.numeric(data$nonmerged+1))) + 
  geom_boxplot() +
  scale_y_log10(breaks = scales::trans_breaks("log10", function(x) 10^x), 
                labels = scales::trans_format("log10", scales::math_format(10^.x))) +
  theme(text = element_text(size = 7)) +
  labs(y="Num. non-merged PRs", x="Month index")

ggarrange(g5, g6, nrow = 2, ncol = 1)

ggsave("merged_nonmerged.png", width = 4, height = 4, dpi = 300)

# Plot
g7 <- ggplot(data, aes(data$month_index, as.numeric(data$users_issues+1))) + 
  geom_boxplot() +
  scale_y_log10(breaks = scales::trans_breaks("log10", function(x) 10^x), 
                labels = scales::trans_format("log10", scales::math_format(10^.x))) +
  theme(text = element_text(size = 7)) +
  labs(y="Issues Users", x="Month index")

g8 <- ggplot(data, aes(data$month_index, as.numeric(data$users_pulls+1))) + 
  geom_boxplot() +
  scale_y_log10(breaks = scales::trans_breaks("log10", function(x) 10^x), 
                labels = scales::trans_format("log10", scales::math_format(10^.x))) +
  theme(text = element_text(size = 7)) +
  labs(y="Users PRs", x="Month index")

ggarrange(g7, g8, nrow = 2, ncol = 1)

ggsave("usersIssuesPR.png", width = 4, height = 4, dpi = 300)

