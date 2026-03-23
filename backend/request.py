import requests


def get_new_tokens():
    url = "http://127.0.0.1:1488/auth/telegram"

    data = {
        "init_data": "query_id=AAHdF6IQAAAAAN0XohB7g3Pj&user=%7B%22id%22%3A712345678%2C%22first_name%22%3A%22Ivan%22%2C%22username%22%3A%22ivan_dev%22%7D&auth_date=2000000000&hash=1d3d5f7f2d0a3a7b3c4c7a1f9c2c54e3bdbfd83a5c94b9c2d4b5e8a1c7d8e9f0"
    }

    r = requests.post(url, json=data)

    print(r.text)


{"access_token":"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNzEyMzQ1Njc4IiwiZXhwIjoxNzczNzQxMDY0LCJ0eXBlIjoiYWNjZXNzIn0._hwugysOUyNgRtk1XpG9BzovPk3xkz45l5y3JG78VOA",
 "refresh_token":"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNzEyMzQ1Njc4IiwiZXhwIjoxNzc4MDU5MjY0LCJ0eXBlIjoicmVmcmVzaCJ9.B5wh6S56HRxHxEfRg_tkf9GKpy7QfD93Me_x8CUy5r0",
 "token_type":"bearer"}


url = "http://127.0.0.1:1488/ask"

headers = {
    "Authorization":f"Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNzEyMzQ1Njc4IiwiZXhwIjoxNzczNzQxMDY0LCJ0eXBlIjoiYWNjZXNzIn0._hwugysOUyNgRtk1XpG9BzovPk3xkz45l5y3JG78VOA"
}

data = {
    "request":"привет ты кто"
}

resp = requests.post(url,json = data,headers=headers)


print(resp.text)