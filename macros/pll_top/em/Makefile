# SPDX-FileCopyrightText: 2026 Vasil Yordanov
# SPDX-License-Identifier: Apache-2.0 WITH SHL-2.1
#
# openEMS inductor flow for pll_top (IHP SG13CMOS5L).
# Run from inside the IIC-OSIC-TOOLS container -- openEMS, gdspy and AppCSXCAD live there.

MAKEFILE_DIR := $(shell dirname $(realpath $(firstword $(MAKEFILE_LIST))))

STACKUP_DIR := stackup
SCRIPTS_DIR := scripts
MODELS_DIR  := models
GDS_DIR     := gds
PLOT_DIR    := plot
RESULTS_DIR := results

STACKUP := $(STACKUP_DIR)/SG13CMOS5L.xml

# Geometry parameters. Override on the command line:
#   make spiral N=4 ROUT=150 W=20 S=10
N    ?= 3
ROUT ?= 218
W    ?= 30
S    ?= 14
NAME ?= spiral_n$(N)_r$(ROUT)_w$(W)_s$(S)
GDS  ?= $(GDS_DIR)/$(NAME).gds

# Simulation parameters
CELLSIZE ?= 6
FSTOP    ?= 15e9
FTANK    ?= 2.45e9
SIMARGS  ?=

.DEFAULT_GOAL := help

help: ## Show this help
	@echo 'openEMS inductor flow (SG13CMOS5L). Run inside the IIC-OSIC-TOOLS container.'
	@echo ''
	@echo 'Targets:'
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  %-18s %s\n", $$1, $$2}'
	@echo ''
	@echo 'Geometry vars : N=$(N) ROUT=$(ROUT) W=$(W) S=$(S)  -> $(GDS)'
	@echo 'Sim vars      : CELLSIZE=$(CELLSIZE) FSTOP=$(FSTOP) FTANK=$(FTANK)'
	@echo ''
	@echo 'Typical first session:'
	@echo '  make check          # confirm the toolchain is reachable'
	@echo '  make stackup-validate'
	@echo '  make spiral         # write the default geometry'
	@echo '  make preview        # look at the mesh in AppCSXCAD before burning CPU'
	@echo '  make sim            # simulate, then: make plot'
.PHONY: help

check: ## Verify openEMS, gdspy and the PDK are reachable
	@echo "openEMS   : $$(command -v openEMS || echo 'NOT FOUND')"
	@echo "AppCSXCAD : $$(command -v AppCSXCAD || echo 'NOT FOUND')"
	@python3 -c "import gdspy; print('gdspy     :', gdspy.__version__)" 2>/dev/null || echo "gdspy     : NOT FOUND"
	@python3 -c "import openEMS, CSXCAD; print('py bindings: ok')" 2>/dev/null || echo "py bindings: NOT FOUND"
	@python3 $(SCRIPTS_DIR)/em_env.py
.PHONY: check

$(STACKUP): $(SCRIPTS_DIR)/gen_stackup.py
	python3 $(SCRIPTS_DIR)/gen_stackup.py

stackup: $(STACKUP) ## Generate the CMOS5L stackup XML from the PDK
.PHONY: stackup

stackup-validate: ## Prove the stackup derivation against IHP's official SG13G2 data
	python3 $(SCRIPTS_DIR)/gen_stackup.py --validate
.PHONY: stackup-validate

stackup-show: ## Print the derived stack without writing anything
	python3 $(SCRIPTS_DIR)/gen_stackup.py --print
.PHONY: stackup-show

spiral: ## Generate spiral geometry (vars: N ROUT W S)
	python3 $(SCRIPTS_DIR)/gen_spiral.py -n $(N) -r $(ROUT) -w $(W) -s $(S) --name $(NAME)
.PHONY: spiral

spiral-show: ## Print spiral geometry summary without writing a GDS
	python3 $(SCRIPTS_DIR)/gen_spiral.py -n $(N) -r $(ROUT) -w $(W) -s $(S) --name $(NAME) --print
.PHONY: spiral-show

preview: $(STACKUP) ## Open the model and mesh in AppCSXCAD (no simulation)
	python3 $(MODELS_DIR)/run_inductor_diffport.py --gds $(GDS) --stackup $(STACKUP) \
		--cellsize $(CELLSIZE) --fstop $(FSTOP) --target-freq $(FTANK) --preview $(SIMARGS)
.PHONY: preview

sim: $(STACKUP) ## Run the differential inductor simulation
	python3 $(MODELS_DIR)/run_inductor_diffport.py --gds $(GDS) --stackup $(STACKUP) \
		--cellsize $(CELLSIZE) --fstop $(FSTOP) --target-freq $(FTANK) $(SIMARGS)
.PHONY: sim

post: $(STACKUP) ## Re-evaluate existing results without re-simulating
	python3 $(MODELS_DIR)/run_inductor_diffport.py --gds $(GDS) --stackup $(STACKUP) \
		--cellsize $(CELLSIZE) --fstop $(FSTOP) --target-freq $(FTANK) --postprocess $(SIMARGS)
.PHONY: post

plot: ## Plot L and Q from the last run of $(NAME)
	gnuplot -e "datafile='$(RESULTS_DIR)/$(NAME)/$(NAME).csv'" \
	        -e "ftank=$(shell python3 -c 'print($(FTANK)/1e9)')" $(PLOT_DIR)/inductor.gp
.PHONY: plot

clean: ## Remove simulation results (geometry and stackup are kept)
	rm -rf $(RESULTS_DIR)/*
.PHONY: clean

clean-all: clean ## Also remove generated GDS and the stackup XML
	rm -f $(GDS_DIR)/*.gds $(STACKUP)
.PHONY: clean-all
