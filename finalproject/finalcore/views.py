from django.shortcuts import render, redirect, get_object_or_404

from django.urls import reverse_lazy, reverse
from django.views import View
from django.views import generic

from django.http import HttpResponse
from django.contrib.auth.mixins import LoginRequiredMixin

from finalcore.models import CountryCases, StateCases, CountyCases, StateProjection
from finalcore.crawlers.crawler import get_country_cases, get_state_cases
from finalcore.crawlers.crawler import get_all_county_cases, get_projection, build_state_url_dict
from finalcore.crawlers.crawler import get_county_cases_in_one_state
from finalcore.crawlers.crawler import COVID19API_URL, NYTCOVID19_URL, CSV_Name
import datetime

from plotly.offline import plot
import plotly.graph_objs as go
from datetime import datetime
import plotly.express as px
from urllib.request import urlopen
import json
from .crawlers.utils import all_US_state_name

# Create your views here.
class WorldCasesView(View):
    def get(self, request):
        get_country_cases()
        data = CountryCases.objects.all()
        today = datetime.now().strftime('%Y-%m-%d')
        data_frame = {'Country_ID': [],'Country_Name': [], 'Confirmed': [],\
            'Deaths': [], 'Recovered': []}
        plot_select = request.GET.get('selection')
        color_Select = "Confirmed"
        color_range = px.colors.sequential.Reds
        # color_range = px.colors.sequential.reds
        title_text=f'World COVID-19 Confirmed Cases for {today}'

        context = {}
        context["select"] = plot_select
        if plot_select == '2':
            color_Select = "Deaths"
            color_range = px.colors.sequential.Greys
            title_text=f'World COVID-19 Death Cases for {today}'

        if plot_select == '3':
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
                            # width = 900,
                            # height = 600
                            )

        fig.update_layout(title_text=title_text, title_x=0.5)
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
        # print(plot_select)
        context = {}
        context["select"] = plot_select
        color_Select = "Confirmed"
        color_range = px.colors.sequential.Reds
        # color_range = px.colors.sequential.reds
        title_text=f'US COVID-19 Confirmed Cases for {today}'

        if plot_select == '2':
            color_Select = "Confirmed_per_capita"
            color_range = px.colors.sequential.Reds
            title_text=f'US COVID-19 Confirmed Per Capita for {today}'

        if plot_select == '3':
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
            data_frame['Confirmed_per_capita'].append(state.Confirmed_Per_100000_People)
            data_frame['Deaths'].append(state.Deaths)
            data_frame['Deaths_per_capita'].append(state.Deaths_Per_100000_People)


        fig = px.choropleth(data_frame = data_frame,
                            locations= "State_abbr",
                            color= color_Select,  # value in column 'Confirmed' determines color
                            hover_name= "State_Name",
                            scope = 'usa',
                            locationmode = 'USA-states',
                            color_continuous_scale= color_range,  #  color scale red, yellow green
                            # width = 900,
                            # height = 600
                            )

        fig.update_layout(title_text=title_text, title_x=0.5)

        div = plot(fig, output_type='div')
        context['graph'] = div

        return render(request, 'finalcore/us_state.html', context)

class USCountyView(View):
    def get(self, request):
        # print(build_state_url_dict())
        today = datetime.now().strftime('%Y-%m-%d')
        params = {'date': today}
        state_dict = build_state_url_dict()
        states = sorted(state_dict.keys())
        state = request.GET.get('state')
        if not state:
            state = 'Michigan'
        get_county_cases_in_one_state(state_dict[state], state, params)

        options_dict = {"Confirmed": "Confirmed",
                   "Confirmed Per Capita": "Confirmed_Per_100000_People",
                    "Deaths": "Deaths",
                    "Death Per Capita": 'Deaths_Per_100000_People'}
        options = options_dict.keys()

        num_dict = {"All": None, "Top 5": 5, "Top 10": 10}
        nums = num_dict.keys()

        context = {}
        context["states"] = states
        context["options"] = options
        context["nums"] = nums

        option = request.GET.get('option')
        if option:
            option_attr = options_dict[option]
        else:
            option = "Confirmed"
            option_attr = "Confirmed"

        num = request.GET.get('num')

        if num:
            num_int = num_dict[num]
        else:
            num = "All"
            num_int = None

        if num_int is None:
            data = CountyCases.objects.filter(State_Name=state).order_by("-" + option_attr)
        else:
            data = CountyCases.objects.filter(State_Name=state).order_by("-" + option_attr)[:num_int]

        today = datetime.now().strftime('%Y-%m-%d')
        data_frame = {'State_Name': [],
                      'County_name':[],
                      'Confirmed': [],
                      'Confirmed_Per_100000_People': [],
                      'Deaths': [],
                      'Deaths_Per_100000_People': []}

        for county in data:
            data_frame['State_Name'].append(county.State_Name)
            data_frame['County_name'].append(county.County_name)
            data_frame['Confirmed'].append(county.Confirmed)
            data_frame['Confirmed_Per_100000_People'].append(county.Confirmed_Per_100000_People)
            data_frame['Deaths'].append(county.Deaths)
            data_frame['Deaths_Per_100000_People'].append(county.Deaths_Per_100000_People)

        bar_data = go.Bar(y=data_frame[option_attr], x=data_frame['County_name'])
        basic_layout = go.Layout(title = option + ' cases ' + num + ' counties in '+state,
              xaxis = dict(title = 'County name'), # 横轴坐标
              yaxis = dict(title = 'Count'), # 总轴坐标
              title_x=0.5,
            #   height = 600
            )
        fig = go.Figure(data=bar_data, layout=basic_layout)
        div = plot(fig, output_type='div')

        context['graph'] = div

        return render(request, 'finalcore/us_county.html', context)


