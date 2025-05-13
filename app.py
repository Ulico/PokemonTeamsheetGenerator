import streamlit as st
from PIL import Image
from pathlib import Path

# Import the necessary functions from generate_team_graphic.py
from generate_team_graphic import parse_team_file, create_teamsheet

# Define base directory using pathlib
BASE_DIR = Path(__file__).parent
team_file_path = BASE_DIR / "team_paste.txt"
output_image_path = BASE_DIR / "teamsheet.png"

# Set the title of the app
st.title("Pokémon Teamsheet Graphic Generator")

# Update the template example for team_data using README.md example
team_data = st.text_area(
    "Paste your team data below:", 
    height=300,
    value="""Pikachu (F) @ Light Ball
Ability: Static
Level: 50
Tera Type: Electric
- Thunderbolt
- Quick Attack
- Iron Tail
- Protect

etc..."""
)

if team_data:
    # Save the pasted data
    team_file_path.write_text(team_data, encoding='utf-8')
    st.success("Team data saved successfully!")

    if st.button("Generate Teamsheet Graphic"):
        try:
            # Parse and create the teamsheet
            team = parse_team_file(team_file_path)
            if team:
                create_teamsheet(team, output_image_path)

                if output_image_path.exists():
                    st.image(Image.open(output_image_path), caption="Generated Teamsheet", use_container_width=True)

                    with output_image_path.open("rb") as file:
                        st.download_button(
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
