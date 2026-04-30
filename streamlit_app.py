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

# Load fruit options
my_dataframe = session.table("smoothies.public.fruit_options").select(col("FRUIT_NAME"))

# Convert to list
fruit_list = [row["FRUIT_NAME"] for row in my_dataframe.collect()]

# Multi-select
ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:',
    fruit_list,
    max_selections=5
)

# -----------------------------
# 🍉 Nutrition Section
# -----------------------------
if ingredients_list:

    ingredients_string = ''

    for fruit_chosen in ingredients_list:

        ingredients_string += fruit_chosen + ', '

        # ✅ Title per fruit (like screenshot)
        st.subheader(f"{fruit_chosen} Nutrition Information")

        try:
            # ✅ Dynamic API call (NOT hardcoded)
            url = f"https://my.smoothiefroot.com/api/fruit/{fruit_chosen.lower()}"
            response = requests.get(url)

            if response.status_code == 200:

                data = response.json()
                nutrition = data["nutrition"]

                # ✅ Convert to table format
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
                # ✅ Handles fruits not in API (like Ximenia)
                st.error("Sorry, that fruit is not in our database.")

        except Exception:
            st.error("Error fetching data.")

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
