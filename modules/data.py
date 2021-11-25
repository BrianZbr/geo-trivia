import os
import json
import random


class Data:
    JSON_FILES = {
        # Keys of this dictionary match those used in the country-json file indicated by the path value.
        "location": r'./country-json/src/country-by-region-in-world.json',
        "city": r'./country-json/src/country-by-capital-city.json',
        "languages": r'./country-json/src/country-by-languages.json',
        "dish": r'./country-json/src/country-by-national-dish.json'
    }

    EXCLUDED_COUNTRIES = {
        # Use this set to ignore minor countries and a few with data issues. The major ones should ideally be fixed in the JSON data and submitted as pull request.
        'Antarctica', 'Bouvet Island', 'British Indian Ocean Territory', 'Congo', 'Congo, The Democratic Republic of the',
        'England', 'French Southern territories', 'Heard Island and McDonald Islands', 'Holy See (Vatican City State)',
        'Hong Kong', 'North Macedonia', 'Northern Ireland', 'Scotland', 'South Georgia and the South Sandwich Islands',
        'Solomon Islands', 'Palestine', 'South Sudan', 'The Democratic Republic of Congo',
        'United States Minor Outlying Islands', 'Wales'
    }

    REGIONS = {
        # used to populate the major region category in the main countries and items dictionaries
        'Africa': ['Western Africa', 'Southern Africa', 'Northern Africa', 'Central Africa', 'Eastern Africa'],
        'Americas': ['Caribbean', 'Central America', 'North America', 'South America'],
        'Asia & Middle East': ['Middle East', 'Southern and Central Asia', 'Eastern Asia', 'Southeast Asia'],
        'Oceania': ['Polynesia', 'Micronesia', 'Melanesia', 'Australia and New Zealand'],
        'Europe': ['Western Europe', 'Nordic Countries', 'Baltic Countries', 'Central and Southeast Europe', 'Eastern Europe', 'British Isles', 'Southern Europe']
    }

    TOPICS = {
        # translates from the keys used in the raw JSON data files to the ones used in the two main dictionaries below
        'location': "minor region",
        'city': "capital",
        'languages': "languages",
        'dish': "dishes"
    }

    def __init__(self):
        self.items = {
            'major region': {},
            'minor region': {},
            'capital': {},
            'languages': {},
            'dishes': {}
        }

        self.countries = {
            'major region': {'World': []},
            'minor region': {},
            'capital': {},
            'languages': {},
            'dishes': {}
        }

        self.raw_data = self.set_raw_data()
        self.main()

    def set_raw_data(self):
        '''Collects the contents of JSON files into a dictionary of raw data'''
        self.raw_data = {}
        for topic in self.JSON_FILES:
            # adjust filepath for OS
            filepath = os.path.relpath(
                self.JSON_FILES[topic].replace('\\', os.sep))
            self.raw_data[topic] = json.load(
                open(filepath, encoding='utf-8'))
        return self.raw_data

    def split_list(self, items):
        '''Currently used for dishes, which come in as individual strings that sometimes represents as comma seperated list'''
        if items == None:
            item_list = None
        else:
            split_result = items.split(',')
        if type(split_result) is str:
            item_list = [split_result]
        elif type(split_result) is list:
            item_list = [item.strip() for item in split_result]
        else:
            print("unexpected input to split_list!", items)
            item_list = None
        return item_list

    def process_raw_data(self):
        '''Does most of the work of translating the raw data from country-json into the two main dictionaries of countries and items.'''
        for item_key in self.raw_data:
            topic = self.TOPICS[item_key]
            for item_data in self.raw_data[item_key]:
                country = item_data['country']
                items = item_data[item_key]
                if not items:
                    continue
                if type(items) == str:
                    if topic == "dishes":
                        items = self.split_list(items)
                    else:
                        items = [items]
                if not country in self.EXCLUDED_COUNTRIES:
                    if country in self.items[topic].keys():
                        self.items[topic][country].append(items)
                    else:
                        self.items[topic][country] = items
                    for subitem in items:
                        # make lists of countries that share the same item
                        if subitem in self.countries[topic].keys():
                            self.countries[topic][subitem].append(country)
                        else:
                            self.countries[topic][subitem] = [country]
        return self.countries, self.items

    def set_major_regions(self):
        '''Adds major region data (e.g. Asia, Europe, etc.) to the countries and items dictionaries based on the minor region data provided by country-json (e.g. Southeast Asia, Central Europe)'''
        for major_region in self.REGIONS:
            # create an empty list for each major region
            self.countries['major region'][major_region] = []
        for country in self.items['minor region']:
            self.countries['major region']['World'].append(country)
            minor_region = self.items['minor region'][country][0]
            for major_region in self.REGIONS:
                if minor_region in self.REGIONS[major_region]:
                    self.countries['major region'][major_region].append(
                        country)
                    self.items['major region'][country] = [major_region]
        return self.countries, self.items

    def main(self):
        self.process_raw_data()
        self.set_major_regions()


if __name__ == "__main__":
    '''For testing and troubleshooting purposes, running this file will provide dictionary statistics.'''
    data = Data()
    print("Question data was successfully loaded from country-json.\n")
    print("ITEMS dictionary contains records for the following numbers of countries:")
    for key in data.items.keys():
        print(key+":", len(data.items[key]))
    print("\nCOUNTRIES dictionary contains records for the following numbers of items:")
    for key in data.countries.keys():
        print(key+":", len(data.countries[key]))
