module model_mod
   implicit none
    type :: model_parameters
        double precision :: vdwA = 0d0
        double precision :: vdwB = 0d0
        double precision :: vdwC = 0d0
        double precision :: vdwD = 0d0
        double precision :: vdwE = 0d0
        double precision :: aDD = 0d0
        double precision :: aCCaCD = 0d0
        double precision :: polarO = 0d0
        double precision :: polarH = 0d0
        double precision :: polarM = 0d0
        double precision :: polfacO = 0d0
        double precision :: polfacH = 0d0
        double precision :: polfacM = 0d0
        double precision :: gammaM = 0d0
        double precision :: dms_param1 = 0d0
        double precision :: dms_param2 = 0d0
        double precision :: dms_param3 = 0d0
    end type model_parameters

integer, parameter          :: MAXITER  = 400
double precision, parameter :: diptol   = 1.d-20
double precision, parameter :: dmix     = 0.7d0
logical, parameter :: debug = .false.
!----------------------------------------------------------------------------!
! CONSTANTS                                                                  !
!----------------------------------------------------------------------------!
!double precision, parameter :: CHARGECON = 18.22261720426243437986d0
double precision, parameter :: CHARGECON = 18.22234397655801030455d0
double precision, parameter :: DEBYE  = 4.8033324d0

end module model_mod
