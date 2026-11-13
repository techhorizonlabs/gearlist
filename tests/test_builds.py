"""Priced builds (builds.json): totals equal the sum of their parts, only usable listings count,
and the page shows the file's own words and nothing else."""
import copy
import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import builds  # noqa: E402

RESOURCES = [{"id": "amd-radeon-ai-pro-r9700", "category": "Hardware", "name": "AMD Radeon AI PRO R9700"},
             {"id": "gemma-4", "category": "Models", "name": "Gemma 4"}]
REAL = json.loads((ROOT / "builds.json").read_text(encoding="utf-8"))
HIDDEN = {"tax_basis": "Hidden tax basis text", "verification": "Hidden verification text",
          "access_notes": "Hidden access notes text"}


def row(rid, part, sku, retailer, price, status="in_stock", usable=True, stock="In stock for delivery", conditions=""):
    return {"id": rid, "part": part, "sku": sku, "retailer": retailer, "price_aud": price, "currency": "AUD",
            "stock": stock, "warranty_displayed": "3 years", "conditions": conditions,
            "source": f"https://shop.example.com/{rid}", "checked_date": "2026-11-13", "promotion_end": None,
            "stock_status": status, "usable_in_component_total": usable, **HIDDEN}


def build(bid, name, parts, total, gpu):
    return {"id": bid, "name": name, "parts": [{"id": i, "quantity": q} for i, q in parts], "total_aud": total,
            "currency": "AUD", "dedicated_gpu_included": gpu, "main_tradeoff": "Lowest initial cost.",
            "upgrade_path": "Add one dedicated GPU in the main slot.",
            "verification": "Sourced planning comparison; nothing tested"}


def sample():
    """A small valid file: a processor at three shops, a drive bought twice and a graphics card."""
    data = {
        "schema_version": "1.0", "title": "Sample builds", "source_checked": "2026-11-13", "currency": "AUD",
        "default_build": "base", "introduction": "Two builds that share a processor.",
        "price_basis": "Prices as listed.", "totals_exclude": "Totals exclude delivery.",
        "unverified": "Fit has not been verified.", "capacity_note": "Two drives are mirrored.",
        "integrated_graphics_source": "https://maker.example.com/processor",
        "builds": [build("base", "Base", [("cpu-a", 1), ("ssd-a", 2)], 1539, False),
                   build("card", "With a card", [("cpu-a", 1), ("ssd-a", 2), ("gpu-a", 1)], 4438, True)],
        "pricebook": [row("cpu-a", "Processor X", "CPU-1", "Alpha", 469),
                      row("cpu-b", "Processor X", "CPU-1", "Beta", 499),
                      row("cpu-c", "Processor X", "CPU-1", "Gamma", 338.5, "out_of_stock", False, "Out of stock"),
                      row("ssd-a", "Drive Y", "SSD-1", "Alpha", 535),
                      row("gpu-a", "Card Z 32GB", "GPU-1", "Beta", 2899, conditions="Limit 1.")],
        "models": [{"tag": "model:9b", "size_gb": 7.6, "quant": "Q4", "purpose": "Small baseline",
                    "fit": "Should fit on one 32GB card.", "context": "Not tested",
                    "url": "https://models.example.com/library/model:9b"}],
        "stock_note": "Sold-out quotes are labelled.", "memory_note": "Download sizes.",
        "model_license_note": "Keep the licence.",
        "technical_sources": [{"topic": "Board slots", "url": "https://maker.example.com/board"}],
        "evaluation_note": "Trial the exact model files.", "selection_note": "This covers selected parts.",
    }
    return {"groups": [{
        "id": "sample", "group": "Hardware", "withheld": {},
        "roles": {"cpu-a": "Processor", "cpu-b": "Processor", "cpu-c": "Processor", "ssd-a": "SSD",
                  "gpu-a": builds.GPU_ROLE},
        "entries": {"gpu-a": "amd-radeon-ai-pro-r9700"}, "model_entries": {"model:9b": "gemma-4"},
        "page": copy.deepcopy(REAL["groups"][0]["page"]), "data": data,
    }]}


def changed(change):
    data = sample()
    change(data["groups"][0])
    return data


