import streamlit as st
import streamlit.components.v1 as components

st.title("Songify")
st.text("Or whatever name we choose")

st.header("Choose your song preferences")

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


# Sidebar
st.sidebar.header("Settings")
st.sidebar.checkbox("Enable developer mode")


st.header("Your recommendation")
st.text("Temporary, to be replaced")

# Temporary output
components.html(
    """<iframe src="https://open.spotify.com/embed/album/1zjw3IyO5IEaC8iu2GNwwA" width="600" height="380" frameborder="0" allowtransparency="true" allow="encrypted-media"></iframe>""",
    height=800, scrolling=True)
