# define SEIRD_model
def SEIRD_model(y, t, N0, alpha, beta, gamma, epsilon, mu):
    S, E, I, R, D, N = y
    dSdt = mu*N -beta * S * I / N0 - mu*S
    dEdt = beta * S * I / N0 - (mu + epsilon) * E
    dIdt = epsilon * E - (gamma + mu + alpha) * I
    dRdt = gamma * I - mu *R
    dDdt = -(dSdt + dEdt + dIdt + dRdt)
    dNdt = -dDdt
    return dSdt, dEdt, dIdt, dRdt, dDdt, dNdt