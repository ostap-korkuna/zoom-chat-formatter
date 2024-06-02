import re


def load_chat_lines(filename):
    with open(filename, 'r') as file:
        lines = file.readlines()
    return lines


def load_chat_from_file(filename):
    chat_all_lines = load_chat_lines(filename)
    chat = parse_lines(chat_all_lines)
    return chat


def is_timestamped_line(line):
    pattern = r'(\d{2}:\d{2}:\d{2}).*'
    return re.match(pattern, line)


def find_original_post(chat, reference):
    for post in chat:
        if post['message'][0].startswith(reference):
            return post
        for reply in post['replies']:
            if reply['message'][0].startswith(reference):
                return reply
    print('Could not locate the original post: {}'.format(reference))
    return None


def add_reaction(chat, reference, reaction):
    original_post = find_original_post(chat, reference)
    original_post['reactions'].append(reaction)


def add_reply(chat, reference, timestamp, author, message):
    original_post = find_original_post(chat, reference)
    # remove empty lines
    while len(message):
        if len(message[0].strip()):
            break
        message.pop(0)
    original_post['replies'].append({
        'timestamp': timestamp,
        'author': author,
        'message': message,
        'reactions': []
    })


def trim_reference(reference):
    if reference.endswith('...'):
        return reference[:-3]
    if reference.endswith('…'):
        return reference[:-1]
    return reference


# chat = [
#     {
#         'timestamp': '00:21:49',
#         'author': 'Oleg R',
#         'message': [
#             'HUGE',
#             'Ship it!'
#         ],
#         'reactions': ['💙', '💙', '👍'],
#         'replies': [
#             {
#                 'timestamp': '00:22:40',
#                 'author': 'Ostap K',
#                 'message': [
#                     'Woa!',
#                     'Yeah!'
#                 ],
#                 'reactions': ['👍'],
#             }
#         ]
#     },
# ]
def parse_lines(chat_lines):
    chat = []
    idx = 0
    while idx < len(chat_lines):
        msg_pattern = r'(\d{2}:\d{2}:\d{2})\t([a-zA-Z0-9\- ]+):\t(.*)'
        line = chat_lines[idx]
        match = re.match(msg_pattern, line)
        if not match:
            idx += 1
            print('Failed parsing: {}'.format(line))
            continue

        timestamp = match.group(1)
        author = match.group(2)
        message = match.group(3)

        full_message = [message]
        idx += 1
        while idx < len(chat_lines) and not is_timestamped_line(chat_lines[idx]):
            # remove newlines at the end of each line
            full_message.append(chat_lines[idx][:-1])
            idx += 1

        # Reaction
        if message.startswith('Reacted to'):
            reaction_pattern = r'Reacted to "(.+)" with (.)'
            match = re.match(reaction_pattern, message)
            if not match:
                print('Failed parsing reaction: {}'.format(message))
            reference = trim_reference(match.group(1))
            reaction = match.group(2)
            add_reaction(chat, reference, reaction)
            continue

        # Reply
        if message.startswith('Replying to'):
            reply_pattern = r'Replying to "(.+)"'
            match = re.match(reply_pattern, message)
            if not match:
                print('Failed parsing reply: {}'.format(message))
            reference = trim_reference(match.group(1))
            add_reply(chat, reference, timestamp, author, full_message[1:])
            continue

        chat.append({
            'timestamp': timestamp,
            'author': author,
            'message': full_message,
            'reactions': [],
            'replies': []
        })

    return chat


def print_chat(chat):
    for post in chat:
        print('{} {}:'.format(post['timestamp'], post['author']))
        print('\n'.join(post['message']))
        if post['reactions']:
            print(' '.join(post['reactions']))
        for reply in post['replies']:
            print('\t|')
            print('\t|- {} {}:'.format(reply['timestamp'], reply['author']))
            for message in reply['message']:
                print('\t| {}'.format(message))
            if reply['reactions']:
                print('\t| {}'.format(' '.join(reply['reactions'])))
        print('')

