def RHS_func(self, t, y_flat, Nij, contact_mats, Aij, par, npi, aij_sparse, y):
    # constraint on values
    lower, upper = (0.0, 1.0)  # bounds for state vars  ## TODO multiple_value_asignment

    # grab index of OOB values so we can zero derivatives (stability...)
    too_low = y_flat <= lower
    too_high = y_flat >= upper

    # TODO we're passing in y.state just to overwrite it, we probably need another class
    # reshape to the usual state tensor (compartment, age, node)
    y.state = y_flat.reshape(y.state_shape)

    # Clip state to be in bounds (except allocs b/c thats a counter)
    xp.clip(y.state, a_min=lower, a_max=upper, out=y.state)

    # init d(state)/dt
    dy = buckyState(y.consts, Nij)  # TODO make a pseudo copy operator w/ zeros

    # effective params after damping w/ allocated stuff
    t_index = min(int(t), npi["r0_reduct"].shape[0] - 1)  # prevent OOB error when integrator overshoots
    BETA_eff = npi["r0_reduct"][t_index] * par["BETA"]
    F_eff = par["F_eff"]
    HOSP = par["H"]
    THETA = y.Rhn * par["THETA"]
    GAMMA = y.Im * par["GAMMA"]
    GAMMA_H = y.Im * par["GAMMA_H"]
    SIGMA = y.En * par["SIGMA"]
    SYM_FRAC = par["SYM_FRAC"]
    # ASYM_FRAC = par["ASYM_FRAC"]
    CASE_REPORT = par["CASE_REPORT"]

    Cij = npi["contact_weights"][t_index] * contact_mats
    Cij = xp.sum(Cij, axis=1)
    Cij /= xp.sum(Cij, axis=2, keepdims=True)

    if aij_sparse:
        Aij_eff = Aij.multiply(npi["mobility_reduct"][t_index])
    else:
        Aij_eff = npi["mobility_reduct"][t_index] * Aij

    # perturb Aij
    # new_R0_fracij = truncnorm(xp, 1.0, .1, size=Aij.shape, a_min=1e-6)
    # new_R0_fracij = xp.clip(new_R0_fracij, 1e-6, None)
    # A = Aij * new_R0_fracij
    # Aij_eff = A / xp.sum(A, axis=0)

    # Infectivity matrix (I made this name up, idk what its really called)
    I_tot = xp.sum(Nij * y.Itot, axis=0) - (1.0 - par["rel_inf_asym"]) * xp.sum(Nij * y.Ia, axis=0)

    # I_tmp = (Aij.T @ I_tot.T).T
    if aij_sparse:
        I_tmp = (Aij_eff.T * I_tot.T).T
    else:
        I_tmp = I_tot @ Aij  # using identity (A@B).T = B.T @ A.T

    beta_mat = y.S * xp.squeeze((Cij @ I_tmp.T[..., None]), axis=-1).T  ## TODO ellipsis NOT_DONE
    ## beta_mat /= Nij  ## TODO
    beta_mat = beta_mat / Nij

    # dS/dt
    dy.S = -BETA_eff * (beta_mat)
    # dE/dt
    dy.E[0] = BETA_eff * (beta_mat) - SIGMA * y.E[0]
    dy.E[1:] = SIGMA * (y.E[:-1] - y.E[1:])

    # dI/dt
    dy.Ia[0] = (1.0 - SYM_FRAC) * SIGMA * y.E[-1] - GAMMA * y.Ia[0]
    dy.Ia[1:] = GAMMA * (y.Ia[:-1] - y.Ia[1:])

    # dIa/dt
    dy.I[0] = SYM_FRAC * (1.0 - HOSP) * SIGMA * y.E[-1] - GAMMA * y.I[0]
    dy.I[1:] = GAMMA * (y.I[:-1] - y.I[1:])

    # dIc/dt
    dy.Ic[0] = SYM_FRAC * HOSP * SIGMA * y.E[-1] - GAMMA_H * y.Ic[0]
    dy.Ic[1:] = GAMMA_H * (y.Ic[:-1] - y.Ic[1:])

    # dRhi/dt
    dy.Rh[0] = GAMMA_H * y.Ic[-1] - THETA * y.Rh[0]
    dy.Rh[1:] = THETA * (y.Rh[:-1] - y.Rh[1:])

    # dR/dt
    dy.R = GAMMA * (y.I[-1] + y.Ia[-1]) + (1.0 - F_eff) * THETA * y.Rh[-1]

    # dD/dt
    dy.D = F_eff * THETA * y.Rh[-1]

    dy.incH = SYM_FRAC * CASE_REPORT * HOSP * SIGMA * y.E[-1]
    dy.incC = SYM_FRAC * CASE_REPORT * SIGMA * y.E[-1]

    # bring back to 1d for the ODE api
    dy_flat = dy.state.ravel()

    # zero derivatives for things we had to clip if they are going further out of bounds
    dy_flat = xp.where(too_low & (dy_flat < 0.0), 0.0, dy_flat)
    dy_flat = xp.where(too_high & (dy_flat > 0.0), 0.0, dy_flat)

    return dy_flat