import pandas as pd
import plotly.express as px  
import plotly.graph_objects as go
from dash import Dash, dcc, html, Input, Output 
from plotly.graph_objects import Layout
from plotly.validator_cache import ValidatorCache
import json

import dash_bootstrap_components as dbc

app = Dash(external_stylesheets=[dbc.themes.SUPERHERO])
colors = {
    'background': '#EBE645',
    'text': '#7FDBFF'
}

# reading the datasets
globaldeath=pd.read_csv('deathsglobal.csv')
confirmedcase=pd.read_csv('confirmglobal.csv')
recovered=pd.read_csv('recoveredglobal.csv')


# for each date there is a specific column like date1,date2,date3... so the next time we add on some more data it is going to add on no of columns 
# so to avoid this abrupt increase in column size we use pandas's melt function   which converts the dataframes long format to wide format
#
confirmdate=confirmedcase.columns[4:]
finalconfirmeddata= confirmedcase.melt(id_vars=['Province/State','Country/Region','Lat','Long'],value_vars=confirmdate, var_name='Date', value_name='total_confirmed_case')

deathdate=globaldeath.columns[4:]
finaldeathdata= globaldeath.melt(id_vars=['Province/State','Country/Region','Lat','Long'], value_vars=deathdate,var_name='Date', value_name='total_confirmed_deaths')


recovereddate=recovered.columns[4:]
finalrecovereddata=recovered.melt(id_vars=['Province/State','Country/Region','Lat','Long'], value_vars=recovereddate,var_name='Date', value_name='total_confirmed_recoveries')


mergesample2=pd.merge(finalconfirmeddata,finaldeathdata)
finalmergedata=pd.merge(mergesample2,finalrecovereddata)

# date present inside the data frame is in string format ,so we need to convert it into actual date format dd-mm-yyyy

finalmergedata['Date']=pd.to_datetime(finalmergedata['Date'],errors ='coerce')
finalmergedata.isna().sum()
# for checking if there is any kind of nan value present in any column of datasets


finalcov=finalmergedata.copy()
# since we know that to get the active no of cases we
# we need to subtract
# Active_case = (confirm_case-deaths-recovered)
finalcov['Active_cases']=finalcov['total_confirmed_case']-finalcov['total_confirmed_deaths']-finalcov['total_confirmed_recoveries']


# now we do grouoby as we use in SQL same concept applies here,
# if dataset goes for m,m,m,c,c,c,t,t therefore after groupby we get a dataset like m-3 ,c-3,t-2
# this groupby is done to arrange all the counrty case(confirm,deaths,recoveries,active) that appeared on that data 
cov_matrix1=finalcov.groupby(['Date'])[['total_confirmed_case','total_confirmed_deaths','total_confirmed_recoveries','Active_cases']].sum().reset_index()

cov_matrix=finalcov.groupby(['Date','Country/Region'])[['total_confirmed_case','total_confirmed_deaths','total_confirmed_recoveries','Active_cases']].sum().reset_index()




