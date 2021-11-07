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