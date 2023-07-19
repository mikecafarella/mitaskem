# simulate lockdown
import numpy as np
from datetime import date

def get_beta(t): 
    # first day of simulation
    day0 = date(2020, 1, 1) #'1-jan-2020'
    tlock =[]
    tunlock  =[]
    scale=[]

    # state of emergency and such [2]
    tlock.append((date(2020, 3, 23)-day0).days) # daysact(day0,'23-mar-2020')
    tunlock.append((date(2020, 7, 17)-day0).days) #daysact(day0,'17-jul-2020')
    scale.append(0.4)

    # stage 3 [3]
    tlock.append((date(2020, 7, 17)-day0).days) #daysact(day0,'17-jul-2020')
    tunlock.append((date(2020, 10, 9)-day0).days) #daysact(day0,'9-oct-2020')
    scale.append(0.55)

    # oops, back to stage 2 [2]
    tlock.append((date(2020, 10, 9)-day0).days) #daysact(day0,'9-oct-2020')
    tunlock.append((date(2020, 11, 23)-day0).days) #daysact(day0,'23-nov-2020')
    scale.append(0.6)

    # strict lockdown, stay at home order [1]
    tlock.append((date(2020, 11, 23)-day0).days) #daysact(day0,'23-nov-2020')
    # tunlock(ind) = daysact(day0,'5-mar-2021');
    tunlock.append((date(2021, 1, 5)-day0).days) #daysact(day0,'5-jan-2021')
    scale.append(0.55)

    # stricter lockdown, stay at home order [1]
    tlock.append((date(2021, 1, 5)-day0).days) #daysact(day0,'5-jan-2021')
    tunlock.append((date(2021, 3, 5)-day0).days) #daysact(day0,'5-mar-2021')
    scale.append(0.3)

    # stay at home order lifted [2]
    tlock.append((date(2021, 3, 5)-day0).days) #daysact(day0,'5-mar-2021')
    tunlock.append((date(2021, 4, 13)-day0).days) #daysact(day0,'13-apr-2021')
    scale.append(0.4)

    # lockdown again [1]
    tlock.append((date(2021, 4, 13)-day0).days) #daysact(day0,'13-apr-2021')
    tunlock.append((date(2021, 6, 11)-day0).days) #daysact(day0,'11-jun-2021')
    scale.append(0.15)

    # stage 2 reopening [3]
    tlock.append((date(2021, 6, 11)-day0).days) #daysact(day0,'11-jun-2021')
    tunlock.append((date(2021, 7, 2)-day0).days) #daysact(day0,'2-jul-2021')
    scale.append(0.2)

    # stage 3 reopening [4]
    tlock.append((date(2021, 7, 2)-day0).days) #daysact(day0,'2-jul-2021')
    tunlock.append((date(2021, 7, 16)-day0).days) #daysact(day0,'16-jul-2021')
    scale.append(0.3)

    # physical distancing [5]
    tlock.append((date(2021, 7, 16)-day0).days) #daysact(day0,'16-jul-2021')
    tunlock.append((date(2021, 9, 1)-day0).days) #daysact(day0,'1-sep-2021')
    scale.append(0.35)

    # physical distancing [5]
    tlock.append((date(2021, 9, 1)-day0).days) #daysact(day0,'1-sep-2021')
    tunlock.append((date(2021, 11, 1)-day0).days) #daysact(day0,'1-nov-2021')
    scale.append(0.4)

    # physical distancing loosening [6]
    tlock.append((date(2021, 11, 1)-day0).days) #daysact(day0,'1-nov-2021')
    tunlock.append((date(2022, 1, 1)-day0).days) #daysact(day0,'1-jan-2022')
    scale.append(0.5)

    # physical distancing tightened [6]
    tlock.append((date(2022, 1, 1)-day0).days) #daysact(day0,'1-jan-2022')
    tunlock.append((date(2023, 1, 1)-day0).days) #daysact(day0,'1-jan-2023')
    scale.append(0.4)

    ilock = np.where(np.array(tlock) <= t)[0].tolist() #find(tlock <= t)
    iunlock = np.where(np.array(tunlock) > t)[0].tolist() #find(t < tunlock)
    ii = list(set(ilock) & set(iunlock)) #intersect(ilock,iunlock)
    if (len(ii) > 1):
        np.array([t,ii])

    if (len(ii)==0): # there is no intersection
        beta_scale = 1
    else: #there is an intersection, should only be 1
        ii = ii[0]
        beta_scale = scale[ii]
    
    return beta_scale