FC=gfortran
SRC=$(addprefix ./, \
	model_mod.f90 \
	ttm2f_mod.f90 \
	ttm3f_mod.f90 \
	nasa_mod.f90 \
	math.f90 \
	smear.f90 \
	nasa.f90 \
	dfpmin.f90)

OBJ=$(addprefix ./, \
	model_mod.o \
	ttm2f_mod.o \
	ttm3f_mod.o \
	nasa_mod.o \
	math.o \
	smear.o \
	nasa.o \
	dfpmin.o)

EXE=libttm.so

FFLAGS=-O2 -fpic

all: $(OBJ)
	        $(FC) -shared -fpic $(FFLAGS) $(OBJ) $(INCLUDE_PATH) $(LIB_PATH) $(LIBSHDF) $(LIBS) -o $(EXE)
	        cp libttm.so ../libttm.so

$(OBJ) : Makefile

%.o:%.f90
	        $(FC) $(FFLAGS) $(DEFS) $(INCLUDE_PATH) -c $< -o $@
%.o:%.F90
	        $(FC) $(FFLAGS) $(DEFS) $(INCLUDE_PATH) -c $< -o $@


clean:
	rm -rf $(OBJ) *.o *.mod
