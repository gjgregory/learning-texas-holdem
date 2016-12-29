#!/usr/bin/env python

import pygtk
pygtk.require('2.0')
import gtk
import texas_holdem
import locale

class PlayHoldem:
    #"constant" variables
    SEA_GREEN = gtk.gdk.Color(0.18, 0.55, 0.34)
    DARK_SLATE_BLUE = gtk.gdk.Color(0.28, 0.24, 0.55)
    GHOST_WHITE = gtk.gdk.Color(0.97, 0.97, 1.0)
    FIREBRICK = gtk.gdk.Color(0.7, 0.13, 0.13)
    PERU = gtk.gdk.Color(0.8, 0.52, 0.25)
    ROYAL_BLUE = gtk.gdk.Color(0.25, 0.41, 0.88)
    FOREST_GREEN = gtk.gdk.Color(0.13, 0.55, 0.13)
    SALOON_BROWN = gtk.gdk.Color(0.28, 0.14, 0.04)
    DARK_SLATE_GRAY = gtk.gdk.Color(0.18, 0.31, 0.31)


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

    def __setCardImage(self, widget, card, x, y):
        #change background color of widget
        widget.destroy()
        widget = gtk.EventBox()
        if card.img_path == 'art_assets/black_joker.png':
            color = self.DARK_SLATE_BLUE
        else:
            color = self.GHOST_WHITE
        widget.modify_bg(gtk.STATE_NORMAL, color)
        #assign (presumably transparent) image to widget
        image = gtk.Image()
        pixbuf = gtk.gdk.pixbuf_new_from_file(card.img_path)
        scaled_pixbuf = pixbuf.scale_simple(100, 150, gtk.gdk.INTERP_BILINEAR)
        image.set_from_pixbuf(scaled_pixbuf)
        image.show()
        widget.add(image)
        widget.show()
        self.layout.put(widget, x, y)

    def __updateDisplay(self):
        self.__setCardImage(self.playercard1, self.player.card1, 220, 450)
        self.__setCardImage(self.playercard2, self.player.card2, 330, 450)

        self.__setCardImage(self.card1, self.game.card1, 55, 250)
        self.__setCardImage(self.card2, self.game.card2, 165, 250)
        self.__setCardImage(self.card3, self.game.card3, 275, 250)
        self.__setCardImage(self.card4, self.game.card4, 385, 250)
        self.__setCardImage(self.card5, self.game.card5, 495, 250)

        self.__setText(self.cpuMoneyText, "CPU: $" + locale.format("%d", self.cpu.balance, grouping=True))
        self.__setText(self.playerMoneyText, "Player: $" + locale.format("%d", self.player.balance, grouping=True))

    def __setText(self, widget, text):
        buf = widget.get_buffer()
        buf.set_text(text)
        widget.set_buffer(buf)
        widget.show()

    def __clickShuffle(self, opt):
        self.game.shuffle()
        self.buttonShuffle.hide()
        self.__toggleInterface(True)
        self.__updateDisplay()
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

    def __cpuMove(self):
        self.game.call(self.cpu)
        print 'sup'
        if self.game.finished:
            self.__toggleInterface(False)

    def __playerMove(self, opt, move):
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

        if self.game.finished:
            self.__toggleInterface(False)
            return True
        self.__updateDisplay()
        if not self.game.finished:
            self.__cpuMove()
        if self.game.finished:
            self.__toggleInterface(False)
            return True
        self.__updateDisplay()

    def __init__(self):
        self.game = texas_holdem.HoldemGame()
        self.player = texas_holdem.Player()
        self.cpu = texas_holdem.Player()
        self.game.add_player(self.cpu)
        self.game.add_player(self.player)
        #self.game.shuffle()
        #self.game.deal()


        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.window.set_title("Machine Learning Texas Hold'em")
        self.window.modify_bg(gtk.STATE_NORMAL, self.SALOON_BROWN)
        self.window.connect("delete_event", self.delete_event)
        self.window.connect("destroy", self.destroy)
        self.window.set_border_width(100)

        #initialize the fixed layout and all of its widgets
        self.layout = gtk.Fixed()

        self.cpuMoneyText = gtk.TextView()
        self.cpuMoneyText.set_editable(False)
        self.__setText(self.cpuMoneyText, "CPU: $" + locale.format("%d", self.cpu.balance, grouping=True))

        self.cpucard1 = gtk.EventBox()
        self.__setCardImage(self.cpucard1, self.cpu.card1, 220, 50)
        self.cpucard2 = gtk.EventBox()
        self.__setCardImage(self.cpucard2, self.cpu.card2, 330, 50)

        self.card1 = gtk.EventBox()
        self.__setCardImage(self.card1, self.game.card1, 55, 250)
        self.card2 = gtk.EventBox()
        self.__setCardImage(self.card2, self.game.card2, 165, 250)
        self.card3 = gtk.EventBox()
        self.__setCardImage(self.card3, self.game.card3, 275, 250)
        self.card4 = gtk.EventBox()
        self.__setCardImage(self.card4, self.game.card4, 385, 250)
        self.card5 = gtk.EventBox()
        self.__setCardImage(self.card5, self.game.card5, 495, 250)

        self.playercard1 = gtk.EventBox()
        self.__setCardImage(self.playercard1, self.player.card1, 220, 450)
        self.playercard2 = gtk.EventBox()
        self.__setCardImage(self.playercard2, self.player.card2, 330, 450)

        self.buttonFold = gtk.Button()
        self.__setButton(self.buttonFold, 'FOLD', self.FIREBRICK)
        self.buttonFold.connect("clicked", self.__playerMove, 'FOLD')
        self.buttonCheck = gtk.Button()
        self.__setButton(self.buttonCheck, 'CHECK', self.PERU)
        self.buttonCheck.connect("clicked", self.__playerMove, 'CHECK')
        self.buttonCall = gtk.Button()
        self.__setButton(self.buttonCall, 'CALL', self.ROYAL_BLUE)
        self.buttonCall.connect("clicked", self.__playerMove, 'CALL')
        self.buttonRaiseBid = gtk.Button()
        self.__setButton(self.buttonRaiseBid, 'RAISE\n    or\n  BID', self.FOREST_GREEN)
        self.buttonRaiseBid.connect("clicked", self.__playerMove, 'RAISE_BID')

        self.playerMoneyText = gtk.TextView()
        self.playerMoneyText.set_editable(False)
        self.__setText(self.playerMoneyText, "Player: $" + locale.format("%d", self.cpu.balance, grouping=True))

        dollarsign = gtk.Label()
        dollarsign.set_markup('<span color="#2E8B57"><span size="14000">$</span></span>') #2E8B57 same as SEA_GREEN
        dollarsign.show()

        self.bidText = gtk.TextView()
        self.__setText(self.bidText, str(texas_holdem.HoldemGame.BASE_BID))
        self.bidText.modify_base(gtk.STATE_NORMAL, self.SEA_GREEN)
        self.bidText.set_justification(gtk.JUSTIFY_CENTER)
        self.bidText.set_size_request(70,20)

        self.buttonShuffle = gtk.Button()
        self.__setButton(self.buttonShuffle, 'SHUFFLE', self.DARK_SLATE_GRAY)
        self.buttonShuffle.connect("clicked", self.__clickShuffle)

        #place all widgets into fixed layout
        self.layout.put(self.cpuMoneyText, 290, 0)
        self.layout.put(self.buttonFold, 0, 500)
        self.layout.put(self.buttonCheck, 105, 500)
        self.layout.put(self.buttonCall, 475, 500)
        self.layout.put(self.buttonRaiseBid, 580, 500)
        self.layout.put(self.playerMoneyText, 285, 635)
        self.layout.put(dollarsign, 567, 470)
        self.layout.put(self.bidText, 580, 475)
        self.layout.put(self.buttonShuffle, 295, 700)
        self.layout.show()

        self.window.add(self.layout)
        self.window.show()

        self.__toggleInterface(False)


    def main(self):
        gtk.main()


if __name__ == "__main__":
    game = PlayHoldem()
    game.main()
