from datetime import datetime
from threading import Timer
from credentials import TOKEN
import telebot
import requests
import json

bot = telebot.TeleBot(TOKEN)

try:
    with open('users.json') as f:
        users = json.load(f)
except:
    users = []


@bot.message_handler(commands=['start'])
def start(message):  # add user to list fo users waiting a issue
    bot.send_message(
        message.from_user.id,
        text='I will send to you all new issues in gitcoin site, you just need to send me a /getNewIssues'
    )


def add_user(user):
    if user in users:
        return
    users.append(user)
    users_list = list(users)
    with open('users.json', 'w') as f:
        json.dump(users_list, f)


@bot.message_handler(commands=['getNewIssues'])
def addUser(message):  # add user to list fo users waiting a issue
    add_user({
        'id': message.from_user.id
    })
    bot.send_message(
        message.from_user.id,
        text='You are in my list of bounty hunters now'
    )


def send_issue(issue):
    text = f"""
*Title*:{issue['title']}
*Description*:{issue['issue_description']}
*Values*: {issue['value_true']} {issue['token_name']} | {issue['value_in_usdt_now']} USD
*Experience level*: {issue['experience_level']}
Links:
    + [Issue in Gitcoin]({issue['url']})
    + [Issue in Github]({issue['github_url']})
"""
    print(text)
    splitted_text = telebot.util.split_string(text, 3000)
    for user in users:
        for t in splitted_text:
            bot.send_message(user['id'], t, parse_mode='markdown')


def check_issues():
    r = requests.get('https://gitcoin.co/api/v0.1/bounties')
    issues = json.loads(r.content)
    for issue in issues:
        now = datetime.strptime(
            issue['now'][0:19],
            '%Y-%m-%dT%H:%M:%S'
        )
        created_on = datetime.strptime(
            issue['created_on'][0:19],
            '%Y-%m-%dT%H:%M:%S'
        )
        diff = now - created_on
        if issue['is_open'] and diff.total_seconds() < 3000 and issue['status'] == 'open':
            send_issue(issue)

    t = Timer(3000, check_issues)  # check new issues every 5 minutes
    t.start()


check_issues()
print('bot is running')
bot.polling(none_stop=True, timeout=1500)
