#!/usr/bin/env Rscript
# Simulated demo data for RAMM-AI. NOT real data.
# Run from the demo folder: Rscript code/make_data.R  (writes inputs/data.csv)
#
# Postnatal development of two synaptic markers in somatosensory cortex:
# 4 mice at each of 7 ages (P7, P10, P14, P21, P28, P42, adult), 28 mice in
# all. Each mouse gives 3 sections, numbered 1-3 within the mouse, and both
# markers are imaged on every section. Outcome: mean fluorescence
# (arbitrary units), positive with a long tail of high values.
#
# Model, on the log scale:
#   log(y) = log(adult level of the marker) + log(fraction of adult at this age)
#            + mouse effect + section effect + measurement noise
# Adult levels: marker_a 1200, marker_b 800. Marker_a starts further below
# its adult level than marker_b and catches up later. Both markers fall from
# P14 to P21 and are back at their P14 level by P28. Mouse SD 0.15,
# section SD 0.08, noise SD 0.10. The seed was fixed before the data were
# looked at.

set.seed(20261109)

ages <- c("P7", "P10", "P14", "P21", "P28", "P42", "adult")
adult_level <- c(marker_a = 1200, marker_b = 800)
fraction_of_adult <- rbind(
  marker_a = c(0.30, 0.45, 0.70, 0.55, 0.70, 0.95, 1.00),
  marker_b = c(0.60, 0.70, 0.85, 0.70, 0.85, 0.95, 1.00)
)
colnames(fraction_of_adult) <- ages
mice_per_age <- 4
sections_per_mouse <- 3
mouse_sd <- 0.15
section_sd <- 0.08
noise_sd <- 0.10

mice <- data.frame(
  mouse_id = sprintf("PM%02d", seq_len(length(ages) * mice_per_age)),
  age_group = rep(ages, each = mice_per_age)
)
mice$mouse_effect <- rnorm(nrow(mice), 0, mouse_sd)

rows <- lapply(seq_len(nrow(mice)), function(i) {
  m <- mice[i, ]
  section_effect <- rnorm(sections_per_mouse, 0, section_sd)
  do.call(rbind, lapply(names(adult_level), function(marker) {
    log_y <- log(adult_level[[marker]]) + log(fraction_of_adult[marker, m$age_group]) +
      m$mouse_effect + section_effect + rnorm(sections_per_mouse, 0, noise_sd)
    data.frame(
      mouse_id = m$mouse_id, age_group = m$age_group, section = seq_len(sections_per_mouse),
      marker = marker, fluorescence = round(exp(log_y), 1)
    )
  }))
})
data <- do.call(rbind, rows)
write.csv(data, file.path("inputs", "data.csv"), row.names = FALSE)
cat(sprintf("Wrote inputs/data.csv: %d measurements from %d mice\n", nrow(data), nrow(mice)))
