# SCOUT

MLB has offered a treasure trove of scouting reports on famous (and not famous) players. But because it's deployed as a Drupal site powered by an access database, the site crashes often. Heck, some of the player URLs have apostrophes in them and won't even load because they're performing SQL injection.

## Scraper

```
fab load_players
```

Rolls through the advanced search, state-by-state, until it has loaded every player. Note: You will have to run this more than once. Once all states have been loaded, it will stop attempting to load URLs.

```
fab load_reports
```

Rolls through all reports which do not have an image attached yet. This will take an excruciatingly long time and many of the requests will fail. You will have to run this more than once. When there are no longer reports left without an image, it will stop attempting to load URLs.

## Application

The application is a lightweight wrapper over MongoDB.

* Queries look like this: [http://jeremybowers.com/scout/raw/?q={"player.last_name":"Smith"}](http://jeremybowers.com/scout/raw/?q={%22player.last_name%22:%22Smith%22})
* Anything passed as JSON in the q parameter is passed directly to a pymongo `.find()` function.

## Future application

Soon, there will be list and detail pages? Probably in Flask. Maybe with templates.