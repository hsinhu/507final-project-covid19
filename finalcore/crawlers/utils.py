def clean_data(data):
    data = data.text.strip()
    if data == "—":
        data = 0
    elif ',' in data:
        data = data.replace(',','')
    elif data == "<1":
        data = 0
    return data


all_US_state_name = [ "United States of America", "Alabama","Alaska","Arizona",
  "Arkansas","California","Colorado","Connecticut","Delaware",'District of Columbia',
"Florida","Georgia","Hawaii","Idaho","Illinois",
  "Indiana","Iowa","Kansas","Kentucky","Louisiana","Maine","Maryland",
  "Massachusetts","Michigan","Minnesota","Mississippi","Missouri","Montana",
  "Nebraska","Nevada","New Hampshire","New Jersey","New Mexico","New York",
  "North Carolina","North Dakota","Ohio","Oklahoma","Oregon","Pennsylvania",
  "Rhode Island","South Carolina","South Dakota","Tennessee","Texas","Utah",
  "Vermont","Virginia","Washington","West Virginia","Wisconsin","Wyoming",]