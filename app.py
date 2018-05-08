from flask import Flask, flash, redirect, render_template, request, session, abort, request
from flask import jsonify
import pandas as pd
import json

df = pd.read_csv(
    'calendar_data.csv',
    encoding='utf-8',
    parse_dates=['start_date_time', 'end_date_time']
)

app = Flask(__name__)


@app.route("/")
def index():
    return render_template(
        'report-template.html',
        df=df.groupby('category').agg(
            {'diff_hours': 'sum'}).reset_index().to_dict(orient='records')
        # df=[{'a': 123, 'b': 456}, {'a': 112233, 'b': 445566}]
    )


@app.route("/<string:year>/<string:month>")
def timebased(year, month):
    '''
    given a month and year, filter the dataframe
    to provide only productivity for that time period.
    '''
    for_date = pd.to_datetime('{}-{}'.format(year, month))
    p_df = df[(df['start_date_time'].dt.month == for_date.month) &
              (df['start_date_time'].dt.year == for_date.year)]
    return render_template(
        'report-template.html',
        df=p_df.groupby('category').agg(
            {'diff_hours': 'sum'}).reset_index().to_dict(orient='records'),
        date=for_date.strftime('%b %y')
    )


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
