# crs_scraper

## crs_scraper.py (still not in the repo due to privacy reasons)
 - scrapes everything from the crs website then outputs a data in the form of list[dict[str, str | list[str]]]
 - TODO:
  - Still needs good input system
  - Still needs good user interface in the terminal 

## crs_data.py (for debugging purposes only, this is just temporary)
 - just contains the data itself for debugging

## data_sorter.py
 - input: the data from crs_scraper
 - outputs: all possible combinations of schedules with no time conflict
 - TODO:
  - Still needs a ranking system based on the chances generated by its available slots
  - Can be good as well if we can consider other constrains as well (e.g. Restrictions/Remarks) 

## crs_main.py
 - controls everything, including crs_data.py, data_sorter.py, crs_scraper.py
 - TODO:
  - Still need to link crs_scraper output here



Still under construction.

Mga kulang pa:
 - Ranking system
 - App interface