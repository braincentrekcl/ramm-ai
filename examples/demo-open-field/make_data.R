#!/usr/bin/env Rscript
# Simulated demo data for RAMM-AI. NOT real data.
# Run from this folder: Rscript make_data.R  (writes data.csv)
#
# Open-field crossover: 12 mice each tested twice, once after vehicle and
# once after diazepam, in counterbalanced order (6 vehicle-first,
# 6 diazepam-first) with a washout between sessions. Outcome: time in the
# centre zone (s) during a 10-minute session.
# Three sessions were lost to corrupted video (two diazepam, one vehicle),
# set by hand, so three mice have only one condition.
#
# Model:
#   y = vehicle mean + drug effect + session-2 practice effect
#       + mouse effect + session noise
# Mouse SD 15 s; session noise SD 15 s. Drug effect +25 s; practice +5 s.
# Centre time is kept within 0-600 s. The seed was fixed before the data
# were looked at.

set.seed(20260928)

vehicle_mean <- 60
mouse_sd <- 15
session_sd <- 15
drug_effect <- 25
practice_effect <- 5
session_seconds <- 600

mice <- data.frame(
  mouse_id = sprintf("OF%02d", 1:12),
  order = rep(c("vehicle_first", "diazepam_first"), times = 6)
)
mice$mouse_effect <- rnorm(nrow(mice), 0, mouse_sd)

lost <- c("OF03_diazepam", "OF08_diazepam", "OF11_vehicle")

rows <- lapply(seq_len(nrow(mice)), function(i) {
  m <- mice[i, ]
  treatment <- if (m$order == "vehicle_first") c("vehicle", "diazepam") else c("diazepam", "vehicle")
  centre <- vehicle_mean + drug_effect * (treatment == "diazepam") + practice_effect * c(0, 1) +
    m$mouse_effect + rnorm(2, 0, session_sd)
  data.frame(
    mouse_id = m$mouse_id, treatment, session = 1:2, order = m$order,
    centre_time_s = round(pmin(session_seconds, pmax(0, centre)), 1)
  )
})
data <- do.call(rbind, rows)
data <- data[!paste(data$mouse_id, data$treatment, sep = "_") %in% lost, ]
write.csv(data, "data.csv", row.names = FALSE)
cat(sprintf("Wrote data.csv: %d sessions from %d mice\n", nrow(data), length(unique(data$mouse_id))))
