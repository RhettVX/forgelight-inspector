from pathlib import Path
from typing import List, Union, Dict, Tuple, Set
from collections import ChainMap
import re

from DbgPack.asset_manager import AssetManager, AbstractAsset

test_path = Path(r'A:\Games\PlanetSide 2 Test')


class ForgeLightGame:
    assets_subpath = r'Resources\Assets'
    locale_subpath = r'Locale'

    def __init__(self, name, path):
        self.name = name
        self.path = path
        self.asset_manager = AssetManager(list((path / self.assets_subpath).glob('*.pack*')))

    def extract_assets(self, asset_names: List[Union[str, int]]):
        outdir = Path(f'./{self.name}_output')
        outdir.mkdir(parents=True, exist_ok=True)

        for name in asset_names:
            asset = self.asset_manager[name]
            if not asset:
                print(f'Skipping {name}')
                continue

            (outdir / (asset.name if asset.name else f'{asset.name_hash:#018x}.bin')).write_bytes(asset.get_data())

    @staticmethod
    def _scrape_asset(asset: AbstractAsset, pattern: str) -> Set[str]:
        data = asset.get_data()
        mo = re.findall(bytes(r'([><\w-]+\.(' + r'|'.join(pattern.split()) + r'))', 'utf-8'), data)
        if mo:
            return set({m[0].decode('utf8').casefold(): m[0].decode('utf8') for m in mo}.values())
        return set()

    def trace_requisites(self, root_name: str, mode='zone'):
        # Key will be the casefolded name. proper case is stored in the asset hopefully
        completed_files: Dict[str, AbstractAsset] = {}

        # use casefold for lookup. value uses scraped case
        skipped_files: Dict[str, str] = {}
        # file_queue: Dict[str, str] = {}

        if mode == 'zone':
            # Initial scrape
            root_asset = self.asset_manager[root_name]
            file_queue = {v.casefold(): v for v in self._scrape_asset(root_asset, 'adr')}
            completed_files[root_name.casefold()] = root_asset
            to_skip = ChainMap(skipped_files, completed_files)

            while file_queue:
                name_pair = file_queue.popitem()
                if name_pair[0] in to_skip:
                    # Skipped this file already for some reason
                    continue

                asset = self.asset_manager[name_pair[1]]
                if not asset:
                    print(f'Skipping {name_pair[1]}')
                    skipped_files[name_pair[0]] = name_pair[1]
                    continue

                print(f'file_queue: {name_pair[0]}')
                # breakpoint()

                file_queue.update({v.casefold(): v for v in self._scrape_asset(asset, 'dme dma dds cdt') if v[0] not in to_skip})
                completed_files[name_pair[0]] = asset
                # breakpoint()

                # Why is this here twice?
                # print(f'file_queue: {name_pair[0]}')
                # # breakpoint()
                #
                # file_queue.update({v.casefold(): v for v in self._scrape_asset(asset, 'dme dma dds cdt') if v[0] not in to_skip})
                # completed_files[name_pair[0]] = asset
                # # breakpoint()

            print('Exporting')
            for a in completed_files.values():
                # print(f'{a.name}')
                outdir = Path('traced_reqs')
                outdir.mkdir(exist_ok=True, parents=True)
                (outdir / a.name).write_bytes(a.get_data())

        breakpoint()


a_names = """
        """.split()

if __name__ == '__main__':
    to_extract = [
        *a_names
    ]

    print('Loading game files...')
    # ps2_test = ForgeLightGame('PS2_Test', test_path)
    psa_game = ForgeLightGame('PS_Arena', Path(r'D:\WindowsUsers\Rhett\Desktop\Planetside Arena'))

    # print('Extracting specified assets...')
    # ps2_test.extract_assets(to_extract)

    print('Tracing requisites...')
    # Nexus makes a good example because it is smaller and has some missing materials that I should be able to trace
    # ps2_test.trace_requisites('Nexus.zone')
    psa_game.trace_requisites('AmerishBR.zone')

    print('Finished')
    pass
