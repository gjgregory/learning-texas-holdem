#!/usr/bin/env python

import pygtk
pygtk.require('2.0')
import gtk
import texas_holdem
import locale
import pango
import random


FACE_DOWN = 'art_assets/black_joker.png'
SEA_GREEN = gtk.gdk.Color(0.18, 0.55, 0.34)
DARK_SLATE_BLUE = gtk.gdk.Color(0.28, 0.24, 0.55)
GHOST_WHITE = gtk.gdk.Color(0.97, 0.97, 1.0)
FIREBRICK = gtk.gdk.Color(0.7, 0.13, 0.13)
PERU = gtk.gdk.Color(0.8, 0.52, 0.25)
ROYAL_BLUE = gtk.gdk.Color(0.25, 0.41, 0.88)
FOREST_GREEN = gtk.gdk.Color(0.13, 0.55, 0.13)
SALOON_BROWN = gtk.gdk.Color(0.28, 0.14, 0.04)
DARK_SLATE_GRAY = gtk.gdk.Color(0.18, 0.31, 0.31)
BIG_FONT = pango.FontDescription('Monospace 14')
DEFAULT_FONT = pango.FontDescription('Monospace 10')

def enum(**enums):
    return type('Enumerator', (), enums)

RankStrings = {0:'2', 1:'3', 2:'4', 3:'5', 4:'6', 5:'7', 6:'8',
                7:'9', 8:'10', 9:'jack', 10:'queen', 11:'king', 12:'ace'}
SuitStrings = {0:'_of_clubs', 1:'_of_diamonds', 2:'_of_hearts', 3:'_of_spades'}

