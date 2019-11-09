import os

config = {
    'web_cube_username': os.environ['USERNAME'],
    'web_cube_password': os.environ['PASSWORD'],
    'db_host': os.environ['DATABASE'] if os.environ['DATABASE'] else 'localhost'
}
