import random

def enum(**enums):
    return type('Enumerator', (), enums)

Ranks = enum(TWO=0, THREE=1, FOUR=2, FIVE=3, SIX=4, SEVEN=5, EIGHT=6,
            NINE=7, TEN=8, JACK=9, QUEEN=10, KING=11, ACE=12)
Suits = enum(CLUBS=0, DIAMONDS=1, HEARTS=2, SPADES=3)

class Card:
    def __init__(self, rank=None, suit=None):
        self.rank = rank
        self.suit = suit


class Deck:
    def __init__(self):
        self.cards = []
        ranks = range(13)
        suits = [Suits.CLUBS, Suits.DIAMONDS, Suits.HEARTS, Suits.SPADES]
        #initialize the full set of playing cards
        for r in ranks:
            for s in suits:
                self.cards.append(Card(r, s))

    def draw_card(self):
        card =  random.choice(self.cards)
        self.cards.remove(card)
        return card


class Player:
    DEF_BALANCE = 10000

    def __init__(self, balance=DEF_BALANCE):
        self.card1 = Card()
        self.card2 = Card()
        self.bid = 0
        self.balance = balance
        self.folded = False
        self.bankrupt = False


class HoldemGame:
    BASE_BID = 0

    def __init__(self):
        self.deck = Deck()
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
        self.deck = Deck()
        for p in self.players:
            p.card1 = Card()
            p.card2 = Card()
            p.bid = 0
            p.folded = False
            p.bankrupt = False
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
        #rotate dealer
        self.dealer = self.players[0]
        self.__next_player()

    def __resolve_game(self):
        self.finished = True
        print "Game Complete!"
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
                player.bid += player.balance
                player.balance = 0
                self.players_left -= 1 #the player can't make moves until next round
                player.bankrupt = True
            else:
                self.pot += self.bid - player.bid
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
            #TODO: make player actually win the pot
            print "Some player won because some player folded!"
            self.__resolve_game()
            self.__next_player()
            return True
        if not self.__end_move():
            self.__next_player()
        return True
