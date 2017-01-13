#!/usr/bin/env python
"""
Texas Hold'em Game GUI implementation

Author: Garrett Gregory

Description:
    This module implements a graphical user face implementation of the texas_holdem
    API. This implemenation is a 1v1 game between the player and an AI.

"Constant" Variables:
    FACE_DOWN (string): Plaintext path to the card-back image
    SEA_GREEN (gtk.gdk.Color): Color to be used in GUI
    .
    .
    .
    BIG_FONT (pango.FontDescription): Large font
    DEFAULT_FONT (pango.FontDescription): Regular font
    RankStrings (dict): Dictionary mapping texas_holdem.Ranks enums to strings
    SuitStrings (dict): Dictionary mapping texas_holdem.Suits enums to strings
"""
#TODO: Write machine learning script, replace randomization with learned behavior in _cpu_move()

import pygtk
import gtk
import texas_holdem
import locale
import pango
import random
pygtk.require('2.0')

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
RankStrings = {0:'2', 1:'3', 2:'4', 3:'5', 4:'6', 5:'7', 6:'8',
                7:'9', 8:'10', 9:'jack', 10:'queen', 11:'king', 12:'ace'}
HandStrings = {0:'HIGH CARD', 1:'PAIR', 2:'TWO PAIR', 3:'THREE OF A KIND', 4:'STRAIGHT', 5:'FLUSH',
                6:'FULL HOUSE', 7:'FOUR OF A KIND', 8:'STRAIGHT FLUSH', 9:'ROYAL FLUSH'}
SuitStrings = {0:'_of_clubs', 1:'_of_diamonds', 2:'_of_hearts', 3:'_of_spades'}

