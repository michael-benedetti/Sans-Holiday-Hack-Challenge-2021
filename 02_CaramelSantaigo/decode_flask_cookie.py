import json
import zlib; import itsdangerous


if __name__ == '__main__':
    cookie = "eJx9UkFu2zAQ_MqCl17kQpYtUfItLdI2RdEUsVugiHNYkSuLlUwKJOXACPL3LtscgiLNRRBmZ3YGw30QNHZiIz4aeyAP7zxpbUhkCf5kbAxicyt2PZ1hoCmC6kkNTIXYk_GwHVENgNP0lhXMAlbBkWw0zpKG4I4U-0TH1s0RtjHRr0_ku9HdA1oNN3OISXzdZ3AF1kWjWBiTYY8aMGk87DwNCTzybOp5NygM9Nz04CJ4wnFkHWFk3l_LOST7MKGiAJ3zYKzmfCFpe_Ra3GVidApTYq5hizbimwDvMcQx1eCmNEkt3IpLbWw7-wNH3SoXR87PjBt3QmvoaDL4YOwTuHPD2WXwGSe0bPFfLZ2HX3jaz3lOeuAGFD1Nvjirnc3g0h7-IGnHD0PWYgYX3Jk3-Kr-hVRpxTd-MOrdqMkz6Svdw0_nWfh9e_HKujsuyfOPO26JtNiUK8kA10vpOl4s4N_8r2V9HoqdTkZF589cIaUneeBDCP1mL3CJUtZV0SzzVYdaSiyokZJwpdZ1US9ztaRSNTJfV1RKKstW1suiY0G76vKq3YuMTyS42Su60hvYC9noqioKuWj0Si_WHX9Q1d1C1VSUbYPrvKz24lE8_gaWOQh3"
    data: dict = json.loads(zlib.decompress(itsdangerous.base64_decode(cookie)).decode())
    for key, value in data.items():
        print(f"{key}: {value}")
