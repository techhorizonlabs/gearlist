(function () {
  "use strict";
  var doc = document;

  /* Copy buttons: data-copy names the element whose text is copied */
  var copyStatus = doc.getElementById("copy-status");
  [].forEach.call(doc.querySelectorAll("button[data-copy]"), function (btn) {
    var target = doc.getElementById(btn.getAttribute("data-copy"));
    if (!target || !copyStatus) return;
    var label = btn.textContent;
    var timer = 0;
    function copied(message, text) {
      copyStatus.textContent = message;
      btn.textContent = text;
      clearTimeout(timer);
      timer = setTimeout(function () {
        btn.textContent = label;
        copyStatus.textContent = "";
      }, 2400);
    }
    function selectText() {
      var range = doc.createRange();
      range.selectNodeContents(target);
      var sel = window.getSelection();
      sel.removeAllRanges();
      sel.addRange(range);
      copied("Text selected. Press Control C or Command C to copy it.", "Selected");
    }
    btn.addEventListener("click", function () {
      var text = target.textContent.trim();
      if (navigator.clipboard && window.isSecureContext) {
        navigator.clipboard.writeText(text).then(function () {
          copied("Copied.", "Copied");
        }, selectText);
      } else {
        selectText();
      }
    });
  });

  /* Search and group filter */
  var q = doc.getElementById("q");
  var status = doc.getElementById("status");
  var empty = doc.getElementById("empty");
  var clear = doc.getElementById("clear");
  var catalog = doc.getElementById("catalog");
  var chips = [].slice.call(doc.querySelectorAll(".chip"));
  var groups = [].slice.call(doc.querySelectorAll(".group"));
  if (!q || !groups.length) return;

  var items = [];
  groups.forEach(function (group) {
    var name = group.querySelector(".group-name").textContent;
    [].forEach.call(group.querySelectorAll(".e"), function (el) {
      var parts = [name];
      [].forEach.call(el.querySelectorAll("h3, .d, .thl, dd"), function (node) {
        parts.push(node.textContent);
      });
      items.push({ el: el, cat: group.getAttribute("data-cat"), text: parts.join(" ").toLowerCase() });
    });
  });
  var total = items.length;
  var current = "all";

  function plural(n) { return n === 1 ? " entry" : " entries"; }

  function apply() {
    var terms = q.value.toLowerCase().split(/\s+/).filter(Boolean);
    var shown = 0;
    var perGroup = {};
    items.forEach(function (item) {
      var ok = (current === "all" || item.cat === current) &&
        terms.every(function (t) { return item.text.indexOf(t) !== -1; });
      item.el.hidden = !ok;
      if (ok) {
        shown += 1;
        perGroup[item.cat] = (perGroup[item.cat] || 0) + 1;
      }
    });
    groups.forEach(function (group) {
      var cat = group.getAttribute("data-cat");
      var count = perGroup[cat] || 0;
      var groupTotal = group.getAttribute("data-total");
      group.hidden = count === 0;
      group.querySelector(".group-n").textContent =
        String(count) === groupTotal ? groupTotal : count + " of " + groupTotal;
    });
    chips.forEach(function (chip) {
      chip.setAttribute("aria-pressed", String(chip.getAttribute("data-filter") === current));
    });
    status.textContent = shown === total ? total + plural(total) : shown + " of " + total + plural(total);
    empty.hidden = shown !== 0;
  }

  var inputTimer = 0;
  q.addEventListener("input", function () {
    clearTimeout(inputTimer);
    inputTimer = setTimeout(apply, 80);
  });
  q.addEventListener("keydown", function (event) {
    if (event.key === "Escape" && q.value) {
      q.value = "";
      apply();
    }
  });

  chips.forEach(function (chip) {
    chip.addEventListener("click", function () {
      current = chip.getAttribute("data-filter");
      apply();
    });
  });

  /* The kit tiles jump to a group without JS. With JS they also filter. */
  [].forEach.call(doc.querySelectorAll(".tile[data-filter]"), function (tile) {
    tile.addEventListener("click", function (event) {
      if (event.button !== 0 || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
      event.preventDefault();
      current = tile.getAttribute("data-filter");
      apply();
      catalog.scrollIntoView({ block: "start" });
      var active = doc.querySelector('.chip[aria-pressed="true"]');
      if (active) active.focus({ preventScroll: true });
    });
  });

  if (clear) {
    clear.addEventListener("click", function () {
      q.value = "";
      current = "all";
      apply();
      q.focus();
    });
  }

  if (q.value) apply();
})();
