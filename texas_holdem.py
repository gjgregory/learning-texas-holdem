import random

def enum(**enums):
    return type('Enumerator', (), enums)

Ranks = enum(TWO=0, THREE=1, FOUR=2, FIVE=3, SIX=4, SEVEN=5, EIGHT=6,
            NINE=7, TEN=8, JACK=9, QUEEN=10, KING=11, ACE=12)
Suits = enum(CLUBS=0, DIAMONDS=1, HEARTS=2, SPADES=3)
Hands = enum(HIGH_CARD=0, PAIR=1, TWO_PAIR=2, THREE_OF_A_KIND=3, STRAIGHT=4,
            FLUSH=5, FULL_HOUSE=6, FOUR_OF_A_KIND=7, STRAIGHT_FLUSH=8, ROYAL_FLUSH=9)
TiebreakerTypes = enum(NONE=0, HIGH_CARD=1, KICKER=2)

class Card:
    def __init__(self, rank=None, suit=None):
        self.rank = rank
        self.suit = suit


class Deck:
    def __init__(self, num_decks):
        self.cards = []
        ranks = range(13)
        suits = range(4)
        #initialize the full set of playing cards
        for _ in range(num_decks):
            for r in ranks:
                for s in suits:
                    self.cards.append(Card(r, s))

    def draw_card(self):
        card =  random.choice(self.cards)
        self.cards.remove(card)
        return card


class Player:
    DEF_BALANCE = 10000

    def __init__(self, name, balance=DEF_BALANCE):
        self.name = name
        self.card1 = Card()
        self.card2 = Card()
        self.bid = 0
        self.in_pot = 0
        self.balance = balance
        self.folded = False
        self.bankrupt = False
        self.hand = 0
        self.kickers = []


