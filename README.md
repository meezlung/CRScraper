<div style="display: flex;" align="center">
  <img src="https://github.com/user-attachments/assets/66ba7847-24ca-4f33-9fd5-930abc59d87b" alt="upd-logo-2019" width="200"/>
</div>


# CRScraper
_Indecisive ka ba sa pagpili ng mga schedule? O eto ang sagot diyan._

This project is a simple schedule maker with probability ranking-based system for University of the Philippines Diliman's [Computerized Registration System (CRS)](https://crs.upd.edu.ph/).

**_Note: This project is still UNDER DEVELOPMENT._**

<br />

## Replication
 1. Go to the terminal and type the following...
 2. Clone the repository
    ```
    git clone https://github.com/meezlung/CRScraper.git
    ```

 3. Go to the directory
    ```
    cd crs_scraper/
    ```

 4. Install required dependencies (I recommend using Docker if you don't want to mess up your dependencies. If you just want to use the app, just proceed.)
    ```
    pip install -r requirements.txt
    ```
    
 5. Run crs_main.py to start back-end.
    ```
    python crs_main.py
    ```

 6. Before starting front-end, install npm (if you haven't).
    ```
    # For Windows
    winget install OpenJS.NodeJS
    
    # For Debian/Ubuntu
    sudo apt update
    sudo apt install npm
    
    # For MacOS (using Homebrew)
    brew install npm
    ```

 7. To start front-end, go to svelte-frontend and install npm dependencies
    ```
    cd svelte-frontend/
    npm install
    npm run build
    ```

 8. Start the Svelte app, and go click the link in the terminal (click the one with http://localhost:...) 
    ```
    npm run start
    ```

    You should see something like this:
    ```
          Your application is ready~! 🚀
    
      ➡ Port 8080 is taken; using 51315 instead
    
      - Local:      http://localhost:51315
      - Network:    Add `--host` to expose
    
    ────────────────── LOGS ──────────────────
    ```

 <br />
    


## If you want to use Docker for Easy Development
 1. Clone the repository
    ```
    git clone https://github.com/meezlung/CRScraper.git
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
 - This is highly inspired by Leonard Ang's code in his [UPD-Course-Probability-Calculator](https://github.com/drew-747/UPD-Course-Probability-Calculator/blob/main/popup.js)
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

# Mga Kulang Pa:
 - Ranking system based on [Rate UP Profs (RUPP)](https://rupp.onrender.com/)
