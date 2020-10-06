import streamlit as st

st.title("Songify")
st.text("Or whatever name we choose")

# Temporary options
# These will later be replaced by the real list of artist, real list of songs, etc.
tempOptions = ["Example 1", "Example 2", "Example 3"]


# Inputs, named by input, input_type and category
# Some inuts we will use for sure, like artist and genre, so I put them here already

# TODO streamlit multiselect will get slow when more than 100 options present
st.multiselect("Select your artist(s)", tempOptions)
st.multiselect("Select your genres(s)", tempOptions)
st.slider("Select your song duration", value=[2, 20], max_value=90)
st.slider("Select the period of the song", value=[
          1990, 2020], min_value=1920, max_value=2020)


st.sidebar.header("Settings")
st.sidebar.checkbox("Enable developer mode")
