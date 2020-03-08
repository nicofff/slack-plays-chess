import chess
import chess.svg
import os
import slack
from cairosvg import svg2png

board = chess.Board()


@slack.RTMClient.run_on(event='message')
def say_hello(**payload):
    data = payload['data']
    web_client = payload['web_client']
    rtm_client = payload['rtm_client']
    channel_id = data['channel']
    if data.get('text', []) == "status":
        svg = chess.svg.board(
            board=board,
            lastmove=board.peek() if board.move_stack != [] else None
        )
        svg2png(bytestring=svg,write_to='board.png')

        web_client.files_upload(
            channels=channel_id,
            file="board.png",
            title="Current Board",
        )
    elif data.get('text', []) == "clear":
        board.clear()

        web_client.chat_postMessage(
            channel=channel_id,
            text=f"Starting a new game!",
        )

    elif data.get('text', []).startswith('move'):
        move = data.get('text', []).split(" ")[1]
        who_moves = "white" if board.turn == chess.WHITE else "black"

        try:
            board.parse_san(move) # This throws if not legal
            board.push_san(move)
            web_client.chat_postMessage(
                channel=channel_id,
                text=f"{who_moves} plays {move}!",
            )
        except ValueError as e:
            print(e)
            web_client.chat_postMessage(
                channel=channel_id,
                text=f"Illegal Move for {who_moves}!",
            )
    elif data.get('text', []) == "help":
        board.clear()

        web_client.chat_postMessage(
            channel=channel_id,
            text="""Say `status` for current game status
            Say `move SAN` to make a move. Eg: move e4
            """,
        )



slack_token = os.environ["SLACK_API_TOKEN"]
rtm_client = slack.RTMClient(token=slack_token)
rtm_client.start()
