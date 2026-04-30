# Import packages
import streamlit as st
from snowflake.snowpark.functions import col
import requests

# Title
st.title("Customize Your Smoothie! 🥤")
st.write("Choose the fruits you want in your custom Smoothie!")

# Input: Name
name_on_order = st.text_input('Name on Smoothie:')
st.write('The name on your Smoothie will be:', name_on_order)

# Snowflake connection
cnx = st.connection("snowflake")
session = cnx.session()

# Load fruit options (✅ include SEARCH_ON)
my_dataframe = session.table("smoothies.public.fruit_options") \
    .select(col("FRUIT_NAME"), col("SEARCH_ON"))

# Convert to dictionary (fruit → search value)
fruit_rows = my_dataframe.collect()

fruit_map = {
    row["FRUIT_NAME"]: row["SEARCH_ON"]
    for row in fruit_rows
}

# Fruit list for UI
fruit_list = list(fruit_map.keys())

# Multi-select
ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:',
    fruit_list,
    max_selections=5
)

# -----------------------------
# 🍉 Nutrition Section
# -----------------------------
ingredients_string = ''

if ingredients_list:

    for fruit_chosen in ingredients_list:

        ingredients_string += fruit_chosen + ', '

        # Title per fruit
        st.subheader(f"{fruit_chosen} Nutrition Information")

        try:
            # ✅ USE SEARCH_ON instead of fruit_chosen
            search_value = fruit_map[fruit_chosen]

            if not search_value:
                st.error("No API mapping available for this fruit.")
                continue

            url = f"https://my.smoothiefroot.com/api/fruit/{search_value.lower()}"
            response = requests.get(url)

            if response.status_code == 200:

                data = response.json()
                nutrition = data["nutrition"]

                # Convert to table format
                table_data = {
                    "family": [data["family"]] * 4,
                    "genus": [data["genus"]] * 4,
                    "id": [data["id"]] * 4,
                    "name": [data["name"]] * 4,
                    "nutrition": list(nutrition.keys()),
                    "value": list(nutrition.values()),
                    "order": [data["order"]] * 4
                }

                st.dataframe(table_data, use_container_width=True)

            else:
                st.error("Sorry, that fruit is not in our database.")

        except Exception as e:
            st.error("Error fetching data.")
            st.write(e)

# -----------------------------
# Submit Order
# -----------------------------
time_to_insert = st.button('Submit Order')

if time_to_insert:

    if not name_on_order:
        st.error("Please enter a name.")

    elif not ingredients_list:
        st.error("Please select at least one ingredient.")

    else:
        try:
            insert_sql = f"""
            INSERT INTO smoothies.public.orders (name_on_order, ingredients, order_filled)
            VALUES ('{name_on_order}', '{ingredients_string}', FALSE)
            """

            session.sql(insert_sql).collect()
            st.success("✅ Order submitted successfully!")

        except Exception as e:
            st.error("Something went wrong while placing the order.")
            st.write(e)
