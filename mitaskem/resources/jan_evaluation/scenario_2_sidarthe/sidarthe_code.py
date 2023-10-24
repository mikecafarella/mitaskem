# define SIDARTHE_model
def SIDARTHE_model(y, t, alpha, beta, gamma, delta, epsilon, mu, zeta, lamda, eta, rho, theta, kappa, nu, xi, sigma, tau):
    S, I, D, A, R, T, H, E = y
    dSdt = -S*(alpha(t)*I + beta(t)*D + gamma(t)*A + delta(t)*R)
    dIdt = S*(alpha(t)*I + beta(t)*D + gamma(t)*A + delta(t)*R) - (epsilon(t) + zeta(t) + lamda(t))*I
    dDdt = epsilon(t)*I - (eta(t) + rho(t))*D
    dAdt = zeta(t)*I - (theta(t) + mu(t) + kappa(t))*A
    dRdt = eta(t)*D + theta(t)*A - (nu(t) + xi(t))*R
    dTdt = mu(t)*A + nu(t)*R - (sigma(t) + tau(t))*T
    dHdt = lamda(t)*I + rho(t)*D + kappa(t)*A + xi(t)*R + sigma(t)*T
    dEdt = tau(t)*T
    
    return dSdt, dIdt, dDdt, dAdt, dRdt, dTdt, dHdt, dEdt