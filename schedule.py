import pulp

FAIRNESS_FACTOR = 10

MONTHS = [
    'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec',
    'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
]

OUTPATIENT_ROTATIONS = VACATIONABLE_ROTATIONS = [
    'Elective', 'Gyn', 'MSK-1',
    'School-based Peds', 'PTF',
]
INPATIENT_ROTATIONS = [
    'FMS', 'OB-UH',
    'Inpatient Peds CHCO',
    'Inpatient Peds DH',
    'MICU-DH', 'MICU-UH',
]
ROTATIONS = INPATIENT_ROTATIONS + OUTPATIENT_ROTATIONS

DH_RESIDENTS = [
    'John', 'Morgan', 'Anita', 'Alicia',
]
UH_RESIDENTS = [
    'Kenny', 'Jeff', 'Cristi', 'Naomi', 'Steve', 'Alisa',
]

RESIDENTS = DH_RESIDENTS + UH_RESIDENTS

x = pulp.LpVariable.dicts(
    'x',
    ((month, rotation, resident)
        for month in MONTHS
        for rotation in ROTATIONS
        for resident in RESIDENTS),
    cat=pulp.LpBinary)

model = pulp.LpProblem('PGY2 Schedule', pulp.LpMaximize)

for resident in RESIDENTS:
    model.addConstraint(
        sum(x[month, 'FMS', resident] for month in MONTHS) == 3,
        '{} must do 3 months of FMS'.format(resident))
    model.addConstraint(
        sum(x[month, 'Elective', resident] for month in MONTHS) == 2,
        '{} must do 2 months of Elective'.format(resident))
    model.addConstraint(
        sum(x[month, 'PTF', resident] for month in MONTHS) == 1,
        '{} must do 1 month of PTF'.format(resident))
    model.addConstraint(
        sum(x[month, 'OB-UH', resident] for month in MONTHS) == 1,
        '{} must do 1 month of OB-UH'.format(resident))
    model.addConstraint(
        sum(x[month, 'School-based Peds', resident] for month in MONTHS) == 1,
        '{} must do 1 month of School-based Peds'.format(resident))
    model.addConstraint(
        (
            sum(x[month, 'Inpatient Peds CHCO', resident] for month in MONTHS) +
            sum(x[month, 'Inpatient Peds DH', resident] for month in MONTHS)
        ) == 1,
        '{} must do 1 month of Inpatient Peds'.format(resident))
    model.addConstraint(
        (
            sum(x[month, 'MICU-DH', resident] for month in MONTHS) +
            sum(x[month, 'MICU-UH', resident] for month in MONTHS)
        ) == 1,
        '{} must do 1 month of MICU'.format(resident))
    model.addConstraint(
        sum(x[month, 'Gyn', resident] for month in MONTHS) == 1,
        '{} must do 1 month of Gyn'.format(resident))
    model.addConstraint(
        sum(x[month, 'MSK-1', resident] for month in MONTHS) == 1,
        '{} must do 1 month of MSK-1'.format(resident))

    # this is the "no time-turners constraint"
    for month in MONTHS:
        model.addConstraint(
            sum(x[month, rotation, resident] for rotation in ROTATIONS) == 1,
            '{} can only do one rotation during {}'.format(resident, month))

for month in MONTHS:
    if month == 'Jun' or month == 'Jul':
        cap = 0
        message = 'No resident can do School-based Peds during {}'.format(month)
    else:
        cap = 1
        message = 'No more than one resident doing School-based Peds during {}'.format(month)

    model.addConstraint(
        sum(x[month, 'School-based Peds', resident] for resident in RESIDENTS) == cap,
        message)

chco_peds_numbers = {
    'Jul': 2, 'Aug': 1, 'Sep': 1,
    'Oct': 1, 'Dec': 1,
}
dh_peds_numbers = {
    'Dec': 1, 'Jan': 1, 'Feb': 1, 'Mar': 1,
}