# here we design a layout for this 
app.layout=dbc.Container([
	dbc.Row([
		dbc.Col([
			# dbc.Card([
			# 	dbc.CardImg(
			# 		src="assets/covid.png",
			# 		top=True,
			# 		style={"height":200,"opacity":1,"width":200}
			# 		)
			# 	])
			# for 
            html.Div([
			html.Img(src="assets/covid.png",style={"width":100,"height":100})
            
            ])
			],width=1),
		dbc.Col([
			html.Div([
				html.H1("CoviTrop")
                ],className="mt-4"
			)
			],width=4),

		dbc.Col([
           html.Div([
           
           	html.Br(),
           
           	
           	],style={'margin-top':40})

			],width=4),

		dbc.Col([
           html.Div([
           	'2020-21',
           	html.Br(),
           	'GlobaL Health Cluster COVID DASHBOARD'
           	
           	],style={'margin-top':40})

			])

		]),


	html.Hr(),
	# for cards and dropdown
	dbc.Row([

# this div is for the global confirmed case

		dbc.Col([

            dbc.Row([
            	# dbc.Card('card1', color="primary", inverse=True)
            	html.Div(id="container1",children=[
            		html.H2('Global Cases',style={'text-align':'center','color':'white','margin-top':8,'fontsize':30}),
            		html.P(f"{cov_matrix1['total_confirmed_case'].iloc[-1]:,.0f}",style={'text-align':'center','color':'orange','font-size':25}),
            		html.P("Latest cases :"+f"{cov_matrix1['total_confirmed_case'].iloc[-1]-cov_matrix1['total_confirmed_case'].iloc[-2]:,.0f}" +"----" +"ROC" '('
            			+str(round(((cov_matrix1['total_confirmed_case'].iloc[-1]-cov_matrix1['total_confirmed_case'].iloc[-2])/cov_matrix1['total_confirmed_case'].iloc[-1])*100,2))+'%)'
            			,style={'text-align':'center','color':'orange'})




            		],style={'backgroundColor':'#1F2C56','height':140,'width':800,'margin-left':15})

            	]),
            # this div is for global death that is on the left side of the screen
            dbc.Row([
            	html.Div(id="container2",children=[
            		html.H2('Global Death',style={'text-align':'center','color':'white','margin-top':8,'fontsize':30}),
            		html.P(f"{cov_matrix1['total_confirmed_deaths'].iloc[-1]:,.0f}",style={'text-align':'center','color':'red','font-size':25}),
            		html.P("Latest deaths :"+f"{cov_matrix1['total_confirmed_deaths'].iloc[-1]-cov_matrix1['total_confirmed_deaths'].iloc[-2]:,.0f}" +"----" +"ROC" '('
            			+str(round(((cov_matrix1['total_confirmed_deaths'].iloc[-1]-cov_matrix1['total_confirmed_deaths'].iloc[-2])/cov_matrix1['total_confirmed_deaths'].iloc[-1])*100,2))+'%)'
            			,style={'text-align':'center','color':'red'})

            		],style={'backgroundColor':'#1F2C56','height':140,'width':800,'margin-left':15,'margin-top':20})


            	]),
            # this div is for global recovered that is also on the left sode of the screen
            dbc.Row([
                    html.Div(id="container3",children=[
                    html.H2('Global Recovered',style={'text-align':'center','color':'white','margin-top':8,'fontsize':30}),
            		html.P(f"{cov_matrix1['total_confirmed_recoveries'].iloc[-1]:,.0f}",style={'text-align':'center','color':'green','font-size':25}),
            		html.P("Latest Recoveries :"+f"{cov_matrix1['total_confirmed_recoveries'].iloc[-1]-cov_matrix1['total_confirmed_recoveries'].iloc[-2]:,.0f}" +"----" +"ROC" '('
            			+str(round(((cov_matrix1['total_confirmed_recoveries'].iloc[-1]-cov_matrix1['total_confirmed_recoveries'].iloc[-2])/cov_matrix1['total_confirmed_recoveries'].iloc[-1])*100,2))+'%)'
            			,style={'text-align':'center','color':'green'})


            		],style={'backgroundColor':'#1F2C56','height':140,'width':800,'margin-left':15,'margin-top':20})
            	]),
            # this div is for the global active tile present on the left sideof the screen
             dbc.Row([
                    html.Div(id="container4",children=[
                    html.H2('Global Active',style={'text-align':'center','color':'white','margin-top':8,'fontsize':30}),
            		html.P(f"{cov_matrix1['Active_cases'].iloc[-1]:,.0f}",style={'text-align':'center','color':'#FFEF78','font-size':25}),
            		html.P("Latest Recoveries :"+f"{cov_matrix1['Active_cases'].iloc[-1]-cov_matrix1['Active_cases'].iloc[-2]:,.0f}" +"----" +"ROC" '('
            			+str(round(((cov_matrix1['Active_cases'].iloc[-1]-cov_matrix1['Active_cases'].iloc[-2])/cov_matrix1['total_confirmed_recoveries'].iloc[-1])*100,2))+'%)'
            			,style={'text-align':'center','color':'yellow'})

            		],style={'backgroundColor':'#1F2C56','height':140,'width':800,'margin-left':15,'margin-top':20})
            	])



			],width=3),
		# col2 row2 for dropdown
		# role of dropdown is to select country  from various countries  , and output is shown in correpondence to that only
		dbc.Col([
			dbc.Row([
 
			html.Div([
			html.Div(["Select Country for which you want to visualise data"],style={'color':'#8FC1D4','margin-bottom':10}),	
            dcc.Dropdown(
            id='select_country',
            options=[{'label':c, 'value':c} for c in (cov_matrix['Country/Region'].unique())],
            value='India',
            multi=False,
            placeholder="CLICK-HERE",
            clearable=True,
            ),
            html.Div(id='dd-output-container')
            ],style={'margin-left':50}),
            ]),

            dbc.Row([
            	html.Div([
            		dcc.Graph(id='pie_chart',
            			config={'displayModeBar':'hover'})
            		]
            		 ,style={'margin-left':50,'margin-top':20}),
            	])
          

			],width=5),

#earth wearing a mask image is inserted on the right of windpw pane using this code
		dbc.Col([
             dbc.Row([
			html.Div([
				html.Img(src="assets/cov.png",style={"width":300,"height":300,'margin-left':80,'margin-top':0})
				],style={'margin-left':10})

			]),

             dbc.Row([
		     	html.Div([

		     	html.P('Total New Cases  on ' + ' '  +str(cov_matrix['Date'].iloc[-1].strftime("%B %d %Y"))+' country specific',style={'color':'white','text-align':'center'})



		     		],style={'width':400,'margin-left':60,'height':50})



		     	],className='ml-10'),
             # the 4tiles set just below the earth is contemplated using this code
                  dbc.Row([
                  	html.Div([
            	 dcc.Graph(id='newconfirmedcases', config={'displayModeBar': False},
                        style={}
                ),
             dcc.Graph(id='newdeaths', config={'displayModeBar': False},
                        style={}
                ),
             dcc.Graph(id='newrecoveredcase', config={'displayModeBar': False},
                        style={}
                ),
             dcc.Graph(id='newactivecase', config={'displayModeBar': False},
                        style={}
                )

            	],style={'margin-top':20})

            ],style={'margin-left':60})

              ]),
		    


		],className="mt-5 mr-4"),
	# for other big 2 image from here

	# new rows start from here
	# all other graphs are positioned using this code

	dbc.Row([
    html.Div([
	dcc.Graph(id='line_chart')
            		])



		],style={'padding-top':20}
		)
	,


	dbc.Row([
		dbc.Col([
    html.Div([
	dcc.Graph(id='line_chart1')
            		])



		],style={'padding-top':20}
		),

		]),
	dbc.Row([

	dbc.Col([
    html.Div([
	dcc.Graph(id='line_chart2')
            		])



		],style={'padding-top':20}
		),
	dbc.Col([
    html.Div([
	dcc.Graph(id='line_chart3')
            		])



		],style={'padding-top':20}
		)



		]),
	dbc.Row([
		html.Div([
'GLOBAL VIEW'

			],style={'align':'center','margin-top':10})



		]),
	dbc.Row([


		 html.Div([
	dcc.Graph(id='map')
            		])

		],style={'padding-top':10})
	
	


	],fluid=True)
