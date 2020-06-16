'use strict';

function _isString (obj) {
    return (Object.prototype.toString.call(obj) === '[object String]');
}

class Card {
    constructor(word, synonyms=[]) {
	this.uid = uuidv4();
	this.word = word;
	this.synonyms = synonyms;
	this.drawn = false;
    }
}

class Deck {
    constructor(cards) {
	this.cards = cards;
	this.rng = new Math.seedrandom();
    }

    // Bind this deck to a given seed
    setSeed(mySeed) {
	if (_isString(mySeed)) {
	    console.log('Setting seed: "' + mySeed + '"')
	    this.rng = new Math.seedrandom(mySeed);
	}
	else {
	    console.log('Seed "' + mySeed + '" must be a string!');
	}
    }

    // Generate an integer in [min, max) using this deck's RNG
    _getRndInt(min, max) {
	min = Math.ceil(min);
	max = Math.floor(max);
	return Math.floor(this.rng() * (max - min)) + min;
    }

    // Draw a card from the deck at random
    draw() {
	let available_cards = this.cards.filter(function(el) { return !el.drawn; });
	if (!available_cards.length) {
	    console.log("No card is available!");
	    return false;
	}
	let idx = this._getRndInt(0, available_cards.length);
	let card = available_cards[idx];
	idx = this.cards.map(function(el) { return el.uid; }).indexOf(card.uid);
	this.cards[idx].drawn = true;
	return this.cards[idx];
    }

    // Return a card to the deck
    replace(card_uid) {
	let idx = this.cards.map(function(el) { return el.uid; }).indexOf(card_uid);
	if (idx === -1) {
	    console.log('Card UID does not match any in deck!');
	    return false;
	}
	this.cards[idx].drawn = false;
	return true;
    }

    //  Get the number of total cards (remaining and drawn)
    numCards() {
	return this.cards.length;
    }

    // Get the number of cards in the deck that have not been drawn
    numRemaining() {
	return this.cards.filter(function(el) { return !el.drawn }).length;
    }
}