for month in MONTHS:
    chco_num = chco_peds_numbers.get(month, 0)
    model.addConstraint(
        sum(x[month, 'Inpatient Peds CHCO', resident]
            for resident in RESIDENTS) == chco_num,
        '{} residents doing CHCO Peds {}'.format(chco_num, month))

    dh_num = dh_peds_numbers.get(month, 0)
    model.addConstraint(
        sum(x[month, 'Inpatient Peds DH', resident]
            for resident in RESIDENTS) == dh_num,
        '{} residents doing DH Peds {}'.format(dh_num, month))

for month in MONTHS:
    for rotation in ('MSK-1', 'Gyn', 'OB-UH'):
        model.addConstraint(
            sum(x[month, rotation, resident] for resident in RESIDENTS) <= 1,
            'You can only have one resident on {} during {}'.format(rotation, month))

for month in MONTHS:
    if month == 'Apr' or month == 'May':
        for dh_res1, dh_res2 in zip(DH_RESIDENTS, DH_RESIDENTS[1:]):
            model.addConstraint(
                x[month, 'PTF', dh_res1] == x[month, 'PTF', dh_res2],
                'Both {} and {} must do PTF in {}, or neither must'.format(
                    dh_res1, dh_res2, month))
        for uh_res1, uh_res2 in zip(UH_RESIDENTS, UH_RESIDENTS[1:]):
            model.addConstraint(
                x[month, 'PTF', uh_res1] == x[month, 'PTF', uh_res2],
                'Both {} and {} must do PTF in {}, or neither must'.format(
                    uh_res1, uh_res2, month))
    else:
        for resident in RESIDENTS:
            model.addConstraint(
                x[month, 'PTF', resident] == 0,
                'PTF is not offered to {} in {}'.format(resident, month))

fms_numbers = {
    'Jul': 2, 'Aug': 3, 'Sep': 2, 'Oct': 2,
    'Nov': 3, 'Dec': 3, 'Jan': 2, 'Feb': 2,
    'Mar': 2, 'Apr': 3, 'May': 3, 'Jun': 3,
}
for month in MONTHS:
    fms_num = fms_numbers[month]
    model.addConstraint(
        sum(x[month, 'FMS', resident] for resident in RESIDENTS) == fms_num,
        '{} residents on FMS in {}'.format(fms_num, month))

model.addConstraint(
    sum(x[month, 'MICU-UH', resident]
        for month in MONTHS
        for resident in RESIDENTS) == 6,
    'You must have 6 residents doing MICU at UH')
model.addConstraint(
    sum(x[month, 'MICU-DH', resident]
        for month in MONTHS
        for resident in RESIDENTS) == 4,
    'You must have 4 residents doing MICU at DH')
for month in MONTHS:
    model.addConstraint(
        sum(x[month, 'MICU-UH', resident] for resident in RESIDENTS) <= 1,
        'No more than 1 resident doing MICU at UH during {}'.format(month))
    model.addConstraint(
        sum(x[month, 'MICU-DH', resident] for resident in RESIDENTS) <= 1,
        'No more than 1 resident doing MICU at DH during {}'.format(month))

# https://cs.stackexchange.com/questions/12102/express-boolean-logic-operations-in-zero-one-integer-linear-programming-ilp
synth_var_ix = 0
def synth_var():
    global synth_var_ix
    synth_var_ix += 1
    return synth_var_ix

def and_together(x1, x2):
    """
    produce a variable that represents x1 && x2

    That variable can then be used in constraints and the objective func.
    """
    y = pulp.LpVariable('({} AND {})_{}'.format(x1.name, x2.name, synth_var()), cat=pulp.LpBinary)
    model.addConstraint(y >= x1 + x2 - 1, 'constraint{}'.format(synth_var()))
    model.addConstraint(y <= x1, 'constraint{}'.format(synth_var()))
    model.addConstraint(y <= x2, 'constraint{}'.format(synth_var()))
    return y

