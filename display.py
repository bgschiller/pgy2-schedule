import pandas as pd
import sys
import json

data = json.load(sys.stdin)
MONTHS = [
    'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec',
    'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
]

if 't' in sys.argv:
    df = (pd.pivot_table(
        pd.DataFrame.from_records(data),
        values='resident',
        index='rotation',
        columns='month',
        aggfunc='LB'.join)
        .fillna('')
        [MONTHS])
else:
    df = (pd.DataFrame.from_records(data)
        .pivot(
        values='rotation',
        index='resident',
        columns='month')
        [MONTHS])


print(df.to_html())

