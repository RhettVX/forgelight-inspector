from pathlib import Path
from typing import List, Union, Dict, Tuple
import re

from DbgPack.asset_manager import AssetManager, AbstractAsset
from DbgPack.hash import crc64

beta_path = Path(r'D:\WindowsUsers\Rhett\Desktop\Planetside 2 Beta')
test_path = Path(r'A:\Games\PlanetSide 2 Test')
live_path = Path(r'A:\Games\PlanetSide 2')

# known_exts = (
#     'adr agr ags apb apx bat bin cdt cnk0 cnk1 cnk2 cnk3 cnk4 cnk5 crc crt cso cur dat db dds def dir dll '
#     'dma dme dmv dsk dx11efb dx11rsb dx11ssb eco efb exe fsb fxd fxo gfx gnf i64 ini jpg lst lua mrn pak '
#     'pem playerstudio png prsb psd pssb tga thm tome ttf txt vnfo wav xlsx xml xrsb xssb zone').split()
# filename_pattern = compile(bytes(r'([><\w-]+\.(' + r'|'.join(known_exts) + r'))', 'utf-8'))


class ForgeLightGame:
    assets_subpath = r'Resources\Assets'
    locale_subpath = r'Locale'

    def __init__(self, name, path):
        self.name = name
        self.path = path
        self.asset_manager = AssetManager(list((path / self.assets_subpath).glob('*.pack*')))

    # Return list of asset objects from the provided list of names/hashes
    def get_assets(self, assets_names: List[Union[str, int]]) -> List[Tuple[str, AbstractAsset]]:
        output_assets: List[Tuple[str, AbstractAsset]] = []

        for name in assets_names:
            if isinstance(name, str):
                a = self.asset_manager[name]
                if not a:
                    print(f'{name} not found.')
                    continue

                output_assets.append((name, a))

            elif isinstance(name, int):
                a = self.asset_manager[name]
                if not a:
                    print(f'{name:#018x} not found.')
                    continue

                output_assets.append((f'{name:#018x}.bin', a))

            else:
                raise TypeError(f'get_assets() needs a filename or a filename hash. \'{type(name)}\' is not valid.')

        return output_assets

    def extract_assets(self, asset_names: List[Union[str, int]]):
        outdir = Path(f'./{self.name}_output')
        outdir.mkdir(parents=True, exist_ok=True)

        for asset in self.get_assets(asset_names):
            (outdir / asset[0]).write_bytes(asset[1].get_data())

        # for name in asset_names:
        #     if isinstance(name, str):
        #         a = self.asset_manager[name]
        #         if not a:
        #             print(f'Skipping "{name}"...')
        #             continue
        #
        #         else:
        #             (outdir / name).write_bytes(a.get_data())
        #
        #     elif isinstance(name, int):
        #         a = self.asset_manager[name]
        #         if not a:
        #             print(f'Skipping "{name:#018x}"...')
        #             continue
        #
        #         else:
        #             (outdir / f'{name:#018x}.bin').write_bytes(a.get_data())

    # TODO: Testing with zones first
    # TODO: only take one name for now
    # FIXME: This whole thing is sloppy
    def trace_requisites(self, asset_names: List[str], mode='zone'):
        completed_files: List[AbstractAsset] = []
        file_queue: List[str] = []

        zone_reqs = 'adr'.split()
        adr_reqs = 'dme dma dds'

        # compile(bytes(r'([><\w-]+\.(' + r'|'.join(known_exts) + r'))', 'utf-8'))

        for i, name in enumerate(asset_names):
            if mode == 'zone':
                # Initial scrape
                data = self.get_assets([name])[0][1].get_data()
                mo = re.findall(bytes(r'([><\w-]+\.(' + r'|'.join(zone_reqs) + r'))', 'utf-8'), data)

                if mo:
                    for m in mo:
                        print(m[0])


# def load_items(self):
#     citems = self.asset_manager['ClientItemDefinitions.txt']
#     print(citems)
#
#     outdir = Path('./output')
#
#     outdir.mkdir(exist_ok=True)
#
#     (outdir / 'ClientItemDefinitions.txt').write_bytes(citems.get_data())
#
#     pass


if __name__ == '__main__':
    to_extract = [
        # 'ClientItemDefinitions.txt'
    ]

    print('Loading game files...')
    ps2_test = ForgeLightGame('PS2_Test', test_path)
    # ps2_testold = ForgeLightGame('PS2_Testold', Path(r'D:\WindowsUsers\Rhett\Desktop\forgelight-toolbox\Backups\05-22-20-TEST'))

    # ps2_live = ForgeLightGame('PS2_Live', live_path)
    # ps2_beta = ForgeLightGame('PS2_Beta', beta_path)

    # print('Extracting specified assets...')
    # ps2_test.extract_assets(to_extract)
    # ps2_testold.extract_assets(to_extract)
    # ps2_live.extract_assets(to_extract)
    # ps2_beta.extract_assets(to_extract)

    print('Tracing requisites...')
    # Nexus makes a good example because it is smaller and has some missing materials that I should be able to trace
    ps2_test.trace_requisites(['Nexus.zone'])

    print('Finished')
    pass
