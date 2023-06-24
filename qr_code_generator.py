import qrcode, os
from imgurpython import ImgurClient


class Generator:
    def __init__(self):
        self._client_id = "d7cac2c21f00f04"
        self._client_secret = "e6e4e578db2adffa7c2e04e33f7937ba312d6610"
        self._access_token = "b4e1cc52d6e5bcf1850221f77a8d3b22be34603a"
        self._refresh_token = "9bcc0c4bf4626cd1392b3a7d84beb7936ed4f676"
        self._client = ImgurClient(self._client_id, self._client_secret, self._access_token, self._refresh_token)
        self._image_path = "temporary_storage/qr_code.png"

    def _generate_code(self, data):
        image = qrcode.make(data)
        image.save(self._image_path)

    def upload_image(self, tittle: str, data):
        self._generate_code(data)
        config = {
            'album': None,
            'name': 'New_employee',
            'title': tittle,
            'description': 'New_employee'
        }
        image = self._client.upload_from_path(self._image_path, config=config, anon=False)
        os.remove(self._image_path)
        return image['link']



