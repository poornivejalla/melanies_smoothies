# Import packages
import streamlit as st
from snowflake.snowpark.functions import col
import requests

# Title
st.title("Customize Your Smoothie! 🥤")
st.write("Choose the fruits you want in your custom Smoothie!")

# Input
name_on_order = st.text_input('Name on Smoothie:')
st.write('The name on your Smoothie will be:', name_on_order)

# Snowflake connection
cnx = st.connection("snowflake")
session = cnx.session()

# Load dataframe (FRUIT_NAME + SEARCH_ON)
my_dataframe = session.table("smoothies.public.fruit_options") \
    .select(col("FRUIT_NAME"), col("SEARCH_ON"))

# Convert to Pandas
pd_df = my_dataframe.to_pandas()

# Multi-select
ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:',
    pd_df["FRUIT_NAME"],
    max_selections=5
)

# -----------------------------
# 🍉 Nutrition Section
# -----------------------------
ingredients_string = ''

if ingredients_list:

    for fruit_chosen in ingredients_list:

        ingredients_string += fruit_chosen + ', '

        # Get SEARCH_ON value
        try:
            search_on = pd_df.loc[
                pd_df["FRUIT_NAME"] == fruit_chosen,
                "SEARCH_ON"
            ].iloc[0]

            if not search_on:
                st.warning(f"No API mapping for {fruit_chosen}")
                continue

        except Exception:
            st.error(f"Search value not found for {fruit_chosen}")
            continue

        # Title
        st.subheader(f"{fruit_chosen} Nutrition Information")

        try:
            # API call
            url = f"https://my.smoothiefroot.com/api/fruit/{search_on.lower()}"
            response = requests.get(url)

            if response.status_code != 200:
                st.error("Fruit not found in SmoothieFroot API")
                continue

            data = response.json()
            nutrition = data["nutrition"]

            # Clean table display
            table_data = {
                "Nutrition": list(nutrition.keys()),
                "Value": list(nutrition.values())
            }

            st.dataframe(table_data, use_container_width=True)

        except Exception as e:
            st.error("Error fetching data")
            st.write(e)

# -----------------------------
# Submit Order
# -----------------------------
if st.button('Submit Order'):

    if not name_on_order:
        st.error("Please enter a name.")

    elif not ingredients_list:
        st.error("Please select ingredients.")

    else:
        try:
            insert_sql = f"""
            INSERT INTO smoothies.public.orders (name_on_order, ingredients, order_filled)
            VALUES ('{name_on_order}', '{ingredients_string}', FALSE)
            """

            session.sql(insert_sql).collect()
            st.success("✅ Order submitted successfully!")

        except Exception as e:
            st.error("Insert failed")
            st.write(e)
