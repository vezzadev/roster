#!/usr/bin/env bash
# Nextcloud post-installation hook — runs ONCE on first boot, before the
# `nextcloud-init` sidecar tries to create rooms.
#
# Installs the Talk (spreed) app. Idempotent: re-runs cleanly if the volume
# already has it (occ app:install is a no-op on already-installed apps).

set -eu
echo "▶ install-talk.sh: installing Talk (spreed) app"
php occ app:install spreed || php occ app:enable spreed
echo "✓ Talk app installed/enabled"
