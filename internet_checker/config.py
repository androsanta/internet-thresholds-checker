import os

config = {
    'web_cube_username': os.environ['USERNAME'],
    'web_cube_password': os.environ['PASSWORD'],
    'db_host': os.environ['DATABASE'] if os.environ.get('DATABASE') else 'localhost',
    'disconnect_threshold': os.environ['DISCONNECT_THRESHOLD'] if os.environ.get('DISCONNECT_THRESHOLD') else 5,
    'daily_remaining_threshold': os.environ['DAILY_THRESHOLD'] if os.environ.get('DAILY_THRESHOLD') else 0.8
}
