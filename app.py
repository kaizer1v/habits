from flask import Flask, render_template
import pandas as pd

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
        # df=[{'a': 123, 'b': 456}, {'a': 112233, 'b': 445566}]
        details=df.groupby(['category', 'split_title']).agg(
            {'delta': 'sum'}).reset_index().to_dict(orient='records')
    )


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
    print(p_df.groupby('category').agg({'delta': 'sum'}))
    return render_template(
        'report-template.html',
        df=p_df.groupby('category').agg(
            {'delta': 'sum'}).reset_index().to_dict(orient='records'),
        date=for_date.strftime('%b %y'),
        details=p_df.groupby(['category', 'split_title']).agg(
            {'delta': 'sum'}).reset_index()
    )


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