# # for choropleth map
# @app.callback(
# 	Output('map1','figure'),
# Input('select_country','value')
# 	)


# def update_graph(v):
#     p={}
#     cov1=finalcov.groupby(['Lat','Long','Country/Region'])[['total_confirmed_case','total_confirmed_deaths','total_confirmed_recoveries','Active_cases']].max().reset_index()
# # 	return {
#     for country in cov1['Country/Region'].unique().tolist():
#         try:
#             cd=pycountry.countries.search_fuzzy(country)
#             cc=cd[0].alpha_3
#             p.update({country:cc})
#         except:
#             p.update({country:' '})
#             print(p)

#     cov1['id']=cov1['Country/Region'].apply(lambda x:p[x])
#     fig=px.choropleth_mapbox(cov1,
#     	geojson=p,
#     	locations='id',
#     	color='total_confirmed_case',
#     	color_continuous_scale="Viridis",
#     	mapbox_style="carto-positron",
#     	zoom=4,
#     	center = {"lat":cov1['Lat'].mean(), "lon":cov1['Long'].mean()},
#     	opacity=0.5)
#     fig.update_layout(margin={"r":0,"t":0,"l":4,"b":0},height=500)
#     return fig

# def update_graph(v):
#     p={}
#     cov1=finalcov.groupby(['Date','Country/Region'])[['total_confirmed_case','total_confirmed_deaths','total_confirmed_recoveries','Active_cases']].max().reset_index()
#     for country in cov1['Country/Region'].unique().tolist():
#         try:
#             cd=pycountry.countries.search_fuzzy(country)
#             cc=cd[0].alpha_3
#             p.update({country:cc})
#         except:
#             p.update({country:' '})
#             print(p)

