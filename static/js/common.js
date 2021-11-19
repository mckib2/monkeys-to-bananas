// *********************************************************************
// createDOMElement(elData)
//
// Requires an input JSON object (example below):
//
//  {
//    "ELtype": "div",
//    "ELclasses": [ "modal", "fade" ],
//    "ELattributes": [
//      { "ELname": "role", "ELvalue": "dialog" }
//    ],
//    "ELhtmlString": "Hello, world!",
//    "ELparentElement": // a DOM element
//  }
//
// *********************************************************************
function createDOMElement(elData) {
    if ("ELtype" in elData) {
        var newElement = document.createElement(elData.ELtype);

        if ("ELclasses" in elData) {
            for (i = 0; i < elData.ELclasses.length; i++) {
                newElement.classList.add(elData.ELclasses[i]);
            }
        }

        if ("ELattributes" in elData) {
            for (i = 0; i < elData.ELattributes.length; i++) {
                newElement.setAttribute(elData.ELattributes[i].ELname, elData.ELattributes[i].ELvalue);
            }
        }

        if ("ELhtmlString" in elData) {
            newElement.innerHTML = elData.ELhtmlString;
        }

        if ("ELparentElement" in elData) {
            elData.ELparentElement.appendChild(newElement);
        }

        return newElement;
    }
    else {
        return -1;
    }
}



// *********************************************************************
// verifyModal(anAnchor, aQuestion, aCallbackFunction)
//
//    anAnchor = a DOM element
//    aQuestion = a string to display
//    
//    "ELtype": "div",
//    "ELclasses": [ "modal", "fade" ],
//    "ELattributes": [
//      { "ELname": "role", "ELvalue": "dialog" }
//    ],
//    "ELhtmlString": "Hello, world!",
//    "ELparentElement": // a DOM element
//  }
//
// *********************************************************************
function verifyModal(anAnchor, aQuestion, aCallbackFunction) {
    console.log("Starting verifyModal()...");

    var newModal = createDOMElement({
        "ELtype": "div",
        "ELclasses": ["modal", "fade", "show"],
        "ELattributes": [
            { "ELname": "id", "ELvalue": "verifyModal" },
            { "ELname": "aria-labelledby", "ELvalue": "verifyModalLabel" },
            { "ELname": "aria-modal", "ELvalue": "true" },
            { "ELname": "role", "ELvalue": "dialog" },
            { "ELname": "tabindex", "ELvalue": "-1" }
        ],
        "ELparentElement": anAnchor
    });

    var newModalDialog = createDOMElement({
        "ELtype": "div",
        "ELclasses": ["modal-dialog"],
        "ELparentElement": newModal
    });

    var newModalContent = createDOMElement({
        "ELtype": "div",
        "ELclasses": ["modal-content"],
        "ELparentElement": newModalDialog
    });

    var newModalHeader = createDOMElement({
        "ELtype": "div",
        "ELclasses": ["modal-header"],
        "ELparentElement": newModalContent
    });

    var newModalTitle = createDOMElement({
        "ELtype": "h5",
        "ELclasses": ["modal-title"],
        "ELattributes": [
            { "ELname": "id", "ELvalue": "verifyModalLabel" }
        ],
        "ELhtmlString": "Wait!",
        "ELparentElement": newModalHeader
    });

    var newModalCloseButton = createDOMElement({
        "ELtype": "button",
        "ELclasses": ["close"],
        "ELattributes": [
            { "ELname": "type", "ELvalue": "button" },
            { "ELname": "data-dismiss", "ELvalue": "modal" },
            { "ELname": "aria-label", "ELvalue": "Close" }
        ],
        "ELparentElement": newModalHeader
    });
    newModalCloseButton.addEventListener("click", function () {
        $(newModal).hide();
    });

    var newModalCloseButtonX = createDOMElement({
        "ELtype": "span",
        "ELattributes": [
            { "ELname": "aria-hidden", "ELvalue": "true" }
        ],
        "ELhtmlString": "x",
        "ELparentElement": newModalCloseButton
    });

    var newModalBody = createDOMElement({
        "ELtype": "div",
        "ELclasses": ["modal-body"],
        "ELparentElement": newModalContent
    });

    var newModalMessageRow = createDOMElement({
        "ELtype": "div",
        "ELclasses": ["row"],
        "ELparentElement": newModalBody
    });

    var newModalMessageCol = createDOMElement({
        "ELtype": "div",
        "ELclasses": ["col", "text-center"],
        "ELparentElement": newModalMessageRow
    });

    var newModalMessage = createDOMElement({
        "ELtype": "span",
        "ELhtmlString": aQuestion,
        "ELparentElement": newModalMessageCol
    });

    var newModalFooter = createDOMElement({
        "ELtype": "div",
        "ELclasses": ["modal-footer"],
        "ELparentElement": newModalContent
    });

    var newModalYesButton = createDOMElement({
        "ELtype": "button",
        "ELclasses": ["btn", "btn-primary"],
        "ELhtmlString": "Yes",
        "ELparentElement": newModalFooter
    });
    newModalYesButton.addEventListener("click", function () {
        $(newModal).hide();
        aCallbackFunction();
    })

    var newModalNoButton = createDOMElement({
        "ELtype": "div",
        "ELclasses": ["btn", "btn-primary"],
        "ELhtmlString": "No",
        "ELparentElement": newModalFooter
    });
    newModalNoButton.addEventListener("click", function () {
        $(newModal).hide();
    });

    $(newModal).on('shown.bs.modal', function () {
        $(newModalNoButton).trigger('focus');
    })

    $(newModal).show();
}

