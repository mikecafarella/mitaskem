import sys
from csv import DictWriter, QUOTE_NONNUMERIC

def get_beta(intrinsic_growth_rate, gamma, susceptible, relative_contact_rate):
    """
    Calculates a rate of exposure given an intrinsic growth rate for COVID-19
    :param intrinsic_growth_rate: Rate of spread of COVID-19 cases
    :param gamma: The expected recovery rate from COVID-19 for infected individuals
    :param susceptible: Current amount of individuals that are susceptible
    :param relative_contact_rate: The relative contact rate amongst individuals in the population
    :return: beta: The rate of exposure of individuals to persons infected with COVID-19
    """
    inv_contact_rate = 1.0 - relative_contact_rate  # The inverse rate of contact between individuals in the population ## get_beta_icr_exp
    updated_growth_rate = intrinsic_growth_rate + gamma  # The intrinsic growth rate adjusted for the recovery rate from infection ## get_beta_ugr_exp
    beta = updated_growth_rate / susceptible * inv_contact_rate  ## get_beta_beta_exp

    return beta


def get_growth_rate(doubling_time):
    """
    Calculate the expected growth rate of COVID-19 infections given a doubling time
    :param doubling_time: The time required for the amount of COVID-19 cases to double
    :return: growth_rate: Rate of spread of COVID-19 cases.
    """
    ## ggr_cond
    if doubling_time == 0:  ## ggr_cond_b0_cond
        growth_rate = 0  ## ggr_cond_b0_exp
    else:
        growth_rate = 2.0 ** (1.0 / doubling_time) - 1.0  ## ggr_cond_b1_exp

    return growth_rate


def sir(s, v, i, i_v, r, vaccination_rate, beta, gamma_unvaccinated, gamma_vaccinated, vaccine_efficacy, n):
    """
    The SIR model, one time step
    :param s: Current amount of individuals that are susceptible
    :param v: Current amount of individuals that are vaccinated
    :param i: Current amount of individuals that are infectious
    :param i_v: Current amount of vaccinated individuals that are infectious
    :param r: Current amount of individuals that are recovered
    :param beta: The rate of exposure of individuals to persons infected with COVID-19
    :param gamma_unvaccinated: Rate of recovery for infected unvaccinated individuals
    :param gamma_vaccinated: Rate of recovery for infected vaccinated individuals
    :param vaccination_rate: The rate of vaccination of susceptible individuals
    :param vaccine_efficacy: The efficacy of the vaccine
    :param n: Total population size
    :return:
    """
    s_n = (
                      -beta * s * i - beta * s * i_v - vaccination_rate * s) + s  # Update to the amount of individuals that are susceptible ## sir_s_n_exp
    v_n = (vaccination_rate * s - beta * (1 - vaccine_efficacy) * v * i - beta * (
                1 - vaccine_efficacy) * v * i_v) + v  # Update to the amount of individuals that are susceptible ## sir_v_n_exp
    i_n = (
                      beta * s * i + beta * s * i_v - gamma_unvaccinated * i) + i  # Update to the amount of individuals that are infectious ## sir_i_n_exp
    i_v_n = (beta * (1 - vaccine_efficacy) * v * i + beta * (
                1 - vaccine_efficacy) * v * i_v - gamma_vaccinated * i_v) + i_v  # Update to the amount of individuals that are infectious ## sir_i_v_n_exp
    r_n = gamma_vaccinated * i_v + gamma_unvaccinated * i + r  # Update to the amount of individuals that are recovered ## sir_r_n_exp

    scale = n / (
                s_n + v_n + i_n + i_v_n + r_n)  # A scaling factor to compute updated disease arizona-extraction ## sir_scale_exp

    s = s_n * scale  ## sir_s_exp
    v = v_n * scale  ## sir_v_exp
    i = i_n * scale  ## sir_i_exp
    i_v = i_v_n * scale  ## sir_i_v_exp
    r = r_n * scale  ## sir_r_exp
    return s, v, i, i_v, r


