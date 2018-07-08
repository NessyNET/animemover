"""
Anilist.py
Handles all of the connections to Anilist.
"""

import requests
import difflib
import traceback
import pprint

req = requests.Session()

uri = 'https://graphql.anilist.co'

search_query = '''query ($search: String, $type: MediaType) {
  Page {
    media(search: $search, type: $type) {
      id
      title {
        romaji
        english
        native
      }
      type
      status
      format
      episodes
      chapters
      volumes
      description
      startDate {
          year
          month
          day
      }
      endDate {
          year
          month
          day
      }
      genres
      synonyms
      nextAiringEpisode {
        airingAt
        timeUntilAiring
        episode
      }
    }
  }
}'''

id_query = '''query ($id: Int) {
  Page {
    media(id: $id) {
      id
      title {
        romaji
        english
        native
      }
      type
      status
      format
      episodes
      chapters
      volumes
      description
      startDate {
          year
          month
          day
      }
      endDate {
          year
          month
          day
      }
      genres
      synonyms
      nextAiringEpisode {
        airingAt
        timeUntilAiring
        episode
      }
    }
  }
}'''


def morph_to_v1(raw):
    raw_results = raw["data"]["Page"]["media"]
    morphed_results = []

    for raw_result in raw_results:
        try:
            morphed = {}
            morphed["id"] = raw_result["id"]
            morphed["title_romaji"] = raw_result["title"]["romaji"]
            morphed["title_english"] = raw_result["title"]["english"]
            morphed["title_japanese"] = raw_result["title"]["native"]
            morphed["type"] = map_media_format(raw_result["format"])
            morphed["start_date_fuzzy"] = raw_result["startDate"]["year"]
            morphed["end_date_fuzzy"] = raw_result["endDate"]["year"]
            morphed["description"] = raw_result["description"]
            morphed["genres"] = raw_result["genres"]
            morphed["synonyms"] = raw_result["synonyms"]
            morphed["total_episodes"] = raw_result["episodes"]
            morphed["total_chapters"] = raw_result["chapters"]
            morphed["total_volumes"] = raw_result["volumes"]
            morphed["airing_status"] = map_media_status(raw_result["status"])
            morphed["publishing_status"] = map_media_status(raw_result["status"])
            morphed["airing"] = {"countdown": raw_result["nextAiringEpisode"]["timeUntilAiring"],
                                 "next_episode": raw_result["nextAiringEpisode"]["episode"]} if raw_result[
                "nextAiringEpisode"] else None

            morphed_results.append(morphed)
        except Exception as e:
            print(e)

    return morphed_results


def map_media_format(media_format):
    mapped_formats = {
        'TV': 'TV',
        'TV_SHORT': 'TV Short',
        'MOVIE': 'Movie',
        'SPECIAL': 'Special',
        'OVA': 'OVA',
        'ONA': 'ONA',
        'MUSIC': 'Music',
        'MANGA': 'Manga',
        'NOVEL': 'Novel',
        'ONE_SHOT': 'One Shot',
    }
    return mapped_formats[media_format]


def map_media_status(media_status):
    mapped_status = {
        'FINISHED': 'Finished',
        'RELEASING': 'Releasing',
        'NOT_YET_RELEASED': 'Not Yet Released',
        'CANCELLED': 'Special'
    }
    return mapped_status[media_status]


# Anilist's database doesn't like weird symbols when searching it, so you have to escape or replace a bunch of stuff.
def escape(text):
    return "".join(escape_table.get(c, c) for c in text)


def getSynonyms(request):
    synonyms = []
    synonyms.extend(request['synonyms']) if request['synonyms'] else None
    return synonyms


def getTitles(request):
    titles = []
    titles.append(request['title_english']) if request['title_english'] else None
    titles.append(request['title_romaji']) if request['title_romaji'] else None
    return titles


def detailsBySearch(searchText, mediaType):
    try:
        search_variables = {
            'search': searchText,
            'type': mediaType
        }

        request = req.post(uri, json={'query': search_query, 'variables': search_variables})
        req.close()

        return morph_to_v1(request.json())

    except Exception as e:
        traceback.print_exc()
        req.close()
        return None


def detailsById(idToFind):
    try:
        id_variables = {
            'id': int(idToFind)
        }

        request = req.post(uri, json={'query': id_query, 'variables': id_variables})
        req.close()

        return morph_to_v1(request.json())[0]

    except Exception as e:
        traceback.print_exc()
        req.close()
        return None


# Returns the closest anime (as a Json-like object) it can find using the given searchtext
def getAnimeDetails(searchText):
    try:
        results = detailsBySearch(searchText, 'ANIME')

        # Of the given list of shows, we try to find the one we think is closest to our search term
        closest_anime = getClosestAnime(searchText, results)

        if closest_anime:
            return closest_anime
        else:
            return None

    except Exception as e:
        traceback.print_exc()
        req.close()
        return None


# Returns the anime details based on an id
def getAnimeDetailsById(animeID):
    try:
        return detailsById(animeID)
    except Exception as e:
        return None


# Given a list, it finds the closest anime series it can.
def getClosestAnime(searchText, animeList):
    try:
        animeNameList = []
        animeNameListNoSyn = []

        # For each anime series, add all the titles/synonyms to an array and do a fuzzy string search to find the one closest to our search text.
        # We also fill out an array that doesn't contain the synonyms. This is to protect against shows with multiple adaptations and similar synonyms (e.g. Haiyore Nyaruko-San)
        for anime in animeList:
            if 'title_english' in anime and anime['title_english']:
                animeNameList.append(anime['title_english'].lower())
                animeNameListNoSyn.append(anime['title_english'].lower())

            if 'title_romaji' in anime and anime['title_romaji']:
                animeNameList.append(anime['title_romaji'].lower())
                animeNameListNoSyn.append(anime['title_romaji'].lower())

            if 'synonyms' in anime and anime['synonyms']:
                for synonym in anime['synonyms']:
                    animeNameList.append(synonym.lower())

        try:
            closestNameFromList = difflib.get_close_matches(searchText.lower(), animeNameList, 1, 0.95)[0]
        except:
            closestNameFromList = None

        if closestNameFromList:
            for anime in animeList:
                if anime['title_english'] and anime['title_english'].lower() == closestNameFromList.lower():
                    return anime
                elif anime['title_romaji'] and anime['title_romaji'].lower() == closestNameFromList.lower():
                    return anime
                else:
                    for synonym in anime['synonyms']:
                        if (synonym.lower() == closestNameFromList.lower()) and (
                                synonym.lower() not in animeNameListNoSyn):
                            return anime

        return None
    except:
        traceback.print_exc()
        return None

