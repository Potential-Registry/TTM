FC = gfortran
PYTHON = python3
FFLAGS ?= -O2
LDFLAGS ?= -shared
# Required for thread-local local arrays; do not use -fno-automatic.
REENTRANT_FLAGS = -fPIC -frecursive -ffree-line-length-none -ffixed-line-length-none
BUILD = build
EXE = ../libttm.so
OBJECTS = $(BUILD)/model_mod.o $(BUILD)/nasa_mod.o $(BUILD)/math.o $(BUILD)/smear.o $(BUILD)/nasa.o $(BUILD)/dfpmin.o $(BUILD)/ttm2f_mod.o $(BUILD)/ttm3f_mod.o $(BUILD)/ctypes_interface.o
.PHONY: all main clean
all: $(EXE)
main: all
$(BUILD):
	mkdir -p $@
$(BUILD)/%.o: %.f90 | $(BUILD)
	$(FC) $(FFLAGS) $(REENTRANT_FLAGS) -J$(BUILD) -I$(BUILD) -c $< -o $@
$(BUILD)/%.o: %.f | $(BUILD)
	$(FC) $(FFLAGS) $(REENTRANT_FLAGS) -J$(BUILD) -I$(BUILD) -c $< -o $@
$(EXE): $(OBJECTS)
	$(FC) $(LDFLAGS) -o $@ $(OBJECTS)
clean:
	rm -rf $(BUILD) $(EXE)
$(BUILD)/nasa.o: $(BUILD)/model_mod.o $(BUILD)/nasa_mod.o
$(BUILD)/ttm2f_mod.o: $(BUILD)/model_mod.o
$(BUILD)/ttm3f_mod.o: $(BUILD)/model_mod.o
$(BUILD)/ctypes_interface.o: $(BUILD)/ttm2f_mod.o $(BUILD)/ttm3f_mod.o
