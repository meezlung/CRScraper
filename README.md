<div style="display: flex;" align="center">
  <img src="https://github.com/user-attachments/assets/66ba7847-24ca-4f33-9fd5-930abc59d87b" alt="upd-logo-2019" width="200"/>
</div>


# CRScraper
_Indecisive ka ba sa pagpili ng mga schedule 'pag CRS enlistment nanaman? O eto ang sagot diyan._

This project is a simple schedule maker with probability ranking-based system for University of the Philippines Diliman's [Computerized Registration System (CRS)](https://crs.upd.edu.ph/). Basically, it generates all possible schedule you can make given a list of courses you want to enlist into! You just have to input your CRS login credentials, and courseURLs in this format ```<course_link0>, <course_link1>, <course_link2>, ...```.

courseURLS sample input: ```https://crs.upd.edu.ph/preenlistment/class_search/5670, https://crs.upd.edu.ph/preenlistment/class_search/18849, https://crs.upd.edu.ph/preenlistment/class_search/18843```

**_Note: Though working, this project is still UNDER DEVELOPMENT. Feel free to contribute din!_** 

<br />

## Use the App through the terminal
 1. In a terminal, clone the repository, and go to the file directory.
    ```
    git clone https://github.com/meezlung/CRScraper.git
    cd CRScraper/
    ```
    
 2. Run the Python file `test.py`.
    ```
    python test.py
    ```
    
 3. Enter your credentials, and the desired courseURLs separated by commas. For example, the following shows the sample format in CS 136, CS 21, CS 33, CS 132, and Eng 30 under the Student Registration tab):
    ```
    CRS Username: gimislang
    CRS Password:
    Enter the course table schedule URLs separated by comma: https://crs.upd.edu.ph/student_registration/class_search/19405, https://crs.upd.edu.ph/student_registration/class_search/19398, https://crs.upd.edu.ph/student_registration/class_search/19403, https://crs.upd.edu.ph/student_registration/class_search/19404, https://crs.upd.edu.ph/student_registration/class_search/19480
    ``` 
    
 4. The generated ranked schedules output will be saved as either `schedules_ranked_test_preenlistment.csv` or `schedules_ranked_test_student_registration.csv` and will be in the same directory as `test.py`.

<br />

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



https://github.com/user-attachments/assets/72262755-f894-4e24-82cc-f969d6786785



https://github.com/user-attachments/assets/8c4a7ae4-fd49-46dd-9710-ea5d16769eba




<br />

## Overview of the files

### crs_scraper_preenlistment.py, crs_scraper_waitlist.py 
 - Consists of the class, ```CRScraper```.
 - ```CRScraper```
   - This just scrapes everything from the CRS website then outputs a data in the form of **list[dict[str, str | list[str]]]**.
   - I used this last Midyear CRS enlistment (2023) and outputted the data as ```raw_data_CS_2ndYear_1stSem_AY_2024-2025.json``` and ```raw_data_CS_2ndYear_1stSem_AY_2024-2025.txt```.
   - They are raw data, so I had to use ```data_sorter.py``` to sort important property data. What I'm thinking now is that I should really optimize this by sorting and organizing properties while scraping the website (see ```optimized_crscraper.py```).

### crs_data.py (for debugging purposes only)
 - This contains the raw data generated by ```crs_scraper.py``` last CRS enlistment during the Midyear for the subjects Physics 72, Math 23, Math 40, CS 20, and CS 32 (my courses this 1st Sem Second Year).

### data_sorter.py
 - Consists of classes, ```DataSorter``` and ```ScheduleGenerator```.
 - ```DataSorter```
   - It needs the raw data from ```crs_scraper.py``` as input.
   - Only formats the raw data beautifully so it's kinda unnecessary. 
 - ```ScheduleGenerator```
   - This generates all possible combinations of schedules with no time conflict.
   - Also has the feature to rank all generated schedule combinations possible by the property probability.
   - TODO:
     - Can be good as well if we can consider other constrains as well (e.g. Restrictions/Remarks) 

### probability_calculator.py
 - Consists of the class, ```ProbabilityCalculator```.
 - ```ProbabilityCalculator```
   - This is highly inspired by _**Leonard Ang**_'s code in his [UPD-Course-Probability-Calculator](https://github.com/drew-747/UPD-Course-Probability-Calculator/blob/main/popup.js)
   - This calculates probability based on available slots, total demand, and preenlistment priority.
   - I think this should not be the only factor in deciding which ranks the best schedule.

### crs_main.py
 - This controls everything, including ```crs_data.py```, ```data_sorter.py```, ```crs_scraper.py``` via import modules.
 - This will also serve as the main backend file for the Svelte frontend via Flask.

### test.py
 - Same behavior as crs_main.py, but is only just for local testing purposes.

<br />



# Mga Kulang Pa (Pero ewan ko kung gagawin ko pa to):
 - Ranking system based on [Rate UP Profs (RUPP)](https://rupp.onrender.com/) or Restrictions/Remarks. **(Still don't know how to implement)**
 - JavaScript scraper in the future so we can upload to Google Extensions?! If not, host in the internet? Though needs a way to host backend and frontend online (consider homemade Linux server).
 - Feed preenlistment and registration priority to Probability Calculator.
 - Add a "You are already registered" detector or something that keeps in mind that it's still not preenlistment or registration period.
 - Also add criterias/filtering functions for organizing schedules (e.g. no weekend classes, no classes after 4 pm, no class start before 9 per se). **(Still don't know how to implement)**
 - Apply DP to overlapping subproblems in the backtrack function. **(Parang hirap pala neto, or ewan ko kung posible ba yan)**
 - Organize documentation per each function.
 - Feature for utilizing similar subjects.
 - Ayusin nga tong documentation na toh.
 - Distinguish preenlistment and waitlisting features properly, both in documentation and src codes.
