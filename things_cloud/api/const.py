from things_cloud.api.settings import APP_ID, USER_AGENT

API_BASE = "https://cloud.culturedcode.com/version/1"

HEADERS = {
    "Accept": "application/json",
    "Accept-Charset": "UTF-8",
    "Accept-Language": "en-gb",
    "Host": "cloud.culturedcode.com",
    "User-Agent": USER_AGENT,
    "Schema": "301",
    "Content-Type": "application/json; charset=UTF-8",
    "App-Id": APP_ID,
    "App-Instance-Id": f"-{APP_ID}",
    "Push-Priority": "5",
}
