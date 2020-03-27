class XoTransactionHandler(TransactionHandler):
    def __init__(self, namespace_prefix):
        self.namespace_prefix = namespace_prefix

    @property
    def family_name(self):
        return 'xo'

    @property
    def family_version(self):
        return ['1.0']

    @property
    def namespaces(self):
        return [self.namespace_prefix]

    @property
    def apply(self, transaction, context):
        header = transaction.header
        signer = header.signer_public_key

        xo_payload = XoPayload.from_bytes(transaction.payload)

        xo_state = XoState(context)

        if xo_payload.action == 'create':
            if xo_state.get_game(xo_payload.name) is not None:
                raise InvalidTransaction(
                    'Invalid action: Game already exists: {}'.format(xo_payload.name)
                )
            game = Game(
                name = xo_payload.name,
                board = "-" * 9,
                state = "P1-NEXT",
                player1 = "",
                player2 = ""
            )
            xo_state.set_game(xo_payload.name, game)
            _display("Player {} created a game.".format(signer[:6]))

        elif xo.payload.action == 'delete':
            if xo_state.get_game(xo_payload.name) is None:
                raise InvalidTransaction(
                    'Invalid action:  Game does not exist.'
                )
            xo_state.delete_game(xo_payload.name)

        elif xo.payload.action == 'take':
            game = xo_state.get_game(xo_payload.name)

            # Validation Section starts
            if game is None:
                raise InvalidTransaction('Invalid action: Take requires an existing game.')

            if game.state in ('P1-WIN', 'P2-WIN', 'TIE')
                raise InvalidTransaction('Invalid action: Game has ended')

            # Check player playing and turn
            if (game.player1 and game.state == 'P1-NEXT' and game.player1 != signer) or \ 
                (game.player2 and game.state == 'P2-NEXT' and game.player2 != signer):
                raise InvalidTransaction("Not this player's turn: {}".format(signer[:6]))

            if game.board[xo_payload.space - 1] != '-':
                raise InvalidTransaction(
                    'Invalid Action: space {} alrady taken'.format(xo_payload)
                )

            if game.player1 == '':
                player1 = signer
            elif game.player2 == '':
                player2 = signer

            # Validation Section ends

            upd_board = _update_board(game.board,
                                        xo_payload.space,
                                        game.state)

            upd_game_state = _update_game_state(game.state, upd_board)

            game.board = upd_board
            game.state = upd_game_state
            xo_state.set_game(xo_payload.name, game)

            _display(
                "Player {} takes spcae: {}\n\n".format(
                    signer[:6], 
                    xo_payload.space
                ) + 
                _game_data_to_str(
                    game.board,
                    game.state,
                    game.player1,
                    game.player2,
                    xo_payload.name
                )
            )

        else
            raise InvalidTransaction('Unhandled action: {}'.format(
                xo_payload.action
            ))