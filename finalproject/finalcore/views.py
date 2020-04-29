from django.shortcuts import render, redirect, get_object_or_404

from django.urls import reverse_lazy, reverse
from django.views import View
from django.views import generic

from django.http import HttpResponse
from django.contrib.auth.mixins import LoginRequiredMixin

from finalcore.models import CountryCases, StateCases, CountyCases, StateProjection
from finalcore.crawlers.crawler import get_country_cases, get_state_cases
from finalcore.crawlers.crawler import get_all_county_cases, get_projection, build_state_url_dict
from finalcore.crawlers.crawler import COVID19API_URL, NYTCOVID19_URL, CSV_Name

from plotly.offline import plot
import plotly.graph_objs as go
from datetime import datetime
import plotly.express as px
from urllib.request import urlopen
import json
import plotly.figure_factory as ff
import pandas as pd

# Create your views here.
class WorldCasesView(View):
    def get(self, request):
        get_country_cases()
        data = CountryCases.objects.all()
        today = datetime.now().strftime('%Y-%m-%d')
        data_frame = {'Country_ID': [],'Country_Name': [], 'Confirmed': [],\
            'Deaths': [], 'Recovered': []}
        plot_select = request.GET.get('selection')
        print(plot_select)
        color_Select = "Confirmed"
        color_range = px.colors.sequential.Reds
        # color_range = px.colors.sequential.reds
        title_text=f'World COVID-19 Confirmed Cases for {today}'

        if plot_select == 'deaths':
            color_Select = "Deaths"
            color_range = px.colors.sequential.Greys
            title_text=f'World COVID-19 Death Cases for {today}'

        if plot_select == 'recovered':
            color_Select = "Recovered"
            color_range = px.colors.sequential.Teal
            title_text=f'World COVID-19 Recovered Cases for {today}'

        for country in data:
            data_frame['Country_ID'].append(country.Country_ID)
            data_frame['Country_Name'].append(country.Country_Name)
            data_frame['Confirmed'].append(country.Confirmed)
            data_frame['Deaths'].append(country.Deaths)
            data_frame['Recovered'].append(country.Recovered)

        fig = px.choropleth(data_frame = data_frame,
                            locations= "Country_ID",
                            color= color_Select,  # value in column 'Confirmed' determines color
                            hover_name= "Country_Name",
                            # color_continuous_scale= color_range,
                            color_continuous_scale=color_range,
                            width = 900,
                            height = 600
                            )

        fig.update_layout(title_text=title_text, title_x=0.5)
        context = {}
        div = plot(fig, output_type='div')
        context['graph'] = div

        return render(request, 'finalcore/world_cases.html', context)


class USStateView(View):
    def get(self, request):
        get_state_cases()
        data = StateCases.objects.all()
        today = datetime.now().strftime('%Y-%m-%d')

        data_frame = {'State_Name': [],
                      'State_abbr':[],
                      'Confirmed': [],
                      'Confirmed_per_capita': [],
                      'Deaths': [],
                      'Deaths_per_capita': []}

        plot_select = request.GET.get('selection')
        print(plot_select)
        color_Select = "Confirmed"
        color_range = px.colors.sequential.Reds
        # color_range = px.colors.sequential.reds
        title_text=f'US COVID-19 Confirmed Cases for {today}'

        if plot_select == '2':
            color_Select = "Confirmed_per_capita"
            color_range = px.colors.sequential.Reds
            title_text=f'US COVID-19 Confirmed Per Capita for {today}'

        if plot_select == '3':
            print("is 3")
            color_Select = "Deaths"
            color_range = px.colors.sequential.Greys
            title_text=f'World COVID-19 Death Cases for {today}'

        if plot_select == '4':
            color_Select = "Deaths_per_capita"
            color_range = px.colors.sequential.Greys
            title_text=f'World COVID-19 Death Per Capita for {today}'

        for state in data:
            data_frame['State_Name'].append(state.State_Name)
            data_frame['State_abbr'].append(state.State_abbr)
            data_frame['Confirmed'].append(state.Confirmed)
            data_frame['Confirmed_per_capita'].append(int(state.Confirmed_Per_100000_People))
            data_frame['Deaths'].append(state.Deaths)
            if state.Deaths_Per_100000_People.isnumeric():
                data_frame['Deaths_per_capita'].append(int(state.Deaths_Per_100000_People))
            else:
                data_frame['Deaths_per_capita'].append(0)

        fig = px.choropleth(data_frame = data_frame,
                            locations= "State_abbr",
                            color= color_Select,  # value in column 'Confirmed' determines color
                            hover_name= "State_Name",
                            scope = 'usa',
                            locationmode = 'USA-states',
                            color_continuous_scale= color_range,  #  color scale red, yellow green
                            width = 900,
                            height = 600
                            )
        context = {}
        fig.update_layout(title_text=title_text, title_x=0.5)

        div = plot(fig, output_type='div')
        context['graph'] = div

        return render(request, 'finalcore/us_state.html', context)

