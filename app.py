import sys
from io import BytesIO
import imp

import telegram
from flask import Flask, request, send_file

from fsm import TocMachine


API_TOKEN = '352682097:AAH_jBdxJr-Tt8i0pPP19ujfyKeG2iuUT2U'
WEBHOOK_URL = '/hook'

app = Flask(__name__)
bot = telegram.Bot(token=API_TOKEN)
machine = TocMachine(
    states=[
        'user',
        'state1',
        'state2',
        'state3',
        'state4',
        'state5',
        'state6',
        'state7',
        'state8',
        'state9',
        'state10',
        'state11'
    ],
    transitions=[
        {
            'trigger': 'advance',
            'source': 'user',
            'dest': 'state1',
            'conditions': 'is_going_to_state1'
        },
        {
            'trigger': 'advance',
            'source': 'state1',
            'dest': 'state2',
            'conditions': 'is_going_to_state2'
        },
        {
            'trigger': 'advance',
            'source': 'state2',
            'dest': 'state3',
            'conditions': 'is_going_to_state3'
        },
        {
            'trigger': 'advance',
            'source': 'state1',
            'dest': 'state4',
            'conditions': 'is_going_to_state4'
        },
        {
            'trigger': 'advance',
            'source': 'state4',
            'dest': 'state5',
            'conditions': 'is_going_to_state5'
        },
        {
            'trigger': 'advance',
            'source': 'state4',
            'dest': 'state6',
            'conditions': 'is_going_to_state6'
        },
        {
            'trigger': 'advance',
            'source': [
                'state5',
                'state6'
            ],
            'dest': 'state7',
            'conditions': 'is_going_to_state7'
        },
        {
            'trigger': 'advance',
            'source': 'state7',
            'dest': 'state8',
            'conditions': 'is_going_to_state8'
        },
        {
            'trigger': 'advance',
            'source': 'state7',
            'dest': 'state9',
            'conditions': 'is_going_to_state9'
        },
        {
            'trigger': 'advance',
            'source': 'state7',
            'dest': 'state10',
            'conditions': 'is_going_to_state10'
        },
        {
            'trigger': 'advance',
            'source': 'state7',
            'dest': 'state11',
            'conditions': 'is_going_to_state11'
        },
        {
            'trigger': 'go_back_32',
            'source': [
                'state3'
            ],
            'dest': 'state2',
        },
        {
            'trigger': 'go_back_84',
            'source': [
                'state8'
            ],
            'dest': 'state4',
        },
        {
            'trigger': 'go_back_97',
            'source': [
                'state9'
            ],
            'dest': 'state7',
        },
        {
            'trigger': 'go_back_107',
            'source': [
                'state10'
            ],
            'dest': 'state7',
        },
        {
            'trigger': 'go_back_117',
            'source': [
                'state11'
            ],
            'dest': 'state7',
        },
        {
            'trigger': 'go_back',
            'source': [
                'state2',
                'state1',
                'state3',
                'state4',
                'state5',
                'state6',
                'state7',
                'state8',
                'state9',
                'state10',
                'state11'
                'user'
            ],
            'dest': 'user',
        }

    ],
    initial='user',
    auto_transitions=False,
    show_conditions=True,
)


def _set_webhook():
    status = bot.set_webhook(WEBHOOK_URL)
    if not status:
        print('Webhook setup failed')
        sys.exit(1)
    else:
        print('Your webhook URL has been set to "{}"'.format(WEBHOOK_URL))


@app.route('/hook', methods=['POST'])
def webhook_handler():
    update = telegram.Update.de_json(request.get_json(force=True), bot)
    machine.advance(update)
    if update.message.text == u"重新查詢":
        machine.go_back(update)
        bot.send_message(chat_id=update.message.chat_id,text = "請鍵入任意鍵繼續")
        print('go back')  
    return 'ok'

@app.route('/show-fsm', methods=['GET'])
def show_fsm():
    byte_io = BytesIO()
    machine.graph.draw(byte_io, prog='dot', format='png')
    byte_io.seek(0)
    return send_file(byte_io, attachment_filename='fsm.png', mimetype='image/png')


if __name__ == "__main__":
    _set_webhook()
    app.run()


