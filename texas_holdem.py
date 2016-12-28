import random
from collections import deque

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

    def add_player(self, player):
        self.players.append(player)

    def deal(self):
        #deal one card at a time, as per standard poker rules (pointless, i know)
        for p in self.players:
            p.card1 = self.deck.draw_card()
        for p in self.players:
            p.card2 = self.deck.draw_card()

    def shuffle(self):
        self.deck = Deck()
        for p in self.players:
            p.card1 = Card()
            p.card2 = Card()
            p.bid = 0
            p.folded = False
        self.bid = self.BASE_BID
        #move first player to last turn (rotating queue)
        temp = self.players.pop(0)
        self.players.append(temp)

    def is_next(self, player):
        if self.players[0] == player:
            return True
        else:
            return False

    def make_bid(self, player, amount):
        #check if player's balance is too low or bid isn't high enough
        if player.balance < (amount - player.bid) or self.bid > amount:
            print "invalid bid. try again."
            return False
        else:
            self.bid = amount
            player.balance -= (amount - player.bid)
            self.pot += (amount - player.bid)
            player.bid = amount
            return True

    def call(self, player):
        #check if player's balance is too low
        if player.balance < (self.bid - player.bid):
            print "player doesn't have enough money to call."
            return False
        else:
            player.balance -= (self.bid - player.bid)
            self.pot += (self.bid - player.bid)
            player.bid = self.bid
            return True

    def check(self, player):
        return True

    def fold(self, player):
        player.folded = True
