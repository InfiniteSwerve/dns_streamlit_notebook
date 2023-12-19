import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px


@st.cache
def load_data():
    df = pd.read_csv("./data/sf_budget_2022-25_cleaned.csv")
    return df


# Function for data overview
def data_overview(df):
    info_df = pd.DataFrame(index=df.columns)
    info_df["DataType"] = df.dtypes
    info_df["Count"] = df.count()
    info_df["Missing Values"] = df.isnull().sum()
    info_df["Unique Values"] = df.nunique()

    int_columns = df.select_dtypes(include="int").columns
    info_df.loc[int_columns, "Min Value"] = df[int_columns].min()
    info_df.loc[int_columns, "Max Value"] = df[int_columns].max()

    return info_df


def display_data_overview(df):
    st.write("## Data Overview")
    info_df = data_overview(df)
    st.dataframe(info_df)


def plot_budget_box(df_melted, title, remove_outliers=False):
    if remove_outliers:
        Q1 = df_melted["Budget"].quantile(0.25)
        Q3 = df_melted["Budget"].quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        df_melted = df_melted[
            (df_melted["Budget"] >= lower_bound) & (df_melted["Budget"] <= upper_bound)
        ]
    fig = px.box(
        df_melted,
        x="Budget Year",
        y="Budget",
        labels={"Budget": "Budget"},
        title=title,
        height=500,
    )
    fig.update_layout(showlegend=False)
    st.plotly_chart(fig)


def plot_budget_distribution(df):
    st.write("## Budget Distribution by Service")
    fig = px.bar(
        df,
        x="service_area",
        y="budget_2022_23",
        color="service_area",
        title="Budget Distribution by Service",
        labels={"budget_2022_23": "Budget", "service_area": "Service"},
    )
    fig.update_layout(xaxis_title="Service", yaxis_title="Budget", barmode="stack")
    st.plotly_chart(fig)


def plot_budget_changes(df):
    st.write("## Budget Changes")
    df["change_22_23_to_23_24"] = df["budget_2023_24"] - df["budget_2022_23"]
    df["change_23_24_to_24_25"] = df["budget_2024_25"] - df["budget_2023_24"]
    fig = px.bar(
        df,
        x="service_area",
        y=["change_22_23_to_23_24", "change_23_24_to_24_25"],
        labels={"value": "Budget Change"},
        title="Budget Change from 22-23 to 23-24 and from 23-24 to 24-25 by Service",
        height=500,
    )
    fig.update_layout(barmode="group")
    st.plotly_chart(fig)


def plot_top_departments_by_budget(df):
    st.write("## Top Departments by Budget")
    df_grouped = df.groupby("department")["budget_2022_23"].sum().reset_index()
    df_grouped = df_grouped.sort_values(by="budget_2022_23", ascending=False).head(15)
    fig = px.bar(
        df_grouped,
        x="budget_2022_23",
        y="department",
        orientation="h",
        title="Top Departments by Budget",
        labels={"budget_2022_23": "Budget", "department": "Department"},
    )
    fig.update_layout(xaxis_title="Budget", yaxis_title="Department", barmode="stack")
    st.plotly_chart(fig)


def main():
    st.title("SF Budget Analysis 2022-25")
    df = load_data()
    display_data_overview(df)

    df_melted = pd.melt(
        df,
        id_vars=None,
        value_vars=["budget_2022_23", "budget_2023_24", "budget_2024_25"],
        var_name="Budget Year",
        value_name="Budget",
    )
    plot_budget_box(df_melted, "Box Plot of Budget by Year")
    plot_budget_box(df_melted, "Box Plot of Budget by Year (Without Outliers)", True)

    # Budget distribution and changes
    plot_budget_distribution(df)
    plot_budget_changes(df)

    # Top departments by budget
    plot_top_departments_by_budget(df)


if __name__ == "__main__":
    main()