class HoldemGame:
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

    def __next_player(self):
        #next player to have a turn is always at index 0
        temp = self.players.pop(0)
        self.players.append(temp)
        while self.players[0].folded or self.players[0].bankrupt:
            temp = self.players.pop(0)
            self.players.append(temp)

    def add_player(self, player):
        self.players.append(player)

    def deal(self):
        #deal one card at a time, as per standard poker rules (pointless, i know)
        for p in self.players:
            if p.folded == False:
                p.card1 = self.deck.draw_card()
        for p in self.players:
            if p.folded == False:
                p.card2 = self.deck.draw_card()

    def shuffle(self):
        #reset cards
        self.deck = Deck(self.num_decks)
        for p in self.players:
            p.card1 = Card()
            p.card2 = Card()
            p.bid = 0
            p.in_pot = 0
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
        self.__next_player()

    def __is_straight(self, player, card_ranks, regular, royal):
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

    def __set_player_hand(self, player, card_ranks, card_suits, rank_counts, suit_counts):
        #ROYAL/STRAIGHT FLUSH
        if 5 in suit_counts or 6 in suit_counts or 7 in suit_counts:
            #separate cards that are part of the flush
            flush_suit = suit_counts.index(max(suit_counts))
            flush_hand = []
            for i in range(7):
                if card_suits[i] == flush_suit:
                    flush_hand.append(card_ranks[i])
            #ROYAL FLUSH
            if self.__is_straight(player, flush_hand, 0, 1):
                player.hand = Hands.ROYAL_FLUSH
                return
            #STRAIGHT_FLUSH
            elif self.__is_straight(player, flush_hand, 1, 0):
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
        elif self.__is_straight(player, card_ranks, 1, 1):
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

    def __set_winners(self):
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

    def __resolve_winnings(self):
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

                self.__set_player_hand(p, card_ranks, card_suits, rank_counts, suit_counts)

            self.__set_winners()

        num_winners = len(self.winners)
        for p in self.winners:
            p.balance += self.pot / num_winners

    def __resolve_game(self):
        self.finished = True
        print "Game Complete!"
        self.__resolve_winnings()
        #reset next player after dealer to first
        while self.players[0] != self.dealer:
            temp = self.players.pop(0)
            self.players.append(temp)
        temp = self.players.pop(0)
        self.players.append(temp)

    def __resolve_game_abrupt(self):
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
        self.__resolve_game()

    def __process_round(self):
        self.movecounter = self.players_left #reset number of non-volatile moves to be performed.
        #reset bid numbers for new round
        for p in self.players:
            p.bid = 0
        self.bid = 0
        self.lastraise = 0
        #before dealing
        if self.players[0].card1.rank is None:
            self.deal()
        #after dealing
        elif not self.finished:
            if self.card5.rank is None:
                self.deck.draw_card() #burn one as per standard poker rules (pointless, i know)
            #draw cards according to game progress
            if self.card1.rank is None:
                self.card1 = self.deck.draw_card()
                self.card2 = self.deck.draw_card()
                self.card3 = self.deck.draw_card()
            elif self.card4.rank is None:
                self.card4 = self.deck.draw_card()
            elif self.card5.rank is None:
                self.card5 = self.deck.draw_card()
            else:
                self.__resolve_game()
                #TODO: resolve hand comparisons, reset queue and increment dealer
                #...
                #reset next player after dealer to first
                return
        #reset next non-folded player after dealer to first
        while self.players[0] != self.dealer:
            temp = self.players.pop(0)
            self.players.append(temp)
        self.__next_player()

    def is_next(self, player):
        if self.players[0] == player:
            return True
        else:
            return False

    def __end_move(self):
        if self.players_left == 0:
            self.__resolve_game_abrupt()
            for p in self.players:
                p.bankrupt = False
        elif self.movecounter == 0:
            self.__process_round()
            return True
        return False

    def make_bid(self, player, amount):
        #check if bid/raise is actually a call
        if amount == 0:
            return self.call(player)
        #check if it's the player's turn
        if not self.is_next(player):
            print "it's not the player's turn yet"
            return False
        #check if player's balance is too low or bid isn't high enough
        amount = min(player.balance, amount)
        if amount < self.lastraise and amount != player.balance:
            print "invalid bid. try again."
            return False
        else:
            self.movecounter = self.players_left #reset number of non-volatile moves to be performed.
            self.movecounter -= 1 #this move counts whether volatile or not
            if self.lastraise < amount:
                self.lastraise = amount
            self.bid += amount
            self.pot += self.bid - player.bid
            player.in_pot += self.bid - player.bid
            player.balance -= self.bid - player.bid
            player.bid = self.bid
            #player went all in
            if player.balance == 0:
                self.players_left -= 1 #the player can't make moves until next round
                player.bankrupt = True
            #turn is over. ready next player's turn.
            if not self.__end_move():
                self.__next_player()
            return True

    def call(self, player):
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
                player.in_pot += player.balance
                player.bid += player.balance
                player.balance = 0
                self.players_left -= 1 #the player can't make moves until next round
                player.bankrupt = True
            else:
                self.pot += self.bid - player.bid
                player.in_pot += self.bid - player.bid
                player.balance -= self.bid - player.bid
                player.bid = self.bid
            self.movecounter -= 1 #this is a non-volatile move
            #turn is over. ready next player's turn.
            if not self.__end_move():
                self.__next_player()
            return True

    def check(self, player):
        #check if it's the player's turn
        if not self.is_next(player):
            print "it's not the player's turn yet"
            return False
        if player.bid < self.bid:
            print "player can't check right now."
            return False
        else:
            self.movecounter -= 1 #this is a non-volatile move
            #turn is over. ready next player's turn.
            if not self.__end_move():
                self.__next_player()
            return True

    def fold(self, player):
        #check if it's the player's turn
        if not self.is_next(player):
            print "it's not the player's turn yet"
            return False
        self.movecounter -= 1 #this is a non-volatile move
        self.players_left -= 1 #the player can't make moves until next round
        player.folded = True
        #turn is over. ready next player's turn.
        if self.players_left == 1:
            self.everyone_folded = True
            self.__resolve_game()
            return True
        if not self.__end_move():
            self.__next_player()
        return True
