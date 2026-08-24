import base64
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from backend.game.map_gallery import (
    _is_valid_png,
    find_map,
    generate_map_image,
    initial_map_records,
    install_initial_maps,
    list_maps,
    load_map_base64,
    register_map,
)
from backend.game.state import GameState


class NoImageProvider:
    pass


class MapGalleryTests(unittest.TestCase):
    def test_space_world_starts_with_universe_and_world_maps(self):
        records = initial_map_records({
            "name": "Star Reach",
            "genre": "space opera",
            "player_request": "Travel between many planets in a starship.",
        })
        self.assertEqual([record["map_type"] for record in records], ["universe", "world"])
        self.assertEqual(records[0]["title"], "Star Reach Universe Map")
        self.assertEqual(records[1]["title"], "Star Reach World Map")

    def test_grounded_world_starts_with_only_world_map(self):
        records = initial_map_records({
            "name": "Harbor County",
            "genre": "modern mystery",
            "player_request": "A detective story in a coastal county.",
        })
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]["map_type"], "world")

    def test_discover_map_state_change_is_saved_once(self):
        with TemporaryDirectory() as directory:
            state = GameState(path=str(Path(directory) / "campaign.json"))
            state.apply_changes([{
                "type": "discover_map",
                "map_type": "town",
                "title": "New York City Map",
                "location": "New York City",
                "description": "Known streets and public landmarks.",
            }])
            state.apply_changes([{
                "type": "discover_map",
                "map_type": "town",
                "title": "New York City Map",
                "location": "New York City",
            }])
            maps = list_maps(state.data)
            self.assertEqual(len(maps), 1)
            self.assertEqual(maps[0]["title"], "New York City Map")

    def test_cached_map_image_loads_as_base64(self):
        with TemporaryDirectory() as directory:
            output_dir = Path(directory)
            state = {}
            records = initial_map_records({"name": "Green Vale", "genre": "fantasy"})
            install_initial_maps(state, records)
            record = find_map(state, records[0]["id"])
            generate_map_image(NoImageProvider(), {"name": "Green Vale"}, record, output_dir)
            encoded = load_map_base64(record, output_dir)
            self.assertTrue(encoded)
            self.assertTrue(base64.b64decode(encoded).startswith(b"\x89PNG"))
            self.assertTrue(_is_valid_png(base64.b64decode(encoded)))
            self.assertEqual(record["image_status"], "ready")

    def test_corrupt_cached_map_is_replaced_automatically(self):
        with TemporaryDirectory() as directory:
            output_dir = Path(directory)
            record = initial_map_records({"name": "Green Vale", "genre": "fantasy"})[0]
            image_path = output_dir / record["image_file"]
            image_path.write_bytes(b"not really a png")
            record["image_status"] = "ready"

            generate_map_image(NoImageProvider(), {"name": "Green Vale"}, record, output_dir)

            repaired = image_path.read_bytes()
            self.assertTrue(_is_valid_png(repaired))
            self.assertEqual(record["image_status"], "ready")
            self.assertEqual(record["image_source"], "fallback")

    def test_truncated_png_is_not_returned_to_godot(self):
        with TemporaryDirectory() as directory:
            output_dir = Path(directory)
            record = initial_map_records({"name": "Green Vale", "genre": "fantasy"})[0]
            image_path = output_dir / record["image_file"]
            image_path.write_bytes(b"\x89PNG\r\n\x1a\n" + b"broken")

            self.assertEqual(load_map_base64(record, output_dir), "")
            self.assertEqual(record["image_status"], "pending")

    def test_map_titles_gain_map_suffix(self):
        state = {"turn": 7}
        record = register_map(state, {
            "map_type": "town",
            "title": "Moonport",
            "location": "Moonport",
        })
        self.assertEqual(record["title"], "Moonport Map")
        self.assertEqual(record["discovered_turn"], 7)


if __name__ == "__main__":
    unittest.main()