def problems(change):
    return builds.check(changed(change), RESOURCES)


class RealFileTest(unittest.TestCase):
    def setUp(self):
        self.resources = json.loads((ROOT / "resources.json").read_text(encoding="utf-8"))["resources"]

    def test_the_real_builds_pass(self):
        self.assertEqual(builds.check(REAL, self.resources), [])

    def test_every_total_is_the_sum_of_its_parts(self):
        for group in REAL["groups"]:
            rows = builds.rows_by_id(group)
            for b in group["data"]["builds"]:
                want = sum(round(rows[p["id"]]["price_aud"] * 100) * p["quantity"] for p in b["parts"])
                self.assertEqual(round(b["total_aud"] * 100), want, b["id"])

    def test_a_build_on_the_page_uses_only_listings_that_can_count_towards_a_total(self):
        for group in REAL["groups"]:
            rows = builds.rows_by_id(group)
            shown = builds.shown_builds(group)
            self.assertIn(group["data"]["default_build"], [b["id"] for b in shown])
            for b in shown:
                for p in b["parts"]:
                    self.assertIs(rows[p["id"]]["usable_in_component_total"], True, f'{b["id"]} {p["id"]}')
                    self.assertEqual(rows[p["id"]]["stock_status"], "in_stock", f'{b["id"]} {p["id"]}')

    def test_a_withheld_build_is_one_the_check_would_refuse(self):
        """A build is withheld for a reason. Once its listings are corrected, take it off the list."""
        for i, group in enumerate(REAL["groups"]):
            for bid in group.get("withheld", {}):
                data = copy.deepcopy(REAL)
                del data["groups"][i]["withheld"][bid]
                found = builds.check(data, self.resources)
                self.assertTrue(any(f"build {bid}:" in p and "not usable" in p for p in found), bid)

    def test_no_excluded_retailer_is_in_the_file(self):
        text = (ROOT / "builds.json").read_text(encoding="utf-8").lower()
        for name, host in builds.EXCLUDED_RETAILERS:
            self.assertNotIn(name.lower(), text)
            self.assertNotIn(host, text)


