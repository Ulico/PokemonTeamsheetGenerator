import streamlit as st
from PIL import Image
import os
import subprocess

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
            # Update the subprocess call to use the virtual environment's Python executable
            # venv_python = os.path.join(os.getcwd(), 'venv', 'Scripts', 'python')
            subprocess.run(["python", "generate_team_graphic.py"], check=True)

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
        except Exception as e:
            st.error(f"An error occurred: {e}")

# Footer
st.markdown("---")
st.markdown("Created by Ulico")