def or_together(x1, x2):
    y = pulp.LpVariable('({} OR {})_{}'.format(x1.name, x2.name, synth_var()), cat=pulp.LpBinary)
    model.addConstraint(y <= x1 + x2, 'constraint{}'.format(synth_var()))
    model.addConstraint(y >= x1, 'constraint{}'.format(synth_var()))
    model.addConstraint(y >= x2, 'constraint{}'.format(synth_var()))
    return y

def or_all(xs):
    if len(xs) == 2:
        return or_together(*xs)
    if len(xs) == 1:
        return xs[0]
    if len(xs) == 0:
        raise ValueError('Cannot OR together zero variables')
    x1, x2, *x_rest = xs
    y = or_together(x1, x2)
    return or_all([*x_rest, y])

def minimum(*xs, name):
    y = pulp.LpVariable('{}_{}'.format(name, synth_var()), cat=pulp.LpContinuous)
    for x in xs:
        model.addConstraint(y <= x, 'constraint{}'.format(synth_var()))
    return y

def negate(x):
    y = pulp.LpVariable('(NOT {})_{}'.format(x.name, synth_var()), cat=pulp.LpBinary)
    model.addConstraint(y == 1 - x, 'constraint_{}'.format(synth_var()))
    return y

def avg(xs):
    return sum(xs) / len(xs)

for resident in RESIDENTS:
    for m1, m2, m3, m4 in zip(MONTHS, MONTHS[1:], MONTHS[2:], MONTHS[3:]):
        m1_inpatient = or_all([x[m1, rotation, resident] for rotation in INPATIENT_ROTATIONS])
        m2_inpatient = or_all([x[m2, rotation, resident] for rotation in INPATIENT_ROTATIONS])
        m3_inpatient = or_all([x[m3, rotation, resident] for rotation in INPATIENT_ROTATIONS])
        m1_and_m2_inpatient = and_together(m1_inpatient, m2_inpatient)
        m1_m2_m3_inpatient = and_together(m1_and_m2_inpatient, m3_inpatient)
        not_m4_inpatient = negate(or_all([x[m4, rotation, resident] for rotation in INPATIENT_ROTATIONS]))
        model.addConstraint(
            m1_m2_m3_inpatient <= not_m4_inpatient,
            '{}: {}, {} and {} inpatient IMPLIES {} is not inpatient'.format(
                resident,
                m1, m2, m3, m4))

no_fms_in_a_row_objective = []
for m1, m2 in zip(MONTHS, MONTHS[1:]):
    for resident in RESIDENTS:
        anded = and_together(x[m1, 'FMS', resident], x[m2, 'FMS', resident])
        model.addConstraint(anded == 0, 'No two FMS in a row for {} ({}, {})'.format(resident, m1, m2))

resident_objective = []
"""
residents will rank their preferences. More weight is given to their
top priority goal. The sum of all their weights will equal 1.

for two choices: 2/3, 1/3
for three choices: 3/6, 2/6, 1/6
for four choices: 4/10, 3/10, 2/10, 1/10
...and so on

this rewards people who have fewer goals.
"""

def no_two_inpatient_in_a_row(resident):
    sequential_inpatient = []
    for m1, m2 in zip(MONTHS, MONTHS[1:]):
        sequential_inpatient.append(
            negate(and_together(
                or_all([x[m1, rotation, resident] for rotation in INPATIENT_ROTATIONS]),
                or_all([x[m2, rotation, resident] for rotation in INPATIENT_ROTATIONS]),
        )))
    # avg rather than sum below because each of "NOT (Jan inpatient & Feb inpatient)" is a request
    return avg(sequential_inpatient)

"""
Anita's Goal

Highly preferred:
#1 A vacation-able month in December

Also would be nice:
#2 Maximum DH months (i.e., MICU, Peds)
#3 Alternating months of inpatient and outpatient throughout the year, within the realm of reason (like two consecutive months of either is not a big deal)
"""
anita_objective = (
    3/6 * sum(x['Dec', rotation, 'Anita'] for rotation in VACATIONABLE_ROTATIONS) +
    1/6 * sum(x[month, 'MICU-DH', 'Anita'] for month in MONTHS) +
    1/6 * sum(x[month, 'Inpatient Peds DH', 'Anita'] for month in MONTHS) +
    1/6 * no_two_inpatient_in_a_row('Anita')
)
resident_objective.append(anita_objective)

