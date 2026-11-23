# The image tests/acceptance_docker.py runs acceptance batches in: the CI image
# from the Dockerfile beside this one, which the script builds first as
# ramm-ai-ci, plus Node and the agents at the versions in
# tests/agent-versions.json, which it passes as AGENT_PACKAGES. A file of its
# own, so changing it does not change the hash the CI image is tagged with.

FROM ramm-ai-ci
COPY --from=node:22-bookworm-slim@sha256:e9f565d32859f0cbfb52125eafe8be39390f24dac302dc3cdf566e8ba3ab21ee /usr/local/bin/node /usr/local/bin/
COPY --from=node:22-bookworm-slim@sha256:e9f565d32859f0cbfb52125eafe8be39390f24dac302dc3cdf566e8ba3ab21ee /usr/local/lib/node_modules /usr/local/lib/node_modules
RUN ln -s ../lib/node_modules/npm/bin/npm-cli.js /usr/local/bin/npm \
    && ln -s ../lib/node_modules/npm/bin/npx-cli.js /usr/local/bin/npx
ARG AGENT_PACKAGES
RUN test -n "$AGENT_PACKAGES" && npm install -g $AGENT_PACKAGES

# Each agent's automatic updates off, so a batch stays on the pinned versions;
# OpenCode reads its setting from the global config only. The home folder is
# writable by whichever user the script runs the container as.
ENV HOME=/home/dev DISABLE_AUTOUPDATER=1 COPILOT_AUTO_UPDATE=false RAMM_AI_DEV_IMAGE=1
RUN mkdir -p /home/dev/.config/opencode \
    && echo '{"update": "disable"}' > /home/dev/.config/opencode/opencode.json \
    && chmod -R a+rwX /home/dev