def sim_sir(s, v, i, i_v, r, vaccination_rate, gamma_unvaccinated, gamma_vaccinated, vaccine_efficacy, i_day,
            ### original inputs
            N_p, betas, days,  ### changes to original CHIME sim_sir to simplify policy bookkeeping
            d_a, s_a, v_a, i_a, i_v_a, r_a, e_a,
            ### changes to original CHIME sim_sir simulation bookkeeping - here, bookkeeping represented as lists that are passed in as arguments
            ):
    n = s + v + i + i_v + r  ## simsir_n_exp
    d = i_day  ## simsir_d_exp

    ### total_days from original CHIME sim_sir was used to determine the size of the
    ### the state bookkeeping across the simulation.
    ### Here, the array size is for this bookkeeping is determined outside of sim_sir
    ### and the arrays are passed in as arguments.

    index = 0  ## simsir_idx_exp
    for p_idx in range(N_p):  ## simsir_loop_1
        beta = betas[p_idx]  ## simsir_loop_1_beta_exp
        n_days = days[p_idx]  ## simsir_loop_1_N_d_exp
        for d_idx in range(n_days):  ## simsir_loop_1_1
            d_a[index] = d  ## simsir_loop_1_1_T_exp
            s_a[index] = s  ## simsir_loop_1_1_S_exp
            v_a[index] = v  ## simsir_loop_1_1_V_exp
            i_a[index] = i  ## simsir_loop_1_1_I_exp
            i_v_a[index] = i_v  ## simsir_loop_1_1_I_V_exp
            r_a[index] = r  ## simsir_loop_1_1_R_exp
            e_a[
                index] = i + i_v + r  # updated "ever" infected (= i + i_v + r)  ### In CHIME sir.py, this is performed at end as sum of two numpy arrays; here perform iteratively

            index += 1  ## simsir_loop_1_1_idx_exp

            s, v, i, i_v, r = sir(s, v, i, i_v, r, vaccination_rate, beta, gamma_unvaccinated, gamma_vaccinated,
                                  vaccine_efficacy, n)  ## simsir_loop_1_1_call_sir_exp

            d += 1  ## simsir_loop_1_1_d_exp

    # Record the last update (since sir() is called at the tail of the inner loop above)
    d_a[index] = d  ## simsir_T_exp
    s_a[index] = s  ## simsir_S_exp
    v_a[index] = v  ## simsir_V_exp
    i_a[index] = i  ## simsir_I_exp
    i_v_a[index] = i_v  ## simsir_I_exp
    r_a[index] = r  ## simsir_R_exp

    return s, v, i, i_v, r, d_a, s_a, v_a, i_a, i_v_a, r_a, e_a  ### return


def main():
    """
    implements generic CHIME configuration without hospitalization calculation
    initializes parameters and population, calculates policy, and runs dynamics
    :return:
    """
    ###

    # initial parameters
    i_day = 17.0  ## main_i_day_exp
    n_days = [14, 90]  ## main_n_days_exp
    N_p = 2  ## main_N_p_exp
    N_t = sum(n_days) + 1  ## main_N_t_exp
    infectious_days_unvaccinated = 14  ## main_inf_days_u_exp
    infectious_days_vaccinated = 10  ## main_inf_days_v_exp
    relative_contact_rate = [0.0, 0.45]  ## main_rcr_exp
    gamma_unvaccinated = 1.0 / infectious_days_unvaccinated  ## main_gamma_u_exp
    gamma_vaccinated = 1.0 / infectious_days_vaccinated  ## main_gamma_v_exp

    # Vaccination parameters
    vaccination_rate = 0.02  ## main_vaccination_rate_exp
    vaccine_efficacy = 0.85  ## main_vaccine_efficacy_exp

    # initialize lists for policy and simulation state bookkeeping
    policys_betas = [0.0] * N_p  ## TODO size      # main_pbetas_seq
    policy_days = [0] * N_p  ## main_pdays_seq
    d_a = [0.0] * N_t  ## main_T_seq
    s_a = [0.0] * N_t  ## main_S_seq
    v_a = [0.0] * N_t  ## main_V_seq
    i_a = [0.0] * N_t  ## main_I_seq
    i_v_a = [0.0] * N_t  ## main_I_V_seq
    r_a = [0.0] * N_t  ## main_R_seq
    e_a = [0.0] * N_t  # "ever" infected (= I + R) ## main_E_seq

    # initial population
    s_n = 1000  ## main_s_n_exp
    v_n = 0  ## main_v_n_exp
    i_n = 1  ## main_i_n_exp
    i_v_n = 0  ## main_i_v_n_exp
    r_n = 0  ## main_r_n_exp

    # calculate beta under policy
    for p_idx in range(N_p):  ## main_loop_1
        doubling_time = 2

        growth_rate = get_growth_rate(doubling_time)  ## main_loop_1_gr_exp
        beta = get_beta(growth_rate, gamma_unvaccinated, s_n,  ## main_loop_1_beta_exp
                        relative_contact_rate[p_idx])
        policys_betas[p_idx] = beta  ## main_loop_1_pbetas_exp
        policy_days[p_idx] = n_days[p_idx]  ## main_loop_1_pdays_exp

    # simulate dynamics (corresponding roughly to run_projection() )
    s_n, v_n, i_n, i_v_n, r_n, d_a, s_a, v_a, i_a, i_v_a, r_a, e_a \
        = sim_sir(s_n, v_n, i_n, i_v_n, r_n, vaccination_rate, gamma_unvaccinated, gamma_vaccinated, vaccine_efficacy,
                  i_day,  ## main_call_simsir_exp
                  N_p, policys_betas, policy_days,
                  d_a, s_a, v_a, i_a, i_v_a, r_a, e_a)

    return d_a, s_a, v_a, i_a, i_v_a, r_a, e_a  # return simulated dynamics


if __name__ == '__main__':
    outfile = sys.argv[1]

    d_a, s_a, v_a, i_a, i_v_a, r_a, e_a = main()

    out_data = list()
    keys = ['d', 's', 'v', 'i', 'i_v', 'r', 'e']
    data_tuples = zip(d_a, s_a, v_a, i_a, i_v_a, r_a, e_a)
    for dat in data_tuples:
        out_data.append(
            dict(zip(keys, dat))
        )

    with open(outfile, 'w') as csvfile:
        writer = DictWriter(csvfile, fieldnames=keys, quoting=QUOTE_NONNUMERIC)
        writer.writeheader()
        writer.writerows(out_data)