"""
Naomi's Goal

#1 Outpatient/vacation eligible month in September (friend's wedding)
#2 Outpatient/vacation eligible month in May (? PTF for UH track?) (friend's wedding that I am in)
#3 Elective/vacation eligible month in any of the following: July, October, January, April (these are months RJ has outpatient so we could hopefully have at least some vacation time together!)
"""
naomi_objective = (
    3/6 * or_all([x['Sep', rotation, 'Naomi'] for rotation in OUTPATIENT_ROTATIONS]) +
    2/6 * or_all([x['May', rotation, 'Naomi'] for rotation in OUTPATIENT_ROTATIONS]) +
    1/6 * avg([
        or_all([x[month, rotation, 'Naomi'] for rotation in OUTPATIENT_ROTATIONS])
        for month in ('Jul', 'Oct', 'Jan', 'Apr')])
)
resident_objective.append(naomi_objective)

"""
Stephen's Goal

1) I would like my electives to be in November and March
2) I would like to be on outpatient (MSK, Gyn, or School Based Peds) in August and January.
"""
stephen_objective = (
    1/3 * x['Nov', 'Elective', 'Steve'] +
    1/3 * x['Mar', 'Elective', 'Steve'] +
    1/6 * sum(x['Aug', rotation, 'Steve'] for rotation in ('MSK-1', 'Gyn', 'School-based Peds')) +
    1/6 * sum(x['Jan', rotation, 'Steve'] for rotation in ('MSK-1', 'Gyn', 'School-based Peds'))
)
resident_objective.append(stephen_objective)

"""
Kenny's Goal

1) A vacationable rotation in September (preferably an elective, but Gyn, MSK-1, or school Peds would work, too).
2) Something outpatient in December (elective, Gyn, MSK-1, or school Peds).
"""
kenny_objective = (
    2/3 * x['Sep', 'Elective', 'Kenny'] +
    1/3 * sum(x['Sep', rotation, 'Kenny'] for rotation in ('Gyn', 'MSK-1', 'School-based Peds')) +
    # Prior two conflict, so it's okay that the weights sum to over 1
    1/3 * sum(x['Dec', rotation, 'Kenny'] for rotation in ('Elective', 'Gyn', 'MSK-1', 'School-based Peds'))
)
resident_objective.append(kenny_objective)

"""
Alicia's Goal

Not do more than 2 inpatient months in a row (my arms will die)
Per Linda, I can’t do FMS during Chautauqua months  since I can’t do OB independently
"""
alicia_objective = no_two_inpatient_in_a_row('Alicia')
model.addConstraint(
    sum(x[month, 'FMS', 'Alicia'] for month in ('Jun', 'Jul', 'Nov')) == 0,
    'Per Linda, Alicia cannot do FMS during Chautauqua months')
resident_objective.append(alicia_objective)

"""
Crist's Goal

1) MICU as early as possible
2) Ob as early as possible
3) school based Peds in December
"""
def as_early_as_possible(resident, rotation):
    divisor = len(MONTHS) - 1
    weights = [w / divisor for w in reversed(range(len(MONTHS)))]
    assert weights[0] == 1
    return sum(w * x[month, rotation, resident] for w, month in zip(weights, MONTHS))

cristi_objective = (
    3/6 * as_early_as_possible('Cristi', 'MICU-DH') +
    3/6 * as_early_as_possible('Cristi', 'MICU-UH') +
    2/6 * as_early_as_possible('Cristi', 'OB-UH') +
    1/3 * x['Dec', 'School-based Peds', 'Cristi']
)
resident_objective.append(cristi_objective)

