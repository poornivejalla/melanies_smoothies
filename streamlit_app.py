# Import packages
import streamlit as st
from snowflake.snowpark.functions import col

# Title
st.title("Customize Your Smoothie! 🥤")
st.write("Choose the fruits you want in your custom Smoothie!")

# Input: Name
name_on_order = st.text_input('Name on Smoothie:')
st.write('The name on your Smoothie will be:', name_on_order)

# ✅ Updated Snowflake connection
cnx = st.connection("snowflake")
session = cnx.session()

# Load fruit options
my_dataframe = session.table("smoothies.public.fruit_options").select(col("FRUIT_NAME"))

# Convert to list
fruit_list = [row["FRUIT_NAME"] for row in my_dataframe.collect()]

# Multi-select (max 5)
ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:',
    fruit_list,
    max_selections=5
)

# Build ingredients string
ingredients_string = ", ".join(ingredients_list)

# Submit button
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
