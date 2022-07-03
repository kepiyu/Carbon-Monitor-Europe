#CM_EU: Calculations of European near-real-time CO2 emissions
#Author: Piyu Ke
#Time: 20220703

#Load packages
import pandas as pd
import numpy as np
import time
import datetime

#Input_data
Baseline_2019 = pd.read_excel('/Users/kepiyu/SeaDrive/我的资料库/PhD/工作/EU_CarbonMonitor/In_put/Baseline_CO2_Carbon+Monitor_2021_v1.1.xlsx',sheet_name='Baseline_CO2_2019',index_col=1)
EU_IPI = pd.read_excel('/Users/kepiyu/SeaDrive/我的资料库/PhD/工作/EU_CarbonMonitor/In_put/EU_IPI.xlsx',sheet_name='Sheet 1',index_col=0)
IE_IPI = pd.read_excel('/Users/kepiyu/SeaDrive/我的资料库/PhD/工作/EU_CarbonMonitor/In_put/IE_IPI.xlsx',sheet_name='Unpivoted',index_col=1,parse_dates=['Month'])
UK_IPI = pd.read_excel('/Users/kepiyu/SeaDrive/我的资料库/PhD/工作/EU_CarbonMonitor/In_put/UK_IPI.xlsx',sheet_name='IoP and Sectors to 4dp',index_col=0,parse_dates=['Time'])
GT_CO2 = pd.read_excel('/Users/kepiyu/SeaDrive/我的资料库/PhD/工作/EU_CarbonMonitor/In_put/Emissions_20211201.xlsx',sheet_name='Emission',index_col=0,parse_dates=['Time'])
RES_CO2 = pd.read_excel('/Users/kepiyu/SeaDrive/我的资料库/PhD/工作/EU_CarbonMonitor/In_put/GlobalResEmis2018-2020Q1(7).xlsx',sheet_name='DailyEmis',index_col=3)

countries = {
    'Austria',
    'Belgium',
    'Bulgaria',
    'Croatia',
    'Cyprus',
    'Czech Republic',
    'Denmark',
    'Estonia',
    'Finland',
    'France',
    'Germany',
    'Greece',
    'Hungary',
    'Ireland',
    'Italy',
    'Latvia',
    'Lithuania',
    'Luxembourg',
    'Malta',
    'Netherlands',
    'Poland',
    'Portugal',
    'Romania',
    'Slovakia',
    'Slovenia',
    'Spain',
    'Sweden',
    'United Kingdom'
}


#Power
Power_countries = {
    'Austria',
    'Belgium',
    'Bulgaria',
    'Croatia',
    'Cyprus',
    'Czech Republic',
    'Denmark',
    'Estonia',
    'Finland',
    'France',
    'Germany',
    'Greece',
    'Hungary',
    'Ireland',
    'Italy',
    'Latvia',
    'Netherlands',
    'Poland',
    'Portugal',
    'Slovakia',
    'Slovenia',
    'Spain',
    'United Kingdom',
    'Romania'
}


Power_daily = pd.DataFrame(index=pd.period_range(start='2019-01-01',end='2022-05-31',freq='D'),columns=countries)
EU_Power = pd.read_excel('/Users/kepiyu/SeaDrive/我的资料库/PhD/工作/EU_CarbonMonitor/In_put/EU_Power.xlsx',index_col=0,parse_dates=['date'])
for country in Power_countries:
    for date in pd.period_range(start='2019-01-01',end='2022-05-31',freq='D'):
        Power_daily.loc[date,country] = EU_Power.loc['%i%2.2i%2.2i'%(date.year,date.month,date.day),country]/1000


Res_Power_countries = {
    'Lithuania',
    'Luxembourg',
    'Malta',
    'Sweden'
}

EU24_daily = pd.DataFrame(index=pd.period_range(start='2019-01-01',end='2022-05-31',freq='D'),columns=['EU24'])
for date in pd.period_range(start='2019-01-01',end='2022-05-31',freq='D'):
    EU24_daily.loc[date,'EU24']=Power_daily.loc[date].sum()

for country in Res_Power_countries:
    year_sum =  EU24_daily['2019-01-01':'2019-12-31'].sum()
    for date in pd.period_range(start='2019-01-01',end='2019-12-31',freq='D'):
        Power_daily.loc[date,country]=Baseline_2019.loc[country,'Power']*float(EU24_daily.loc[date])/float(year_sum)

for year in [2020,2021,2022]:
    for country in Res_Power_countries:
        if year == 2022:
            for date in pd.period_range(start='%i-01-01'%(year),end='%i-05-31'%(year),freq='D'):
                Power_daily.loc[date,country]=Power_daily.loc[pd.Period('2019-01-01',freq='D'),country]*float(EU24_daily.loc[date])/float(EU24_daily.loc[pd.Period('2019-01-01',freq='D')])
        else:
            for date in pd.period_range(start='%i-01-01'%(year),end='%i-12-31'%(year),freq='D'):
                Power_daily.loc[date,country]=Power_daily.loc[pd.Period('2019-01-01',freq='D'),country]*float(EU24_daily.loc[date])/float(EU24_daily.loc[pd.Period('2019-01-01',freq='D')])