class USCountyView(View):
    def get(self, request):
        # print(build_state_url_dict())
        get_all_county_cases()
        data = CountyCases.objects.all()
        today = datetime.now().strftime('%Y-%m-%d')
        data_frame = {'State_Name': [],
                      'County_name':[],
                      'County_fips':[],
                      'Confirmed': [],
                      'Confirmed_per_capita': [],
                      'Deaths': [],
                      'Deaths_per_capita': []}

        plot_select = request.GET.get('selection')
        print(plot_select)
        color_Select = "Confirmed"
        color_range = px.colors.sequential.Reds
        # color_range = px.colors.sequential.reds
        title_text=f'US COVID-19 Confirmed Cases for {today}'

        if plot_select == '2':
            color_Select = "Confirmed_per_capita"
            color_range = px.colors.sequential.Reds
            title_text=f'US COVID-19 Confirmed Per Capita for {today}'

        if plot_select == '3':
            print("is 3")
            color_Select = "Deaths"
            color_range = px.colors.sequential.Greys
            title_text=f'World COVID-19 Death Cases for {today}'

        if plot_select == '4':
            color_Select = "Deaths_per_capita"
            color_range = px.colors.sequential.Greys
            title_text=f'World COVID-19 Death Per Capita for {today}'

        for county in data:
            data_frame['State_Name'].append(county.State_Name)
            data_frame['County_name'].append(county.County_name)
            data_frame['County_fips'].append(county.County_fips)
            data_frame['Confirmed'].append(county.Confirmed)
            if county.Confirmed_Per_100000_People.isnumeric():
                data_frame['Confirmed_per_capita'].append(int(county.Confirmed_Per_100000_People))
            else:
                data_frame['Confirmed_per_capita'].append(0)
            data_frame['Deaths'].append(county.Deaths)
            if county.Deaths_Per_100000_People.isnumeric():
                data_frame['Deaths_per_capita'].append(int(county.Deaths_Per_100000_People))
            else:
                data_frame['Deaths_per_capita'].append(0)
        # fig = ff.create_choropleth(fips=data_frame['County_fips'], values=data_frame['Confirmed'], scope=['usa'])
        counties_file = open('geojson-counties-fips.json', 'r')
        counties_contents = counties_file.read()
        counties = json.loads(counties_contents)
        counties_file.close()
        fig = px.choropleth(data_frame = data_frame,
                            geojson=counties,
                            locations= "County_fips",
                            color= color_Select,  # value in column 'Confirmed' determines color
                            hover_name= "County_name",
                            scope = 'usa',
                            # locationmode = 'USA-states',
                            color_continuous_scale= color_range,  #  color scale red, yellow green
                            width = 1000,
                            height = 700
                            )

        context = {}
        fig.update_layout(title_text=title_text)

        div = plot(fig, output_type='div')
        context['graph'] = div

        return render(request, 'finalcore/us_county.html', context)


# class USProjection(View):
#     def get(self, request):
#         # print(build_state_url_dict())
#         get_projection()
#         data = StateProjection.objects.all()
#         today = datetime.now().strftime('%Y-%m-%d')
#         data_frame = {'State_Name': [],
#                       'date_reported':[],
#                       'allbed_mean':[],
#                       'ICUbed_mean': [],
#                       'InvVen_mean': [],
#                       'deaths_mean_daily': [],
#                       'totalDeath_mean': [],
#                       'bedshortage_mean': [],
#                       'icushortage_mean':[]
#                       }

#         for county in data:
#             data_frame['State_Name'].append(county.State_Name)
#             data_frame['date_reported'].append(county.date_reported)
#             data_frame['allbed_mean'].append(county.allbed_mean)
#             data_frame['ICUbed_mean'].append(county.ICUbed_mean)
#             data_frame['InvVen_mean'].append(county.InvVen_mean)
#             data_frame['deaths_mean_daily'].append(county.deaths_mean_daily)
#             data_frame['totalDeath_mean'].append(county.totalDeath_mean)
#             data_frame['bedshortage_mean'].append(county.bedshortage_mean)
#             data_frame['icushortage_mean'].append(county.icushortage_mean)
#         # traces = []
#         # traces.append((go.Scatter(x=data_frame['date_reported'], \
#         #     y=data_frame['allbed_mean'], name='All beds for COVID19')))
#         # fig = px.choropleth(data_frame = data_frame,
#         #                     locations= "County_fips",
#         #                     color= color_Select,  # value in column 'Confirmed' determines color
#         #                     hover_name= "State_Name",
#         #                     scope = 'usa',
#         #                     # locationmode = 'USA-states',
#         #                     color_continuous_scale= color_range,  #  color scale red, yellow green
#         #                     width = 900,
#         #                     height = 700
#         #                     )
#         context = {}
#         # fig.update_layout(title_text=title_text)

#         # div = plot(go.Data(traces), output_type='div')
#         # context['graph'] = div

#         return render(request, 'finalcore/us_projection.html', context)