class CheckTest(unittest.TestCase):
    def test_a_good_file_passes(self):
        self.assertEqual(builds.check(sample(), RESOURCES), [])

    def expect(self, change, words):
        found = problems(change)
        self.assertTrue(any(words in p for p in found), f"{words!r} not in {found}")

    def test_unknown_part_ids_are_refused(self):
        self.expect(lambda g: g["data"]["builds"][0]["parts"].append({"id": "no-such-row", "quantity": 1}),
                    "is not a pricebook id")

    def test_a_total_that_is_not_the_sum_of_its_parts_is_refused(self):
        def one_dollar(g):
            g["data"]["builds"][0]["total_aud"] = 1540

        def one_cent(g):
            g["data"]["builds"][0]["total_aud"] = 1539.01

        def quantity(g):
            g["data"]["builds"][0]["parts"][1]["quantity"] = 1

        def price(g):
            g["data"]["pricebook"][0]["price_aud"] = 470

        for change in (one_dollar, one_cent, quantity, price):
            self.expect(change, "but its parts add up to")
        found = problems(one_dollar)
        self.assertTrue(any("A$1,540" in p and "A$1,539" in p and "a difference of A$1" in p for p in found), found)

    def test_a_listing_that_cannot_count_towards_a_total_is_refused_in_a_build(self):
        def out_of_stock(g):
            g["data"]["builds"][0]["parts"][0]["id"] = "cpu-c"
            g["data"]["builds"][0]["total_aud"] = 1408.5

        def flagged(g):
            g["data"]["pricebook"][3]["usable_in_component_total"] = False

        for change in (out_of_stock, flagged):
            self.expect(change, "is not usable in a component total")

    def test_a_withheld_build_may_hold_such_a_listing_but_stays_off_the_page(self):
        def hold(g):
            g["data"]["pricebook"][4].update(stock_status="out_of_stock", usable_in_component_total=False)
            g["withheld"] = {"card": "Its graphics card listing is flagged out of stock."}

        data = changed(hold)
        self.assertEqual(builds.check(data, RESOURCES), [])
        self.assertEqual([b["id"] for b in builds.shown_builds(data["groups"][0])], ["base"])

    def test_the_default_build_must_be_on_the_page(self):
        self.expect(lambda g: g["data"].update(default_build="nope"), "is not a build id")
        self.expect(lambda g: g.update(withheld={"base": "Held."}), "is withheld")
        self.expect(lambda g: g.update(withheld={"nope": "Held."}), "is not a build id")

    def test_usable_listings_must_be_in_stock(self):
        self.expect(lambda g: g["data"]["pricebook"][1].update(stock_status="out_of_stock"),
                    "is marked usable in a total but its stock_status is out_of_stock")
        self.expect(lambda g: g["data"]["pricebook"][1].update(stock_status="maybe"), "stock_status must be one of")
        self.expect(lambda g: g["data"]["pricebook"][1].update(usable_in_component_total="yes"), "must be true or false")

    def test_source_links_must_be_plain_https(self):
        for url in ("http://shop.example.com/cpu-a", "https://shop.example.com/cpu a", "javascript:alert(1)",
                    "https://user:pw@shop.example.com/x", "//shop.example.com/x", "", None):
            self.expect(lambda g, u=url: g["data"]["pricebook"][0].update(source=u), "must be one https URL")
        for url in ("https://shop.example.com/cpu-a?ref=gearlist", "https://shop.example.com/cpu-a?utm_source=x",
                    "https://shop.example.com/cpu-a#reviews"):
            self.expect(lambda g, u=url: g["data"]["pricebook"][0].update(source=u), "must not carry a query string")
        self.expect(lambda g: g["data"]["models"][0].update(url="http://models.example.com/x"), "must be one https URL")
        self.expect(lambda g: g["data"]["technical_sources"][0].update(url="ftp://maker.example.com/x"), "must be one https URL")
        self.expect(lambda g: g["data"].update(integrated_graphics_source="http://maker.example.com/x"), "must be one https URL")

    def test_dates_must_be_present_and_real(self):
        for value in (None, "", "13 November 2026", "2026-11-31", "2026-13-01"):
            self.expect(lambda g, v=value: g["data"]["pricebook"][0].update(checked_date=v), "checked_date must be a real date")
            self.expect(lambda g, v=value: g["data"].update(source_checked=v), "source_checked must be a real date")
        self.expect(lambda g: g["data"]["pricebook"][0].pop("checked_date"), "checked_date must be a real date")
        self.expect(lambda g: g["data"]["pricebook"][0].update(checked_date="2026-11-14"), "is after the package's source_checked date")

    def test_en_and_em_dashes_are_refused_anywhere_in_the_file(self):
        changes = [
            lambda g: g["data"].update(introduction="Two builds \u2013 one processor."),
            lambda g: g["data"]["builds"][0].update(upgrade_path="Add a card \u2014 later."),
            lambda g: g["data"]["pricebook"][0].update(stock="Ships in 2\u20134 days"),
            lambda g: g["data"]["pricebook"][0].update(access_notes="Hidden \u2013 but still checked"),
            lambda g: g["data"]["models"][0].update(fit="Fits \u2013 just."),
            lambda g: g["page"].update(default_label="Start \u2013 here"),
            lambda g: g["roles"].update({"cpu-a": "Processor \u2013 main"}),
        ]
        for change in changes:
            self.expect(change, "has an en or em dash")

    def test_control_characters_and_line_breaks_are_refused(self):
        for bad in ("two\nlines", "tab\there", "nul\x00", "sep\u2028arator", "esc\x1b[0m"):
            self.expect(lambda g, b=bad: g["data"]["builds"][0].update(main_tradeoff=b), "control character")
            self.expect(lambda g, b=bad: g["data"]["pricebook"][0].update(conditions=b), "control character")

    def test_overlong_and_empty_text_is_refused(self):
        self.expect(lambda g: g["data"].update(unverified="x" * (builds.NOTE_MAX + 1)), f"over {builds.NOTE_MAX} characters")
        self.expect(lambda g: g["data"]["pricebook"][0].update(part="x" * (builds.SHORT_MAX + 1)), f"over {builds.SHORT_MAX} characters")
        self.expect(lambda g: g["data"]["builds"][0].update(name=""), "text is empty")
        self.expect(lambda g: g["data"].update(totals_exclude=" Padded"), "has spaces at the start or end")
        self.expect(lambda g: g["data"].pop("stock_note"), "must be text")

    def test_prices_are_written_with_a_dollar_sign_after_an_a(self):
        self.expect(lambda g: g["data"]["builds"][0].update(main_tradeoff="Costs $350 more."), "write prices as A$8,630")
        self.expect(lambda g: g["data"]["pricebook"][0].update(price_aud=0), "price_aud must be a number above zero")
        self.expect(lambda g: g["data"]["pricebook"][0].update(price_aud="469"), "price_aud must be a number above zero")
        self.expect(lambda g: g["data"]["pricebook"][0].update(price_aud=469.005), "at most two decimal places")
        self.expect(lambda g: g["data"]["pricebook"][0].update(currency="USD"), "currency must be AUD")

    def test_a_figure_in_a_sentence_must_come_from_the_pricebook(self):
        ok = sample()
        ok["groups"][0]["data"]["builds"][1]["main_tradeoff"] = "A$2,899 above the base build, all of it the card."
        self.assertEqual(builds.check(ok, RESOURCES), [])
        self.expect(lambda g: g["data"]["builds"][1].update(main_tradeoff="A$2,900 above the base build."),
                    "A$2,900 is not a pricebook price")
        self.expect(lambda g: g["data"].update(selection_note="Save A$123 here."), "A$123 is not a pricebook price")

    def test_hype_words_are_refused_in_sentences_but_not_in_links(self):
        for word in ("seamless", "powerful", "robust", "unlock", "leverage", "game-changing", "best"):
            self.expect(lambda g, w=word: g["data"]["builds"][0].update(main_tradeoff=f"The {w} choice."), "uses the word")
        ok = sample()
        ok["groups"][0]["data"]["pricebook"][0]["source"] = "https://shop.example.com/unlocked-processor-best-price"
        self.assertEqual(builds.check(ok, RESOURCES), [])

    def test_listings_from_excluded_retailers_are_refused(self):
        for name, host in builds.EXCLUDED_RETAILERS:
            self.expect(lambda g, n=name: g["data"]["pricebook"][1].update(retailer=n), "are not published")
            self.expect(lambda g, h=host: g["data"]["pricebook"][1].update(source=f"https://www.{h}/product/x"), "are not published")

    def test_parts_need_whole_quantities_and_no_repeats(self):
        self.expect(lambda g: g["data"]["builds"][0]["parts"][0].update(quantity=0), "whole quantity of 1 or more")
        self.expect(lambda g: g["data"]["builds"][0]["parts"][0].update(quantity=1.5), "whole quantity of 1 or more")
        self.expect(lambda g: g["data"]["builds"][0]["parts"].append({"id": "cpu-a", "quantity": 1}), "is listed twice")
        self.expect(lambda g: g["data"]["builds"][0].update(parts=[]), "parts must be a non-empty list")
        self.expect(lambda g: g["data"]["builds"].append(copy.deepcopy(g["data"]["builds"][0])), "id is repeated")
        self.expect(lambda g: g["data"]["pricebook"].append(copy.deepcopy(g["data"]["pricebook"][0])), "id is repeated")

    def test_the_wrapper_maps_must_match_the_data(self):
        self.expect(lambda g: g["roles"].pop("ssd-a"), "ssd-a has no role")
        self.expect(lambda g: g["roles"].update({"ghost": "Case"}), "'ghost' is not a pricebook id")
        self.expect(lambda g: g["roles"].update({"cpu-b": "Case"}), "must share one role")
        self.expect(lambda g: g["entries"].update({"gpu-a": "no-such-entry"}), "is not an entry id in resources.json")
        self.expect(lambda g: g["entries"].update({"ghost": "gemma-4"}), "is not a pricebook id")
        self.expect(lambda g: g["model_entries"].update({"ghost:1b": "gemma-4"}), "is not a model tag")
        self.expect(lambda g: g.update(group="No such group"), "is not a Gearlist group")
        self.expect(lambda g: g.update(id="Not A Slug"), "id must be lowercase letters")
        self.expect(lambda g: g["data"]["builds"][0].update(dedicated_gpu_included=True), "but its parts say otherwise")
        self.expect(lambda g: g["data"]["pricebook"][1].update(part="Processor W"), "must share one part name")

    def test_the_page_wording_is_checked_too(self):
        self.expect(lambda g: g["page"].pop("read_line"), "page read_line: must be text")
        self.expect(lambda g: g["page"].update(read_line="Read on {day}."), "uses {day}")
        self.expect(lambda g: g["page"].update(default_label="Start {here"), "unmatched curly bracket")
        self.expect(lambda g: g["page"].update(group_link="See the builds."), "must hold {link} once")
        self.expect(lambda g: g["page"].update(parts_columns=["Part"]), "must list 6 column names")
        self.expect(lambda g: g["page"]["not_compared"].pop("conditional"), "needs one label for each of")
        self.expect(lambda g: g["page"].update(extra="Unused"), "has labels the page does not use")
        self.expect(lambda g: g["page"].update(default_label="The best one"), "uses the word")

    def test_messages_have_no_en_or_em_dashes(self):
        for p in problems(lambda g: g["data"].update(introduction="Two builds \u2013 one processor.")):
            self.assertNotRegex(p, "[\u2013\u2014]")