class USProjection(View):
    def get(self, request):
        context = {}
        context['states'] = all_US_state_name
        state = request.GET.get('state')
        if not state:
            state = 'United States of America'
        get_projection()
        data = StateProjection.objects.filter(State_Name=state)
        data_frame = {'State_Name': [],
                      'date_reported':[],
                      'allbed_mean':[],
                      'ICUbed_mean': [],
                      'InvVen_mean': [],
                      'deaths_mean_daily': [],
                      'totalDeath_mean': [],
                      'bedshortage_mean': [],
                      'icushortage_mean':[]
                      }

        for county in data:
            data_frame['date_reported'].append(county.date_reported)
            data_frame['allbed_mean'].append(county.allbed_mean)
            data_frame['ICUbed_mean'].append(county.ICUbed_mean)
            data_frame['InvVen_mean'].append(county.InvVen_mean)
            data_frame['deaths_mean_daily'].append(county.deaths_mean_daily)
            data_frame['totalDeath_mean'].append(county.totalDeath_mean)
            data_frame['bedshortage_mean'].append(county.bedshortage_mean)
            data_frame['icushortage_mean'].append(county.icushortage_mean)

        # for medical resource
        trace1 = go.Scatter(x=data_frame['date_reported'],
                            y=data_frame['allbed_mean'],
                            line = {'dash':'dot'},
                            name="All beds needed")
        trace2 = go.Scatter(x=data_frame['date_reported'],
                            y=data_frame['ICUbed_mean'],
                            line = {'dash':'dot'},
                            name="ICU beds needed")
        trace3 = go.Scatter(x=data_frame['date_reported'],
                            y=data_frame['InvVen_mean'],
                            line = {'dash':'dot'},
                            name="Invasive Ventilation Needed")
        basic_layout = go.Layout(title = 'Medical Resources Needed for '+state,
              xaxis = dict(title = 'Date'), # 横轴坐标
              yaxis = dict(title = 'Resource count'), # 总轴坐标
              title_x=0.5,
            #   height = 600
            )
        data = [trace1, trace2, trace3]
        fig = go.Figure(data=data, layout = basic_layout)
        div = plot(fig, output_type='div')

        context['graph_resource'] = div
        context['state'] = state

        # for medical resource shortage
        trace1 = go.Scatter(x=data_frame['date_reported'],
                            y=data_frame['bedshortage_mean'],
                            line = {'dash':'dot'},
                            name="All beds shortage")
        trace2 = go.Scatter(x=data_frame['date_reported'],
                            y=data_frame['icushortage_mean'],
                            line = {'dash':'dot'},
                            name="ICU beds shortage")
        basic_layout = go.Layout(title = 'Medical Resources shortage for '+state,
              xaxis = dict(title = 'Date'), # 横轴坐标
              yaxis = dict(title = 'Resource count'), # 总轴坐标
              title_x=0.5,
            #   height = 600
            )
        data = [trace1, trace2]
        fig = go.Figure(data=data, layout = basic_layout)
        div = plot(fig, output_type='div')

        context['graph_resource_shortage'] = div
        context['state'] = state

        # for death rate
        trace = go.Scatter(x=data_frame['date_reported'],
                            y=data_frame['deaths_mean_daily'],
                            line = {'color':'red'})

        basic_layout = go.Layout(title = 'Deaths per day for '+state,
              xaxis = dict(title = 'Date'), # 横轴坐标
              yaxis = dict(title = 'Deaths per day'), # 总轴坐标
              title_x=0.5,
            #   height = 600
            )
        fig = go.Figure(data=trace, layout = basic_layout)
        div = plot(fig, output_type='div')

        context['graph_death_daily'] = div

        # for Total Death
        trace = go.Scatter(x=data_frame['date_reported'],
                            y=data_frame['totalDeath_mean'])

        basic_layout = go.Layout(title = 'Total deaths for '+state,
              xaxis = dict(title = 'Date'), # 横轴坐标
              yaxis = dict(title = 'Total Deaths'), # 总轴坐标
              title_x=0.5,
            #   height = 600
            )
        fig = go.Figure(data=trace, layout = basic_layout)
        div = plot(fig, output_type='div')

        context['graph_death_total'] = div

        return render(request, 'finalcore/us_projection.html', context)