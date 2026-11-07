import streamlit as st
import pandas as pd
import json
from datetime import datetime

## Functions

## association strength based on lift
def get_lift_strength(lift):

    if lift >= 5:
        return "Very Strong", "purple", "lavender"

    elif lift >= 3:
        return "Strong", "green", "lightgreen"

    elif lift >= 1.5:
        return "Moderate", "darkorange", "lightyellow"

    else:
        return "Weak", "blue", "lightblue"



## Starting webpage
st.set_page_config(
    page_title='Boréal Marché', 
    layout="wide", 
    page_icon="🛒"
    )

st.title('🛒 Boréal Marché - Recommendation Engine')
st.write("Product Recommendation Engine - Choose an item from the list and get recommendations.")



## loading rules, metadata, and data
products = pd.read_csv('data/products.csv')
popular_items = pd.read_csv('data/popular_items_by_session.csv')

with open('models/rules.json', 'r') as f:
    rules = json.load(f)

with open('models/metadata.json', 'r') as f:
    metadata = json.load(f)

## Displaying association rules and product summary
st.header("Summary")

col1, col2, col3, col4, col5, col6 = st.columns(6)

col1.metric("Products", len(products) )
col2.metric("Total Rules", len(rules))
col3.metric("Winter Rules", metadata['num_winter_rules'])
col4.metric("Spring Rules", metadata['num_spring_rules'])
col5.metric("Summer Rules", metadata['num_summer_rules'])
col6.metric("Fall Rules", metadata['num_fall_rules'])


# Initialize the shopping basket
if "basket" not in st.session_state:
    st.session_state.basket = []


# st.title("🛒 Boréal Marché Seasonal Recommendations")
# st.write("Seasonal Product Recommendation System")

st.title("🛒 Boréal Marché")

st.caption(
    "Discover products based on your shopping basket "
    "and seasonal purchasing patterns."
)

st.divider()

## Chekcing the current season
def get_current_season():
    month = datetime.now().month
    if month in [12, 1, 2]:
        return 'Winter'
    elif month in [3, 4, 5]:
        return 'Spring'
    elif month in [6, 7, 8]:
        return 'Summer'
    else:
        return 'Fall'

# Creating season selector

# Season selection
st.subheader("Shopping Season")

col1, col2 = st.columns([1, 2])

with col1:
    seasons = ["Winter", "Spring", "Summer", "Fall"]

    current_season = get_current_season()

    selected_season = st.selectbox(
        "Select the shopping season:",
        options=seasons,
        index=seasons.index(current_season)
    )

# Filter association rules
seasonal_rules = [
    rule for rule in rules
    if rule["season_name"] == selected_season
]

with col2:
    st.metric(
        label="Available Association Rules",
        value=f"{len(seasonal_rules):,}"
    )



## Buidling product catalog by season

# Product Catalogue and Basket

st.divider()

catalogue_col, recommendations_col, basket_col = st.columns([4, 4, 2])

# PRODUCT CATALOGUE
with catalogue_col:

    st.header("Product Catalogue")

    categories = sorted(products["Category"].dropna().unique())
    categories = ["All categories"] + categories
    
    selected_category = st.selectbox(
            "Filter by category:",
            options=categories
        )
    
    search_text = st.text_input(
        "Search products:",
        placeholder="Enter a product name..."
    )

    
    filtered_products = products.copy()

    if search_text:
        filtered_products = filtered_products[
            filtered_products["Item"].str.contains(
                search_text, case=False, na=False, regex=False
            )
            |
            filtered_products["Item_EN"].str.contains(
                search_text, case=False, na=False, regex=False
            )
        ]

    if selected_category != "All categories":
        filtered_products = filtered_products[
            filtered_products["Category"] == selected_category
        ]

    st.write(f"Products found: {len(filtered_products)}")

    # Scrollable product list
    with st.container(height=600, border=True):

        for _, product in filtered_products.iterrows():

            col1, col2, col3 = st.columns([3, 1, 1])

            with col1:
                st.write(f"**{product['Item']}**")
                st.caption(
                    f"{product['Item_EN']} | {product['Category']}"
                )

            with col2:
                st.write(f"${product['Price']:.2f}")

            with col3:
                if st.button("Add", key=f"add_{product['Item']}"):
                    st.session_state.basket.append(product["Item"])
                    st.rerun()

            st.divider()



