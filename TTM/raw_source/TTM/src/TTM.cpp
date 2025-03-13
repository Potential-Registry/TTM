
#include "Python.h"
#include "plzffi/FFIModule.hpp"
#include <numeric>

using namespace plzffi;

// Put all module functions in here
namespace TTM {

    static FFIModule Data("TTM", "provides linkage for the TTM family of potentials");
    static PyModuleDef Module;

    // Declare our linkage -> could be in TTM.hpp, but why bother
    extern "C" {
        void __ttm3f_mod_MOD_ttm3f(int *, double *, double *, double *);
        void __ttm2f_mod_MOD_ttm2f(int *, double *, double *, double *, int *);
        }

    // all functions should take a single argument "FFIParameters"
    // data can be extracted by using the `.value` method with the name of the parameter
    double ttm(FFIParameters &params) {
        // Load extra args (if necessary)

//        printf("    > extracting parameters for call into TTM\n");
        auto nwaters = params.value<int>("nwaters");
        auto imodel = params.value<int>("imodel");
        auto coords = params.value<double*>("coords");

//        printf("    > setting up storage to feed to Fortran\n");
        double derivs[nwaters * 9];
        double energy = -1000.;

        // calling ttm from Fortran module ttm_mod
        if (imodel == 3) {
            __ttm3f_mod_MOD_ttm3f(&nwaters, coords, derivs, &energy);
        } else {
            __ttm2f_mod_MOD_ttm2f(&nwaters, coords, derivs, &energy, &imodel);
        };

//        printf("    > sucessfully got energy!\n");
        return energy / 627.5094740631;
    }

    std::vector<double> ttm_vec(FFIParameters &params) {
        // Load extra args (if necessary)


//        printf("    > extracting parameters for call into TTM\n");
        auto nwaters = params.value<int>("nwaters");
        auto imodel = params.value<int>("imodel");
        auto coords = params.value<double*>("coords");
        auto coords_shape = params.shape("coords");

//        printf("    > setting up storage for call into TTM (%lu calls)\n", coords_shape[0]);
        std::vector<double> energies(coords_shape[0]);
        auto block_size = std::accumulate(coords_shape.begin()+1, coords_shape.end(), 1, std::multiplies<>());

        for (size_t w = 0; w < coords_shape[0]; w++) {

//            printf("    > calling structure %lu\n", w);

            double derivs[nwaters * 9];
            double energy = -1000.;

            // calling ttm from Fortran module ttm_mod
            if (imodel == 3) {
                __ttm3f_mod_MOD_ttm3f(&nwaters, coords + w*block_size, derivs, &energy);
            } else {
                __ttm2f_mod_MOD_ttm2f(&nwaters, coords + w*block_size, derivs, &energy, &imodel);
            };

            energies[w] = energy / 627.5094740631;

        }

//        printf("    > sucessfully got energy %f %f %f!\n", energies[0], energies[1], energies[2]);

        return energies;
    }

    // need a load function that can be called in PYMODINIT
    void load() {
        // load modules and return python def

        // add data for first obj
        Data.add<double>(
                "get_pot",
                {
                        {"nwaters", FFIType::Int, {}},
                        {"coords", FFIType::Double, {0, 0, 3}},
                        {"imodel", FFIType::Int, {}}
                },
                ttm
                );
        // add data for vectorized version
        Data.add<double>(
                "get_pot_vec",
                {
                        {"nwaters", FFIType::Int, {}},
                        {"coords", FFIType::Double, {0, 0, 3}},
                        {"imodel", FFIType::Int, {}}
                },
                ttm_vec
        );

        Module = Data.get_def(); // uses new
    }

}

PyMODINIT_FUNC PyInit_TTM(void)
{

    TTM::load();
    PyObject *m;
    m = PyModule_Create(&TTM::Module);
    if (m == NULL) { return NULL; }
    TTM::Data.attach(m);

    return m;
}