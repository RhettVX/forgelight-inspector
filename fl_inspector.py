from pathlib import Path
from typing import List, Union, Dict, Tuple, Set
from collections import ChainMap
import re
import itertools
from pprint import pprint

from jenkins_hash.jenkins import lookup2

from DbgPack.asset_manager import AssetManager, AbstractAsset

test_path = Path(r'C:\A\Games\PlanetSide 2 Test')
oldtest_path = Path(r'D:\WindowsUsers\Rhett\Desktop\forgelight-toolbox\Backups\04-16-21-TEST')
live_path = Path(r'C:\A\Games\PlanetSide 2')
admin_path = Path(r'D:\WindowsUsers\Rhett\Desktop\PlanetSide 2 Admin')
beta_path = Path(r'D:\WindowsUsers\Rhett\Desktop\PlanetSide 2 Beta')
js_path = Path(r'D:\WindowsUsers\Rhett\Desktop\H1Z1 - Just Survive')

class ForgeLightGame:
    assets_subpath = r'Resources\Assets'
    locale_subpath = r'Locale'

    def __init__(self, name, path):
        self.name = name
        self.path = path
        self.asset_manager = AssetManager(list((path / self.assets_subpath).glob('*.pack*')))

    def extract_assets(self, asset_names: List[Union[str, int]], out_path: Path = None):
        if not out_path:
            outdir = Path(f'./{self.name}_output')
        else:
            outdir = out_path

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

    # TODO(rhett): THIS IS SUUUUUPER WASTEFUL
    # TODO(rhett): This WHOOOOLE thing is so BAAAAAD
    def combine_weapon_info(self):
        example_id = 6009891

        client_item_definitions    = self.asset_manager['ClientItemDefinitions.txt']
        client_item_datasheet_data = self.asset_manager['ClientItemDatasheetData.txt']
        fire_mode_display_stats    = self.asset_manager['FireModeDisplayStats.txt']
        # projectile_display_stats   = self.asset_manager['ProjectileDisplayStats.txt']

        # store data
        item_definition_data  = [line.split('^')[:-1] for line in client_item_definitions.get_data().decode('utf8').split('\r\n')]
        item_datasheet_data   = [line.split('^')[:-1] for line in client_item_datasheet_data.get_data().decode('utf8').split('\r\n')]
        firemode_display_data = [line.split('^')[:-1] for line in fire_mode_display_stats.get_data().decode('utf8').split('\r\n')]

        # Create key list
        item_definition_keys  = item_definition_data[0]
        item_datasheet_keys   = item_datasheet_data[0]
        firemode_display_keys = firemode_display_data[0]
        # print(item_definition_keys)
        # print(item_datasheet_keys)
        # print(firemode_display_keys)

        for i in range(6009891, 6009910+1):

            # go to id in item defs
            item_definition = {}
            for entry in item_definition_data[1:]:
                if int(entry[0]) == i:
                    # read def entry
                    item_definition = dict(zip(item_definition_keys, entry))
                    break

            # go to id in datasheet
            item_datasheet = {}
            for entry in item_datasheet_data[1:]:
                if int(entry[0]) == i:
                    # read datasheet entry
                    item_datasheet = dict(zip(item_datasheet_keys, entry))
                    break

            # go to id in datasheet
            firemode_display = {}
            for entry in firemode_display_data[1:]:
                if int(entry[0]) == 0:
                # if int(entry[0]) == int(item_datasheet['WEAPON_ID']):
                    # read datasheet entry
                    firemode_display = dict(zip(firemode_display_keys, entry))
                    break

            locale_info = [x.split('\t') for x in (self.path / self.locale_subpath / 'en_us_data.dir').read_text().split('\n')[:-1] if x[0] != '#']



            locale_data = (self.path / self.locale_subpath / 'en_us_data.dat').read_bytes()

            name_hash = lookup2(f'Global.Text.{item_definition["NAME_ID"]}')
            description_hash = lookup2(f'Global.Text.{item_definition["DESCRIPTION_ID"]}')

            name = ''
            description = ''

            for entry in locale_info:
                if int(entry[0]) == name_hash:
                    # print(entry)
                    name = locale_data[int(entry[1]):int(entry[1])+int(entry[2])].decode('utf8').split('\t')[2]
                    break
            # print(name)

            for entry in locale_info:
                if int(entry[0]) == description_hash:
                    # print(entry)
                    description = locale_data[int(entry[1]):int(entry[1])+int(entry[2])].decode('utf8').split('\t')[2]
                    break
            # print(description)

            # return

            # raw_string = locale_data[]
            # pprint(locale_entries[0])
            # locale_dict = {int(x[0]): x[2] for x in locale_entries}
            # pprint(locale_dict)


            # print(name);

            with open('nso_weapons.txt', 'a') as out_file:

                # pprint(item_definition)
                # pprint(item_datasheet)
                # pprint(firemode_display)

                out_file.write(('-'*64)+'\n')
                out_file.write((f'Item Id: {i}\n'))
                out_file.write((f'Name: {name}\n'))
                out_file.write((f'Description: {description}\n'))
                out_file.write((f'Actor: {item_definition["MODEL_NAME"]}\n'))

                out_file.write((f'\nMax Damage (real): {item_datasheet["DAMAGE_FALLOFF"]}\n'))
                out_file.write((f'Firerate: {round(60000 / float(item_datasheet["REFIRE_TIME_MS"]))}rpm\n'))
                # out_file.write((f'(?)Max Damage range: {firemode_display["MAX_DAMAGE"]}@{firemode_display["MAX_DAMAGE_RANGE"]}m\n'))
                # out_file.write((f'(?)Min Damage range: {firemode_display["MIN_DAMAGE"]}@{firemode_display["MIN_DAMAGE_RANGE"]}m\n'))

                out_file.write((f'\nMagazine Size: {item_datasheet["CLIP_SIZE"]}\n'))
                out_file.write((f'Short Reload: {float(item_datasheet["RELOAD_TIME_MS"]) / 1000}s\n\n\n'))


    def trace_requisites(self, root_name: str, mode='zone'):
        # Key will be the casefolded name. proper case is stored in the asset hopefully
        completed_files: Dict[str, AbstractAsset] = {}

        # use casefold for lookup. value uses scraped case
        skipped_files: Dict[str, str] = {}
        # file_queue: Dict[str, str] = {}

        if mode == 'dma':
            root_asset = self.asset_manager[root_name]
            used_textures = {v.casefold(): v for v in self._scrape_asset(root_asset, 'dds')}
            for x in used_textures:
                # print(x)
                asset = self.asset_manager[x]
                if asset:
                    completed_files[x.casefold()] = asset

            print('Exporting')
            for a in completed_files.values():
                # print(f'{a.name}')
                outdir = Path('traced_reqs')
                outdir.mkdir(exist_ok=True, parents=True)
                (outdir / a.name).write_bytes(a.get_data())


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

        # breakpoint()


a_names = """
          """.split()

if __name__ == '__main__':
    to_extract = [
        *a_names,
    ]

    print('Loading game files...')
    # ps2_live = ForgeLightGame('PS2_Live', live_path)
    ps2_test = ForgeLightGame('PS2_Test', test_path)
    # old_live = ForgeLightGame('PS2_Live_Old', Path(r'D:\WindowsUsers\Rhett\Desktop\forgelight-toolbox\Backups\05-20-21-LIVE'))
    # test_next = ForgeLightGame('PS2_Test_Next', Path(r'D:\WindowsPrograms\Steam\steamapps\common\PlanetSide 2 - Test'))

    print('Merging weapon data...')
    ps2_test.combine_weapon_info()
    # ps2_live.combine_weapon_info()

    # print('Extracting specified assets...')
    # ps2_live.extract_assets(to_extract)
    # ps2_test.extract_assets(to_extract)
    # old_live.extract_assets(to_extract)
    # test_next.extract_assets(to_extract)

    # print('Tracing requisites...')
    # psa_final.trace_requisites('Sanctuary.zone')
    # Nexus makes a good example because it is smaller and has some missing materials that I should be able to trace

    print('Finished')
    pass