# SHOPPING BASKET
with basket_col:

    st.header("Shopping Basket")

    st.write(f"Total items: {len(st.session_state.basket)}")

    if len(st.session_state.basket) == 0:
        st.info("Your basket is empty.")

    else:
        total_price = 0

        # Display each product only once
        for item in dict.fromkeys(st.session_state.basket):

            # Count how many units are in the basket
            quantity = st.session_state.basket.count(item)

            # Find the product price
            product = products[products["Item"] == item].iloc[0]
            price = product["Price"]

            # Calculate the subtotal
            subtotal = price * quantity
            total_price += subtotal

            col1, col2 = st.columns([3, 1])

            with col1:
                st.write(f"**{item}**")
                st.caption(
                    f"{quantity} × ${price:.2f} = ${subtotal:.2f}"
                )

            with col2:
                if st.button("-", key=f"remove_{item}"):
                    st.session_state.basket.remove(item)
                    st.rerun()

        st.divider()

        st.write(f"**Total: ${total_price:.2f}**")

        if st.button("Clear Basket"):
            st.session_state.basket = []
            st.rerun()



## ##############################################
# Starting rules recomendations

basket_itemset = set(st.session_state.basket)

# Ignore the reusable bag for rule matching
basket_itemset.discard("Sac réutilisable")

# Finding matching rules
recommendations = {}
matched_subset_size = 0

for subset_size in range(len(basket_itemset), 0, -1):

    for rule in seasonal_rules:

        antecedents = set(rule["antecedents"].split(","))

        antecedents = {item.strip() for item in antecedents}

        consequent = rule["consequents"].strip()

        # Check if the rule matches the current subset size
        if (
            len(antecedents) == subset_size
            and antecedents.issubset(basket_itemset)
        ):

            # Do not recommend products already purchased
            if consequent not in st.session_state.basket:

                # Keep the rule with the highest lift
                if consequent not in recommendations:
                    recommendations[consequent] = rule

                elif rule["lift"] > recommendations[consequent]["lift"]:
                    recommendations[consequent] = rule

    # Stop when matching recommendations are found
    if recommendations:
        matched_subset_size = subset_size
        break

# Sort recommendations by lift
sorted_recommendations = sorted(
    recommendations.items(),
    key=lambda item: item[1]["lift"],
    reverse=True
)

# Keep the top 5
top_recommendations = sorted_recommendations[:5]



# ------------------------------------
# Seasonal Popularity Fallback
# ------------------------------------

fallback_product = None

# Only use fallback when no association rules match
if len(top_recommendations) == 0:

    # Get popular products for the selected season
    season_name = selected_season

    # The popularity file uses Autumn instead of Fall
    if season_name == "Fall":
        season_name = "Autumn"

    seasonal_popular = popular_items[
        popular_items["season_name"] == season_name
    ]

    # Sort from most popular to least popular
    seasonal_popular = seasonal_popular.sort_values(
        "count", ascending=False
    )

    # Find the first product not already in the basket
    for item in seasonal_popular["item"]:

        if item not in st.session_state.basket:
            fallback_product = item
            break


# ------------------------------------
# Recommendation Validation
# ------------------------------------

validation_errors = []

for product_name, rule in top_recommendations:

    antecedents = {
        item.strip()
        for item in rule["antecedents"].split(",")
    }

    # Check antecedents
    if not (
        len(antecedents) == matched_subset_size
        and antecedents.issubset(basket_itemset)
    ):
        validation_errors.append(
            f"Invalid antecedents for product: {product_name}"
        )

    # Check recommended product
    if product_name in st.session_state.basket:
        validation_errors.append(
            f"Product already in basket: {product_name}"
        )

    # Check season
    if rule["season_name"] != selected_season:
        validation_errors.append(
            f"Incorrect season: {product_name}"
        )


# Displaying recommendations

