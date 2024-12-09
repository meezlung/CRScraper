<div style="display: flex;" align="center">
  <img src="https://github.com/user-attachments/assets/66ba7847-24ca-4f33-9fd5-930abc59d87b" alt="upd-logo-2019" width="200"/>
</div>


# CRScraper
_Indecisive ka ba sa pagpili ng mga schedule 'pag CRS enlistment nanaman? O eto ang sagot diyan._

This project is a simple schedule maker with probability ranking-based system for University of the Philippines Diliman's [Computerized Registration System (CRS)](https://crs.upd.edu.ph/). Basically, it generates all possible schedule you can make given a list of courses you want to enlist into! You just have to input your CRS login credentials, and courseURLs in this format ```https://crs.upd.edu.ph/student_registration/class_search/5670```.

**_Note: Though working, this project is still UNDER DEVELOPMENT. Feel free to contribute din!_** 

<br />

## Docker
 1. Clone the repository
    ```
    git clone https://github.com/meezlung/CRScraper.git
    cd CRScraper/
    ```

 2. Build Docker
    ```
    docker-compose up --build
    ```

    Note: If you want the composed container to be removed, run the following:
    ```
    docker-compose down
    ```

 3. Go to ``` http://localhost:3000 ```
    

<br />


## Overview of the files

### crs_scraper.py 
 - This just scrapes everything from the CRS website then outputs a data in the form of **list[dict[str, str | list[str]]]**.
 - I used this last Midyear CRS enlistment (2023) and outputted the data as ```data.json``` and ```data.txt```.
 - They are raw data, so I really had to use ```data_sorter.py``` to sort important property data. What I'm thinking now is that I should really optimize this by sorting and organizing properties while scraping the website (see ```optimized_crscraper.py```).
 - TODO:
   - Still needs good user interface in the Svelte App. We can do something like it updates the website for each scrape that has happened. So, it will have realtime updates.


### crs_data.py (for debugging purposes only, this is just temporary)
 - This contains the raw data generated by ```crs_scraper.py``` last Midyear CRS enlistment for the subjects Physics 72, Math 23, Math 40, CS 20, and CS 32 (my courses this second sem).


### data_sorter.py
 - It needs the raw data from ```crs_scraper.py``` as input.
 - This generates all possible combinations of schedules with no time conflict.
 - Also has the feature to rank all generated schedule combinations possible by the property probability.
 - TODO:
   - Can be good as well if we can consider other constrains as well (e.g. Restrictions/Remarks) 


### probability_calculator.py
 - This is highly inspired by _**Leonard Ang**_'s code in his [UPD-Course-Probability-Calculator](https://github.com/drew-747/UPD-Course-Probability-Calculator/blob/main/popup.js)
 - This calculates probability based on available slots, total demand, and preenlistment priority.
 - I think this should not be the only factor in deciding which ranks the best schedule.


### crs_main.py
 - This controls everything, including crs_data.py, data_sorter.py, crs_scraper.py
 - This will also serve as the main backend file for the Svelte frontend.
 - TODO:
   - Still need to link crs_scraper output here. We can optimize the crs_scraper to already sort on-the-fly.


### optimized_crscraper.py (NOT YET IMPLEMENTED AND TESTED)
 - I still need to test this when waitlisting schedules are done already. December 9 will be the next enlistment period.

<br />

# Demo
<!-- https://github.com/user-attachments/assets/d52ab5b3-2fb4-4619-aead-3e4819f82a00 -->


https://github.com/user-attachments/assets/12f6a4ef-b45d-498a-8d60-f4f842129c96



<br />

# Mga Kulang Pa (Pero ewan ko kung gagawin ko pa to):
 - Ranking system based on [Rate UP Profs (RUPP)](https://rupp.onrender.com/) or Restrictions/Remarks (Still don't know how to implement)
 - There should be a ```crscraper.py``` authenticator for each input of username, password, and courseURL, depending how the CRS website responded to those input.
 - If kaya, host sana 'yung app sa internet.
 - Mas epic din kung iupload sa Google Extension so it's accessible by many.
 - I still need a way to host my backend, frontend online.
   - I think I need to install Linux server on a laptop then try to host from there.
 - I think we need to scrape Preenlistment Priority as well to feed it into the Course Probability Calculator
 - Also add criterias for organizing schedules (e.g. no weekend classes, no classes after 4 pm, no class start before 9 per se).
