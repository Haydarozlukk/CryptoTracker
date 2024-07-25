import streamlit as st
import cryptocompare
from datetime import datetime, date
import pandas as pd
import plotly.graph_objs as go

# Kripto para sembolü ve itibari para birimi
crypto_symbol1 = st.sidebar.text_input('Kripto Para Sembolü 1', value='BTC')
crypto_symbol2 = st.sidebar.text_input('Kripto Para Sembolü 2', value='ETH')
currency = st.sidebar.text_input('İtibari Para Birimi', value='USD')

st.title(f"{crypto_symbol1}/{currency} ve {crypto_symbol2}/{currency} Fiyat Grafikleri")

# Başlangıç ve bitiş tarihleri
start_date = st.sidebar.date_input('Başlangıç Tarihi', value=date(2020, 1, 1))
end_date = st.sidebar.date_input('Bitiş Tarihi', value=datetime.now().date())

# Başlangıç ve bitiş tarihlerini datetime nesnesine çevirme
start_date = datetime.combine(start_date, datetime.min.time())
end_date = datetime.combine(end_date, datetime.min.time())

# Veri aralığı seçimi
interval = st.sidebar.selectbox('Zaman Aralığı', ('5M', '15M', '30M', '1H', '2H', '4H', '1D', '1W', '1M'))

# Veri çekme fonksiyonu
def get_crypto_data(symbol, currency, start_date, end_date, interval):
    start_timestamp = int(start_date.timestamp())
    end_timestamp = int(end_date.timestamp())
    
    if interval in ['4H', '2H', '1H']:
        data = cryptocompare.get_historical_price_hour(symbol, currency, limit=2000, toTs=end_timestamp)
    elif interval in ['30M', '15M', '5M']:
        data = cryptocompare.get_historical_price_minute(symbol, currency, limit=2000, toTs=end_timestamp)
    elif interval == '1D':
        data = cryptocompare.get_historical_price_day(symbol, currency, limit=2000, toTs=end_timestamp)
    elif interval in ['1W', '1M']:
        data = cryptocompare.get_historical_price_day(symbol, currency, limit=2000, toTs=end_timestamp)
    
    df = pd.DataFrame(data)
    df['time'] = pd.to_datetime(df['time'], unit='s')
    df = df[(df['time'] >= start_date) & (df['time'] <= end_date)]
    
    resample_map = {
        '4H': '4H',
        '2H': '2H',
        '1H': '1H',
        '30M': '30min',
        '15M': '15min',
        '5M': '5min',
        '1D': '1D',
        '1W': '1W',
        '1M': '1M'
    }

    if interval in resample_map:
        df = df.set_index('time').resample(resample_map[interval]).agg({
            'open': 'first',
            'high': 'max',
            'low': 'min',
            'close': 'last',
            'volumefrom': 'sum',
            'volumeto': 'sum'
        }).dropna().reset_index()

    # Tarihe göre sıralama
    df = df.sort_values(by='time', ascending=False)

    return df

# İki farklı kripto para için veri çekme
df1 = get_crypto_data(crypto_symbol1, currency, start_date, end_date, interval)
df2 = get_crypto_data(crypto_symbol2, currency, start_date, end_date, interval)

# İçeriği tam genişliğe yaymak için st.container() kullanma
with st.container():
    # İlk grafik
    if df1 is not None and not df1.empty:
        fig1 = go.Figure()
        fig1.add_trace(go.Scatter(x=df1['time'], y=df1['close'], mode='lines', name=f'{crypto_symbol1} Kapanış Fiyatı'))
        fig1.update_layout(
            title=f"{crypto_symbol1}/{currency} Fiyat Grafiği ({interval})",
            xaxis_title='Tarih',
            yaxis_title='Fiyat',
            xaxis_rangeslider_visible=True
        )
        st.plotly_chart(fig1, use_container_width=True)

    # İkinci grafik
    if df2 is not None and not df2.empty:
        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(x=df2['time'], y=df2['close'], mode='lines', name=f'{crypto_symbol2} Kapanış Fiyatı'))
        fig2.update_layout(
            title=f"{crypto_symbol2}/{currency} Fiyat Grafiği ({interval})",
            xaxis_title='Tarih',
            yaxis_title='Fiyat',
            xaxis_rangeslider_visible=True
        )
        st.plotly_chart(fig2, use_container_width=True)

# Tabloları genişletmek için tekrar st.container() kullanma
with st.container():
    st.subheader(f'{crypto_symbol1} Rakamlar')
    st.write(df1)

    st.subheader(f'{crypto_symbol2} Rakamlar')
    st.write(df2)
