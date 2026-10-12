"""Check discovery, portable installation, and installed tool execution."""

import base64
import json
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from build_skill import ROOT, BUNDLE, build
from install_skill import install


class CodexSkillTests(unittest.TestCase):
    def test_bundle_is_current(self):
        self.assertEqual(build(check=True), [])

    def test_stale_script_is_detected_without_writing(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            for name in ('SKILL.template.md', 'requirements.txt', 'LICENSE'):
                (root / name).write_bytes((ROOT / name).read_bytes())
            (root / 'scripts').mkdir()
            source = root / 'scripts/tool.py'
            source.write_text('print(1)\n')
            build(root)
            before = (root / BUNDLE / 'scripts/tool.py').read_bytes()
            source.write_text('print(2)\n')
            self.assertIn(BUNDLE / 'scripts/tool.py', build(root, check=True))
            self.assertEqual((root / BUNDLE / 'scripts/tool.py').read_bytes(), before)
            build(root)
            self.assertEqual(build(root, check=True), [])

    def test_install_is_portable_and_preserves_existing_skill(self):
        with tempfile.TemporaryDirectory(prefix='spine skill test ') as temp:
            destination = install(Path(temp) / 'skills/spine-animation')
            self.assertTrue((destination / 'LICENSE').is_file())
            text = (destination / 'SKILL.md').read_text()
            for link in re.findall(r'\]\(([^)]+)\)', text):
                self.assertTrue((destination / link).is_file(), link)
            with self.assertRaises(FileExistsError):
                install(destination)
            config = Path(temp) / 'config.json'
            config.write_text(json.dumps({
                'skeleton': {'name': 'test', 'width': 100, 'height': 200},
                'bones': [{'name': 'root'}, {'name': 'hip', 'parent': 'root', 'y': 50},
                          {'name': 'torso', 'parent': 'hip'}],
                'slots': [{'name': 'body', 'bone': 'hip', 'attachment': 'body'}],
                'attachments': {'body': {'width': 100, 'height': 200}},
                'animations': ['idle'],
            }))
            skeleton = Path(temp) / 'skeleton.json'
            subprocess.run([sys.executable, str(destination / 'scripts/build_spine_json.py'),
                            '--config', str(config), '--output', str(skeleton)],
                           check=True, capture_output=True)
            data = json.loads(skeleton.read_text())
            self.assertTrue(data['skeleton']['spine'].startswith('4.2'))
            self.assertIn('idle', data['animations'])
            self.assertEqual(data['slots'][0]['bone'], 'hip')
            atlas = Path(temp) / 'test.atlas'
            atlas.write_text('test.png\nsize: 1,1\nformat: RGBA8888\nfilter: Linear,Linear\nrepeat: none\n')
            image = Path(temp) / 'test.png'
            # Valid 1x1 PNG; no external image generation is needed.
            image.write_bytes(base64.b64decode(
                "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8"
                "/x8AAwMCAO+aXioAAAAASUVORK5CYII="))
            preview = Path(temp) / 'preview.html'
            subprocess.run([sys.executable, str(destination / 'scripts/generate_spine_player.py'),
                            '--skeleton', str(skeleton), '--atlas', str(atlas),
                            '--atlas-image', str(image), '--output', str(preview)],
                           check=True, capture_output=True)
            html = preview.read_text()
            self.assertIn('spine-player', html)
            self.assertIn('data:', html)


if __name__ == '__main__':
    unittest.main()
