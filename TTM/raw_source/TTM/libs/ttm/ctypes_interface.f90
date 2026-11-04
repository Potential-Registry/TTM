subroutine ttm_potential(nwaters, ngeom, coords, grad, energy, imodel) bind(C, name='ttm_potential')
    use iso_c_binding
    use ttm2f_mod, only: ttm2f
    use ttm3f_mod, only: ttm3f
    implicit none
    integer(c_int), value, intent(in) :: nwaters, ngeom, imodel
    real(c_double), intent(in) :: coords(3,3*nwaters,ngeom)
    real(c_double), intent(out) :: grad(3,3*nwaters,ngeom), energy(ngeom)
    integer :: i
    do i=1,ngeom
        if (imodel == 3) then
            call ttm3f(nwaters,coords(:,:,i),grad(:,:,i),energy(i))
        else
            call ttm2f(nwaters,coords(:,:,i),grad(:,:,i),energy(i),imodel)
        endif
    enddo
end subroutine
