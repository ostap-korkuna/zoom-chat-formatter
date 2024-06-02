from datetime import datetime, timedelta
import re


def load_transcript_lines(filename):
    with open(filename, 'r') as file:
        lines = file.readlines()
    return lines


def load_presenters_from_file(filename, recording_offset_sec=0):
    all_lines = load_transcript_lines(filename)
    presenters = parse_transcript_presenters(all_lines, recording_offset_sec)
    return presenters


def time_diff(start_time_str, end_time_str):
    time_format = "%H:%M:%S"
    start_time = datetime.strptime(start_time_str, time_format)
    end_time = datetime.strptime(end_time_str, time_format)
    return (end_time - start_time).total_seconds()


def time_shift(timestamp_str, offset_sec):
    time_format = "%H:%M:%S"
    timestamp = datetime.strptime(timestamp_str, time_format) + timedelta(seconds=offset_sec)
    return timestamp.strftime(time_format)


def parse_transcript_presenters(transcript_lines, recording_offset_sec = 0):
    phrases = []
    # skip first two lines
    idx = 2
    while idx < len(transcript_lines):
        # 1
        # 00:00:00.330 --> 00:00:10.600
        # SF-6-06-AllHands: There we go alright. So we're gonna kick this off the way this demo works is that every team
        time_line = transcript_lines[idx+1]
        phrase_line = transcript_lines[idx+2]
        idx += 3
        start_time = time_line[:8]
        end_time = time_line[17:25]
        phrase_pattern = r'([a-zA-Z0-9\- ]+): (.+)'
        match = re.match(phrase_pattern, phrase_line)
        if not match:
            # Some lines aren't attributed. Skip them.
            continue
        speaker = match.group(1)
        phrases.append((start_time, end_time, speaker))

    presenters = []
    presentation_min_time_sec = 60
    idx = 0
    while idx < len(phrases):
        start_time = phrases[idx][0]
        speaker = phrases[idx][2]
        next_idx = idx+1
        while next_idx < len(phrases) and phrases[next_idx][2] == phrases[idx][2]:
            next_idx += 1
        end_time = phrases[next_idx-1][1]
        time_diff_sec = time_diff(start_time, end_time)
        if time_diff_sec > presentation_min_time_sec:
            presenters.append({
                'speaker': speaker,
                'start_time': time_shift(start_time, recording_offset_sec),
                'end_time': time_shift(end_time, recording_offset_sec)
            })
        idx = next_idx

    return presenters


def print_presenters(presenters):
    for presenter in presenters:
        print('{} - {}: {} presenting'.format(presenter['start_time'], presenter['end_time'], presenter['speaker']))


# presenters = [
#     {
#         'speaker': 'Oleg R',
#         'start_time': '00:20:30',
#         'end_time': '00:22:35',
#     }
# ]

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
def add_presenters_to_chat(chat, presenters):
    chat_w_presenters = []
    chat_idx = 0
    for presenter in presenters:
        while chat_idx < len(chat) and chat[chat_idx]['timestamp'] < presenter['start_time']:
            chat_w_presenters.append(chat[chat_idx])
            chat_idx += 1
        chat_w_presenters.append({
            'timestamp': presenter['start_time'],
            'author': '======================================================== {} presenting ========================================================'.format(presenter['speaker']),
            'message': [
                ''
            ],
            'reactions': [],
            'replies': []
        })

    while chat_idx < len(chat):
        chat_w_presenters.append(chat[chat_idx])
        chat_idx += 1

    return chat_w_presenters