#     cov1['id']=cov1['Country/Region'].apply(lambda x:p[x])
#     fig=px.choropleth(cov1,locations='id',geojson=p,color="total_confirmed_case")


#     return fig























# for the big map
@app.callback(
Output('map','figure'),
Input('select_country','value')
	)

def update_graph(v):
	cov1=finalcov.groupby(['Lat','Long','Country/Region'])[['total_confirmed_case','total_confirmed_deaths','total_confirmed_recoveries','Active_cases']].max().reset_index()
	return {
	'data':[go.Scattermapbox(
		lon=cov1['Long'],
		lat=cov1['Lat'],
		mode='markers',
		marker=go.scattermapbox.Marker(
			size=cov1['total_confirmed_case']/1500,
			color=cov1['total_confirmed_case'],
			colorscale='hsv',
			showscale=True,
			sizemode='area',
			opacity=0.3),
		hoverinfo='text',
		hovertext=
		'<b>Country</b> :' +cov1['Country/Region'].astype(str)+ '<br>' +
		'<b>Longitude</b> :' +cov1['Long'].astype(str) + '<br>' +
		'<b>Latitude</b> :'  +cov1['Lat'].astype(str) + '<br>'  +
		'<b>Confirmed</b> :' + [f'{x:,.0f}' for x in cov1['total_confirmed_case']]+'<br>' +
		'<b>Death</b>     :' +[f'{x:,.0f}' for x in cov1['total_confirmed_deaths']] + '<br>'+
		'<b>Recovered</b> :' +[f'{x:,.0f}' for x in cov1['total_confirmed_recoveries']]+'<br>'+
		'<b>Active</b>    :' +[f'{x:,.0f}' for x in cov1['Active_cases']]+'<br>' 
		)],
	'layout': go.Layout(
            margin={'r':0,'t':0,'l':0,'b':0},
            hovermode='closest',
            mapbox=dict(accesstoken='pk.eyJ1Ijoic3Vrcml0YmFuc2FsIiwiYSI6ImNrd3A2amswbTA5dm0ydmwwOTF2ZjlhaXQifQ.J2BH8WNsbLoJ4fsvCcTNzw',
                        center=go.layout.mapbox.Center(lat=36, lon=-5.4),
                        style='open-street-map',
                        zoom=1.2),
            autosize=True,
        )



	}







# for getting graph for total confirmed case graph for all the countries
@app.callback(
Output('line_chart','figure'),
Input('select_country','value')

	)
def update_graph(v):
	# here we are basically doing group by on date and country it will arrange data in this format d1c1,d1c2,d1c3,d1c4 we add upon each country cases ,that appears to be 
	# no of cases till date like till 11th day
	cov=finalcov.groupby(['Date','Country/Region'])[['total_confirmed_case','total_confirmed_deaths','total_confirmed_recoveries','Active_cases']].sum().reset_index()
	cov1=cov[cov['Country/Region']==v][['Country/Region','Date','total_confirmed_case']].reset_index()
	# to calculate on daily base we do case till [case on ith- case on(i-1)th],, this is done by shift method , as it shifts the data set whole by 1 , then we subtract
	cov1['daily_based_confirm']=cov1['total_confirmed_case']-cov1['total_confirmed_case'].shift(1)
