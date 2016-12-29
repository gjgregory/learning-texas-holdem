import random

class Card:
    def __init__(self, rank=None, suit=None, img_path='art_assets/black_joker.png'):
        self.rank = rank
        self.suit = suit
        self.img_path = img_path


class Deck:
    def __init__(self):
        self.cards = []
        ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'jack', 'queen', 'king', 'ace']
        suits = ['clubs', 'diamonds', 'hearts', 'spades']
        #initialize the full set of playing cards
        for r in ranks:
            for s in suits:
                self.cards.append(Card(r, s, 'art_assets/'+r+'_of_'+s+'.png'))

    def draw_card(self):
        card =  random.choice(self.cards)
        self.cards.remove(card)
        return card


class Player:
    def __init__(self, balance=10000):
        self.card1 = Card()
        self.card2 = Card()
        self.bid = 0
        self.balance = balance
        self.folded = False


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
        self.players = []
        self.dealer = None
        self.movecounter = 0
        self.movetotal = 0

    def __next_player(self):
        #next player to have a turn is always at index 0
        temp = self.players.pop(0)
        self.players.append(temp)
        while self.players[0].folded:
            temp = self.players.pop(0)
            self.players.append(temp)

    def add_player(self, player):
        self.players.append(player)

    def deal(self):
        #deal one card at a time, as per standard poker rules (pointless, i know)
        for p in self.players:
            p.card1 = self.deck.draw_card()
        for p in self.players:
            p.card2 = self.deck.draw_card()

    def shuffle(self):
        #reset cards
        self.deck = Deck()
        for p in self.players:
            p.card1 = Card()
            p.card2 = Card()
            p.bid = 0
            p.folded = False
        self.card1 = Card()
        self.card2 = Card()
        self.card3 = Card()
        self.card4 = Card()
        self.card5 = Card()
        self.bid = self.BASE_BID
        self.pot = 0
        self.movecounter = len(self.players)
        self.movetotal = len(self.players)
        #rotate dealer
        self.dealer = self.players[0]
        self.__next_player()

    def __process_round(self):
        self.movecounter = self.movetotal #reset number of non-volatile moves to be performed.
        if self.card5.rank is None: self.deck.draw_card() #burn one as per standard poker rules (pointless, i know)
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
            print "all cards are already revealed."
            #TODO: resolve hand comparisons, reset queue and increment dealer
            #...
            #reset next player after dealer to first
            while self.players[-1] != self.dealer:
                temp = self.players.pop(0)
                self.players.append(temp)
            temp = self.players.pop(0)
            self.players.append(temp)
            return
        #reset next non-folded player after dealer to first
        while self.players[-1] != self.dealer:
            temp = self.players.pop(0)
            self.players.append(temp)
        self.__next_player()


    def is_next(self, player):
        if self.players[0] == player:
            return True
        else:
            return False

    def make_bid(self, player, amount):
        #check if it's the player's turn
        if not self.is_next(player):
            print "it's not the player's turn yet"
            return False
        #check if player's balance is too low or bid isn't high enough
        if player.balance < (amount - player.bid) or self.bid > amount:
            print "invalid bid. try again."
            return False
        else:
            if amount > self.bid:
                self.movecounter = self.movetotal #reset number of non-volatile moves to be performed.
            self.movecounter -= 1 #this move counts whether volatile or not
            self.bid = amount
            player.balance -= (amount - player.bid)
            self.pot += (amount - player.bid)
            player.bid = amount
            #turn is over. ready next player's turn.
            self.__next_player()
            if self.movecounter == 0:
                self.__process_round()
            return True

    def call(self, player):
        #check if it's the player's turn
        if not self.is_next(player):
            print "it's not the player's turn yet"
            return False
        #check if player's balance is too low
        if player.balance < (self.bid - player.bid):
            print "player doesn't have enough money to call."
            return False
        else:
            self.movecounter -= 1 #this is a non-volatile move
            player.balance -= (self.bid - player.bid)
            self.pot += (self.bid - player.bid)
            player.bid = self.bid
            #turn is over. ready next player's turn.
            self.__next_player()
            if self.movecounter == 0:
                self.__process_round()
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
            self.__next_player()
            if self.movecounter == 0:
                self.__process_round()
            return True

    def fold(self, player):
        #check if it's the player's turn
        if not self.is_next(player):
            print "it's not the player's turn yet"
            return False
        self.movecounter -= 1 #this is a non-volatile move
        self.movetotal -= 1 #the player can't make moves until next round
        player.folded = True
        #turn is over. ready next player's turn.
        self.__next_player()
        if self.movecounter == 0:
            self.__process_round()