with recommendations_col:

    st.header("Recommendations")

    number_of_recommendations = len(top_recommendations)

    if fallback_product is not None:
        number_of_recommendations = 1

    st.caption(
        f"Season: {selected_season} | "
        f"Products: {number_of_recommendations}"
    )

    if len(top_recommendations) == 0:

        if fallback_product is not None:

            product = products[
                products["Item"] == fallback_product
            ]

            if not product.empty:

                product = product.iloc[0]

                st.info("Popular product for this season")

                col1, col2 = st.columns([4, 1])

                with col1:
                    st.write(
                        f"**{fallback_product}** "
                        f"({product['Item_EN']})"
                    )

                with col2:
                    if st.button("Add", key="add_fallback"):
                        st.session_state.basket.append(fallback_product)
                        st.rerun()

                st.write(f"Price: **${product['Price']:.2f}**")
                st.caption(
                    "Suggested based on seasonal popularity, "
                    "not association rules."
                )

            else:
                st.info("No seasonal product available.")

        else:
            st.info("No seasonal product available.")

    else:
        with st.container(height=800, border=True):

            for product_name, rule in top_recommendations:

                product = products[
                    products["Item"] == product_name
                ]

                if product.empty:
                    continue

                product = product.iloc[0]

                # Product name on left, Add button on right
                col1, col2, col3 = st.columns([4, 1, 1])

                with col1:
                    st.markdown(
                        f"**{product_name}** ({product['Item_EN']})"
                    )

                with col2:
                    st.write(f"${product['Price']:.2f}")

                with col3:
                    if st.button("Add", key=f"recommend_{product_name}"):
                        st.session_state.basket.append(product_name)
                        st.rerun()

                # Association metrics
                st.caption(
                    f"Lift: {rule['lift']:.2f} | "
                    f"Confidence: {rule['confidence']:.1%} | "
                    f"Support: {rule['support']:.1%}"
                )

                # Explain the recommendation
                st.write(
                f"Recommended because your basket contains "
                f"{rule['antecedents']}. "
                f"In the historical data, "
                f"{rule['confidence']:.1%} of baskets containing "
                f"these products also contained {product_name}. "
                f"This is {rule['lift']:.1f} times the rate "
                f"expected under independence."
                )

                # Association strength
                strength, text_color, bg_color = get_lift_strength(
                    rule["lift"]
                )

                st.markdown(
                    f"""
                    <span style="
                        background-color: {bg_color};
                        color: {text_color};
                        padding: 5px 12px;
                        border-radius: 15px;
                        font-weight: bold;
                        font-size: 13px;
                        display: inline-block;
                    ">
                        {strength} association
                    </span>
                    """,
                    unsafe_allow_html=True
                )

                st.divider()



# ------------------------------------
# Matching Association Rules
# ------------------------------------


st.divider()
st.subheader("Matching Association Rules")

matching_rules = []

# Find all rules matching the selected subset size
for rule in seasonal_rules:

    antecedents = {
        item.strip()
        for item in rule["antecedents"].split(",")
    }

    consequent = rule["consequents"].strip()

    # Match the subset size selected by the recommendation engine
    if (
        matched_subset_size > 0
        and len(antecedents) == matched_subset_size
        and antecedents.issubset(basket_itemset)
    ):

        # Exclude products already in the basket
        if consequent not in st.session_state.basket:
            matching_rules.append(rule)

# Sort all matching rules by lift descending
matching_rules = sorted(
    matching_rules,
    key=lambda rule: rule["lift"],
    reverse=True
)

st.caption(
    f"Season: {selected_season} | "
    f"Matching rules: {len(matching_rules)} | "
    f"Matched products: {matched_subset_size}/{len(basket_itemset)}"
)

# Build the table
if len(matching_rules) == 0:

    st.info("No matching association rules for this basket.")

else:

    rules_table = pd.DataFrame(matching_rules)

    rules_table = rules_table[
        ["antecedents", "consequents",
         "support", "confidence", "lift"]
    ]

    # Display percentages
    rules_table["support"] = rules_table["support"] * 100
    rules_table["confidence"] = rules_table["confidence"] * 100

    # Rename columns
    rules_table.columns = [
        "Antecedents",
        "Consequents",
        "Support (%)",
        "Confidence (%)",
        "Lift"
    ]

    # Display inside a scrollable table
    st.dataframe(
        rules_table,
        height=300,
        hide_index=True,
        use_container_width=True
    )


