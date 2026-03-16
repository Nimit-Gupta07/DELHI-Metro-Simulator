#Delhi Metro Route and Schedule Simulator

A Python-based simulator for the Delhi Metro network covering the 
Blue, Pink, and Magenta lines.

Features
- Metro Timing Module — enter your station and time, get the next 
  3 metro arrivals in both directions
- Journey Planner — finds the fastest route between any two stations,
  including interchanges, total travel time, and fare calculation
- Smart station name matching — suggests correct station names even 
  if you make spelling mistakes
- Peak and off-peak smart card fare discounts

Files
- app.py — web version built with Streamlit
- metro simulator.py — original terminal version (run locally)
- metro_data.txt — station and timing data for all lines

How to Run Locally
pip install streamlit
streamlit run app.py

Live Demo
https://delhi-metro-simulator-qq5mf996r9ksuaqo2o7bhf.streamlit.app/

Built With
Python, Streamlit
