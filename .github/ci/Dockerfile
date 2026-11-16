# Image the repository checks run in on CI, so every R chunk test runs there.
# R, the package snapshot and the system libraries are the ones the reproduce
# skill's container template uses, as recorded in docs/tested-versions.md.
# .github/workflows/ci-image.yml publishes it to ghcr.io, tagged with a hash of
# this file, so any change here builds a new image.

FROM ghcr.io/astral-sh/uv:0.13.4@sha256:9f130421e930bfbdc563c00740466603f8723158e90297d07957c2294640262b AS uv

FROM rocker/r-ver:4.4.2@sha256:df26749182af64d5263bf64149d51a427b476ed28c4e046997143be3f97fdd7c

LABEL org.opencontainers.image.source=https://github.com/braincentrekcl/ramm-ai

# System libraries for R packages with C/C++ dependencies, as in the reproduce
# skill's template, plus git for actions/checkout. ca-certificates is upgraded
# from the base image's 2024 bundle, which still trusts the eMudhra root
# Ubuntu distrusted in October 2026 (LP: #2171507).
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    libcurl4-openssl-dev \
    libssl-dev \
    libxml2-dev \
    libfontconfig1-dev \
    libharfbuzz-dev \
    libfribidi-dev \
    libfreetype6-dev \
    libpng-dev \
    libtiff5-dev \
    libjpeg-dev \
    libgit2-dev \
    cmake \
    git \
    && rm -rf /var/lib/apt/lists/*

# Pin CRAN to the dated Posit Package Manager snapshot the reproduce skill uses.
RUN echo 'options(repos = c(CRAN = "https://packagemanager.posit.co/cran/__linux__/noble/2025-01-15"))' \
    >> /usr/local/lib/R/etc/Rprofile.site

# The packages the R chunk tests load (car for the lm() Type III test), and
# readxl for the data-prep skill's spreadsheet tests. install.packages() only
# warns when a package fails, so check they all load and stop the build if not.
RUN R -e "pkgs <- c('lme4', 'lmerTest', 'emmeans', 'ggplot2', 'dplyr', \
    'broom.mixed', 'readr', 'readxl', 'car'); \
    install.packages(pkgs); \
    missing <- pkgs[!vapply(pkgs, requireNamespace, logical(1), quietly = TRUE)]; \
    if (length(missing) > 0) stop('Packages failed to install: ', paste(missing, collapse = ', '))"

# uv, and a Python for it in a fixed folder, so uv finds it whatever HOME the
# container runs with (by default it would go under /root).
COPY --from=uv /uv /uvx /usr/local/bin/
ENV UV_PYTHON_INSTALL_DIR=/opt/uv/python
RUN uv python install 3.13
