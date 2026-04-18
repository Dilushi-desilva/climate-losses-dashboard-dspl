import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="European Climate Economic Losses",
    layout="wide"
)

df_country = pd.read_csv('df_country.csv')
df_year = pd.read_csv('df_year.csv')
df_type = pd.read_csv('df_type.csv')
df_country_type = pd.read_csv('df_country_type.csv')
df_country_year = pd.read_csv('df_country_year.csv')

df_country = df_country.drop_duplicates(subset=["Name"], keep="first")

st.sidebar.title("Navigation")
st.sidebar.markdown("---")
st.sidebar.write("Explore economic losses from weather and climate-related disasters across Europe, 1980-2024.")
st.sidebar.markdown("---")
page = st.sidebar.radio("Go to", [
    "Overview",
    "The Cost of Climate Change",
    "Country Analysis",
    "Hazard Breakdown",
    "Insured vs Uninsured",
    "Fatalities"
])
st.sidebar.markdown("---")
st.sidebar.write("Data source: European Environment Agency")


if page == "Overview":
    st.title("European Climate Economic Losses")
    st.write("Weather and climate-related extreme events across 38 European countries, 1980-2024")
    
    # Headline numbers
    total_losses = df_country["Losses (M€)"].sum()
    total_insured = df_country["Insured losses (M€)"].sum()
    total_fatalities = int(df_country["FATALITIES"].sum())
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Losses", f"€{total_losses/1000:,.0f}B")
    col2.metric("Total Fatalities", f"{total_fatalities:,}")
    col3.metric("Insured Losses", f"€{total_insured/1000:,.0f}B")

    st.subheader("Annual Losses Over Time")
    df_year["Total"] = df_year["meteorological"] + df_year["hydrological"] + df_year["climatological"]
    fig = px.line(df_year, x="Year", y="Total", 
                  title="Total Climate Losses per Year (M€)",
                  color_discrete_sequence=["#670910"])
    fig.update_layout(plot_bgcolor="white", 
                      paper_bgcolor="white",
                      font=dict(size=14))
    st.plotly_chart(fig, use_container_width=True)

elif page == "The Cost of Climate Change":
    st.title("The Cost of Climate Change")
    st.write("How much has climate change cost Europe since 1980?")
    
    year_range = st.slider("Select year range", min_value=1980, max_value=2024, value=(1980, 2024))
    
    df_filtered = df_year[(df_year["Year"] >= year_range[0]) & (df_year["Year"] <= year_range[1])].copy()
    df_filtered["Total"] = df_filtered["meteorological"] + df_filtered["hydrological"] + df_filtered["climatological"]
    df_filtered["Decade"] = (df_filtered["Year"] // 10 * 10).astype(str) + "s"
    df_decade = df_filtered.groupby("Decade")["Total"].sum().reset_index()
    
    fig = px.bar(df_decade, x="Decade", y="Total",
                 title="Total Losses per Decade (M€)",
                 labels={"Total": "Losses (M€)", "Decade": "Decade"},
                 color_discrete_sequence=["#ec932d"])
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Losses by Hazard Type Over Time")
    df_melt = df_filtered.melt(id_vars=["Year"], 
                                value_vars=["meteorological", "hydrological", "climatological"],
                                var_name="Hazard Type", 
                                value_name="Losses (M€)")
    fig2 = px.line(df_melt, x="Year", y="Losses (M€)", 
                   color="Hazard Type",
                   title="Losses by Hazard Type Over Time")
    st.plotly_chart(fig2, use_container_width=True)

elif page == "Country Analysis":
    st.title("Country Analysis")
    st.write("Which countries suffered the most losses?")
    
    fig = px.choropleth(df_country, 
                        locations="Name",
                        locationmode="country names",
                        color="Losses (M€)",
                        hover_name="Name",
                        scope="europe",
                        title="Total Economic Losses by Country (M€)",
                        color_continuous_scale="Reds")
    st.plotly_chart(fig, use_container_width=True)


    top15 = df_country.nlargest(15, "Losses (M€)")
    fig2 = px.bar(top15, x="Losses (M€)", y="Name", 
                  orientation="h",
                  title="Top 15 Countries by Total Losses (M€)",
                  labels={"Name": ""},
                  color_discrete_sequence=["#ce7980"])
    st.plotly_chart(fig2, use_container_width=True)


elif page == "Hazard Breakdown":
    st.title("Hazard Breakdown")
    st.write("Which type of disaster causes the most damage?")
    
    fig = px.pie(df_type, values="Losses (M€)", names="Hazard",
                 title="Total Losses by Hazard Type",
                 color_discrete_sequence=["#0b5513"])
    st.plotly_chart(fig, use_container_width=True)
    
    fig2 = px.bar(df_type, x="Hazard", y="Fatalities",
                  title="Fatalities by Hazard Type",
                  labels={"Hazard": "Hazard Type"},
                  color_discrete_sequence=["#81a72a"])
    st.plotly_chart(fig2, use_container_width=True)

elif page == "Insured vs Uninsured":
    st.title("Insured vs Uninsured")
    st.write("How much of the losses were actually covered by insurance?")
    
    total = df_country["Losses (M€)"].sum()
    insured = df_country["Insured losses (M€)"].sum()
    uninsured = total - insured
    
    col1, col2 = st.columns(2)
    col1.metric("Insured", f"€{insured/1000:,.0f}B")
    col2.metric("Uninsured", f"€{uninsured/1000:,.0f}B")
    
    fig = px.pie(values=[insured, uninsured],
                 names=["Insured", "Uninsured"],
                 title="Insured vs Uninsured Losses",
                 color_discrete_sequence=["#13095d"])  
    st.plotly_chart(fig, use_container_width=True)



elif page == "Fatalities":
    st.title("Fatalities")
    st.write("The human cost of climate disasters in Europe since 1980.")
    
    total_fatalities = int(df_country["FATALITIES"].sum())
    st.metric("Total Fatalities", f"{total_fatalities:,}")
    
    fig = px.bar(df_type, x="Hazard", y="Fatalities",
                 title="Fatalities by Hazard Type",
                 labels={"Hazard": "Hazard Type"},
                 color="Fatalities",
                 color_continuous_scale="Reds")
    st.plotly_chart(fig, use_container_width=True)
    
    selected_countries = st.multiselect(
        "Select countries to compare",
        options=df_country["Name"].tolist(),
        default=["Germany", "France", "Italy", "Spain"]
    )
    
    df_selected = df_country[df_country["Name"].isin(selected_countries)]
    
    fig2 = px.bar(df_selected, x="Name", y="FATALITIES",
                  title="Fatalities by Selected Countries",
                  labels={"Name": "Country", "FATALITIES": "Fatalities"},
                  color_discrete_sequence=["#5a0e52"])
    st.plotly_chart(fig2, use_container_width=True)