class HelpersTest(unittest.TestCase):
    def test_money(self):
        self.assertEqual(builds.money(8630), "A$8,630")
        self.assertEqual(builds.money(338.5), "A$338.50")
        self.assertEqual(builds.money(888.99), "A$888.99")
        self.assertEqual(builds.money(16199), "A$16,199")
        self.assertEqual(builds.money(49), "A$49")

    def test_sums_are_exact_in_cents(self):
        group = sample()["groups"][0]
        group["data"]["pricebook"][0]["price_aud"] = 0.1
        group["data"]["builds"][0]["parts"] = [{"id": "cpu-a", "quantity": 3}]
        self.assertEqual(builds.build_cents(group["data"]["builds"][0], builds.rows_by_id(group)), 30)

    def test_the_cheapest_in_stock_listing_is_named_and_out_of_stock_ones_are_not_compared(self):
        group = sample()["groups"][0]
        (sku, noted), = builds.same_part_shops(group)
        self.assertEqual(sku, "CPU-1")
        self.assertEqual([(r["id"], kind, more) for r, kind, more in noted],
                         [("cpu-a", "lowest", 0), ("cpu-b", "more", 3000), ("cpu-c", "not_compared", 0)])
        # The out-of-stock listing is cheaper than both, and still is not the lowest.
        self.assertLess(group["data"]["pricebook"][2]["price_aud"], group["data"]["pricebook"][0]["price_aud"])
        group["data"]["pricebook"][1]["price_aud"] = 469
        (_, noted), = builds.same_part_shops(group)
        self.assertEqual([kind for _, kind, _ in noted], ["equal_lowest", "equal_lowest", "not_compared"])

    def test_graphics_cards_and_long_dates(self):
        group = sample()["groups"][0]
        base, card = group["data"]["builds"]
        self.assertEqual(builds.graphics_cards(group, base), [])
        self.assertEqual([r["id"] for r in builds.graphics_cards(group, card)], ["gpu-a"])
        self.assertEqual(builds.long_date("2026-11-13"), "13 November 2026")
        self.assertEqual(builds.split_link("See {link} on {date}.", date="1 May"), ("See ", " on 1 May."))


