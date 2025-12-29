var list = document.getElementById("toc");
var content = document.getElementById("content");
var headings = content.querySelectorAll('h1, h2, h3, h4, h5, h6');
var lastLevel = 0;

headings.forEach(function(heading, index) {
    var level = parseInt(heading.tagName.slice(1));
    if (index === 0) {
        // First element, make a new list
        var childList = document.createElement("ul");
        list.appendChild(childList);
        list = childList;
    } else if (level > lastLevel) {
        // More indentation, make a new list per level
        for (var i = 0; i < level - lastLevel; ++i) {
            var childList = document.createElement("ul");
            list.appendChild(childList);
            list = childList;
        }
    } else if (level < lastLevel) {
        // Less indentation, move back a few levels
        for (var i = 0; i < lastLevel - level; ++i) {
            list = list.parentNode;
        }
    }
    
    // From Hasse's answer
    var ref = toc + index;
    if (heading.hasAttribute("id")) {
        ref = heading.getAttribute("id");
    } else {
        heading.setAttribute("id", ref);
    }

    var item = document.createElement("li");

    // Add link to corresponding header
    var link = document.createElement("a");
    link.setAttribute("href", "#" + ref);
    link.textContent = heading.textContent;
    item.appendChild(link);
    
    list.appendChild(item);
    lastLevel = level;
});