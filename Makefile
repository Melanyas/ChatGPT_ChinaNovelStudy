.PHONY: run-workflow run-workflow-loop run-workflow-debug

RUN_ID ?= local
MAX_SECONDS ?= 600
INTERVAL_SECONDS ?= 10
RUN_ID_PREFIX ?= loop
MAX_RUNS ?= 0
CONTINUE_ON_ERROR ?= 0
DEBUG ?= 0
AUDIT ?= 1
AUTO_UPDATE ?= 0
GENERATE ?= 0
GENERATE_CHAPTERS ?= 3
COLLOQUIAL_DIALOGUE ?= 1

run-workflow:
	python workflow/scripts/run_pipeline.py --run-id $(RUN_ID) $(if $(filter 1,$(GENERATE)),--generate --generate-chapters $(GENERATE_CHAPTERS),) $(if $(filter 1,$(COLLOQUIAL_DIALOGUE)),--colloquial-dialogue,)

run-workflow-debug:
	python workflow/scripts/run_pipeline.py --run-id $(RUN_ID) --debug --audit --auto-update

run-workflow-loop:
	python workflow/scripts/run_loop.py --max-seconds $(MAX_SECONDS) --interval-seconds $(INTERVAL_SECONDS) --run-id-prefix $(RUN_ID_PREFIX) --max-runs $(MAX_RUNS) --generate-chapters $(GENERATE_CHAPTERS) $(if $(filter 1,$(COLLOQUIAL_DIALOGUE)),--colloquial-dialogue,) $(if $(filter 1,$(CONTINUE_ON_ERROR)),--continue-on-error,) $(if $(filter 1,$(DEBUG)),--debug,) $(if $(filter 1,$(AUDIT)),--audit,) $(if $(filter 1,$(AUTO_UPDATE)),--auto-update,) $(if $(filter 1,$(GENERATE)),--generate,)

run-generate-novel:
	python workflow/scripts/novel_generator.py --output workflow/artifacts/generated_novel_$(RUN_ID).md --meta-output workflow/artifacts/generated_novel_$(RUN_ID).json --chapters $(GENERATE_CHAPTERS) $(if $(filter 1,$(COLLOQUIAL_DIALOGUE)),--colloquial,)
