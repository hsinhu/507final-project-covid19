def clean_data(data):
    data = data.text.strip()
    if data == "—":
        data = "NULL"
    elif ',' in data:
        data = data.replace(',','')
    return data