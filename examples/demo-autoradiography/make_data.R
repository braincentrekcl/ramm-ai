#!/usr/bin/env Rscript
# Simulated demo data for RAMM-AI. NOT real data.
# Run from this folder: Rscript make_data.R  (writes data.csv)
#
# Receptor autoradiography: [3H]-ligand specific binding (uCi/g tissue
# equivalent), WT / het / hom knockout, 10 mice each.
# Two slides per mouse, 3 coronal sections per slide, one mouse per slide:
#   striatal slide:    striatum and sensory cortex on every section
#   hippocampal slide: dorsal hippocampus on every section
# On every section one ROI per region is drawn in each hemisphere (L, R),
# giving 6 replicates per region per mouse (sections 1-3, L and R).
#
# Hierarchy: mouse > slide > section > ROI; region is a fixed factor, and
# striatum and sensory cortex share sections.
# Model:
#   y = region mean + effect(region) * gene dose
#       + mouse effect + slide effect + section effect + ROI noise
# The knockout lowers binding by d = 1.5 SD of mouse means in striatum and
# by half that in sensory cortex and hippocampus; het is half of hom.
# Losses are set by hand: torn sections (every ROI on the section lost),
# damaged hemispheres (that hemisphere's ROIs on the section lost) and one
# cracked slide. The seed was fixed before the data were looked at.

set.seed(20260928)

slide_regions <- list(striatal = c("striatum", "sensory_cortex"), hippocampal = "dorsal_hippocampus")
region_mean <- c(striatum = 120, sensory_cortex = 80, dorsal_hippocampus = 90)
mouse_sd <- 12
slide_sd <- 6
section_sd <- 8
roi_sd <- 10
rois_per_region <- 6
d <- 1.5
# SD of a mouse's mean over its 6 ROIs in one region (1 slide, 3 sections)
mouse_mean_sd <- sqrt(mouse_sd^2 + slide_sd^2 + section_sd^2 / 3 + roi_sd^2 / rois_per_region)
hom_effect <- -d * mouse_mean_sd * c(striatum = 1, sensory_cortex = 0.5, dorsal_hippocampus = 0.5)
gene_dose <- c(WT = 0, het = 0.5, hom = 1)

mice <- data.frame(mouse_id = sprintf("M%02d", 1:30), genotype = rep(c("WT", "het", "hom"), each = 10))
mice$mouse_effect <- rnorm(nrow(mice), 0, mouse_sd)

torn_sections <- c(
  "M04_striatal_S1", "M04_striatal_S2", "M09_striatal_S1", "M09_striatal_S3", "M16_striatal_S2",
  "M16_striatal_S3", "M24_striatal_S1", "M24_striatal_S2", "M29_striatal_S3", "M29_hippocampal_S1",
  "M07_hippocampal_S3", "M13_striatal_S2", "M21_hippocampal_S1"
)
damaged_hemispheres <- c(
  "M02_striatal_S2_L", "M09_striatal_S2_R", "M11_hippocampal_S3_L", "M16_striatal_S1_L",
  "M20_hippocampal_S2_R", "M24_striatal_S3_R", "M27_striatal_S1_L", "M29_striatal_S2_R"
)
cracked_slides <- c("M18_hippocampal")

rows <- list()
for (i in seq_len(nrow(mice))) {
  m <- mice[i, ]
  for (slide in names(slide_regions)) {
    slide_effect <- rnorm(1, 0, slide_sd)
    regions <- slide_regions[[slide]]
    for (section in 1:3) {
      section_effect <- rnorm(1, 0, section_sd)
      rois <- expand.grid(hemisphere = c("L", "R"), region = regions, stringsAsFactors = FALSE)
      binding <- region_mean[rois$region] + hom_effect[rois$region] * gene_dose[[m$genotype]] +
        m$mouse_effect + slide_effect + section_effect + rnorm(nrow(rois), 0, roi_sd)
      rows[[length(rows) + 1]] <- data.frame(
        mouse_id = m$mouse_id, genotype = m$genotype,
        slide_id = sprintf("%s_%s", m$mouse_id, slide), section = section,
        region = rois$region, hemisphere = rois$hemisphere,
        replicate = sprintf("%d%s", section, rois$hemisphere),
        specific_binding = round(unname(binding), 1)
      )
    }
  }
}
data <- do.call(rbind, rows)
section_key <- sprintf("%s_S%d", data$slide_id, data$section)
data <- data[!data$slide_id %in% cracked_slides &
  !section_key %in% torn_sections &
  !sprintf("%s_%s", section_key, data$hemisphere) %in% damaged_hemispheres, ]
write.csv(data, "data.csv", row.names = FALSE)
cat(sprintf("Wrote data.csv: %d ROI measurements, %d slides, %d mice\n",
  nrow(data), length(unique(data$slide_id)), length(unique(data$mouse_id))))
