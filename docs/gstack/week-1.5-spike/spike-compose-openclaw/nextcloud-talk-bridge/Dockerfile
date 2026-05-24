# nextcloud-talk-bridge — per-identity Talk poller that pokes each agent's
# OpenClaw gateway via `docker exec`.
#
# Image needs:
#   - python + httpx (poll OCS)
#   - docker CLI (to exec into gateway containers — socket mounted at runtime)
#
# Built on python-slim for the smallest viable surface.

FROM python:3.13-slim

# docker CLI only — no daemon, no compose. We rely on the host docker socket
# being bind-mounted at /var/run/docker.sock.
RUN apt-get update \
 && apt-get install -y --no-install-recommends ca-certificates curl gnupg \
 && install -m 0755 -d /etc/apt/keyrings \
 && curl -fsSL https://download.docker.com/linux/debian/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg \
 && chmod a+r /etc/apt/keyrings/docker.gpg \
 && echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/debian $(. /etc/os-release && echo "$VERSION_CODENAME") stable" > /etc/apt/sources.list.d/docker.list \
 && apt-get update \
 && apt-get install -y --no-install-recommends docker-ce-cli \
 && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir httpx==0.27.2

WORKDIR /app
COPY bridge.py /app/bridge.py

ENV BRIDGE_STATE_FILE=/state/bridge-state.json
ENV BRIDGE_CONFIG=/etc/bridge/identities.json

ENTRYPOINT ["python", "-u", "/app/bridge.py"]