class SiteBuilderTest(unittest.TestCase):
    """site/build_site.py checks builds.json itself, and the page shows the file's words only."""

    @classmethod
    def setUpClass(cls):
        spec = importlib.util.spec_from_file_location("build_site_for_builds", ROOT / "site" / "build_site.py")
        cls.site = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.site)
        cls.entries = [
            {"id": "amd-radeon-ai-pro-r9700", "category": "Hardware", "name": "AMD Radeon AI PRO R9700",
             "source_checked": "2026-11-07"},
            {"id": "gemma-4", "category": "Models", "name": "Gemma 4", "source_checked": "2026-11-07"},
        ]

    def render(self, data):
        self.assertEqual(builds.check(data, self.entries), [])
        groups = self.site.group_entries(self.entries, {}, data["groups"])
        g = next(x for x in groups if x["builds"])
        b = g["builds"][0]
        og = ("https://gearlist.build/social-preview.png", 1280, 640, "Alt")
        title, description = self.site.builds_title(b), self.site.builds_description(b)
        html = self.site.render_builds_page(b, g, title=title, description=description, og=og, groups=groups,
                                            assets={"css": "", "head_js": "", "app_js": ""})
        md = self.site.render_builds_md(b, g, groups, title=title, description=description, og=og)
        main = html[html.index("<main"):html.index("</main>")]
        return main, md, g

    def load_with(self, data):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "builds.json"
            path.write_text(json.dumps(data), encoding="utf-8")
            with mock.patch.object(self.site, "BUILDS_FILE", path):
                return self.site.load_builds(RESOURCES)

    def test_the_standalone_builder_refuses_bad_builds(self):
        bad = [changed(lambda g: g["data"]["builds"][0].update(total_aud=1)),
               changed(lambda g: g["data"]["pricebook"][0].update(source="http://shop.example.com/x")),
               changed(lambda g: g["data"]["builds"][0]["parts"].append({"id": "nope", "quantity": 1})),
               changed(lambda g: g["data"].update(introduction="An em dash \u2014 here."))]
        for data in bad:
            with self.assertRaises(SystemExit):
                self.load_with(data)
        self.assertEqual([g["id"] for g in self.load_with(sample())], ["sample"])

    def test_a_standalone_build_stops_on_bad_builds_before_writing(self):
        bad = copy.deepcopy(REAL)
        bad["groups"][0]["data"]["builds"][1]["total_aud"] += 1
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "builds.json"
            path.write_text(json.dumps(bad), encoding="utf-8")
            wrote = []
            with mock.patch.object(self.site, "BUILDS_FILE", path), \
                    mock.patch.object(self.site, "build_pages", side_effect=lambda *a, **k: wrote.append(1)), \
                    mock.patch.object(self.site.sys, "argv", ["build_site.py"]):
                with self.assertRaises(SystemExit) as stop:
                    self.site.main()
            self.assertIn("but its parts add up to", str(stop.exception))
            self.assertEqual(wrote, [])

    def test_the_page_shows_each_total_parts_and_the_cheapest_shop_in_words(self):
        main, md, _ = self.render(sample())
        for text in ("A$1,539", "A$4,438", "A$1,070", "2 at A$535 each", "A$2,899", "A$338.50"):
            self.assertIn(text, main)
            self.assertIn(text, md)
        self.assertIn("<strong>Lowest in stock</strong>", main)
        self.assertIn("<strong>A$30 more</strong>", main)
        self.assertIn("<strong>Out of stock, not compared</strong>", main)
        self.assertIn('<a href="/tools/amd-radeon-ai-pro-r9700/">Card Z 32GB</a>', main)
        self.assertIn("[Card Z 32GB](https://gearlist.build/tools/amd-radeon-ai-pro-r9700/)", md)
        self.assertIn('href="https://shop.example.com/gpu-a" rel="noopener"', main)
        self.assertEqual(main.count('<span class="pick">Start here</span>'), 2)
        self.assertIn("Base (Start here)", md)
        self.assertIn('<details class="build" id="build-base" open>', main)
        self.assertIn('<details class="build" id="build-card">', main)

    def test_a_withheld_build_is_named_but_its_total_and_parts_are_not_shown(self):
        def hold(g):
            g["data"]["pricebook"][4].update(stock_status="out_of_stock", usable_in_component_total=False)
            g["withheld"] = {"card": "Its graphics card listing is flagged out of stock."}

        main, md, _ = self.render(changed(hold))
        for out in (main, md):
            self.assertNotIn("A$4,438", out)
            self.assertIn("Held back until a listing each one uses is confirmed: With a card.", out)
        self.assertNotIn('id="build-card"', main)

    def test_hidden_listing_fields_never_reach_the_page_or_its_markdown(self):
        main, md, _ = self.render(sample())
        for name in self.site.BUILDS_HIDDEN_ROW_FIELDS:
            self.assertIn(name, HIDDEN)
            self.assertNotIn(HIDDEN[name], main)
            self.assertNotIn(HIDDEN[name], md)

    def test_every_sentence_on_the_page_comes_from_the_file(self):
        """Swap every string in the data and the page wording for a marker. If the page still
        shows an old sentence, the builder is holding wording of its own."""
        before, before_md, _ = self.render(sample())
        data = sample()
        group = data["groups"][0]
        marks = {}

        def mark(holder, key, keep=""):
            marks[f"MARK{len(marks)}X"] = holder[key]
            holder[key] = f"MARK{len(marks) - 1}X{keep}"

        pack = group["data"]
        for key in ("title", "introduction", "totals_exclude", "unverified", "capacity_note", "stock_note",
                    "memory_note", "model_license_note", "evaluation_note", "selection_note"):
            mark(pack, key)
        for b in pack["builds"]:
            for key in ("name", "main_tradeoff", "upgrade_path"):
                mark(b, key)
        for r in pack["pricebook"]:
            for key in ("stock", "conditions"):
                if r[key]:
                    mark(r, key)
        for m in pack["models"]:
            for key in ("purpose", "fit"):
                mark(m, key)
        for s in pack["technical_sources"]:
            mark(s, "topic")
        role_marks = {}
        for rid, role in group["roles"].items():
            if role != builds.GPU_ROLE:  # this role name is how a graphics card is found, so it stays
                if role not in role_marks:
                    mark(group["roles"], rid)
                    role_marks[role] = group["roles"][rid]
                group["roles"][rid] = role_marks[role]
        page = group["page"]
        for key, allowed in builds.PAGE_TEXT.items():
            mark(page, key, "".join(" {" + a + "}" for a in sorted(allowed)))
        for key in builds.PAGE_COLUMNS:
            for i in range(len(page[key])):
                mark(page[key], i)
        for status in page["not_compared"]:
            mark(page["not_compared"], status)
        after, after_md, _ = self.render(data)
        for marker, old in marks.items():
            if len(old) < 12 or old == builds.GPU_ROLE:
                continue  # short labels such as "Source" can sit inside other text; the role stays
            self.assertNotIn(old, after, f"the page still shows {old!r}")
            self.assertNotIn(old, after_md, f"the Markdown still shows {old!r}")
        shown = [m for m in marks if m in after]
        self.assertGreater(len(shown), 55)
        # The only wording missing from the main block is for the head, the group page and
        # llms.txt, or for a case this sample does not have: a tie, a withheld build, and
        # listings left out of the comparison for a reason other than being out of stock.
        missing = {marks[m] for m in marks if m not in after}
        page_real = sample()["groups"][0]["page"]
        elsewhere = {page_real[k] for k in ("title_tag", "description", "og_alt", "og_tile_title", "og_tile_text",
                                            "group_link", "llms_line", "equal_lowest", "withheld_note")}
        elsewhere |= {page_real["not_compared"][k] for k in ("in_stock", "conditional")}
        self.assertLessEqual(missing, elsewhere, missing - elsewhere)

    def test_text_is_escaped_in_html_and_markdown(self):
        data = changed(lambda g: g["data"]["builds"][0].update(
            main_tradeoff="<script>alert(1)</script> | [x](https://evil.example) & more"))
        main, md, _ = self.render(data)
        self.assertNotIn("<script>alert(1)", main)
        self.assertIn("&lt;script&gt;alert(1)&lt;/script&gt;", main)
        self.assertNotIn("](https://evil.example)", md)
        self.assertNotIn("<script>", md)

    def test_the_group_page_gets_one_sentence_with_the_link(self):
        _, _, g = self.render(sample())
        html = self.site.builds_links_html(g)
        self.assertEqual(html.count("<p "), 1)
        self.assertIn('See <a href="/builds/sample/">Sample builds</a> for part lists with Australian retailer prices '
                      "read on 13 November 2026.</p>", html)
        md = "\n".join(self.site.builds_links_md(g))
        self.assertIn("See [Sample builds](https://gearlist.build/builds/sample/) for part lists", md)


if __name__ == "__main__":
    unittest.main()
