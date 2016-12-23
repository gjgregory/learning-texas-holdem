import random

class Card:
    def __init__(self, rank, suit, img_path):
        self.rank = rank
        self.suit = suit
        self.img_path = img_path


class Deck:
    def __init__(self):
        self.cards = []
        ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'jack', 'queen', 'king', 'ace']
        suits = ['clubs', 'diamonds', 'hearts', 'spades']

        for r in ranks:
            for s in suits:
                self.cards.append(Card(r, s, 'art_assets/'+r+'_of_'+s+'.png'))


    def draw_card(self):
        card =  random.choice(self.cards)
        self.cards.remove(card)
        return card