#Industry
EU_IPI=EU_IPI.dropna(axis=1,how='all')
for col in EU_IPI.columns:
    if col.startswith('Unnamed'):
        del EU_IPI[col]
EU_IPI = pd.DataFrame(EU_IPI.values.T, index=EU_IPI.columns, columns=EU_IPI.index)
EU_IPI.index = pd.period_range(start='2019-01',end='2022-05',freq='M')
IE_IPI.index = pd.period_range(start='2015-01',end='2022-05',freq='M')
UK_IPI.index = pd.period_range(start='1997-01',end='2022-05',freq='M')
EU_IPI['Ireland']=IE_IPI.loc['2019-01':'2022-05','VALUE']
EU_IPI['United Kingdom'] = UK_IPI.loc['2019-01':'2022-05','Manufacturing']

df_monthly = pd.DataFrame(index=pd.period_range(start='2019-01',end='2022-05',freq='M'),columns=countries)

for country in countries:
    #print(country)
    allindex=0
    for month in range(1,13):
        monthindex = EU_IPI.loc[pd.to_datetime('2019-%2.2i'%(month)),country]
        allindex=allindex+monthindex
    #print(allindex)
    for month in range(1,13):
        df_monthly.loc[pd.to_datetime('2019-%2.2i'%(month)),country] = Baseline_2019.loc[country,'Industry (incl. Cement Process)']*EU_IPI.loc[pd.to_datetime('2019-%2.2i'%(month)),country]/allindex

for country in countries:
    #print(country)
    allindex=0
    monthindex=0
    for month in range(1,13):
        monthindex = EU_IPI.loc[pd.to_datetime('2020-%2.2i'%(month)),country]/EU_IPI.loc[pd.to_datetime('2019-%2.2i'%(month)),country]
        df_monthly.loc[pd.to_datetime('2020-%2.2i'%(month)),country] = df_monthly.loc[pd.to_datetime('2019-%2.2i'%(month)),country]*monthindex
    monthindex=0
    for month in range(1,13):
        monthindex = EU_IPI.loc[pd.to_datetime('2021-%2.2i'%(month)),country]/EU_IPI.loc[pd.to_datetime('2019-%2.2i'%(month)),country]
        df_monthly.loc[pd.to_datetime('2021-%2.2i'%(month)),country] = df_monthly.loc[pd.to_datetime('2019-%2.2i'%(month)),country]*monthindex
    for month in range(1,6):
        monthindex = EU_IPI.loc[pd.to_datetime('2022-%2.2i'%(month)),country]/EU_IPI.loc[pd.to_datetime('2019-%2.2i'%(month)),country]
        df_monthly.loc[pd.to_datetime('2022-%2.2i'%(month)),country] = df_monthly.loc[pd.to_datetime('2019-%2.2i'%(month)),country]*monthindex


df_daily = pd.DataFrame(index=pd.period_range(start='2019-01-01',end='2022-05-31'),columns=countries)
days = pd.period_range(start='2019-01-01',end='2022-05-31')

for country in countries:
    for day in days:
        df_daily.loc[day,country] = df_monthly.loc[pd.Period('%i-%2.2i'%(day.year,day.month),freq='M'),country]*Power_daily.loc[day,country]/Power_daily.loc['%i-%2.2i'%(day.year,day.month),country].sum()

#Ground Transport
GT_daily = pd.DataFrame(index=pd.period_range(start='2019-01-01',end='2022-05-31'),columns=countries)

GT_countries = {
    'Austria',
    'Belgium',
    'Bulgaria',
    'Czech Republic',
    'Denmark',
    'Estonia',
    'Finland',
    'France',
    'Germany',
    'Greece',
    'Hungary',
    'Ireland',
    'Italy',
    'Latvia',
    'Lithuania',
    'Luxembourg',
    'Netherlands',
    'Poland',
    'Portugal',
    'Romania',
    'Slovakia',
    'Slovenia',
    'Spain',
    'Sweden',
    'United Kingdom'
}

Res_GT_countries = {
    'Croatia',
    'Cyprus',
    'Malta'
}

for country in GT_countries:
    for date in pd.period_range(start='2019-01-01',end='2022-05-31',freq='D'):
        GT_daily.loc[date,country] = GT_CO2.loc['%i-%2.2i-%2.2i 00:00:00'%(date.year,date.month,date.day),country]/1000000

GT25_daily = pd.DataFrame(index=pd.period_range(start='2019-01-01',end='2022-05-31',freq='D'),columns=['GT25'])
for date in pd.period_range(start='2019-01-01',end='2022-05-31',freq='D'):
    GT25_daily.loc[date,'GT25']=GT_daily.loc[date].sum()

