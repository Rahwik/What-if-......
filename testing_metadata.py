import requests
files_url = "https://dataverse.harvard.edu/api/datasets/:persistentId/versions/:latest/files?persistentId=doi:10.7910/DVN/WWRT1V"
response = requests.get(files_url)
files_info = response.json()
print(files_info)