# here we have use go maps to add on to the  scatter plots
	return{
	'data':[go.Scatter(
		x=cov1[cov1['Country/Region']==v]['Date'],
		y=cov1[cov1['Country/Region']==v]['daily_based_confirm'],
		mode='lines',
		line=dict(width=3,color='orange'),
		hoverinfo='text',
		hovertext=
		'<b>Date</b>: ' + cov1[cov1['Country/Region'] == v]['Date'].astype(str) + '<br>' +
                           '<b>Daily Confirmed</b>: ' + [f'{x:,.0f}' for x in cov1[cov1['Country/Region'] == v]['daily_based_confirm']] + '<br>')],
		
	'layout':go.Layout(
		plot_bgcolor='#1F2C56',
		paper_bgcolor='#1F2C56',
		title={
		'text':'Confirmed cases  :'+(v),
		'y':0.93,
		'x':0.5,
		'xanchor':'center',
		'yanchor':'top'
		},
		titlefont={
		'color':'white',
		'size':20

		},
		hovermode='x',
		xaxis=dict(
			title='<b>Date</b>',
			color='white',
			showline=True,
			showgrid=True,
			showticklabels=True,
			linecolor='white',
			linewidth=2,
			ticks='outside',
			tickfont=dict(
				family='Arial',
				size=12,
				color='white'

				)


			),
		yaxis=dict(
			title='<b>Cumulative Cases</b>',
			color='white',
			showline=True,
			showgrid=True,
			showticklabels=True,
			linecolor='white',
			linewidth=2,
			ticks='outside',
			tickfont=dict(
				family='Arial',
				size=12,
				color='white'

				)

			),
		legend={
		'orientation':'h',
		'bgcolor':'#1F2C56',
		'xanchor':'center','x':0.5,'y':-0.3

		},
		font=dict(
			family='sans-serif',
			size=12,
			color='white'

			),


		)




	}

# for biggraph 2
@app.callback(
Output('line_chart1','figure'),
Input('select_country','value')

	)
# similar concept
def update_graph(v):
	cov=finalcov.groupby(['Date','Country/Region'])[['total_confirmed_case','total_confirmed_deaths','total_confirmed_recoveries','Active_cases']].sum().reset_index()
	cov1=cov[cov['Country/Region']==v][['Country/Region','Date','total_confirmed_recoveries']].reset_index()
	cov1['daily_based_confirm']=cov1['total_confirmed_recoveries']-cov1['total_confirmed_recoveries'].shift(1)

	return{
	'data':[go.Scatter(
		x=cov1[cov1['Country/Region']==v]['Date'],
		y=cov1[cov1['Country/Region']==v]['daily_based_confirm'],
		mode='lines',
		line=dict(width=3,color='green'),
		hoverinfo='text',
		hovertext=
		'<b>Date</b>: ' + cov1[cov1['Country/Region'] == v]['Date'].astype(str) + '<br>' +
                           '<b>Daily Confirmed</b>: ' + [f'{x:,.0f}' for x in cov1[cov1['Country/Region'] == v]['daily_based_confirm']] + '<br>')],
		
	'layout':go.Layout(
		plot_bgcolor='#1F2C56',
		paper_bgcolor='#1F2C56',
		title={
		'text':'Confirmed Recoveries  :'+(v),
		'y':0.93,
		'x':0.5,
		'xanchor':'center',
		'yanchor':'top'
		},
		titlefont={
		'color':'white',
		'size':20

		},
		hovermode='x',
		xaxis=dict(
			title='<b>Date</b>',
			color='white',
			showline=True,
			showgrid=True,
			showticklabels=True,
			linecolor='white',
			linewidth=2,
			ticks='outside',
			tickfont=dict(
				family='Arial',
				size=12,
				color='white'

				)


			),
		yaxis=dict(
			title='<b>Cumulative Cases</b>',
			color='white',
			showline=True,
			showgrid=True,
			showticklabels=True,
			linecolor='white',
			linewidth=2,
			ticks='outside',
			tickfont=dict(
				family='Arial',
				size=12,
				color='white'

				)

			),
		legend={
		'orientation':'h',
		'bgcolor':'#1F2C56',
		'xanchor':'center','x':0.5,'y':-0.3

		},
		font=dict(
			family='sans-serif',
			size=12,
			color='white'

			),


		)




	}



@app.callback(
Output('line_chart2','figure'),
Input('select_country','value')

	)
