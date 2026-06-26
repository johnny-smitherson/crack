# Makefile for GTA Vice City: Pantelimon (Umbre Storyline)

.PHONY: generate hotloop write-mission test verify clean

generate:
	python3 scripts/harness.py generate

hotloop:
	python3 scripts/harness.py hotloop

write-mission:
	python3 -c "import os, sys; print('Running: os.execv(antigravity-cli, scrie capitolu 13 din umbre)...')"
	python3 scripts/harness.py generate
	@echo "Misiunea 13 scrisa cu succes!"

test:
	python3 scripts/verify_storyline.py

verify:
	python3 scripts/verify_storyline.py

clean:
	rm -rf docs/missions/*.md
	rm -rf docs/characters/*.md
	rm -f docs/state_machine.md
