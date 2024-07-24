import streamlit as st
import cryptocompare
from datetime import datetime, date
import pandas as pd
import plotly.graph_objs as go

# Kripto para sembolü ve itibari para birimi
crypto_symbol = st.sidebar.text_input('Kripto Para Sembolü', value='BTC')
currency = st.sidebar.text_input('İtibari Para Birimi', value='USD')

st.title(f"{crypto_symbol}/{currency} Fiyat Grafiği")

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
    df = df.sort_values(by='time')

    return df

df = get_crypto_data(crypto_symbol, currency, start_date, end_date, interval)

if df is not None and not df.empty:
    df['open'] = df['open'].map(lambda x: f"{x:,.4f}".replace(",", "X").replace(".", ",").replace("X", "."))
    df['high'] = df['high'].map(lambda x: f"{x:,.4f}".replace(",", "X").replace(".", ",").replace("X", "."))
    df['low'] = df['low'].map(lambda x: f"{x:,.4f}".replace(",", "X").replace(".", ",").replace("X", "."))
    df['close'] = df['close'].map(lambda x: f"{x:,.4f}".replace(",", "X").replace(".", ",").replace("X", "."))
    df['volumefrom'] = df['volumefrom'].map(lambda x: f"{x:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
    df['volumeto'] = df['volumeto'].map(lambda x: f"{x:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))

    df.columns = ['Tarih', 'Açılış', 'Yüksek', 'Düşük', 'Kapanış', 'Hacim (Miktar)', 'Hacim (Değer)']

    fig = go.Figure()

    fig.add_trace(go.Scatter(x=df['Tarih'], y=df['Kapanış'], mode='lines', name='Kapanış Fiyatı'))

    fig.update_layout(
        title=f"{crypto_symbol}/{currency} Fiyat Grafiği ({interval})",
        xaxis_title='Tarih',
        yaxis_title='Fiyat',
        xaxis_rangeslider_visible=True,
        yaxis=dict(
            fixedrange=False,
            tickformat=",.4f",
            autorange=True
        ),
        xaxis=dict(
            tickformat="%d-%m-%Y %H:%M",
            tickformatstops=[
                dict(dtickrange=[None, 86400000], value="%H:%M:%S"),
                dict(dtickrange=[86400000, 604800000], value="%d-%m %H:%M"),
                dict(dtickrange=[604800000, None], value="%d-%m-%Y")
            ]
        )
    )

    st.plotly_chart(fig)

    st.subheader('Rakamlar')
    st.write(df)