class M2BCard {
    constructor(anAnchorElement, anInfoObject) {
        this.anchorElement = anAnchorElement;
        /*
            anInfoObject = {
                "cardColor": "red" | "green",
                "cardText": [
                    "main term",
                    "supporting text 1",
                    "supporting text 2"
                ],
                "cardIndex": aNumber, // Represents the index of the card definition in carddecks.py
                "cardButtonText": "Play this card" | "Select this card" // Whatever the button is supposed to display
            }
        */
       this.cardColor = anInfoObject.cardColor;
       this.bgColor = "bg-danger";
       if (this.cardColor === "green") {
           this.bgColor = "bg-light-success";
       }
       this.cardText = anInfoObject.cardText;
       this.cardIndex = anInfoObject.cardIndex;
       this.cardButtonText = anInfoObject.cardButtonText;
    }

    draw() {
        var cardDiv = createDOMElement({
            "ELtype": "div",
            "ELclasses": [ "card", "m-2", this.bgColor ],
            "ELattributes": [
                { "ELname": "style", "ELvalue": "width: 18rem; min-height: 20rem;" }
            ],
            "ELparentElement": this.anchorElement
        });

        var cardHeader = createDOMElement({
            "ELtype": "div",
            "ELclasses": [ "card-header", "bg-white" ],
            "ELparentElement": cardDiv
        });

        if (this.cardText.length > 0) {
            var cardTitle = createDOMElement({
                "ELtype": "h3",
                "ELclasses": [ "card-title", "fw-bolder" ],
                "ELhtmlString": this.cardText[0],
                "ELparentElement": cardHeader
            });
        }

        var cardBody = createDOMElement({
            "ELtype": "div",
            "ELclasses": [ "card-body", this.bgColor ],
            "ELparentElement": cardDiv
        });

        if (this.cardText.length > 1) {
            var text1 = createDOMElement({
                "ELtype": "span",
                "ELclasses": [ "card-text", "fw-bold" ],
                "ELhtmlString": this.cardText[1],
                "ELparentElement": cardBody
            });

            if (this.cardText.length > 2) {
                var supportingTextUL = createDOMElement({
                    "ELtype": "ul",
                    "ELparentElement": cardBody
                });

                for (var i = 2; i < this.cardText.length; i++) {
                    var supportingText = createDOMElement({
                        "ELtype": "i",
                        "ELclasses": [ "fst-italic" ],
                        "ELhtmlString": this.cardText[i],
                        "ELparentElement": supportingTextUL
                    });
                }
            }
        }

        if (this.cardColor == "red" && this.cardText.length > 0) {
            var thisObject = this;
            var cardFooter = createDOMElement({
                "ELtype": "div",
                "ELclasses": [ "card-footer" ],
                "ELparentElement": cardDiv
            });

            var playCardButton = createDOMElement({
                "ELtype": "a",
                "ELclasses": [ "btn", "btn-success", "align-bottom" ],
                "ELhtmlString": this.cardButtonText,
                "ELparentElement": cardFooter
            });
            playCardButton.addEventListener("click", function() {
                // var theForm = document.getElementById("redCardForm-" + thisObject.cardIndex);
                document["redCardForm-" + thisObject.cardIndex].submit();
            });
        }
    }
}