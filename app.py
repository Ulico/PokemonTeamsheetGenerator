import streamlit as st
from PIL import Image
import os

# Import the necessary functions from generate_team_graphic.py
from generate_team_graphic import parse_team_file, create_teamsheet

# Set the title of the app
st.title("Pokémon Teamsheet Graphic Generator")

# Replace the file uploader with a text area for pasting the team data
team_data = st.text_area("Paste your team data below:", height=300)

# Button to generate the teamsheet graphic
if team_data:
    # Save the pasted data temporarily
    with open("team_paste.txt", "w") as f:
        f.write(team_data)

    st.success("Team data saved successfully!")

    if st.button("Generate Teamsheet Graphic"):
        try:
            # Parse the team data
            team = parse_team_file("team_paste.txt")

            if team:
                # Generate the teamsheet
                create_teamsheet(team, "teamsheet.png")

                # Display the generated teamsheet graphic
                if os.path.exists("teamsheet.png"):
                    st.image(Image.open("teamsheet.png"), caption="Generated Teamsheet", use_container_width=True)

                    # Provide a download link for the teamsheet
                    with open("teamsheet.png", "rb") as file:
                        btn = st.download_button(
                            label="Download Teamsheet",
                            data=file,
                            file_name="teamsheet.png",
                            mime="image/png"
                        )
                else:
                    st.error("Failed to generate teamsheet graphic. Please check the script.")
            else:
                st.error("Failed to parse team data. Please check the input format.")
        except Exception as e:
            st.error(f"An error occurred: {e}")

# Footer
st.markdown("---")
st.markdown("Created by Ulico")
