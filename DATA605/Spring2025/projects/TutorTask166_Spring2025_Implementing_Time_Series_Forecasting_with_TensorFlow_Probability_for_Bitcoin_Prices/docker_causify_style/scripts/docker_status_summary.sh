#!/usr/bin/env bash
echo "All services:"
docker compose config --services | sed 's/^/   • /'
echo
echo "✅ Running:"
docker compose ps --services --status running | sed 's/^/   • /'
echo
echo "⚠️  Not running:"
comm -23 \
  <(docker compose config --services   | sort) \
  <(docker compose ps --services --status running | sort) \
  | sed 's/^/   • /'