def update_graph(v):
	cov=finalcov.groupby(['Date','Country/Region'])[['total_confirmed_case','total_confirmed_deaths','total_confirmed_recoveries','Active_cases']].sum().reset_index()
	cov1=cov[cov['Country/Region']==v][['Country/Region','Date','total_confirmed_deaths']].reset_index()
	cov1['daily_based_confirm']=cov1['total_confirmed_deaths']-cov1['total_confirmed_deaths'].shift(1)

	return{
	'data':[go.Scatter(
		x=cov1[cov1['Country/Region']==v]['Date'],
		y=cov1[cov1['Country/Region']==v]['daily_based_confirm'],
		mode='lines',
		line=dict(width=3,color='red'),
		hoverinfo='text',
		hovertext=
		'<b>Date</b>: ' + cov1[cov1['Country/Region'] == v]['Date'].astype(str) + '<br>' +
                           '<b>Daily Confirmed</b>: ' + [f'{x:,.0f}' for x in cov1[cov1['Country/Region'] == v]['daily_based_confirm']] + '<br>')],
		
	'layout':go.Layout(
		plot_bgcolor='#1F2C56',
		paper_bgcolor='#1F2C56',
		title={
		'text':'Confirmed Deaths  :'+(v),
		'y':0.93,
		'x':0.5,
		'xanchor':'center',
		'yanchor':'top'
		},
		titlefont={
		'color':'white',
		'size':20

		},
		hovermode='x',
		xaxis=dict(
			title='<b>Date</b>',
			color='white',
			showline=True,
			showgrid=True,
			showticklabels=True,
			linecolor='white',
			linewidth=2,
			ticks='outside',
			tickfont=dict(
				family='Arial',
				size=12,
				color='white'

				)


			),
		yaxis=dict(
			title='<b>Cumulative Cases</b>',
			color='white',
			showline=True,
			showgrid=True,
			showticklabels=True,
			linecolor='white',
			linewidth=2,
			ticks='outside',
			tickfont=dict(
				family='Arial',
				size=12,
				color='white'

				)

			),
		legend={
		'orientation':'h',
		'bgcolor':'#1F2C56',
		'xanchor':'center','x':0.5,'y':-0.3

		},
		font=dict(
			family='sans-serif',
			size=12,
			color='white'

			),


		)




	}


@app.callback(
Output('line_chart3','figure'),
Input('select_country','value')

	)
def update_graph(v):
	cov=finalcov.groupby(['Date','Country/Region'])[['total_confirmed_case','total_confirmed_deaths','total_confirmed_recoveries','Active_cases']].sum().reset_index()
	cov1=cov[cov['Country/Region']==v][['Country/Region','Date','Active_cases']].reset_index()
	

	return{
	'data':[go.Scatter(
		x=cov1[cov1['Country/Region']==v]['Date'],
		y=cov1[cov1['Country/Region']==v]['Active_cases'],
		mode='lines',
		line=dict(width=3,color='yellow'),
		hoverinfo='text',
		hovertext=
		'<b>Date</b>: ' + cov1[cov1['Country/Region'] == v]['Date'].astype(str) + '<br>' +
                           '<b>Daily Confirmed</b>: ' + [f'{x:,.0f}' for x in cov1[cov1['Country/Region'] == v]['Active_cases']] + '<br>')],
		
	'layout':go.Layout(
		plot_bgcolor='#1F2C56',
		paper_bgcolor='#1F2C56',
		title={
		'text':'Active Cases  :'+(v),
		'y':0.93,
		'x':0.5,
		'xanchor':'center',
		'yanchor':'top'
		},
		titlefont={
		'color':'white',
		'size':20

		},
		hovermode='x',
		xaxis=dict(
			title='<b>Date</b>',
			color='white',
			showline=True,
			showgrid=True,
			showticklabels=True,
			linecolor='white',
			linewidth=2,
			ticks='outside',
			tickfont=dict(
				family='Arial',
				size=12,
				color='white'

				)


			),
		yaxis=dict(
			title='<b>Cumulative Cases</b>',
			color='white',
			showline=True,
			showgrid=True,
			showticklabels=True,
			linecolor='white',
			linewidth=2,
			ticks='outside',
			tickfont=dict(
				family='Arial',
				size=12,
				color='white'

				)

			),
		legend={
		'orientation':'h',
		'bgcolor':'#1F2C56',
		'xanchor':'center','x':0.5,'y':-0.3

		},
		font=dict(
			family='sans-serif',
			size=12,
			color='white'

			),


		)




	}






# making all the callback
# callback for new confirmed cases tile below the earth 
# role of callback is to intially create a space for the output and in later when the output is calculated
# it is returned using callback to div created above
@app.callback(
Output('newconfirmedcases','figure'),
Input('select_country','value')
	)

