import streamlit as st
import requests
from datetime import datetime,date
import matplotlib.pyplot as plt
from collections import defaultdict
import matplotlib.dates as mdates



API_KEY= 'c81936517a6bd48fe0438a3e3d98c596'

## Streamlit app UI
st.set_page_config(
    page_title="Weather dashboard",
    page_icon="🌄",
    layout="wide",
)

st.title("🌤️Weather Dashboard",anchor=False)
CITY = st.text_input("Enter the City name",'Mumbai')

if CITY:
    results = requests.get(f"https://api.openweathermap.org/data/2.5/forecast?q={CITY}&appid={API_KEY}&units=metric")
    if results.status_code == 200:
        data = results.json()

        # Get today's date in 'YYYY-MM-DD' and time format
        now = datetime.now()

        forecast_list = data["list"]

        # Find the closest forecast entry
        closest_entry = min(
            forecast_list,
            key=lambda entry: abs(datetime.strptime(entry["dt_txt"], "%Y-%m-%d %H:%M:%S") - now)
        )

        # --- MAIN WEATHER METRICS ---
        temp =round( closest_entry["main"]["temp"])
        feels_like = round(closest_entry["main"]["feels_like"])
        temp_min =closest_entry["main"]["temp_min"]
        temp_max =closest_entry["main"]["temp_max"]
        pressure = closest_entry["main"]["pressure"]
        humidity = closest_entry["main"]["humidity"]

        # --- WEATHER DESCRIPTION ---
        weather_main = closest_entry["weather"][0]["main"]
        weather_desc = closest_entry["weather"][0]["description"]
        weather_icon = closest_entry["weather"][0]["icon"]

        # --- WIND DETAILS ---
        wind_speed = closest_entry["wind"]["speed"]
        wind_deg = closest_entry["wind"]["deg"]
        wind_gust = closest_entry["wind"].get("gust", "N/A")

        # --- CLOUD COVER & VISIBILITY ---
        clouds = closest_entry["clouds"]["all"]
        visibility = closest_entry.get("visibility", "N/A")


        col1, col2, col3 = st.columns(3)
        with col1:
            st.image(f"http://openweathermap.org/img/wn/{weather_icon}@2x.png", width=200)

        with col2:
            st.markdown(
                f"""
                       <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@600&display=swap" rel="stylesheet">
                       <div style='
                           font-family: "Poppins", sans-serif;
                           font-size: 64px;
                           color: white;
                           text-shadow: 1px 1px 2px #aaa;
                       '>
                           {temp}°C
                       </div>
                       """,
                unsafe_allow_html=True
            )
            st.markdown(f"<h2 style='color: #90D5FF;'>{weather_main} | {weather_desc}</h2>", unsafe_allow_html=True)

        with col3:
            col6, col7 = st.columns(2)
            with col6:
                st.markdown(f"""
                    <div style='font-size: 20px; color: white;'>
                        <p><strong>Humidity</strong>: {humidity}%</p>
                        <p><strong>Wind</strong>: {wind_speed} m/s</p>
                        <p><strong>Wind Direction</strong>: {wind_deg}°</p>
                        <p><strong>Visibility</strong>: {visibility} m</p>
                    </div>
                """, unsafe_allow_html=True)

            with col7:
                st.image("Images/new.png", width=80)


        st.subheader(f"🌡️Max/Min Temperature: {temp_max}°C/{temp_min}°C", divider=False,anchor=False)
        container = st.container(border=True)




        tab1, tab2, tab3 = st.tabs(["Today Forcast", "🌧️ 3-Hour Rainfall Forecast (Next 5 Days)","📆 5-Day Weather Forecast"])
        with tab2:
            daily_rain = defaultdict(float)

            for entry in data["list"]:
                dt = datetime.strptime(entry["dt_txt"], "%Y-%m-%d %H:%M:%S")
                date_str = dt.strftime("%Y-%m-%d")
                rain = entry.get("rain", {}).get("3h", 0)
                daily_rain[date_str] += rain

            # Prepare data for plotting
            dates = list(daily_rain.keys())
            totals = list(daily_rain.values())

            # Plot
            fig1, ax = plt.subplots(figsize=(10, 5))
            ax.bar(dates, totals, color='dodgerblue', edgecolor='black')

            # Styling
            ax.set_title("Total Daily Rainfall Forecast (Next 5 Days)", fontsize=16)
            ax.set_xlabel("Date", fontsize=12)
            ax.set_ylabel("Rainfall (mm)", fontsize=12)
            plt.xticks(rotation=45)
            plt.grid(axis='y')

            # Show in Streamlit
            st.pyplot(fig1)

            # --- Spacer ---
            st.markdown("---")

            ##Second Graph(Line graph)
            # Extract timestamps and rainfall values
            timestamps = []
            rainfall = []

            for entry in data["list"]:
                dt = datetime.strptime(entry["dt_txt"], "%Y-%m-%d %H:%M:%S")
                rain = entry.get("rain", {}).get("3h", 0)  # mm of rain in last 3h
                timestamps.append(dt)
                rainfall.append(rain)

            # Create the plot
            fig2, ax = plt.subplots(figsize=(12, 5))
            ax.plot(timestamps, rainfall, color='royalblue', marker='o', linestyle='-', linewidth=2, markersize=5)

            # Format the plot
            ax.set_title(f"3-Hour Interval Rainfall Forecast for {CITY}", fontsize=16)
            ax.set_xlabel("Date & Time", fontsize=12)
            ax.set_ylabel("Rainfall (mm)", fontsize=12)
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%d %b %H:%M'))
            plt.xticks(rotation=45)
            plt.grid(True)

            # Show in Streamlit
            st.pyplot(fig2)

        with tab3:
            st.markdown("""
                <style>
                .weather-card {
                    background-color: #e0e0e0;
                    border: 1px solid #ccc;
                    border-radius: 10px;
                    padding: 15px;
                    margin-bottom: 15px;
                    color: black !important;
                }
                .weather-card h4, .weather-card p {
                    color: black !important;
                    margin: 4px 0;
                }
                .weather-content {
                    display: flex;
                    align-items: center;
                    justify-content: space-between;
                }
                .weather-info {
                    flex: 1.5;
                    padding-left: 15px;
                }
                .weather-extra {
                    flex: 1;
                    text-align: right;
                }
                </style>
            """, unsafe_allow_html=True)


            # Group by date
            daily_data = defaultdict(list)
            for entry in data["list"]:
                date_str = entry["dt_txt"].split(" ")[0]
                daily_data[date_str].append(entry)

            for i, (date, entries) in enumerate(daily_data.items()):
                if i >= 5:
                    break

                temps = [e["main"]["temp"] for e in entries]
                icons = [e["weather"][0]["icon"] for e in entries]
                descriptions = [e["weather"][0]["description"] for e in entries]
                pops = [e.get("pop", 0) for e in entries]

                temp_max = round(max(temps))
                temp_min = round(min(temps))
                description = max(set(descriptions), key=descriptions.count).capitalize()
                icon = icons[0]
                pop_percent = int(max(pops) * 100)

                day_name = datetime.strptime(date, "%Y-%m-%d").strftime("%A")
                date_label = f"{day_name} ({datetime.strptime(date, '%Y-%m-%d').strftime('%d %b')})"

                # Card HTML
                st.markdown(f"""
                    <div class="weather-card">
                        <div class="weather-content">
                            <div>
                                <img src="http://openweathermap.org/img/wn/{icon}@2x.png" width="60">
                            </div>
                            <div class="weather-info">
                                <h4>{date_label}</h4>
                                <p>🌡️ {temp_max}° / {temp_min}°</p>
                                <p>☁️ {description}</p>
                            </div>
                            <div class="weather-extra">
                                <p>💧 {pop_percent}%<br>chance of rain</p>
                            </div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)

        with tab1:

            # --- Filter Only Today's Data ---
            today_str = now.strftime("%Y-%m-%d")
            today_data = [entry for entry in data["list"] if entry["dt_txt"].startswith(today_str)]

            # --- Extract Time, Temp, Humidity ---
            times = [entry["dt_txt"].split(" ")[1][:5] for entry in today_data]
            temps = [entry["main"]["temp"] for entry in today_data]
            humidity = [entry["main"]["humidity"] for entry in today_data]

            # --- Plot 1: Temperature vs Time ---
            fig1, ax1 = plt.subplots(figsize=(8, 4))
            ax1.plot(times, temps, marker='o', color='orange', linewidth=2)
            ax1.set_title("🌡️ Temperature vs Time (Today)")
            ax1.set_xlabel("Time")
            ax1.set_ylabel("Temperature (°C)")
            ax1.grid(True)
            st.pyplot(fig1)

            # --- Spacer ---
            st.markdown("---")

            # --- Plot 2: Temperature & Humidity (Dual Axis) ---
            fig2, ax2 = plt.subplots(figsize=(8, 5))

            # Temp on left Y-axis
            ax2.set_xlabel("Time")
            ax2.set_ylabel("Temperature (°C)", color="orangered")
            ax2.plot(times, temps, color="orangered", marker='o', label="Temperature")
            ax2.tick_params(axis="y", labelcolor="orangered")

            # Humidity on right Y-axis
            ax3 = ax2.twinx()
            ax3.set_ylabel("Humidity (%)", color="blue")
            ax3.plot(times, humidity, color="blue", marker='s', label="Humidity")
            ax3.tick_params(axis="y", labelcolor="blue")

            fig2.suptitle("🌡️📈 Temperature & Humidity Forecast (Today)", fontsize=14)
            fig2.tight_layout()
            st.pyplot(fig2)
    else:
        st.title("❌City Not Found",anchor=False)
        st.header("Enter a valid city name🏙️")

else:
    st.title("❌City Not Found",anchor=False)
    st.header("Enter a valid city name🏙️",anchor=False   )









