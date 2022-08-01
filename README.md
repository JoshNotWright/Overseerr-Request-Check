# Overseerr-Request-Check

## Usage 

If you're a user of Overseerr, then you're probably aware that it marks content as "partially available" until every announced episode is released. This doesn't really make much sense, and it gets pretty annoying having to manually mark series as avaiable so the requesting user gets notified. This script does all of that work for you. Each time you run it, it will go through all of your processing requests and check Sonarr to see if you have all released episodes downloaded, and will automatically mark them as available in Overseerr if you do.

## Getting Started

1. Either clone or download a zip of this repo
2. Fill in your details in the config.json file
    ```
    {
      "overseerrAPIKEY": "",
      "sonarrAPIKEY": "",
      "tmdbAPIKEY": "",
      "overseerrUrlBase": "http://example.net:5055",
      "sonarrUrlBase": "http://example.net:8989"
    }
    ```
3. Run the script
   ```
   python requestCheck.py
   ```
