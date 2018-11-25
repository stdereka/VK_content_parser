import vk
from getpass import getpass
from argparse import ArgumentParser
from datetime import datetime
import time as t
import os


def get_timestamp(dt):
    return datetime.strptime(dt, "%d/%m/%Y").timestamp()


def send_email():
    with open('e-mails.txt', 'r') as f:
        emails = f.read().replace('\n', ' ')
        os.system('cat mail.txt | mail -v -s "VK parsing results" ' + emails + ' >> log.txt 2>&1')
        f.close()


def add_to_index(s):
    with open('index.txt', 'a') as f:
        f.write(s + '\n')
        f.close()


def read_index():
    with open('index.txt', 'r') as f:
        res = [s[:-1] for s in f.readlines()]
        f.close()
    return res


def truncate_index(max_size):
    idxs = read_index()
    if len(idxs) > max_size:
        with open('index.txt', 'w') as f:
            f.write('\n'.join(idxs[-max_size:])+'\n')
            f.close()


def write_letter(s):
    with open('mail.txt', 'a') as f:
        f.write(s + '\n')
        f.close()


def run():
    app_id = 6753116
    # 10 days
    interval = 864000.0
    index_size = 500

    parser = ArgumentParser()
    # parser.add_argument("--date")
    parser.add_argument("--verbose", '-v', action='store_true')
    args = parser.parse_args()

    # user = getpass(prompt="E-mail/Phone number:", stream=None)
    # password = getpass(prompt="Password:", stream=None)

    user = '89257977195'
    password = '098qwe'

    session = vk.AuthSession(app_id=app_id, user_login=user, user_password=password, scope='messages')
    del user
    del password
    api = vk.API(session)

    with open("domains.txt", "r") as f:
        domains = [s[:-1] for s in f.readlines()]
        f.close()

    with open("keywords.txt", "r") as f:
        keywords = [s[:-1] for s in f.readlines()]
        f.close()

    with open("users.txt", "r") as f:
        users = [s[:-1] for s in f.readlines()]
        f.close()

    # date = get_timestamp(args.date)
    date = t.time() - interval

    indexed_items = read_index()

    for domain in domains:
        if args.verbose:
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
                    post_idx = str(owner_id) + str(post_id)
                    is_post_new = False
                    if post_idx not in indexed_items:
                        add_to_index(post_idx)
                        is_post_new = True
                    if is_post_new:
                        write_letter("Post found: "+post_link+'\n')
                    if args.verbose:
                        print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
                        print("Post found:")
                        print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
                        print(post_link)
                        print()
                    break
            comments = [comment for comment in api.wall.getComments(post_id=post_id, owner_id=owner_id, v='5.52',
                                                                    count='100')['items'] if comment['date'] >= date]
            t.sleep(0.5)
            flag = True
            for comment in comments:
                for keyword in keywords:
                    if keyword in comment['text']:
                        comment_idx = str(owner_id) + str(post_id) + str(comment['id'])
                        is_comment_new = False
                        if comment_idx not in indexed_items:
                            add_to_index(comment_idx)
                            is_comment_new = True
                        if flag and is_comment_new:
                            if args.verbose:
                                print('----------------------------------')
                                print("Comments for post", post_link, "are found:")
                                print('----------------------------------')
                            write_letter('Comments for post ' + post_link + ' are found:')
                            flag = False
                        if is_comment_new:
                            write_letter(comment['text']+'\n')
                            if args.verbose:
                                print()
                                print(comment['text'])
                                print()
                        break

    truncate_index(index_size)

    if os.stat('mail.txt').st_size != 0:
        with open('mail.txt', 'r') as f:
            text = f.read()
            for user in users:
                api.messages.send(domain=user, message=text, v='5.52')
        send_email()
        with open('mail.txt', 'w') as f:
            f.write('')
            f.close()


if __name__ == "__main__":
    run()
