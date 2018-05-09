import os
import httplib2
import pandas as pd
from oauth2client import tools
from oauth2client import client
from apiclient import discovery
from oauth2client.file import Storage

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/calendar-python-quickstart.json
SCOPES = 'https://www.googleapis.com/auth/calendar.readonly'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Google Calendar API Python Quickstart'


def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'calendar-python-quickstart.json')

    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else:  # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials


def main(str_start_date, str_end_date):
    """Shows basic usage of the Google Calendar API.

    Creates a Google Calendar API service object and outputs a list of the next
    10 events on the user's calendar.
    """
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('calendar', 'v3', http=http)

    # utc = datetime.datetime.utcnow().isoformat() + 'Z'  # 'Z' = UTC time
    start_date = pd.to_datetime(str_start_date, dayfirst=True)
    end_date = pd.to_datetime(str_end_date, dayfirst=True)

    print('downloading data...')
    eventsResult = service.events().list(
        calendarId='primary',
        timeMin=start_date.strftime('%Y-%m-%dT%H:%M:%SZ'),
        timeMax=end_date.strftime('%Y-%m-%dT%H:%M:%SZ'),
        # maxResults=10,
        singleEvents=True,
        orderBy='startTime'
    ).execute()
    events = eventsResult.get('items', [])

    events_data = []
    if not events:
        print('No events found since {}.'.format(start_date.strftime('%b-%y')))
    for event in events:
        start = event['start'].get('date', event['start'].get('dateTime'))
        end = event['end'].get('date', event['end'].get('dateTime'))
        # org = event['organizer'].get(
        #     'displayName', event['organizer'].get('email'))

        events_data.append({
            'start_date_time': start,
            'end_date_time': end,
            'title': event['summary'],
            # 'desc': event.get('description', ''),
            # 'location': event.get('location', ''),
            # 'link': event['htmlLink'],
            # 'organizer': org
        })

    df = pd.DataFrame(events_data)
    # separate out the category from the title
    cat_df = pd.DataFrame(df.title.str.split(
        ' - ', 1).tolist(), columns=['category', 'split_title'])
    cat_df['split_title'].fillna(cat_df['category'], inplace=True)
    # categorize titles which aren't into `Misc`
    ind = cat_df['category'] == cat_df['split_title']
    cat_df.loc[ind, 'category'] = 'Misc'

    # add `category` and `split_title` into df
    df = pd.concat([df, cat_df], axis=1)

    # compute difference in datetime
    df = df.astype({
        'start_date_time': 'datetime64[ns]',
        'end_date_time': 'datetime64[ns]'
    })
    diff_components = (df['end_date_time'] -
                       df['start_date_time']).dt.components
    # df['diff_days'], df[
    #     'diff_hours'] = diff_components.days, (diff_components.minutes / 60)
    df.loc[:, 'diff_days'] = diff_components.days
    df.loc[:, 'diff_hours'] = (df['end_date_time'] -
                               df['start_date_time']) / pd.np.timedelta64(1, 'h')
    df.loc[:, 'delta'] = df['end_date_time'] - df['start_date_time']

    # download as a csv
    print('saving {} - {} data into a csv file...'.format(
        str_start_date, str_end_date))
    df.loc[:, df.columns != 'title'].to_csv(
        'calendar_data.csv', index=False, encoding='utf-8')


def longest_streak(df, col_val, col='category'):
    cont = df[df[col] == col_val]['start_date_time'].diff().dt.days
    streaks = []
    streak = 0
    for c in cont:
        if c != 1:
            streak = 0
        streak += 1
        streaks.append(streak)
    return max(streaks)


if __name__ == '__main__':
    main('01-01-2018', pd.to_datetime('today'))
