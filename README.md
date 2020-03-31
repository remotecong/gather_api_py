# Gather-API
> Web scraper to search an address and find the owner's name then return a reverse address phone number lookup

## Setup - Docker
```bash
git clone https://github.com/remotecong/gather_api_py
cd gather_api_py
docker-compose up
open "localhost:7730"
```

## Setup - Python
```bash
git clone https://github.com/remotecong/gather_api_py
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python gather.py
```

## Other territories
In an effort to prepare this app for other territories, things have moved. Any new territories should be a module added under [app/owner_parsers](app/owner_parsers). Copy the [app/owner_parsers/tulsa](app/owner_parsers/tulsa) module and repurpose it to scrape the appropriate municipality's assessor or other service that can look up homeowners. The output should match:

```json
{
  "owner_name": "DOE, JOHN S", /* string */
  "lives_there": true, /* boolean */
  "last_name": "DOE", /* string */
}
```

Those three values are necessary for the **ThatsThem** phone number lookup to be able to match results appropriately. There are other values that are being returned in `tulsa` but they aren't necessary.

