# full paths
CHAPTERS_FULL:=$(filter %/, $(wildcard manual/*/))
# names only
CHAPTERS:=$(notdir $(sort $(CHAPTERS_FULL:%/=%)))
# intersect make goals and possible chapters
QUICKY_CHAPTERS=$(filter $(MAKECMDGOALS),$(CHAPTERS))

$(CHAPTERS): all

all:
	# './' (input), './html/' (output)
	QUICKY_CHAPTERS=$(QUICKY_CHAPTERS) \
	sphinx-build -b html ./manual ./html
	@echo "google-chrome" $(shell pwd)"/html/"

pdf:
	QUICKY_CHAPTERS=$(QUICKY_CHAPTERS) \
	sphinx-build -b latex ./manual ./latex
	make -C ./latex
	@echo "evince latex/blender_manual.pdf"


clean:
	rm -rf html latex


# -----------------------------------------------------------------------------
# Help for build targets
help:
	@echo ""
	@echo "Convenience targets provided for building docs"
	@echo "- pdf        - create a PDF with latex"
	@echo "  ... otherwise defaults to HTML"
	@echo ""
	@echo "Chapters - for quickly building a single chapter"

	@$(foreach ch,$(CHAPTERS),echo "- "$(ch);)

