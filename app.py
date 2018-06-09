import pandas as pd
from pandas.tseries.offsets import DateOffset
from flask import Flask, render_template, request

df = pd.read_csv(
    'calendar_data.csv',
    encoding='utf-8',
    parse_dates=['start_date_time', 'end_date_time']
)
df.loc[:, 'delta'] = df['end_date_time'] - df['start_date_time']

app = Flask(__name__)


@app.route("/")
def index():
    return render_template(
        'report-template.html',
        df=df.groupby('category').agg(
            {'delta': 'sum'}).reset_index().to_dict(orient='records'),
        details=df.groupby(['category', 'split_title']).agg(
            {'delta': 'sum'}).reset_index().to_dict(orient='records')
    )


@app.route('/a')
def something():
    return render_template('another_template.html')


@app.route("/<string:year>/<string:month>")
def timebased(year, month):
    '''
    given a month and year, filter the dataframe
    to provide only productivity for that time period.

    @param `year` <int> - needs to be in YYYY format
    @param `month` <str> - needs to short hand for month name eg Apr, Oct etc.
    '''
    for_date = pd.to_datetime('{}-{}'.format(year, month))
    p_df = df[(df['start_date_time'].dt.month == for_date.month) &
              (df['start_date_time'].dt.year == for_date.year)]

    return render_template(
        'report-template.html',
        df=p_df.groupby('category').agg(
            {'delta': 'sum'}).reset_index().to_dict(orient='records'),
        date=for_date.strftime('%b %y'),
        prev_month='{}{}/{}'.format(
            request.url_root,
            (for_date - DateOffset(months=1)).strftime('%Y'),
            (for_date - DateOffset(months=1)).strftime('%m')
        ),
        next_month='{}{}/{}'.format(
            request.url_root,
            (for_date + DateOffset(months=1)).strftime('%Y'),
            (for_date + DateOffset(months=1)).strftime('%m')
        ),
        details=p_df.groupby(['category', 'split_title']).agg(
            {'delta': 'sum'}).reset_index()
    )


@app.route("/abcd")
def tryme():
    import json
    print("this is form the python end...")
    return json.dumps({'a': 123, 'b': False, 'c': [11, 22, 33]})


def longest_streak(df, col_val, col='category'):
    '''
    method to calculate the longest streak of an activity
    INCOMPLETE
    '''
    cont = df[df[col] == col_val]['start_date_time'].diff().dt.days
    streaks = []
    streak = 0
    for c in cont:
        if c != 1:
            streak = 0
        streak += 1
        streaks.append(streak)
    return max(streaks)


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