"""
John's Goal

1) ICU and OB early
2) An elective over winter at some point
"""
john_objective = (
    1/3 * as_early_as_possible('John', 'MICU-DH') +
    1/3 * as_early_as_possible('John', 'MICU-UH') +
    1/3 * as_early_as_possible('John', 'OB-UH') +
    1/3 * avg([x[month, 'Elective', 'John'] for month in ('Dec', 'Jan', 'Feb')])
)
resident_objective.append(john_objective)

"""
Alisa's Goal

1. Outpatient May
2. Outpatient Sep
3. Outpatient Jul
4. Outpatient Dec
5. Alternating inpatient, outpatient
"""
alisa_objective = (
    5/15 * sum(x['May', rotation, 'Alisa'] for rotation in OUTPATIENT_ROTATIONS) +
    4/15 * sum(x['Sep', rotation, 'Alisa'] for rotation in OUTPATIENT_ROTATIONS) +
    3/15 * sum(x['Jul', rotation, 'Alisa'] for rotation in OUTPATIENT_ROTATIONS) +
    2/15 * sum(x['Dec', rotation, 'Alisa'] for rotation in OUTPATIENT_ROTATIONS) +
    1/15 * no_two_inpatient_in_a_row('Alisa')
)
resident_objective.append(alisa_objective)

"""
Morgan's Goal

1. Inpatient rotations in 'Jul', 'Aug', 'Sep', 'Nov', 'Dec'
2. MICU in Jul, Aug, Sep
3. Elective in October

constraint: Per Linda, Inpatient peds Dec or earlier
"""
morgan_objective = (
    3/6 * avg([
        sum(x[month, rotation, 'Morgan'] for rotation in INPATIENT_ROTATIONS)
        for month in ('Jul', 'Aug', 'Sep', 'Nov', 'Dec')]) +
    2/6 * sum(x[month, rotation, 'Morgan'] for month in ('Jul', 'Aug', 'Sep') for rotation in ('MICU-DH', 'MICU-UH')) +
    1/6 * x['Oct', 'Elective', 'Morgan']
)
resident_objective.append(morgan_objective)

model.addConstraint(
    sum(x[month, rotation, 'Morgan']
        for month in ('Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun')
        for rotation in ('Inpatient Peds CHCO', 'Inpatient Peds DH')) == 0,
    'Per Linda, morgan must do Inpatient peds Dec or earlier')

fairness_objective = minimum(*resident_objective, name='least satisfied resident goals')

program_objective = (
    # Prefer to have DH residents doing Inpatient Peds DH
    avg([x[month, 'Inpatient Peds DH', resident]
        for resident in DH_RESIDENTS
        for month in MONTHS]) +

    # Prefer to have UH residents doing Inpatient Peds CHCO
    avg([x[month, 'Inpatient Peds CHCO', resident]
        for resident in UH_RESIDENTS
        for month in MONTHS]) +

    # Prefer to have DH residents doing MICU-DH
    avg([x[month, 'MICU-DH', resident]
        for resident in DH_RESIDENTS
        for month in MONTHS]) +

    # Prefer to have UH residents doing MICU-UH
    avg([x[month, 'MICU-UH', resident]
        for resident in UH_RESIDENTS
        for month in MONTHS])
)

model += program_objective + sum(resident_objective) + FAIRNESS_FACTOR * fairness_objective

# pulp.LpSolverDefault.msg = 1
model.solve()
if pulp.LpStatus[model.status] != 'Optimal':
    raise ValueError(pulp.LpStatus[model.status])

# data = [{
#     'resident': resident,
#     'schedule': [
#         {
#             'month': month,
#             'rotation': max(ROTATIONS, key=lambda r: x[month, r, resident].varValue),
#         } for month in MONTHS
#     ]}
#     for resident in RESIDENTS
# ]
data = [{
    'resident': resident,
    'month': month,
    'rotation': max(ROTATIONS, key=lambda r: x[month, r, resident].varValue),
} for resident in RESIDENTS for month in MONTHS]

import json
import sys
json.dump(data, sys.stdout)
