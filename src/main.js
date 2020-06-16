
// Depends on:
//     seedrandom.js
//     uuidv4.js
//     deck.js
//     redcards.js
//     greencards.js

function main(seedInput, startButton, redCards, greenCard) {

    startButton.addEventListener('click', function(ev) {

	// Make sure we have a good seed value
	let mySeed = seedInput.value;
	if (mySeed === '') {
	    alert('Enter a phrase!');
	    return false;
	}

	// Initialize decks; start with red cards
	let words = _RedCards();
	let cards = [];
	for (let ii = 0; ii < words.length; ++ii) {
	    cards.push(new Card(words[ii]));
	}
	let RedDeck = new Deck(cards);
	console.log('Created red deck with ' + RedDeck.numCards() + ' cards');

	// Get the green cards
	words = _GreenCards();
	cards = [];
	for (let ii = 0; ii < words.length; ++ii) {
	    cards.push(new Card(words[ii][0], words[ii].splice(1, words[ii].length)));
	}
	let GreenDeck = new Deck(cards);
	console.log('Created green deck with ' + GreenDeck.numCards() + ' cards');
	GreenDeck.setSeed(mySeed);

	// Populate red cards
	redCards.innerHTML = ''; // remove previous cards
	let redcards = [];
	for (let ii = 0; ii < 5; ++ii) {
	    let card = RedDeck.draw();
	    redcards.push(card);
	    redCards.innerHTML += card.word + ',';
	}

	// Draw green card
	greenCard.innerHTML = ''; // remove previous card
	let greencards = [];
	let card = GreenDeck.draw();
	greencards.push(card);
	greenCard.innerHTML = card.word + ' (' + card.synonyms.join(', ') + ')';
    });

}