for country in Res_GT_countries:
    year_sum =  GT25_daily['2019-01-01':'2019-12-31'].sum()
    for date in pd.period_range(start='2019-01-01',end='2019-12-31',freq='D'):
        GT_daily.loc[date,country]=Baseline_2019.loc[country,'Ground Transport']*float(GT25_daily.loc[date])/float(year_sum)

for year in [2020,2021,2022]:
    for country in Res_GT_countries:
        if year == 2022:
            for date in pd.period_range(start='%i-01-01'%(year),end='%i-05-31'%(year),freq='D'):
                GT_daily.loc[date,country]=GT_daily.loc[pd.Period('2019-01-01',freq='D'),country]*float(GT25_daily.loc[date])/float(GT25_daily.loc[pd.Period('2019-01-01',freq='D')])
        else:
            for date in pd.period_range(start='%i-01-01'%(year),end='%i-12-31'%(year),freq='D'):
                GT_daily.loc[date,country]=GT_daily.loc[pd.Period('2019-01-01',freq='D'),country]*float(GT25_daily.loc[date])/float(GT25_daily.loc[pd.Period('2019-01-01',freq='D')])

#Residential
del RES_CO2['IPCC-Annex']
del RES_CO2['World Region']
del RES_CO2['ISO_A3']
del RES_CO2['IPCC']
del RES_CO2['IPCC_description']
RES_CO2 = pd.DataFrame(RES_CO2.values.T, index=RES_CO2.columns, columns=RES_CO2.index)

RES_daily = pd.DataFrame(index=pd.period_range(start='2019-01-01',end='2022-05-31'),columns=countries)

for country in countries:
    for date in pd.period_range(start='2019-01-01',end='2022-05-31',freq='D'):
        RES_daily.loc[date,country] = RES_CO2.loc['%i%2.2i%2.2i'%(date.year,date.month,date.day),country]/1000

#Domestic Aviation/International Aviation
DA_daily = pd.DataFrame(index=pd.period_range(start='2019-01-01',end='2022-05-31'),columns=countries)
IA_daily = pd.DataFrame(index=pd.period_range(start='2019-01-01',end='2022-05-31'),columns=countries)

for sector in ['dom','int']:
    for year in ['2019','2020','2021','2022']:
        if year=='2022':
            dates = pd.period_range(start=str(year)+'-01-01',end=str(year)+'-05-31',freq='D')
        else:
            dates = pd.period_range(start=str(year)+'-01-01',end=str(year)+'-12-31',freq='D')
        FR_CO2 = pd.read_excel('/Users/kepiyu/SeaDrive/我的资料库/PhD/工作/EU_CarbonMonitor/In_put/fr24.xlsx',sheet_name='CO2 emissions '+str(year),index_col=0,parse_dates=['time'])
        if sector == 'dom':
            for country in countries:
                for date in dates:
                    DA_daily.loc[date,country]=FR_CO2.loc['%i-%2.2i-%2.2i'%(date.year,date.month,date.day),str(country)+'_dom']
        else:
            for country in countries:
                for date in dates:
                    IA_daily.loc[date,country]=FR_CO2.loc['%i-%2.2i-%2.2i'%(date.year,date.month,date.day),str(country)+'_int']


result_daily = {
    'Power_daily':'Power',
    'df_daily':'Industry',
    'GT_daily':'Ground Transport',
    'RES_daily':'Residential',
    'DA_daily':'Domestic Aviation',
    'IA_daily':'International Aviation'
}
for r_daily in result_daily.keys():
    exec("%s['EU27 & UK'] = %s.apply(lambda x: x.sum(),axis=1)"%(r_daily,r_daily))

countries = {
    'Austria',
    'Belgium',
    'Bulgaria',
    'Croatia',
    'Cyprus',
    'Czech Republic',
    'Denmark',
    'Estonia',
    'Finland',
    'France',
    'Germany',
    'Greece',
    'Hungary',
    'Ireland',
    'Italy',
    'Latvia',
    'Lithuania',
    'Luxembourg',
    'Malta',
    'Netherlands',
    'Poland',
    'Portugal',
    'Romania',
    'Slovakia',
    'Slovenia',
    'Spain',
    'Sweden',
    'United Kingdom',
    'EU27 & UK'
}

result = pd.DataFrame(index = range(0,1247*29*6,1),columns=['country','date','sector','value','timestamp'])


i=0
for r_daily in result_daily.keys():
    for index, row in eval(r_daily).iterrows():
        for country in countries:
            result.loc[i,'country']= country
            result.loc[i,'date'] = row.name.strftime('%d/%m/%Y')
            result.loc[i,'sector']= result_daily[r_daily]
            result.loc[i,'value'] = row[country]
            result.loc[i,'timestamp'] = time.mktime(row.name.to_timestamp().to_pydatetime().timetuple())
            i=i+1


result.to_csv('/Users/kepiyu/Desktop/CM_EU.csv', index=False)
