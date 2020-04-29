# 507final-project-covid19
A website built by Django and use Plotly to visualize COVID19 related data. The front-end is built by Bootstrap 4.
## How to run
```
pip install -r requirements.txt
python3 manage.py makemigrations
python3 manage.py migrate
python3 manage.py runserver 
```
## How to interact 
There are 4 visualization options for this website. User can select visualization options from nav bar on every page or go from the home page intruduction part.
### World Cases page
For World Cases page, it shows today’s world map of COVID19, where user can select Confirmed, Deaths and Recovered for the world map. Default is Confirmed. A country has more cases and will has deeper color than other countries. When users hover the map, it will show the exact case number for the country. 
### US State Cases page
For US State Cases page, it shows today's US map of COVID19, where user can select Confirmed, Confirmed Per Capita (per 100,000 people), Deaths, Deaths Per Capita to show. Default is also Confirmed. When users hover the map, it will show the exact case number for the state. Also, a state has more cases and will has deeper color than other states. 
### US County Cases page
For US County Cases, it can show all counties, top 5 counties or top 10 counties of user selected states in user selected fields including Confirmed, Confirmed Per Capita, Deaths, Deaths Per Capita by bar plot. The data has been sorted by the selected field and the bar plot from left to right is in descending order. The default is Michigan, Confirmed, all counties. 
### US Projection page
For US Projection, it shows projected daily needed medical resources, daily death number and total death number from covid19 start to future for selected state by users. This includes 4 line charts for each state. The first is medical resources needed which shows all needed beds, needed ICU beds and needed invasive ventilations together. The second is medical resources shortage which shows all needed beds shortage and needed ICU beds shortage together. The third is deaths per day. The fourth is total deaths. User can select all states they want. The default is the whole US. 

