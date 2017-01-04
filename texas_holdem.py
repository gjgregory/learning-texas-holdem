"""
Texas Hold'em Game API (texas_holdem)

Author: Garrett Gregory

Description:
    This module provides an object-oriented Texas Hold'em game implementation. It should
    be noted that it has been designed for an arbitrary number of players and combined
    decks, but ignores the "split pot" concept.

Attributes:
    Ranks (enum): Enumerates card ranks
    Suits (enum): Enumerates card suits
    Hands (enum): Enumerates hand types
"""

import random

def _enum(**enums):
    return type('Enumerator', (), enums)

Ranks = _enum(TWO=0, THREE=1, FOUR=2, FIVE=3, SIX=4, SEVEN=5, EIGHT=6,
            NINE=7, TEN=8, JACK=9, QUEEN=10, KING=11, ACE=12)
Suits = _enum(CLUBS=0, DIAMONDS=1, HEARTS=2, SPADES=3)
Hands = _enum(HIGH_CARD=0, PAIR=1, TWO_PAIR=2, THREE_OF_A_KIND=3, STRAIGHT=4,
            FLUSH=5, FULL_HOUSE=6, FOUR_OF_A_KIND=7, STRAIGHT_FLUSH=8, ROYAL_FLUSH=9)

class Card:
    """
    Card objects hold basic information to be identified by.

    Note:
        Use Ranks/Suits enums for args.

    Args:
        rank (int): Card rank
        suit (int): Card suit

    Attributes:
        rank (int): Card rank
        suit (int): Card suit
    """
    def __init__(self, rank=None, suit=None):
        self.rank = rank
        self.suit = suit


class Deck:
    """
    Deck objects hold a specified amount of sets of Card objects.

    Note:
        Default is 1 deck's worth (52 cards)

    Args:
        rank (int, optional): Number of 52-card sets to initialize

    Attributes:
        _cards (Card[]): List of Card objects remaining in the deck
    """
    def __init__(self, num_decks):
        self._cards = []
        ranks = range(13)
        suits = range(4)
        #initialize the full set of playing cards
        for _ in range(num_decks):
            for r in ranks:
                for s in suits:
                    self._cards.append(Card(r, s))

    def draw_card(self):
        card =  random.choice(self._cards)
        self._cards.remove(card)
        return card


class Player:
    """
    Player object is owned by the game.

        The Player attributes both identify the player itself and
        track its current money state in the game.

    Note:
        Hand attribute is always set to a Hands enum.

    Args:
        name (string): Plaintext name for the player
        balance(int, optional): Initial amount of money alotted to the player

    Attributes:
        name (string): Plaintext name for the player
        card1 (Card): First card in the player's hand
        card2 (Card): Second card in the player's hand
        bid (int): Amount of money the player has bid in the current round of bidding
        balance (int): Amount of money the player has left
        folded (boolean): Denotes whether or not the player has folded
        bankrupt (boolean): Denotes whether or not the player has gone bankrupt
        hand (int): Type of hand the player has at end of game
        kickers (int[]): List of ranks of cards used case of tiebreaker at end of game
    """
    DEF_BALANCE = 10000

    def __init__(self, name, balance=DEF_BALANCE):
        self.name = name
        self.card1 = Card()
        self.card2 = Card()
        self.bid = 0
        self.balance = balance
        self.folded = False
        self.bankrupt = False
        self.hand = 0
        self.kickers = []


