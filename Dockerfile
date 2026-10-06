# syntax=docker/dockerfile:1
# Cellframe Node — DEPLOY image. Contains NO sources: binaries are expected
# prebuilt (by Dockerfile.build) in docker-artifacts/, plus the runtime data
# shipped with the package (dist/, dist/etc).
#
# Flow:
#   1) docker build -t cellframe-node-builder -f Dockerfile.build .
#      docker run --rm -v "$PWD:/src" -v "$PWD/docker-artifacts:/out" cellframe-node-builder
#   2) docker build -t cellframe-node:local .
#   3) docker run -d --name cellframe-node -p 127.0.0.1:12345:12345 cellframe-node:local
#
# Environment knobs (docker/entrypoint.sh): CELLFRAME_NETWORKS (Backbone),
# CELLFRAME_NODE_ROLE (full), CELLFRAME_DEBUG_MODE (false).

FROM debian:12-slim

RUN apt-get update -qq && DEBIAN_FRONTEND=noninteractive apt-get install -y -qq --no-install-recommends \
        libmagic1 libmagic-mgc libjson-c5 libffi8 libsqlite3-0 libssl3 libcurl4 \
        libstdc++6 ca-certificates curl tini \
    && rm -rf /var/lib/apt/lists/* \
    && useradd --system --home /opt/cellframe-node --shell /usr/sbin/nologin cellframe

ENV BASE=/opt/cellframe-node
WORKDIR /opt/cellframe-node

# Prebuilt artifacts (no sources anywhere - see Dockerfile.build for the builder)
COPY docker-artifacts/bin/ bin/
COPY docker-artifacts/python-lib/ python/lib/

# Runtime data shipped with the package: share/ (ca, config templates, docs),
# etc/ (network chain templates, cfg.d). Pristine copies live under
# share.tpl/ so the entrypoint can populate an empty mounted volume.
COPY dist/     share.tpl/dist/
COPY dist/etc/ share.tpl/etc/
COPY docker/entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod +x /usr/local/bin/entrypoint.sh \
    && mkdir -p var/lib/global_db var/lib/wallet var/log var/run tmp etc/network etc/cellframe-node.cfg.d \
    && chown -R cellframe:cellframe /opt/cellframe-node

USER cellframe
EXPOSE 8079 8089 12345

# State: chain data, wallets, logs. etc/ may be mounted read-write so the
# entrypoint can write the generated cellframe-node.cfg there.
VOLUME ["/opt/cellframe-node/var", "/opt/cellframe-node/etc"]

HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=5 \
    CMD curl -fsS -m 4 http://127.0.0.1:12345/health || exit 1

ENTRYPOINT ["/usr/bin/tini", "--", "/usr/local/bin/entrypoint.sh"]
CMD ["./bin/cellframe-node"]
