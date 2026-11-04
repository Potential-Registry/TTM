program native_checks
    use iso_c_binding
    use, intrinsic :: ieee_arithmetic
    implicit none
    interface
        subroutine evaluate(nw,n,x,g,v,model) bind(C,name='ttm_potential')
            import c_int,c_double
            integer(c_int), value :: nw,n,model
            real(c_double), intent(in) :: x(3,3*nw,n)
            real(c_double), intent(out) :: g(3,3*nw,n),v(n)
        end subroutine
    end interface
    real(c_double), allocatable :: x(:,:,:),g(:,:,:)
    real(c_double) :: v(1),o(3)
    integer :: nw,w,i,model
    integer, parameter :: models(3)=[2,21,3]
    call ieee_set_halting_mode(ieee_invalid,.true.)
    call ieee_set_halting_mode(ieee_divide_by_zero,.true.)
    call ieee_set_halting_mode(ieee_overflow,.true.)
    do nw=1,3
        allocate(x(3,3*nw,1),g(3,3*nw,1))
        do w=1,nw
            o=[2.8d0*(w-1),0.5d0*mod(w-1,2),0.2d0*(w-1)]
            x(:,w,1)=o
            x(:,nw+2*w-1,1)=o+[0.9572d0,0d0,0d0]
            x(:,nw+2*w,1)=o+[-0.2399872d0,0.927297d0,0d0]
        enddo
        do i=1,3
            model=models(i)
            call evaluate(nw,1,x,g,v,model)
            if (.not.all(ieee_is_finite(v))) error stop "nonfinite energy"
            if (.not.all(ieee_is_finite(g))) error stop "nonfinite gradient"
        enddo
        deallocate(x,g)
    enddo
    print *, 'All three TTM models and cluster sizes passed IEEE and bounds checks'
end program
