def estimate_cfr(
    g_data,
    base_CFR,
    case_to_death_time,
    Rh_gamma_k,
    S_age_dist,
    days_back=7,
):
    """Estimate CFR from recent case data."""

    mean = case_to_death_time  # params["H_TIME"] + params["I_TO_H_TIME"] #+ params["D_REPORT_TIME"]
    adm2_mean = xp.sum(S_age_dist * mean[..., None], axis=0)
    k = Rh_gamma_k

    rolling_case_hist = g_data.csse_data.incident_cases
    rolling_death_hist = g_data.csse_data.incident_deaths

    t_max = rolling_case_hist.shape[0]
    x = xp.arange(0.0, t_max)

    # adm0
    adm0_inc_cases = xp.sum(rolling_case_hist, axis=1)
    adm0_inc_deaths = xp.sum(rolling_death_hist, axis=1)

    adm0_theta = xp.sum(adm2_mean * g_data.Nj / g_data.N) / k

    w = 1.0 / (xp.special.gamma(k) * adm0_theta**k) * x ** (k - 1) * xp.exp(-x / adm0_theta)
    w = w / (1.0 - w)
    w = w / xp.sum(w)
    w = w[::-1]

    # n_loc = rolling_case_hist.shape[1]
    cfr = xp.empty((days_back,))
    for i in range(days_back):
        d = i + 1
        cfr[i] = adm0_inc_deaths[-d] / (xp.sum(w[d:] * adm0_inc_cases[:-d], axis=0))

    adm0_cfr = 1.0 / xp.nanmean(1.0 / cfr, axis=0)

    # adm1
    adm1_inc_cases = g_data.sum_adm1(rolling_case_hist.T).T
    adm1_inc_deaths = g_data.sum_adm1(rolling_death_hist.T).T

    adm1_theta = g_data.sum_adm1(adm2_mean * g_data.Nj) / g_data.adm1_Nj / k

    x = xp.tile(x, (adm1_theta.shape[0], 1)).T
    w = 1.0 / (xp.special.gamma(k) * adm1_theta**k) * x ** (k - 1) * xp.exp(-x / adm1_theta)
    w = w / (1.0 - w)
    w = w / xp.sum(w, axis=0)
    w = w[::-1]
    cfr = xp.empty((days_back, adm1_theta.shape[0]))
    for i in range(days_back):
        d = i + 1
        cfr[i] = adm1_inc_deaths[-d] / (xp.sum(w[d:] * adm1_inc_cases[:-d], axis=0))

    adm1_cfr = 1.0 / xp.nanmean(1.0 / cfr, axis=0)

    baseline_adm1_cfr = g_data.sum_adm1(xp.sum(base_CFR * S_age_dist, axis=0) * g_data.Nj) / g_data.adm1_Nj

    cfr_fac = (adm1_cfr / baseline_adm1_cfr)[g_data.adm1_id]

    baseline_adm0_cfr = xp.sum(xp.sum(base_CFR * S_age_dist, axis=0) * g_data.Nj) / g_data.N
    adm0_cfr_fac = adm0_cfr / baseline_adm0_cfr
    valid = xp.isfinite(cfr_fac) & (cfr_fac > 0.002) & (xp.mean(adm1_inc_deaths[-days_back:]) > 4.0)
    cfr_fac[~valid] = adm0_cfr_fac

    # cfr_fac = 2.0 / (1.0 / cfr_fac + 1.0 / adm0_cfr_fac[..., None])
    # cfr_fac = xp.sqrt(cfr_fac * adm0_cfr_fac[..., None])

    return xp.clip(base_CFR * cfr_fac, 0.0, 1.0)

def estimate_chr(
    g_data,
    base_CHR,
    I_to_H_time,
    Rh_gamma_k,
    S_age_dist,
    days_back=7,
):
    """Estimate CHR from recent case data."""

    mean = I_to_H_time

    adm2_mean = xp.sum(S_age_dist * mean[..., None], axis=0)
    k = Rh_gamma_k

    rolling_case_hist = g_data.csse_data.incident_cases
    rolling_hosp_hist = g_data.hhs_data.incident_hospitalizations

    t_max = rolling_case_hist.shape[0]
    x = xp.arange(0.0, t_max)

    # adm0
    adm0_inc_cases = xp.sum(rolling_case_hist, axis=1)
    adm0_inc_hosp = xp.sum(rolling_hosp_hist, axis=1)

    adm0_theta = xp.sum(adm2_mean * g_data.Nj / g_data.N) / k

    w = 1.0 / (xp.special.gamma(k) * adm0_theta**k) * x ** (k - 1) * xp.exp(-x / adm0_theta)
    w = w / (1.0 - w)

    w = w / xp.sum(w)
    w = w[::-1]

    chr_ = xp.empty((days_back,))
    for i in range(days_back):
        d = i + 1
        chr_[i] = adm0_inc_hosp[-d] / (xp.sum(w[d:] * adm0_inc_cases[:-d], axis=0))

    adm0_chr = 1.0 / xp.nanmean(1.0 / chr_, axis=0)

    # adm1
    adm1_inc_cases = g_data.sum_adm1(rolling_case_hist.T).T
    adm1_inc_hosp = rolling_hosp_hist

    adm1_theta = g_data.sum_adm1(adm2_mean * g_data.Nj) / g_data.adm1_Nj / k

    x = xp.tile(x, (adm1_theta.shape[0], 1)).T
    w = 1.0 / (xp.special.gamma(k) * adm1_theta**k) * x ** (k - 1) * xp.exp(-x / adm1_theta)
    w = w / (1.0 - w)
    w = w / xp.sum(w, axis=0)
    w = w[::-1]
    chr_ = xp.empty((days_back, adm1_theta.shape[0]))
    for i in range(days_back):
        d = i + 1
        chr_[i] = adm1_inc_hosp[-d] / (xp.sum(w[d:] * adm1_inc_cases[:-d], axis=0))

    adm1_chr = 1.0 / xp.nanmean(1.0 / chr_, axis=0)

    baseline_adm1_chr = g_data.sum_adm1(xp.sum(base_CHR * S_age_dist, axis=0) * g_data.Nj) / g_data.adm1_Nj

    chr_fac = (adm1_chr / baseline_adm1_chr)[g_data.adm1_id]

    baseline_adm0_chr = xp.sum(xp.sum(base_CHR * S_age_dist, axis=0) * g_data.Nj) / g_data.N
    adm0_chr_fac = adm0_chr / baseline_adm0_chr
    valid = xp.isfinite(chr_fac) & (chr_fac > 0.002) & (xp.mean(adm1_inc_hosp[-7:]) > 4.0)
    chr_fac[~valid] = adm0_chr_fac

    return xp.clip(base_CHR * chr_fac, 0.0, 1.0)