class HoldemGame:
    """
    Texas Hold'em game instance

    Note:
        Players must be instantiated separately and added to game.

    Args:
        num_decks (int): Number of 52-card sets to be initialized in Deck object

    Attributes:
        deck (Deck): Deck of cards to be drawn from for the current game
        num_decks (int): Number of 52-card sets to be initialized in Deck object
        card1 (Card): First card in the 5-card flop
        card2 (Card): Second card in the 5-card flop
        card3 (Card): Third card in the 5-card flop
        card4 (Card): Fourth card in the 5-card flop
        card5 (Card): Fifth card in the 5-card flop
        pot (int): Amount of money currently in the pot
        bid (int): Current highest bid from any player
        lastraise (int): Last amount the bid was raised by
        players (Player[]): List of all players in the game
        dealer (Player): Current dealer
        movecounter (int): Tracks how many non-volatile moves left in round
        players_left (int): Tracks how many players haven't folded/bankrupted
        winners (Player[]): List of players who win the pot at end of game
        tiebreaker (boolean): Denotes whether or not a tiebreaker was used to decide winner(s)
        tiebreaker_value (int): Card rank that broke a tie, if there was one
        everyone_folded (boolean): Denotes whether or not all except one player has folded
    """
    BASE_BID = 0
    DEF_NUM_DECKS = 1

    def __init__(self, num_decks=DEF_NUM_DECKS):
        self.deck = Deck(num_decks)
        self.num_decks = num_decks
        self.card1 = Card()
        self.card2 = Card()
        self.card3 = Card()
        self.card4 = Card()
        self.card5 = Card()
        self.pot = 0
        self.bid = self.BASE_BID
        self.lastraise = 0
        self.players = []
        self.dealer = None
        self.movecounter = 0
        self.players_left = 0
        self.finished = False
        self.winners = []
        self.tiebreaker = False
        self.tiebreaker_value = 0
        self.everyone_folded = False

    def _next_player(self):
        """
        Helper function to rotate the players queue until it reaches the
        next player who is still able to make moves.
        """
        #next player to have a turn is always at index 0
        temp = self.players.pop(0)
        self.players.append(temp)
        while self.players[0].folded or self.players[0].bankrupt:
            temp = self.players.pop(0)
            self.players.append(temp)

    def _is_straight(self, player, card_ranks, regular, royal):
        """
        Helper function used by _set_player_hand() to generate kickers for
        any hand that is considered to have a straight.
        """
        #royal and regular must be 0 or 1, denoting the range of straights to check for
        for i in range(Ranks.NINE+royal, Ranks.NINE-(8*regular), -1):
            if (i in card_ranks and i+1 in card_ranks and i+2 in card_ranks and
                        i+3 in card_ranks and i+4 in card_ranks):
                player.kickers.append(i+4)
                return True
        if (regular and Ranks.ACE in card_ranks and Ranks.TWO in card_ranks and Ranks.THREE
                    in card_ranks and Ranks.FOUR in card_ranks and Ranks.FIVE in card_ranks):
            player.kickers.append(Ranks.FIVE)
            return True
        return False

    def _set_player_hand(self, player, card_ranks, card_suits, rank_counts, suit_counts):
        """
        Helper function used by _resolve_winnings() to determine the player's hand strength
        and generate kickers to be used as potential tiebreakers.
        """
        #ROYAL/STRAIGHT FLUSH
        if 5 in suit_counts or 6 in suit_counts or 7 in suit_counts:
            #separate cards that are part of the flush
            flush_suit = suit_counts.index(max(suit_counts))
            flush_hand = []
            for i in range(7):
                if card_suits[i] == flush_suit:
                    flush_hand.append(card_ranks[i])
            #ROYAL FLUSH
            if self._is_straight(player, flush_hand, 0, 1):
                player.hand = Hands.ROYAL_FLUSH
                return
            #STRAIGHT_FLUSH
            elif self._is_straight(player, flush_hand, 1, 0):
                player.hand = Hands.STRAIGHT_FLUSH
                return
        #FOUR OF A KIND
        if 4 in rank_counts or 5 in rank_counts or 6 in rank_counts or 7 in rank_counts:
            player.hand = Hands.FOUR_OF_A_KIND
            while len(player.kickers) < 5:
                temp = rank_counts.index(max(rank_counts))
                if temp in card_ranks:
                    player.kickers.append(temp)
                    card_ranks.remove(temp)
                else:
                    player.kickers.append(max(card_ranks))
        #FULL HOUSE
        elif (2 in rank_counts and 3 in rank_counts) or rank_counts.count(3) == 2:
            player.hand = Hands.FULL_HOUSE
            while len(player.kickers) < 5 and 3 in rank_counts:
                temp = len(rank_counts)-1 - rank_counts[::-1].index(3) #get index of last 3
                while len(player.kickers) < 5 and temp in card_ranks:
                    player.kickers.append(temp)
                    card_ranks.remove(temp)
                rank_counts[temp] = 0
            while len(player.kickers) < 5:
                temp = rank_counts.index(2)
                while temp in card_ranks:
                    player.kickers.append(temp)
                    card_ranks.remove(temp)
        #FLUSH
        elif 5 in suit_counts or 6 in suit_counts or 7 in suit_counts:
            player.hand = Hands.FLUSH
            #separate cards that are part of the flush
            flush_suit = suit_counts.index(max(suit_counts))
            flush_hand = []
            for i in range(7):
                if card_suits[i] == flush_suit:
                    flush_hand.append(card_ranks[i])
            for _ in range(5):
                temp = max(flush_hand)
                player.kickers.append(temp)
                flush_hand.remove(temp)
        #STRAIGHT
        elif self._is_straight(player, card_ranks, 1, 1):
            player.hand = Hands.STRAIGHT
        #THREE OF A KIND
        elif 3 in rank_counts:
            player.hand = Hands.THREE_OF_A_KIND
            temp = rank_counts.index(3)
            for _ in range(3):
                player.kickers.append(temp)
                card_ranks.remove(temp)
            for _ in range(2):
                temp = max(card_ranks)
                player.kickers.append(temp)
                card_ranks.remove(temp)
        #TWO PAIR
        elif rank_counts.count(2) >= 2:
            player.hand = Hands.TWO_PAIR
            while len(player.kickers) < 4 and 2 in rank_counts:
                temp = len(rank_counts)-1 - rank_counts[::-1].index(2) #get index of last 2
                while temp in card_ranks:
                    player.kickers.append(temp)
                    card_ranks.remove(temp)
                rank_counts[temp] = 0
            player.kickers.append(max(card_ranks))
        #PAIR
        elif 2 in rank_counts:
            player.hand = Hands.PAIR
            temp = rank_counts.index(2)
            for _ in range(2):
                player.kickers.append(temp)
                card_ranks.remove(temp)
            for _ in range(3):
                temp = max(card_ranks)
                player.kickers.append(temp)
                card_ranks.remove(temp)
        #HIGH CARD
        else:
            player.hand = Hands.HIGH_CARD
            for _ in range(5):
                temp = max(card_ranks)
                player.kickers.append(temp)
                card_ranks.remove(temp)

    def _set_winners(self):
        """
        Helper function used by _resolve_winnings() to determine which player(s)
        win the current game and get the money in the pot.
        """
        self.winners = []
        tiebreakers = []
        for p in self.players:
            tiebreakers.append(p.hand)
        maxval = max(tiebreakers)
        for p in self.players:
            if p.hand == maxval:
                self.winners.append(p)
        if len(self.winners) == 1:
            self.tiebreaker = False
            return
        kicker_count = len(self.winners[0].kickers)
        for i in range(kicker_count):
            tiebreakers = []
            for p in self.winners:
                tiebreakers.append(p.kickers[i])
            maxval = max(tiebreakers)
            for p in self.winners:
                if p.kickers[i] < maxval:
                    self.winners.remove(p)
            if len(self.winners) == 1:
                self.tiebreaker = True
                self.tiebreaker_value = maxval
                return
        self.tiebreaker = False
        return

    def _resolve_winnings(self):
        """
        Helper function used by _resolve_game() to perform end-of-game resolutions.
        """
        if self.everyone_folded:
            for p in self.players:
                if not p.folded:
                    self.winners.append(p)
                    break
        else:
            for p in self.players:
                #cumulate hand values
                card_ranks = [p.card1.rank, p.card2.rank, self.card1.rank, self.card2.rank,
                                    self.card3.rank, self.card4.rank, self.card5.rank]
                card_suits = [p.card1.suit, p.card2.suit, self.card1.suit, self.card2.suit,
                                    self.card3.suit, self.card4.suit, self.card5.suit]
                rank_counts = [card_ranks.count(Ranks.TWO), card_ranks.count(Ranks.THREE), card_ranks.count(Ranks.FOUR),
                                card_ranks.count(Ranks.FIVE), card_ranks.count(Ranks.SIX), card_ranks.count(Ranks.SEVEN),
                                card_ranks.count(Ranks.EIGHT), card_ranks.count(Ranks.NINE), card_ranks.count(Ranks.TEN),
                                card_ranks.count(Ranks.JACK), card_ranks.count(Ranks.QUEEN), card_ranks.count(Ranks.KING),
                                card_ranks.count(Ranks.ACE)]
                suit_counts = [card_suits.count(Suits.CLUBS), card_suits.count(Suits.DIAMONDS), card_suits.count(Suits.HEARTS),
                                card_suits.count(Suits.SPADES)]

                self._set_player_hand(p, card_ranks, card_suits, rank_counts, suit_counts)
            self._set_winners()
        num_winners = len(self.winners)
        for p in self.winners:
            p.balance += self.pot / num_winners

    def _resolve_game(self):
        """
        Helper function used to end the current game and set the next player after dealer to
        take an action next.
        """
        self.finished = True
        self._resolve_winnings()
        #reset next player after dealer to first
        while self.players[0] != self.dealer:
            temp = self.players.pop(0)
            self.players.append(temp)
        temp = self.players.pop(0)
        self.players.append(temp)

    def _resolve_game_abrupt(self):
        """
        Helper function used to draw all cards without actions being taken and end the game, in the
        situation where all or all but one player has folded/brankrupted.
        """
        if self.players[0].card1.rank is None:
            self.deal()
        if self.card1.rank is None:
            self.deck.draw_card() #burn one as per standard poker rules (pointless, i know)
            self.card1 = self.deck.draw_card()
            self.card2 = self.deck.draw_card()
            self.card3 = self.deck.draw_card()
        if self.card4.rank is None:
            self.deck.draw_card() #burn one as per standard poker rules (pointless, i know)
            self.card4 = self.deck.draw_card()
        if self.card5.rank is None:
            self.deck.draw_card() #burn one as per standard poker rules (pointless, i know)
            self.card5 = self.deck.draw_card()
        self._resolve_game()

    def _process_round(self):
        """
        Helper function used to determine whether to reveal more cards in the flop or
        to end the game at the end of each round, then do so.
        """
        self.movecounter = self.players_left #reset number of non-volatile moves to be performed.
        #reset bid numbers for new round
        for p in self.players:
            p.bid = 0
        self.bid = 0
        self.lastraise = 0
        if self.players_left <= 1:
            #game should end before more turns are taken
            self._resolve_game_abrupt()
            return
        if self.players[0].card1.rank is None:
            #hands haven't been dealt yet
            self.deal()
        else:
            #draw cards or end game according to game progress
            if self.card5.rank is None:
                #burn one as per standard poker rules (pointless, i know)
                self.deck.draw_card()
            if self.card1.rank is None:
                self.card1 = self.deck.draw_card()
                self.card2 = self.deck.draw_card()
                self.card3 = self.deck.draw_card()
            elif self.card4.rank is None:
                self.card4 = self.deck.draw_card()
            elif self.card5.rank is None:
                self.card5 = self.deck.draw_card()
            else:
                self._resolve_game()
                return
        #reset next non-folded player after dealer to first
        while self.players[0] != self.dealer:
            temp = self.players.pop(0)
            self.players.append(temp)
        self._next_player()

    def _end_move(self):
        """
        Helper function used after a move to either end the current game abruptly
        or process the current round if necessary. Otherwise nothing will happen.
        """
        #no players have money left
        if self.players_left == 0:
            self._resolve_game_abrupt()
            for p in self.players:
                p.bankrupt = False
        elif self.movecounter == 0:
            self._process_round()
            return True
        return False

    def add_player(self, player):
        """
        Adds a Player object to the game.

        Args:
            player (Player): The Player object to be added
        """
        self.players.append(player)

    def deal(self):
        """Deals two cards to each player."""
        #deal one card at a time, as per standard poker rules (pointless, i know)
        for p in self.players:
            if p.folded == False:
                p.card1 = self.deck.draw_card()
        for p in self.players:
            if p.folded == False:
                p.card2 = self.deck.draw_card()

    def shuffle(self):
        """
        Gets the game ready for a new round.

        This includes resetting, the deck, all cards in player, game attributes,
        and rotating the dealer to the next player after them.
        """
        #reset cards
        self.deck = Deck(self.num_decks)
        for p in self.players:
            p.card1 = Card()
            p.card2 = Card()
            p.bid = 0
            p.folded = False
            p.bankrupt = False
            p.hand = 0
            p.kickers = []
            if p.balance == 0:
                p.balance = Player.DEF_BALANCE
        self.card1 = Card()
        self.card2 = Card()
        self.card3 = Card()
        self.card4 = Card()
        self.card5 = Card()
        self.bid = self.BASE_BID
        self.lastraise = 0
        self.pot = 0
        self.movecounter = len(self.players)
        self.players_left = len(self.players)
        self.finished = False
        self.everyone_folded = False
        self.winners = []
        #rotate dealer
        self.dealer = self.players[0]
        self._next_player()

    def is_next(self, player):
        """
        Checks if it's currently the Player object's turn.

        Args:
            player (Player): The player in question

        Returns:
            True if player is next, False otherwise.
        """
        if self.players[0] == player:
            return True
        else:
            return False

    def make_bid(self, player, amount):
        """
        Performs a raise or bid action for the specified player.

        If no one has bidded yet, this will be a bid action. Otherwise, it
        will be a raise action. This is considered the only volatile action.

        Args:
            player (Player): The player to perform the action
            amount (int): The amount of money to bid/raise

        Returns:
            True if successful, False otherwise.
        """
        #check if it's the player's turn
        if not self.is_next(player):
            print "it's not the player's turn yet"
            return False
        #check if bid/raise is actually a call
        if amount == 0:
            return self.call(player)
        #check if player's balance is too low or bid isn't high enough
        if amount < self.lastraise:
            print "invalid bid. try again."
            return False
        elif player.balance < amount + self.bid - player.bid:
            print "player needs more money to raise."
            return False
        else:
            self.movecounter = self.players_left #reset number of non-volatile moves to be performed.
            self.movecounter -= 1 #this move counts whether volatile or not
            if self.lastraise < amount:
                self.lastraise = amount
            self.bid += amount
            self.pot += self.bid - player.bid
            player.balance -= self.bid - player.bid
            player.bid = self.bid
            #player went all in
            if player.balance == 0:
                self.players_left -= 1 #the player can't make moves until next round
                player.bankrupt = True
            #turn is over. ready next player's turn.
            if not self._end_move():
                self._next_player()
            return True

    def call(self, player):
        """
        Performs a call action for the specified player.

        The player matches the current bid amount.

        Args:
            player (Player): The player to perform the action

        Returns:
            True if successful, False otherwise.
        """
        #check if it's the player's turn
        if not self.is_next(player):
            print "it's not the player's turn yet"
            return False
        elif player.bid == self.bid:
            print "player has already bid enough. checking instead."
            return self.check(player)
        else:
            #player went all in
            if player.balance <= self.bid - player.bid:
                print "player went all in!"
                self.pot += player.balance
                player.bid += player.balance
                player.balance = 0
                self.players_left -= 1 #the player can't make moves until next round
                player.bankrupt = True
            else:
                self.pot += self.bid - player.bid
                player.balance -= self.bid - player.bid
                player.bid = self.bid
            self.movecounter -= 1
            #turn is over. ready next player's turn.
            if not self._end_move():
                self._next_player()
            return True

    def check(self, player):
        """
        Performs a check action for the specified player.

        The player has bid enough and chooses not to increase their bid.

        Args:
            player (Player): The player to perform the action

        Returns:
            True if successful, False otherwise.
        """
        #check if it's the player's turn
        if not self.is_next(player):
            print "it's not the player's turn yet"
            return False
        if player.bid < self.bid:
            print "player can't check right now."
            return False
        else:
            self.movecounter -= 1
            #turn is over. ready next player's turn.
            if not self._end_move():
                self._next_player()
            return True

    def fold(self, player):
        """
        Performs a fold action for the specified player.

        The player is overwhelmed and opts out of the current game
        instead of matching the current bid.

        Args:
            player (Player): The player to perform the action

        Returns:
            True if successful, False otherwise.
        """
        #check if it's the player's turn
        if not self.is_next(player):
            print "it's not the player's turn yet"
            return False
        self.movecounter -= 1
        self.players_left -= 1
        player.folded = True
        #turn is over. ready next player's turn.
        if self.players_left == 1:
            self.everyone_folded = True
            self._resolve_game()
            return True
        if not self._end_move():
            self._next_player()
        return True
