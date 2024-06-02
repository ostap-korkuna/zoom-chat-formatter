from chat_parsing import print_chat, load_chat_from_file
from transcript_parsing import load_presenters_from_file, print_presenters, add_presenters_to_chat

CHAT_FILE = 'chat.txt'
TRANSCRIPT_FILE = 'transcript.vtt'


def main():
    # Parse Zoom chat
    chat = load_chat_from_file(CHAT_FILE)
    # print_chat(chat)

    # Parse presentations from transcript
    # presenters = load_presenters_from_file(TRANSCRIPT_FILE, recording_offset_sec=17*60+30)
    presenters = load_presenters_from_file(TRANSCRIPT_FILE, recording_offset_sec=0)
    # print_presenters(presenters)

    chat_w_presenters = add_presenters_to_chat(chat, presenters)
    print_chat(chat_w_presenters)


if __name__ == '__main__':
    main()
