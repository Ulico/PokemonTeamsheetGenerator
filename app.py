import streamlit as st
from PIL import Image
import os

# Import the necessary functions from generate_team_graphic.py
from generate_team_graphic import parse_team_file, create_teamsheet

# Get base directory of the current script
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Set the title of the app
st.title("Pokémon Teamsheet Graphic Generator")

# Replace the file uploader with a text area for pasting the team data
team_data = st.text_area("Paste your team data below:", height=300)

# Button to generate the teamsheet graphic
if team_data:
    # Define the absolute path for the input and output files
    team_file_path = os.path.join(BASE_DIR, "team_paste.txt")
    output_image_path = os.path.join(BASE_DIR, "teamsheet.png")

    # Save the pasted data temporarily
    with open(team_file_path, "w") as f:
        f.write(team_data)

    st.success("Team data saved successfully!")

    if st.button("Generate Teamsheet Graphic"):
        try:
            # Parse the team data
            team = parse_team_file(team_file_path)

            if team:
                # Generate the teamsheet
                create_teamsheet(team, output_image_path)

                # Display the generated teamsheet graphic
                if os.path.exists(output_image_path):
                    st.image(Image.open(output_image_path), caption="Generated Teamsheet", use_container_width=True)

                    # Provide a download link for the teamsheet
                    with open(output_image_path, "rb") as file:
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
