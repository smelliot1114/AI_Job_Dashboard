#!/usr/bin/env python
# coding: utf-8

# In[17]:


pip install dash plotly pandas geopandas


# In[18]:


import dash
from dash import dcc, html
import plotly.express as px
import pandas as pd

# ====== Load Data ======
density_map_data = pd.read_csv("DensityMapDataV2_Cleaned.csv")  # Ensure correct file
top_ai_skills_data = pd.read_csv("TopAISkillsChartDataV2.csv")
top_ai_career_data = pd.read_csv("TopAICareerDataV2.csv")

# ====== 🔥 FIX STATE ABBREVIATIONS ======
state_abbrev = {
    "Alabama": "AL", "Alaska": "AK", "Arizona": "AZ", "Arkansas": "AR", "California": "CA",
    "Colorado": "CO", "Connecticut": "CT", "Delaware": "DE", "Florida": "FL", "Georgia": "GA",
    "Hawaii": "HI", "Idaho": "ID", "Illinois": "IL", "Indiana": "IN", "Iowa": "IA",
    "Kansas": "KS", "Kentucky": "KY", "Louisiana": "LA", "Maine": "ME", "Maryland": "MD",
    "Massachusetts": "MA", "Michigan": "MI", "Minnesota": "MN", "Mississippi": "MS",
    "Missouri": "MO", "Montana": "MT", "Nebraska": "NE", "Nevada": "NV", "New Hampshire": "NH",
    "New Jersey": "NJ", "New Mexico": "NM", "New York": "NY", "North Carolina": "NC",
    "North Dakota": "ND", "Ohio": "OH", "Oklahoma": "OK", "Oregon": "OR", "Pennsylvania": "PA",
    "Rhode Island": "RI", "South Carolina": "SC", "South Dakota": "SD", "Tennessee": "TN",
    "Texas": "TX", "Utah": "UT", "Vermont": "VT", "Virginia": "VA", "Washington": "WA",
    "West Virginia": "WV", "Wisconsin": "WI", "Wyoming": "WY", "Washington, D.C.": "DC"
}

# Apply state abbreviation mapping
density_map_data["state_abbrev"] = density_map_data["state_name"].map(state_abbrev)

# ====== 🗺️ AI Job Density Map (No Changes to This) ======
fig_density = px.choropleth(
    density_map_data,
    locations="state_abbrev",
    locationmode="USA-states",
    color="count",  # Color based on AI job count
    hover_name="state_name",
    hover_data={"count": True, "percent": True},  # Corrected hover order
    color_continuous_scale="Blues",
    scope="usa",
    title="AI Job Density by State"
)

fig_density.update_traces(
    hovertemplate="<b>%{hovertext}</b><br>AI Job Count: %{customdata[0]:,.0f}<br>Percentage of AI Listings: %{customdata[1]:.2f}%<extra></extra>"
)

# ====== 🔴 Dash App ======
app = dash.Dash(__name__)

app.layout = html.Div([
    html.H1("AI Job Market Dashboard", style={"textAlign": "center", "fontFamily": "Arial, sans-serif", "color": "#ffffff"}),
    
    # 🗺️ Density Map (at the top)
    dcc.Graph(figure=fig_density),

    # 📌 Select States Dropdown for Career Areas
    html.Div([
        html.Label("Select State 1:", style={"color": "#ffffff"}),
        dcc.Dropdown(
            id="career_state_1",
            options=[{"label": state, "value": state} for state in top_ai_career_data["state_name"].unique()],
            value="California",
            clearable=False
        ),
        html.Label("Select State 2:", style={"color": "#ffffff"}),
        dcc.Dropdown(
            id="career_state_2",
            options=[{"label": state, "value": state} for state in top_ai_career_data["state_name"].unique()],
            value="Texas",
            clearable=False
        ),
    ], style={"width": "40%", "margin": "auto"}),

    # 📊 Career Area Comparison Chart
    dcc.Graph(id="career_comparison_chart"),

    # 📌 Select States Dropdown for AI Skills
    html.Div([
        html.Label("Select State 1:", style={"color": "#ffffff"}),
        dcc.Dropdown(
            id="skills_state_1",
            options=[{"label": state, "value": state} for state in top_ai_skills_data["state_name"].unique()],
            value="California",
            clearable=False
        ),
        html.Label("Select State 2:", style={"color": "#ffffff"}),
        dcc.Dropdown(
            id="skills_state_2",
            options=[{"label": state, "value": state} for state in top_ai_skills_data["state_name"].unique()],
            value="Texas",
            clearable=False
        ),
    ], style={"width": "40%", "margin": "auto"}),

    # 📊 AI Skills Comparison Chart
    dcc.Graph(id="skills_comparison_chart")

], style={"backgroundColor": "#2c2c2c", "padding": "20px"})  # Grey background


# ====== 🔄 Callbacks for Dynamic Updates (Only Changes Proportion × 100) ======
@app.callback(
    dash.Output("career_comparison_chart", "figure"),
    [dash.Input("career_state_1", "value"), dash.Input("career_state_2", "value")]
)
def update_career_chart(state1, state2):
    filtered_data = top_ai_career_data[top_ai_career_data["state_name"].isin([state1, state2])]
    filtered_data["proportion"] *= 100  # Convert proportion to percentage

    fig = px.bar(
        filtered_data,
        x="lot_career_area_name",
        y="proportion",
        color="state_name",
        hover_data={"entry_count": True, "proportion": ":.1f"},  # Show proper percentage
        title=f"Top 12 AI Career Areas: {state1} vs {state2}",
        labels={"lot_career_area_name": "Career Area", "proportion": "Percentage of AI Listings"},
        barmode="group"
    )
    fig.update_layout(xaxis_tickangle=-45, yaxis_title="Percentage (%)", plot_bgcolor="#2c2c2c", paper_bgcolor="#2c2c2c", font={"color": "white"})

    return fig


@app.callback(
    dash.Output("skills_comparison_chart", "figure"),
    [dash.Input("skills_state_1", "value"), dash.Input("skills_state_2", "value")]
)
def update_skills_chart(state1, state2):
    filtered_data = top_ai_skills_data[top_ai_skills_data["state_name"].isin([state1, state2])]
    filtered_data["proportion"] *= 100  # Convert proportion to percentage

    fig = px.bar(
        filtered_data,
        x="skills_name",
        y="proportion",
        color="state_name",
        hover_data={"skill_count": True, "proportion": ":.1f"},  # Show proper percentage
        title=f"Top 10 AI Skills: {state1} vs {state2}",
        labels={"skills_name": "AI Skill", "proportion": "Percentage of AI Listings"},
        barmode="group"
    )
    fig.update_layout(xaxis_tickangle=-30, yaxis_title="Percentage (%)", plot_bgcolor="#2c2c2c", paper_bgcolor="#2c2c2c", font={"color": "white"})

    return fig


# ====== 🚀 Run the Dash App ======
if __name__ == "__main__":
    app.run_server(debug=True, host="0.0.0.0", port=8050)


# In[ ]:




