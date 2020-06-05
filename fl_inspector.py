from pathlib import Path
from typing import List, Union, Dict, Tuple, Set
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

    # Return asset object from the provided name/hash
    # def get_asset(self, name: Union[str, int]) -> AbstractAsset:  #Tuple[str, AbstractAsset]:
    #     if isinstance(name, str):
    #         a = self.asset_manager[name]
    #         if a:
    #             return name, a
    #         print(f'{name} not found.')
    #
    #     elif isinstance(name, int):
    #         a = self.asset_manager[name]
    #         if a:
    #             return f'{name:#018x}.bin', a
    #         print(f'{name:#018x} not found.')
    #
    #     else:
    #         raise TypeError(f'get_assets() needs a filename or a filename hash. \'{type(name)}\' is not valid.')

    # FIXME: I am changing get_assets
    # def extract_assets(self, asset_names: List[Union[str, int]]):
    #     outdir = Path(f'./{self.name}_output')
    #     outdir.mkdir(parents=True, exist_ok=True)
    #
    #     for asset in self.get_assets(asset_names):
    #         (outdir / asset[0]).write_bytes(asset[1].get_data())
    #
    #     # for name in asset_names:
    #     #     if isinstance(name, str):
    #     #         a = self.asset_manager[name]
    #     #         if not a:
    #     #             print(f'Skipping "{name}"...')
    #     #             continue
    #     #
    #     #         else:
    #     #             (outdir / name).write_bytes(a.get_data())
    #     #
    #     #     elif isinstance(name, int):
    #     #         a = self.asset_manager[name]
    #     #         if not a:
    #     #             print(f'Skipping "{name:#018x}"...')
    #     #             continue
    #     #
    #     #         else:
    #     #             (outdir / f'{name:#018x}.bin').write_bytes(a.get_data())

    @staticmethod
    def _scrape_asset(asset: AbstractAsset, pattern: str) -> Set[str]:
        data = asset.get_data()
        mo = re.findall(bytes(r'([><\w-]+\.(' + r'|'.join(pattern.split()) + r'))', 'utf-8'), data)
        if mo:
            # return [x[0].decode('utf8') for x in mo]
            # name = m[0].decode('utf8')
            return set({m[0].decode('utf8').casefold(): m[0].decode('utf8') for m in mo}.values())
        return set()

    def trace_requisites(self, root_name: str, mode='zone'):
        # Key will be the casefolded name. proper case is stored in the asset hopefully
        completed_files: Dict[str, AbstractAsset] = {}

        # use casefold for lookup. value uses scraped case
        skipped_files: Dict[str, str] = {}
        file_queue: Dict[str, str] = {}

        # zone_reqs = 'adr'
        # adr_reqs = 'dme dma dds'

        # compile(bytes(r'([><\w-]+\.(' + r'|'.join(known_exts) + r'))', 'utf-8'))

        if mode == 'zone':
            # Initial scrape
            root_asset = self.asset_manager[root_name]
            file_queue = {v.casefold(): v for v in self._scrape_asset(root_asset, 'adr')}
            completed_files[root_name.casefold()] = root_asset
            breakpoint()

            # root_asset = self.get_asset(root_name)
            # file_queue = {v.casefold: v for v in self._scrape_asset(root_asset[1], 'adr')}
            # completed_files[root_asset[0].casefold()] = root_asset[1]
            #
            # while file_queue:
            #     name = file_queue.popitem()
            #     if name[0] in completed_files or name[0] in skipped_files:
            #         # We scraped this asset already or couldn't find it
            #         continue
            #
            #     try:
            #         asset = self.get_asset(name[1])
            #
            #     except KeyError:
            #         print(f'{name[0]} not found. Skipping')
            #         skipped_files[name[0]] = name[1]
            #         continue
            #
            #     file_queue.update({asset[0]: self._scrape_asset(asset[1], 'dme dma dds')})

            # if nameupper() in completed_files or name in skipped_files:
                #     continue
                #
                # try:
                #     asset = self.get_asset(name)
                # except KeyError as e:
                #     print(f'{name} not found. Skipping')
                #     skipped_files.add(name)
                #     continue
                #
                # file_queue.update(self._scrape_asset(asset[1], 'dme dma dds'))
                # completed_files.append(asset[1])

            # breakpoint()





            # # Initial scrape
            # asset = self.get_asset(name)
            # if not asset:
            #     raise KeyError(f'{name} not found. Aborting')
            #
            # data = asset[1].get_data()
            # mo = re.findall(bytes(r'([><\w-]+\.(' + r'|'.join(zone_reqs.split()) + r'))', 'utf-8'), data)
            #
            # if mo:
            #     for m in mo:
            #         # print(m[0])
            #         file_queue.append(m[0].decode('utf8'))
            #
            # completed_files.append(asset[1])
            #
            # # FIXME: Don't use <name>2
            # # TODO: A lot of the initial scrape code can be function
            # while file_queue:
            #     name2 = file_queue.pop()
            #     if name2 in [x.name for x in completed_files] or name2 in file_queue or name2 in skipped_files:
            #         # We already scraped this asset so skip
            #         continue
            #
            #     asset2 = self.get_asset(name2)
            #     if not asset2:
            #         print(f'{name2} not found. Skipping')
            #         skipped_files.append(name2)
            #
            #     data2 = asset2[1].get_data()
            #     mo2 = re.findall(bytes(r'([><\w-]+\.(' + r'|'.join(adr_reqs.split()) + r'))', 'utf-8'), data2)
            #
            #     if mo2:
            #         for m2 in mo2:
            #             test = m2[0].decode('utf8')
            #             # if test == 'Esamir_Flora_Radial_IceRock03_LOD0.dme': breakpoint()
            #             if test not in file_queue:
            #                 print(test)
            #                 file_queue.append(test)
            #                 pass


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
    ps2_test.trace_requisites('Nexus.zone')

    print('Finished')
    pass