def update_confirmed(v):
	cov_matrix2=finalcov.groupby(['Date','Country/Region'])[['total_confirmed_case','total_confirmed_deaths','total_confirmed_recoveries','Active_cases']].sum().reset_index()
	# after the country is selected from the dropsdown ,using callback input value is stored in v , from where upon , the data with respect to 
	# it is mined and we get the total reuired cases for each graph , 
	no_confirmed=cov_matrix2[cov_matrix2['Country/Region']==v]['total_confirmed_case'].iloc[-1]-cov_matrix2[cov_matrix2['Country/Region']==v]['total_confirmed_case'].iloc[-2]
	diff_confirmed=(cov_matrix2[cov_matrix2['Country/Region']==v]['total_confirmed_case'].iloc[-2]-cov_matrix2[cov_matrix2['Country/Region']==v]['total_confirmed_case'].iloc[-3])
	
	return {
            'data': [ go.Indicator(
                    mode='number+delta',
                    value=no_confirmed,
                    delta={'reference': diff_confirmed,
                           'position': 'right',
                           'valueformat': ',g',
                           'relative': False,
                           'font': {'size': 15}},
                    number={'valueformat': ',',
                            'font': {'size': 20}},
                    domain={'y':[0,1], 'x':[0,1]}
            )],
            'layout': go.Layout(
                    title={'text':'New Confirmed Case',
                           'y': 0.87,
                           'x': 0.5,
                           'xanchor': 'center',
                           'yanchor': 'top'},
                    font=dict(color='orange'),
                    paper_bgcolor='#1F2C56',
                    plot_bgcolor='#1F2C56',
                    height=50)
           



            	}


# this is the callback for indicator graph of new deaths
@app.callback(
Output('newdeaths','figure'),
Input('select_country','value')
	)

def update_confirmed(v):
	cov_matrix2=finalcov.groupby(['Date','Country/Region'])[['total_confirmed_case','total_confirmed_deaths','total_confirmed_recoveries','Active_cases']].sum().reset_index()
	# since we have the cumulative sum case at ith day - case at i-1th day gives the  new required cases for that country
	no_confirmed=cov_matrix2[cov_matrix2['Country/Region']==v]['total_confirmed_deaths'].iloc[-1]-cov_matrix2[cov_matrix2['Country/Region']==v]['total_confirmed_deaths'].iloc[-2]
	diff_confirmed=cov_matrix2[cov_matrix2['Country/Region']==v]['total_confirmed_deaths'].iloc[-2]-cov_matrix2[cov_matrix2['Country/Region']==v]['total_confirmed_deaths'].iloc[-3]
	
	return {
            'data': [ go.Indicator(
                    mode='number+delta',
                    value=no_confirmed,
                    delta={'reference': diff_confirmed,
                           'position': 'right',
                           'valueformat': ',g',
                           'relative': False,
                           'font': {'size': 15}},
                    number={'valueformat': ',',
                            'font': {'size': 20}},
                    domain={'y':[0,1], 'x':[0,1]}
            )],
            'layout': go.Layout(
                    title={'text':'New Deaths',
                           'y': 0.87,
                           'x': 0.5,
                           'xanchor': 'center',
                           'yanchor': 'top'},
                    font=dict(color='orange'),
                    paper_bgcolor='#1F2C56',
                    plot_bgcolor='#1F2C56',
                    height=50)
           



            	}


 # this is the callback for the new recovered case tile
 # similar concpet as of new death is used here 
@app.callback(
Output('newrecoveredcase','figure'),
Input('select_country','value')
	)

def update_confirmed(v):
	cov_matrix2=finalcov.groupby(['Date','Country/Region'])[['total_confirmed_case','total_confirmed_deaths','total_confirmed_recoveries','Active_cases']].sum().reset_index()
	no_confirmed=cov_matrix2[cov_matrix2['Country/Region']==v]['total_confirmed_recoveries'].iloc[-1]-cov_matrix2[cov_matrix2['Country/Region']==v]['total_confirmed_recoveries'].iloc[-2]
	diff_confirmed=cov_matrix2[cov_matrix2['Country/Region']==v]['total_confirmed_recoveries'].iloc[-2]-cov_matrix2[cov_matrix2['Country/Region']==v]['total_confirmed_recoveries'].iloc[-3]
	
	return {
            'data': [ go.Indicator(
                    mode='number+delta',
                    value=no_confirmed,
                    delta={'reference': diff_confirmed,
                           'position': 'right',
                           'valueformat': ',g',
                           'relative': False,
                           'font': {'size': 15}},
                    number={'valueformat': ',',
                            'font': {'size': 20}},
                    domain={'y':[0,1], 'x':[0,1]}
            )],
            'layout': go.Layout(
                    title={'text':'New Confirmed Recoveries',
                           'y': 0.87,
                           'x': 0.5,
                           'xanchor': 'center',
                           'yanchor': 'top'},
                    font=dict(color='orange'),
                    paper_bgcolor='#1F2C56',
                    plot_bgcolor='#1F2C56',
                    height=50)
           



            	}
    # this is the callback for new active cases 

