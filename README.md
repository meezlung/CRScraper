<div style="display: flex;" align="center">
  <img src="https://github.com/user-attachments/assets/66ba7847-24ca-4f33-9fd5-930abc59d87b" alt="upd-logo-2019" width="200"/>
</div>


# CRScraper
_Indecisive ka ba sa pagpili ng mga schedule 'pag CRS enlistment nanaman? O eto ang sagot diyan._

This project is a simple schedule maker with probability ranking-based system for University of the Philippines Diliman's [Computerized Registration System (CRS)](https://crs.upd.edu.ph/). Basically, it generates all possible schedule you can make given a list of courses you want to enlist into! You just have to input your CRS login credentials, and courseURLs in this format ```<course_link0>, <course_link1>, <course_link2>, ...```.

courseURLS sample input: ```https://crs.upd.edu.ph/preenlistment/class_search/5670, https://crs.upd.edu.ph/preenlistment/class_search/18849, https://crs.upd.edu.ph/preenlistment/class_search/18843```

**_Note: Though working, this project is still UNDER DEVELOPMENT. Feel free to contribute din!_** 

<br />

## Simple Testing
 1. Clone the repository
    ```
    git clone https://github.com/meezlung/CRScraper.git
    cd CRScraper/
    ```
    
 2. Search for your preferred courses in CRS and copy paste the input as follows:
    ```
    all_course_table_schedule_url_cs_test = [
                                      "https://crs.upd.edu.ph/preenlistment/class_search/19405", 
                                     "https://crs.upd.edu.ph/preenlistment/class_search/19398", 
                                     "https://crs.upd.edu.ph/preenlistment/class_search/19403",
                                     "https://crs.upd.edu.ph/preenlistment/class_search/19404",
                                     "https://crs.upd.edu.ph/preenlistment/class_search/19480",
                                     ] # Sample format for CS 136, CS 21, CS 33, CS 132, and Eng 30
    # Note: Each URL corresponds to a search result table of a DESIRED COURSE, 
    # obtained after searching for a class in the CRS search bar. You may edit this list as you please.
    ```
    
 3. Open ```test.py``` in a text editor, and modify the ```all_course_table_schedule_url_cs_test``` variable.
    
 5. Feel free to edit the ```filename``` variable as well.
    
 6. Run ```test.py``` in the terminal.
    ```
    python test.py
    ```
    
 7. The CSV output will be in the same directory as ```test.py```.


## Use the App through Docker
 1. Download [Docker](https://docs.docker.com/desktop/) (if you don't have one yet).
 2. Clone the repository
    ```
    git clone https://github.com/meezlung/CRScraper.git
    cd CRScraper/
    ```

 3. Build Docker (make sure Docker is running at the background)
    ```
    docker-compose up --build
    ```

    Note: If you want the composed container to be removed, run the following:
    ```
    docker-compose down
    ```

 4. Go to ``` http://localhost:3000 ```
    

<br />


# Demo
<!-- https://github.com/user-attachments/assets/d52ab5b3-2fb4-4619-aead-3e4819f82a00 -->

<!-- https://github.com/user-attachments/assets/12f6a4ef-b45d-498a-8d60-f4f842129c96 -->


https://github.com/user-attachments/assets/8c4a7ae4-fd49-46dd-9710-ea5d16769eba




<br />

## Overview of the files

### crs_scraper.py 
 - This just scrapes everything from the CRS website then outputs a data in the form of **list[dict[str, str | list[str]]]**.
 - I used this last Midyear CRS enlistment (2023) and outputted the data as ```raw_data_CS_2ndYear_1stSem_AY_2024-2025.json``` and ```raw_data_CS_2ndYear_1stSem_AY_2024-2025.txt```.
 - They are raw data, so I had to use ```data_sorter.py``` to sort important property data. What I'm thinking now is that I should really optimize this by sorting and organizing properties while scraping the website (see ```optimized_crscraper.py```).


### crs_data.py (for debugging purposes only)
 - This contains the raw data generated by ```crs_scraper.py``` last CRS enlistment during the Midyear for the subjects Physics 72, Math 23, Math 40, CS 20, and CS 32 (my courses this 1st Sem Second Year).


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
 - This will also serve as the main backend file for the Svelte frontend via Flask.


<br />



# Mga Kulang Pa (Pero ewan ko kung gagawin ko pa to):
 - Ranking system based on [Rate UP Profs (RUPP)](https://rupp.onrender.com/) or Restrictions/Remarks. **(Still don't know how to implement)**
 - There should be a ```crscraper.py``` authenticator for each input of username, password, and courseURL, depending how the CRS website responded to those input.
 - JavaScript scraper in the future so we can upload to Google Extensions?!
 - If kaya, host sana 'yung app sa internet. I still need a way to host my backend and frontend online.
   - I think I need to install Linux server on a laptop then try to host from there.
 - I think we need to scrape Preenlistment Priority as well to feed it into the Course Probability Calculator
 - Also add criterias for organizing schedules (e.g. no weekend classes, no classes after 4 pm, no class start before 9 per se). **(Still don't know how to implement)**