class PlayHoldem:

    def delete_event(self, widget, event, data=None):
        return False

    def destroy(self, widget, data=None):
        gtk.main_quit()

    def __setButton(self, widget, label, color):
        #change background color of widget (normal and mouseover)
        widget.modify_bg(gtk.STATE_NORMAL, color)
        widget.modify_bg(gtk.STATE_PRELIGHT, color)
        #set button caption and default size
        widget.set_label(label)
        widget.set_size_request(70, 70)
        widget.show()

    def __setCardImage(self, box, image, card):
        #get appropriate color/image
        if card.rank == None:
            color = DARK_SLATE_BLUE
            img_path = FACE_DOWN
        else:
            color = GHOST_WHITE
            img_path = 'art_assets/' + RankStrings[card.rank] + SuitStrings[card.suit] + '.png'
        #change background color of widget
        box.modify_bg(gtk.STATE_NORMAL, color)
        #assign (presumably transparent) image to widget
        pixbuf = gtk.gdk.pixbuf_new_from_file(img_path)
        scaled_pixbuf = pixbuf.scale_simple(100, 150, gtk.gdk.INTERP_BILINEAR)
        image.set_from_pixbuf(scaled_pixbuf)

    def __updateDisplay(self, update_cpu):
        self.__setCardImage(self.playercard1_box, self.playercard1, self.player.card1)
        self.__setCardImage(self.playercard2_box, self.playercard2, self.player.card2)

        self.__setCardImage(self.card1_box, self.card1, self.game.card1)
        self.__setCardImage(self.card2_box, self.card2, self.game.card2)
        self.__setCardImage(self.card3_box, self.card3, self.game.card3)
        self.__setCardImage(self.card4_box, self.card4, self.game.card4)
        self.__setCardImage(self.card5_box, self.card5, self.game.card5)

        if self.game.finished:
            self.__setText(self.prompt, self.__getWinnerMessage())
        self.layout.move(self.prompt, 325-int(self.prompt.get_buffer().get_char_count()*5.5), 0)
        self.__setText(self.potText, "Pot: $" + locale.format("%d", self.game.pot, grouping=True))
        self.layout.move(self.potText, 325-int(self.potText.get_buffer().get_char_count()*5.5), 40)
        self.__setText(self.cpuMoneyText, "CPU: $" + locale.format("%d", self.cpu.balance, grouping=True))
        self.layout.move(self.cpuMoneyText, 325-(self.cpuMoneyText.get_buffer().get_char_count()*4), 100)
        self.__setText(self.cpuBidText, "Bid: $" + locale.format("%d", self.cpu.in_pot, grouping=True))
        self.layout.move(self.cpuBidText, 325-(self.cpuBidText.get_buffer().get_char_count()*4), 120)
        self.__setText(self.playerMoneyText, "Player: $" + locale.format("%d", self.player.balance, grouping=True))
        self.layout.move(self.playerMoneyText, 325-(self.playerMoneyText.get_buffer().get_char_count()*4), 735)
        self.__setText(self.playerBidText, "Bid: $" + locale.format("%d", self.player.in_pot, grouping=True))
        self.layout.move(self.playerBidText, 325-(self.playerBidText.get_buffer().get_char_count()*4), 715)
        self.__setText(self.bidText, str(self.game.lastraise))


        if update_cpu:
            self.__setCardImage(self.cpucard1_box, self.cpucard1, self.cpu.card1)
            self.__setCardImage(self.cpucard2_box, self.cpucard2, self.cpu.card2)

        #deactivate buttons if moves shouldn't be performed
        if self.player.bid < self.game.bid:
            self.buttonCheck.set_sensitive(False)
            self.buttonCall.set_sensitive(True)
        else:
            self.buttonCheck.set_sensitive(True)
            self.buttonCall.set_sensitive(False)

    def __setText(self, widget, text):
        buf = widget.get_buffer()
        buf.set_text(text)
        widget.set_buffer(buf)
        widget.show()

    def __clickShuffle(self, opt):
        self.__setText(self.prompt, self.cpu.name + " dealt.")
        self.game.shuffle()
        self.buttonShuffle.hide()
        self.__toggleInterface(True)
        self.__updateDisplay(True)
        if self.game.is_next(self.cpu):
            self.__cpuMove()

    def __toggleInterface(self, show):
        self.bidText.set_sensitive(show)
        self.buttonFold.set_sensitive(show)
        self.buttonCheck.set_sensitive(show)
        self.buttonCall.set_sensitive(show)
        self.buttonRaiseBid.set_sensitive(show)
        if not show:
            self.buttonShuffle.show()

    def __getWinnerMessage(self):
        if self.game.everyone_folded:
            message = self.game.winners[0].name + " wins $" \
                    + locale.format("%d", self.game.pot, grouping=True) + " for not folding!"
        else:
            if len(self.game.winners) == 1:
                message = self.game.winners[0].name + " wins $" \
                        + locale.format("%d", self.game.pot, grouping=True) + " with a "
            else:
                message = "Tie game! Both players win $" \
                        + locale.format("%d", self.game.pot/2, grouping=True) + " with an equal "
            winType = self.game.winners[0].hand
            if winType == texas_holdem.Hands.HIGH_CARD:
                message += "HIGH CARD."
            elif winType == texas_holdem.Hands.PAIR:
                message += "PAIR."
            elif winType == texas_holdem.Hands.TWO_PAIR:
                message += "TWO PAIR."
            elif winType == texas_holdem.Hands.THREE_OF_A_KIND:
                message += "THREE OF A KIND"
            elif winType == texas_holdem.Hands.STRAIGHT:
                message += "STRAIGHT."
            elif winType == texas_holdem.Hands.FLUSH:
                message += "FLUSH."
            elif winType == texas_holdem.Hands.FULL_HOUSE:
                message += "FULL HOUSE."
            elif winType == texas_holdem.Hands.FOUR_OF_A_KIND:
                message += "FOUR OF A KIND."
            elif winType == texas_holdem.Hands.STRAIGHT_FLUSH:
                message += "STRAIGHT FLUSH."
            elif winType == texas_holdem.Hands.ROYAL_FLUSH:
                message += "ROYAL FLUSH."
            if self.game.tiebreaker:
                cardRank = self.game.tiebreaker_value
                if cardRank == texas_holdem.Ranks.TWO:
                    message += " (TWO tiebreaker)"
                elif cardRank == texas_holdem.Ranks.THREE:
                    message += " (THREE tiebreaker)"
                elif cardRank == texas_holdem.Ranks.FOUR:
                    message += " (FOUR tiebreaker)"
                elif cardRank == texas_holdem.Ranks.FIVE:
                    message += " (FIVE tiebreaker)"
                elif cardRank == texas_holdem.Ranks.SIX:
                    message += " (SIX tiebreaker)"
                elif cardRank == texas_holdem.Ranks.SEVEN:
                    message += " (SEVEN tiebreaker)"
                elif cardRank == texas_holdem.Ranks.EIGHT:
                    message += " (EIGHT tiebreaker)"
                elif cardRank == texas_holdem.Ranks.NINE:
                    message += " (NINE tiebreaker)"
                elif cardRank == texas_holdem.Ranks.TEN:
                    message += " (TEN tiebreaker)"
                elif cardRank == texas_holdem.Ranks.JACK:
                    message += " (JACK tiebreaker)"
                elif cardRank == texas_holdem.Ranks.QUEEN:
                    message += " (QUEEN tiebreaker)"
                elif cardRank == texas_holdem.Ranks.KING:
                    message += " (KING tiebreaker)"
                elif cardRank == texas_holdem.Ranks.ACE:
                    message += " (ACE tiebreaker)"
        return message

    def __cpuMove(self):
        print 'cpumove', 'turns left =', self.game.movecounter
        #self.game.call(self.cpu)
        decision = random.randrange(4)
        print "lastraise = ", self.game.lastraise, decision
        if decision == 1 and self.game.lastraise == 0: #shouldn't call. check instead.
            decision = 0
        elif decision == 0 and self.cpu.bid < self.game.lastraise: #can't check. call instead.
            decision = 1
        if decision == 0:
            self.game.check(self.cpu)
            self.__setText(self.prompt, self.cpu.name + " checked.")
        elif decision == 1:
            self.game.call(self.cpu)
            self.__setText(self.prompt, self.cpu.name + " called.")
        elif decision >= 2:
            bid_amount = random.randrange(self.game.lastraise, self.game.lastraise*2+1)
            bid_amount += 50 - (bid_amount % 50)
            self.game.make_bid(self.cpu, bid_amount)
            self.__setText(self.prompt, self.cpu.name + " raised the bet to " \
                    + locale.format("%d", self.game.bid, grouping=True) + ".")

        self.__updateDisplay(False)
        if self.game.is_next(self.cpu) and not self.game.finished:
            self.__cpuMove()

    def __playerMove(self, opt, move):
        print 'playermove', 'turns left =', self.game.movecounter
        if move == 'FOLD':
            if self.game.fold(self.player) == False:
                return False
        elif move == 'CHECK':
            if self.game.check(self.player) == False:
                return False
        elif move == 'CALL':
            if self.game.call(self.player) == False:
                return False
        elif move == 'RAISE_BID':
            #get text from TextView
            buf = self.bidText.get_buffer()
            start = buf.get_start_iter()
            end = buf.get_end_iter()
            #do move
            if self.game.make_bid(self.player, int(buf.get_text(start, end))) == False:
                return False

        self.__updateDisplay(False)
        if self.game.finished:
            self.__updateDisplay(not self.player.folded)
            self.__toggleInterface(False)
            return True
        elif self.game.is_next(self.cpu):
            self.__cpuMove()
            self.__updateDisplay(False)
            if self.game.finished:
                self.__updateDisplay(not self.cpu.folded)
                self.__toggleInterface(False)
        return True

    def __init__(self):
        #initialize a 2-player game
        self.game = texas_holdem.HoldemGame()
        self.player = texas_holdem.Player('The player')
        self.cpu = texas_holdem.Player('PokerMaster 3000')
        self.game.add_player(self.cpu)
        self.game.add_player(self.player)

        #initialize window
        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.window.set_title("Machine Learning Texas Hold'em")
        self.window.modify_bg(gtk.STATE_NORMAL, SALOON_BROWN)
        self.window.connect("delete_event", self.delete_event)
        self.window.connect("destroy", self.destroy)
        self.window.set_border_width(100)

        #initialize the fixed layout and all of its widgets
        self.layout = gtk.Fixed()

        self.prompt = gtk.TextView()
        self.prompt.set_editable(False)
        self.prompt.modify_font(BIG_FONT)
        self.__setText(self.prompt, "Press the SHUFFLE button to start a new hand")

        self.potText = gtk.TextView()
        self.potText.set_editable(False)
        self.potText.modify_font(BIG_FONT)
        self.__setText(self.potText, "Pot: $" + locale.format("%d", self.game.pot, grouping=True))

        self.cpuMoneyText = gtk.TextView()
        self.cpuMoneyText.set_editable(False)
        self.cpuMoneyText.modify_font(DEFAULT_FONT)
        self.__setText(self.cpuMoneyText, "CPU: $" + locale.format("%d", self.cpu.balance, grouping=True))
        self.cpuBidText = gtk.TextView()
        self.cpuBidText.set_editable(False)
        self.cpuBidText.modify_font(DEFAULT_FONT)
        self.__setText(self.cpuBidText, "Bid: $" + locale.format("%d", self.cpu.in_pot, grouping=True))

        self.cpucard1_box = gtk.EventBox()
        self.cpucard1 = gtk.Image()
        self.cpucard1_box.add(self.cpucard1)
        self.cpucard1_box.show()
        self.cpucard1.show()
        self.__setCardImage(self.cpucard1_box, self.cpucard1, self.cpu.card1)
        self.cpucard2_box = gtk.EventBox()
        self.cpucard2 = gtk.Image()
        self.cpucard2_box.add(self.cpucard2)
        self.cpucard2_box.show()
        self.cpucard2.show()
        self.__setCardImage(self.cpucard2_box, self.cpucard2, self.cpu.card2)

        self.card1_box = gtk.EventBox()
        self.card1 = gtk.Image()
        self.card1_box.add(self.card1)
        self.card1_box.show()
        self.card1.show()
        self.__setCardImage(self.card1_box, self.card1, self.game.card1)
        self.card2_box = gtk.EventBox()
        self.card2 = gtk.Image()
        self.card2_box.add(self.card2)
        self.card2_box.show()
        self.card2.show()
        self.__setCardImage(self.card2_box, self.card2, self.game.card2)
        self.card3_box = gtk.EventBox()
        self.card3 = gtk.Image()
        self.card3_box.add(self.card3)
        self.card3_box.show()
        self.card3.show()
        self.__setCardImage(self.card3_box, self.card3, self.game.card3)
        self.card4_box = gtk.EventBox()
        self.card4 = gtk.Image()
        self.card4_box.add(self.card4)
        self.card4_box.show()
        self.card4.show()
        self.__setCardImage(self.card4_box, self.card4, self.game.card4)
        self.card5_box = gtk.EventBox()
        self.card5 = gtk.Image()
        self.card5_box.add(self.card5)
        self.card5_box.show()
        self.card5.show()
        self.__setCardImage(self.card5_box, self.card5, self.game.card5)

        self.playercard1_box = gtk.EventBox()
        self.playercard1 = gtk.Image()
        self.playercard1_box.add(self.playercard1)
        self.playercard1_box.show()
        self.playercard1.show()
        self.__setCardImage(self.playercard1_box, self.playercard1, self.player.card1)
        self.playercard2_box = gtk.EventBox()
        self.playercard2 = gtk.Image()
        self.playercard2_box.add(self.playercard2)
        self.playercard2_box.show()
        self.playercard2.show()
        self.__setCardImage(self.playercard2_box, self.playercard2, self.player.card2)

        self.buttonFold = gtk.Button()
        self.__setButton(self.buttonFold, 'FOLD', FIREBRICK)
        self.buttonFold.connect("clicked", self.__playerMove, 'FOLD')
        self.buttonCheck = gtk.Button()
        self.__setButton(self.buttonCheck, 'CHECK', PERU)
        self.buttonCheck.connect("clicked", self.__playerMove, 'CHECK')
        self.buttonCall = gtk.Button()
        self.__setButton(self.buttonCall, 'CALL', ROYAL_BLUE)
        self.buttonCall.connect("clicked", self.__playerMove, 'CALL')
        self.buttonRaiseBid = gtk.Button()
        self.__setButton(self.buttonRaiseBid, 'RAISE\n    or\n  BID', FOREST_GREEN)
        self.buttonRaiseBid.connect("clicked", self.__playerMove, 'RAISE_BID')

        self.playerMoneyText = gtk.TextView()
        self.playerMoneyText.set_editable(False)
        self.playerMoneyText.modify_font(DEFAULT_FONT)
        self.__setText(self.playerMoneyText, "Player: $" + locale.format("%d", self.cpu.balance, grouping=True))
        self.playerBidText = gtk.TextView()
        self.playerBidText.set_editable(False)
        self.playerBidText.modify_font(DEFAULT_FONT)
        self.__setText(self.playerBidText, "Bid: $" + locale.format("%d", self.player.bid, grouping=True))

        dollarsign = gtk.Label()
        dollarsign.set_markup('<span color="#2E8B57"><span size="14000">$</span></span>') #2E8B57 same as SEA_GREEN
        dollarsign.show()

        self.bidText = gtk.TextView()
        self.__setText(self.bidText, str(self.game.lastraise))
        self.bidText.modify_base(gtk.STATE_NORMAL, SEA_GREEN)
        self.bidText.set_justification(gtk.JUSTIFY_CENTER)
        self.bidText.set_size_request(70,20)

        self.buttonShuffle = gtk.Button()
        self.__setButton(self.buttonShuffle, 'SHUFFLE', DARK_SLATE_GRAY)
        self.buttonShuffle.connect("clicked", self.__clickShuffle)

        #place all widgets into fixed layout
        self.layout.put(self.prompt, 325-int(self.prompt.get_buffer().get_char_count()*5.5), 0)
        self.layout.put(self.potText, 325-int(self.potText.get_buffer().get_char_count()*5.5), 40)
        self.layout.put(self.cpuMoneyText, 325-(self.cpuMoneyText.get_buffer().get_char_count()*4), 100)
        self.layout.put(self.cpuBidText, 325-(self.cpuBidText.get_buffer().get_char_count()*4), 120)
        self.layout.put(self.buttonFold, 0, 600)
        self.layout.put(self.buttonCheck, 105, 600)
        self.layout.put(self.buttonCall, 475, 600)
        self.layout.put(self.buttonRaiseBid, 580, 600)
        self.layout.put(self.playerMoneyText, 325-(self.playerMoneyText.get_buffer().get_char_count()*4), 735)
        self.layout.put(self.playerBidText, 325-(self.playerBidText.get_buffer().get_char_count()*4), 715)
        self.layout.put(dollarsign, 567, 570)
        self.layout.put(self.bidText, 580, 575)
        self.layout.put(self.buttonShuffle, 295, 800)
        self.layout.put(self.cpucard1_box, 220, 150)
        self.layout.put(self.cpucard2_box, 330, 150)
        self.layout.put(self.card1_box, 55, 350)
        self.layout.put(self.card2_box, 165, 350)
        self.layout.put(self.card3_box, 275, 350)
        self.layout.put(self.card4_box, 385, 350)
        self.layout.put(self.card5_box, 495, 350)
        self.layout.put(self.playercard1_box, 220, 550)
        self.layout.put(self.playercard2_box, 330, 550)
        self.layout.show()

        self.window.add(self.layout)
        self.window.show()

        #player clicks shuffle to start game
        self.__toggleInterface(False)


    def main(self):
        gtk.main()


if __name__ == "__main__":
    game = PlayHoldem()
    game.main()