@app.callback(
Output('newactivecase','figure'),
Input('select_country','value')
	)

def update_confirmed(v):
	cov_matrix2=finalcov.groupby(['Date','Country/Region'])[['total_confirmed_case','total_confirmed_deaths','total_confirmed_recoveries','Active_cases']].sum().reset_index()
	no_confirmed=cov_matrix2[cov_matrix2['Country/Region']==v]['Active_cases'].iloc[-1]-cov_matrix2[cov_matrix2['Country/Region']==v]['Active_cases'].iloc[-2]
	diff_confirmed=cov_matrix2[cov_matrix2['Country/Region']==v]['Active_cases'].iloc[-2]-cov_matrix2[cov_matrix2['Country/Region']==v]['Active_cases'].iloc[-3]
	
	return {
            'data': [ go.Indicator(
                    mode='number+delta',
                    value=no_confirmed,
                    delta={'reference': diff_confirmed,
                           'position': 'right',
                           'valueformat': ',g',
                           'relative': False,
                           'font': {'size': 15}},
                    number={'valueformat': ',',
                            'font': {'size': 20}},
                    domain={'y':[0,1], 'x':[0,1]}
            )],
            'layout': go.Layout(
                    title={'text':'New Confirmed Case',
                           'y': 0.87,
                           'x': 0.5,
                           'xanchor': 'center',
                           'yanchor': 'top'},
                    font=dict(color='orange'),
                    paper_bgcolor='#1F2C56',
                    plot_bgcolor='#1F2C56',
                    height=50)
           



            	}



@app.callback(
Output('pie_chart','figure'),
Input('select_country','value')

	)

def update_graph(v):
	cov=finalcov.groupby(['Date','Country/Region'])[['total_confirmed_case','total_confirmed_deaths','total_confirmed_recoveries','Active_cases']].sum().reset_index()
	# here we update the pie chart from the cumulative sum cases from the datasets
	final_confirmed=cov[cov['Country/Region']==v]['total_confirmed_case'].iloc[-1]
	final_death = cov[cov['Country/Region'] == v]['total_confirmed_deaths'].iloc[-1]
	final_recovered = cov[cov['Country/Region'] == v]['total_confirmed_recoveries'].iloc[-1]
	final_active = cov[cov['Country/Region'] == v]['Active_cases'].iloc[-1]
		# making a colors array
	colors=['orange','#dd1e3f','green','#e55467']
	return {
		      'data':[go.Pie(
			   labels=['total_confirmed_case','total_confirmed_deaths','total_confirmed_recoveries','Active_cases'],
			   values=[final_confirmed,final_death,final_recovered,final_active],
			   marker=dict(colors=colors),
			   hoverinfo='label+value+percent',
			   textinfo='label+value',
			   textfont=dict(size=13),
			   hole=0.7,
			   rotation=45

			   )],
		      'layout': go.Layout(
	            plot_bgcolor='#1F2C56',
	            paper_bgcolor='#1F2C56',
	            hovermode='closest',
	            title={'text':'Total Cases : ' + (v),
	                   'y':0.93,
	                   'x':0.5,
	                   'xanchor':'center',
	                   'yanchor':'top'},
	            titlefont={'color':'white',
	                       'size':20},
	            legend={'orientation': 'h',
	                    'bgcolor': '#272b30',
	                    'xanchor': 'center',
	                    'x':0.5,
	                    'y':-0.07},
	            font=dict(
	                size=12,
	                color='white'
	            )
	        )



		}
            

   



if __name__ == '__main__':
    app.run_server(debug=True)