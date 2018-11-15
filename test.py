import vk
from getpass import getpass
from argparse import ArgumentParser
from datetime import datetime
import time as t


app_id = 6753116


parser = ArgumentParser()
parser.add_argument("--date")
args = parser.parse_args()


def get_timestamp(dt):
    return datetime.strptime(dt, "%d/%m/%Y").timestamp()


user = getpass(prompt="E-mail/Phone number:", stream=None)
password = getpass(prompt="Password:", stream=None)


session = vk.AuthSession(app_id=app_id, user_login=user, user_password=password)
del user
del password
api = vk.API(session)


with open("domains.txt", "r") as f:
    domains = [s[:-1] for s in f.readlines()]

with open("keywords.txt", "r") as f:
    keywords = [s[:-1] for s in f.readlines()]


date = get_timestamp(args.date)


for domain in domains:
    print("##################################")
    print("Searching in", domain)
    print("##################################")
    print()
    posts = [post for post in api.wall.get(domain=domain, v='5.52', count='100')['items'] if post['date'] > date]
    for post in posts:
        post_id = post['id']
        owner_id = post['owner_id']
        post_link = 'https://vk.com/' + str(domain) + '?w=wall' + str(post['owner_id']) + '_' + str(post['id'])
        for keyword in keywords:
            if keyword in post['text']:
                print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
                print("Post found:")
                print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
                print(post_link)
                print()
        comments = [comment for comment in api.wall.getComments(post_id=post_id, owner_id=owner_id, v='5.52',
                                                                count='100')['items'] if comment['date'] >= date]
        flag = True
        for comment in comments:
            for keyword in keywords:
                if keyword in comment['text']:
                    if flag:
                        print('----------------------------------')
                        print("Comments for post", post_link, "are found:")
                        print('----------------------------------')
                        flag = False
                    print()
                    print(comment['text'])
                    print()
        t.sleep(0.3)