class PlayHoldem:
    """Texas Hold'em GUI Implementation class"""

    def delete_event(self, widget, event, data=None):
        return False

    def destroy(self, widget, data=None):
        gtk.main_quit()

    def _set_button(self, button, label, color):
        """Helper function to set a button's label and background color."""
        #change background color of button (normal and mouseover)
        button.modify_bg(gtk.STATE_NORMAL, color)
        button.modify_bg(gtk.STATE_PRELIGHT, color)
        #set button caption and default size
        button.set_label(label)
        button.set_size_request(70, 70)
        button.show()

    def _set_card_image(self, box, image, card):
        """Helper function to set card box's background color and image according to
        the specified image path."""
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

    def _update_display(self, update_cpu):
        """Helper function to update the GUI to reflect recent changes in the game's state."""
        self._set_card_image(self.player_card1_box, self.player_card1, self.player.card1)
        self._set_card_image(self.player_card2_box, self.player_card2, self.player.card2)

        self._set_card_image(self.card1_box, self.card1, self.game.card1)
        self._set_card_image(self.card2_box, self.card2, self.game.card2)
        self._set_card_image(self.card3_box, self.card3, self.game.card3)
        self._set_card_image(self.card4_box, self.card4, self.game.card4)
        self._set_card_image(self.card5_box, self.card5, self.game.card5)

        if self.game.finished:
            self._set_text(self.prompt, self._get_winner_message())
        if self.player.balance < self.game.bid - self.player.bid:
            #player doesn't have enough money to raise
            self.button_raise_bid.set_sensitive(False)
            self.bid_text.set_sensitive(False)
        self.layout.move(self.prompt, 325-int(self.prompt.get_buffer().get_char_count()*5.5), 0)
        self._set_text(self.pot_text, "Pot: $" + locale.format("%d", self.game.pot, grouping=True))
        self.layout.move(self.pot_text, 325-int(self.pot_text.get_buffer().get_char_count()*5.5), 40)
        self._set_text(self.cpu_money_text, "CPU: $" + locale.format("%d", self.cpu.balance, grouping=True))
        self.layout.move(self.cpu_money_text, 325-(self.cpu_money_text.get_buffer().get_char_count()*4), 100)
        self._set_text(self.cpu_bid_text, "Bid: $" + locale.format("%d", self.cpu.bid, grouping=True))
        self.layout.move(self.cpu_bid_text, 325-(self.cpu_bid_text.get_buffer().get_char_count()*4), 120)
        self._set_text(self.player_money_text, "Player: $" + locale.format("%d", self.player.balance, grouping=True))
        self.layout.move(self.player_money_text, 325-(self.player_money_text.get_buffer().get_char_count()*4), 735)
        self._set_text(self.player_bid_text, "Bid: $" + locale.format("%d", self.player.bid, grouping=True))
        self.layout.move(self.player_bid_text, 325-(self.player_bid_text.get_buffer().get_char_count()*4), 715)
        self._set_text(self.bid_text, str(max(50, self.game.lastraise)))

        if update_cpu:
            self._set_card_image(self.cpu_card1_box, self.cpu_card1, self.cpu.card1)
            self._set_card_image(self.cpu_card2_box, self.cpu_card2, self.cpu.card2)

        #deactivate buttons if moves shouldn't be performed
        if self.player.bid < self.game.bid:
            self.button_check.set_sensitive(False)
            self.button_call.set_sensitive(True)
        else:
            self.button_check.set_sensitive(True)
            self.button_call.set_sensitive(False)

    def _set_text(self, widget, text):
        """Helper function to change the text in a TextView."""
        buf = widget.get_buffer()
        buf.set_text(text)
        widget.set_buffer(buf)
        widget.show()

    def _click_shuffle(self, opt):
        """Function called when the user clicks the Shuffle button."""
        self._set_text(self.prompt, self.cpu.name + " dealt.")
        self.game.shuffle()
        self.button_shuffle.hide()
        self._toggle_interface(True)
        self._update_display(True)
        if self.game.is_next(self.cpu):
            self._cpu_move()

    def _toggle_interface(self, show):
        """Helper function to toggle the main game interface on/off when game starts/ends."""
        self.bid_text.set_sensitive(show)
        self.button_fold.set_sensitive(show)
        self.button_check.set_sensitive(show)
        self.button_call.set_sensitive(show)
        self.button_raise_bid.set_sensitive(show)
        if not show:
            self.button_shuffle.show()

    def _get_winner_message(self):
        """Helper function to generate a message at end of game."""
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
            win_type = self.game.winners[0].hand
            message += HandStrings[win_type] + "."
            if self.game.tiebreaker:
                card_rank = self.game.tiebreaker_value
                message += " (" + RankStrings[card_rank].upper() + " tiebreaker)"

        return message

    def _cpu_move(self):
        """Performs a move by the AI."""
        #self.game.call(self.cpu)
        decision = random.randrange(4)
        if decision == 1 and self.game.lastraise == 0: #shouldn't call. check instead.
            decision = 0
        elif decision == 0 and self.cpu.bid < self.game.lastraise: #can't check. call instead.
            decision = 1
        if decision == 0:
            self.game.check(self.cpu)
            self._set_text(self.prompt, self.cpu.name + " checked.")
        elif decision == 1:
            self.game.call(self.cpu)
            self._set_text(self.prompt, self.cpu.name + " called.")
        elif decision >= 2:
            bid_amount = random.randrange(self.game.lastraise, self.game.lastraise*2+1)
            bid_amount += 50 - (bid_amount % 50)
            self.game.make_bid(self.cpu, bid_amount)
            self._set_text(self.prompt, self.cpu.name + " raised the bet to " \
                    + locale.format("%d", self.game.bid, grouping=True) + ".")

        self._update_display(False)
        if self.game.is_next(self.cpu) and not self.game.finished:
            self._cpu_move()

    def _player_move(self, opt, move):
        """Performs a move by the player when an action button is clicked."""
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
            buf = self.bid_text.get_buffer()
            start = buf.get_start_iter()
            end = buf.get_end_iter()
            #do move
            if self.game.make_bid(self.player, int(buf.get_text(start, end))) == False:
                return False

        self._update_display(False)
        if self.game.finished:
            self._update_display(not self.player.folded)
            self._toggle_interface(False)
            return True
        elif self.game.is_next(self.cpu):
            self._cpu_move()
            self._update_display(False)
            if self.game.finished:
                self._update_display(not self.cpu.folded)
                self._toggle_interface(False)
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
        self._set_text(self.prompt, "Press the SHUFFLE button to start a new hand.")

        self.pot_text = gtk.TextView()
        self.pot_text.set_editable(False)
        self.pot_text.modify_font(BIG_FONT)
        self._set_text(self.pot_text, "Pot: $" + locale.format("%d", self.game.pot, grouping=True))

        self.cpu_money_text = gtk.TextView()
        self.cpu_money_text.set_editable(False)
        self.cpu_money_text.modify_font(DEFAULT_FONT)
        self._set_text(self.cpu_money_text, "CPU: $" + locale.format("%d", self.cpu.balance, grouping=True))
        self.cpu_bid_text = gtk.TextView()
        self.cpu_bid_text.set_editable(False)
        self.cpu_bid_text.modify_font(DEFAULT_FONT)
        self._set_text(self.cpu_bid_text, "Bid: $" + locale.format("%d", self.cpu.bid, grouping=True))

        self.cpu_card1_box = gtk.EventBox()
        self.cpu_card1 = gtk.Image()
        self.cpu_card1_box.add(self.cpu_card1)
        self.cpu_card1_box.show()
        self.cpu_card1.show()
        self._set_card_image(self.cpu_card1_box, self.cpu_card1, self.cpu.card1)
        self.cpu_card2_box = gtk.EventBox()
        self.cpu_card2 = gtk.Image()
        self.cpu_card2_box.add(self.cpu_card2)
        self.cpu_card2_box.show()
        self.cpu_card2.show()
        self._set_card_image(self.cpu_card2_box, self.cpu_card2, self.cpu.card2)

        self.card1_box = gtk.EventBox()
        self.card1 = gtk.Image()
        self.card1_box.add(self.card1)
        self.card1_box.show()
        self.card1.show()
        self._set_card_image(self.card1_box, self.card1, self.game.card1)
        self.card2_box = gtk.EventBox()
        self.card2 = gtk.Image()
        self.card2_box.add(self.card2)
        self.card2_box.show()
        self.card2.show()
        self._set_card_image(self.card2_box, self.card2, self.game.card2)
        self.card3_box = gtk.EventBox()
        self.card3 = gtk.Image()
        self.card3_box.add(self.card3)
        self.card3_box.show()
        self.card3.show()
        self._set_card_image(self.card3_box, self.card3, self.game.card3)
        self.card4_box = gtk.EventBox()
        self.card4 = gtk.Image()
        self.card4_box.add(self.card4)
        self.card4_box.show()
        self.card4.show()
        self._set_card_image(self.card4_box, self.card4, self.game.card4)
        self.card5_box = gtk.EventBox()
        self.card5 = gtk.Image()
        self.card5_box.add(self.card5)
        self.card5_box.show()
        self.card5.show()
        self._set_card_image(self.card5_box, self.card5, self.game.card5)

        self.player_card1_box = gtk.EventBox()
        self.player_card1 = gtk.Image()
        self.player_card1_box.add(self.player_card1)
        self.player_card1_box.show()
        self.player_card1.show()
        self._set_card_image(self.player_card1_box, self.player_card1, self.player.card1)
        self.player_card2_box = gtk.EventBox()
        self.player_card2 = gtk.Image()
        self.player_card2_box.add(self.player_card2)
        self.player_card2_box.show()
        self.player_card2.show()
        self._set_card_image(self.player_card2_box, self.player_card2, self.player.card2)

        self.button_fold = gtk.Button()
        self._set_button(self.button_fold, 'FOLD', FIREBRICK)
        self.button_fold.connect("clicked", self._player_move, 'FOLD')
        self.button_check = gtk.Button()
        self._set_button(self.button_check, 'CHECK', PERU)
        self.button_check.connect("clicked", self._player_move, 'CHECK')
        self.button_call = gtk.Button()
        self._set_button(self.button_call, 'CALL', ROYAL_BLUE)
        self.button_call.connect("clicked", self._player_move, 'CALL')
        self.button_raise_bid = gtk.Button()
        self._set_button(self.button_raise_bid, 'RAISE\n    or\n  BID', FOREST_GREEN)
        self.button_raise_bid.connect("clicked", self._player_move, 'RAISE_BID')

        self.player_money_text = gtk.TextView()
        self.player_money_text.set_editable(False)
        self.player_money_text.modify_font(DEFAULT_FONT)
        self._set_text(self.player_money_text, "Player: $" + locale.format("%d", self.cpu.balance, grouping=True))
        self.player_bid_text = gtk.TextView()
        self.player_bid_text.set_editable(False)
        self.player_bid_text.modify_font(DEFAULT_FONT)
        self._set_text(self.player_bid_text, "Bid: $" + locale.format("%d", self.player.bid, grouping=True))

        dollarsign = gtk.Label()
        dollarsign.set_markup('<span color="#2E8B57"><span size="14000">$</span></span>') #2E8B57 same as SEA_GREEN
        dollarsign.show()

        self.bid_text = gtk.TextView()
        self.bid_text.set_editable(True)
        self._set_text(self.bid_text, str(self.game.lastraise))
        self.bid_text.modify_base(gtk.STATE_NORMAL, SEA_GREEN)
        self.bid_text.set_justification(gtk.JUSTIFY_CENTER)
        self.bid_text.set_size_request(70,20)

        self.button_shuffle = gtk.Button()
        self._set_button(self.button_shuffle, 'SHUFFLE', DARK_SLATE_GRAY)
        self.button_shuffle.connect("clicked", self._click_shuffle)

        #place all widgets into fixed layout
        self.layout.put(self.prompt, 325-int(self.prompt.get_buffer().get_char_count()*5.5), 0)
        self.layout.put(self.pot_text, 325-int(self.pot_text.get_buffer().get_char_count()*5.5), 40)
        self.layout.put(self.cpu_money_text, 325-(self.cpu_money_text.get_buffer().get_char_count()*4), 100)
        self.layout.put(self.cpu_bid_text, 325-(self.cpu_bid_text.get_buffer().get_char_count()*4), 120)
        self.layout.put(self.button_fold, 0, 600)
        self.layout.put(self.button_check, 105, 600)
        self.layout.put(self.button_call, 475, 600)
        self.layout.put(self.button_raise_bid, 580, 600)
        self.layout.put(self.player_money_text, 325-(self.player_money_text.get_buffer().get_char_count()*4), 735)
        self.layout.put(self.player_bid_text, 325-(self.player_bid_text.get_buffer().get_char_count()*4), 715)
        self.layout.put(dollarsign, 567, 570)
        self.layout.put(self.bid_text, 580, 575)
        self.layout.put(self.button_shuffle, 295, 800)
        self.layout.put(self.cpu_card1_box, 220, 150)
        self.layout.put(self.cpu_card2_box, 330, 150)
        self.layout.put(self.card1_box, 55, 350)
        self.layout.put(self.card2_box, 165, 350)
        self.layout.put(self.card3_box, 275, 350)
        self.layout.put(self.card4_box, 385, 350)
        self.layout.put(self.card5_box, 495, 350)
        self.layout.put(self.player_card1_box, 220, 550)
        self.layout.put(self.player_card2_box, 330, 550)
        self.layout.show()

        self.window.add(self.layout)
        self.window.show()

        #player clicks shuffle to start game
        self._toggle_interface(False)


    def main(self):
        gtk.main()


if __name__ == "__main__":
    game = PlayHoldem()
    game.main()
