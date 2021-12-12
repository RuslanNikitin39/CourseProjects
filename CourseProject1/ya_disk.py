import requests

class YandexDisk:
    def __init__(self, token: str):
        self.token = token

    def get_headers(self):
        return {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': 'OAuth {}'.format(self.token)
        }

    def _get_up_link(self, file_path):
        upload_url = "https://cloud-api.yandex.net/v1/disk/resources/upload"
        headers = self.get_headers()
        params = {"path": file_path, "overwrite": "true"}
        response = requests.get(upload_url, headers=headers, params=params)

        return response.json()

    def upload(self, file_path: str, filename):
        href = self._get_up_link(file_path=file_path).get("href", "")
        response = requests.put(href, data=open(filename, 'rb'))
        response.raise_for_status()
        if response.status_code == 201:
            print("Success")

    def upload_url(self, url: str, file_path: str):
        up_url = "https://cloud-api.yandex.net/v1/disk/resources/upload"
        params = {'url': url,'path': file_path, 'disable_redirects': True}
        response = requests.post(up_url, headers=self.get_headers(), params=params)
        return response

    def mkdir(self, path: str):
        """Создание папки. path: Путь к создаваемой папке."""
        url = 'https://cloud-api.yandex.net/v1/disk/resources'
        requests.put(f'{url}?path={path}', headers=self.get_headers())

    def exists(self, path):
        """ Проверка существования папки. path: Путь к проверяемой папке."""
        url = 'https://cloud-api.yandex.net/v1/disk/resources'
        response = requests.get(f'{url}?path={path}', headers=self.get_headers())
        if response.status_code == 200:
            return True
        else:
            return False