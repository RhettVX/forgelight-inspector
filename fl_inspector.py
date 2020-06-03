from pathlib import Path
from typing import List, Union, Dict, Tuple

from DbgPack.asset_manager import AssetManager, AbstractAsset
from DbgPack.hash import crc64

beta_path = Path(r'D:\WindowsUsers\Rhett\Desktop\Planetside 2 Beta')
test_path = Path(r'A:\Games\PlanetSide 2 Test')
live_path = Path(r'A:\Games\PlanetSide 2')


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

    # def trace_requirements(self, asset_names: List[str]):


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
        'ClientItemDefinitions.txt'
    ]

    print('Loading game files...')
    ps2_test = ForgeLightGame('PS2_Test', test_path)
    # ps2_testold = ForgeLightGame('PS2_Testold', Path(r'D:\WindowsUsers\Rhett\Desktop\forgelight-toolbox\Backups\05-22-20-TEST'))

    # ps2_live = ForgeLightGame('PS2_Live', live_path)
    # ps2_beta = ForgeLightGame('PS2_Beta', beta_path)

    print('Extracting specified assets...')
    ps2_test.extract_assets(to_extract)
    # ps2_testold.extract_assets(to_extract)
    # ps2_live.extract_assets(to_extract)
    # ps2_beta.extract_assets(to_extract)

    print('Finished')
    pass
