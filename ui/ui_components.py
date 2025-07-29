import streamlit as st
import streamlit.components.v1 as components

def display_section(header: str, data: dict, level: int = 1):
    """
    Display a section with labeled fields and copy buttons.
    Handles nested dicts, and auto-switches between text_input and text_area based on value length.
    """
    header_prefix = "#" * (level + 2)  # ###, #### etc.
    st.markdown(f"{header_prefix} 🧩 {header}")

    for key, value in data.items():
        # Handle nested dicts recursively
        if isinstance(value, dict):
            display_section(f"{header} → {key}", value, level=level + 1)
            continue

        # Generate unique key for Streamlit widgets
        field_key = f"{header}_{key}"

        # Columns: field and copy button
        col1, col2 = st.columns([4, 1])
        with col1:
            str_value = str(value)

            # Choose widget based on text length
            if len(str_value) > 50 or "\n" in str_value:
                st.text_area(label=key, value=str_value, key=field_key, disabled=True, height=100)
            else:
                st.text_input(label=key, value=str_value, key=field_key, disabled=True)

        with col2:
            # Safe escaping for JS clipboard
            escaped_value = str_value.replace("'", "\\'").replace("\n", "\\n")
            copy_code = f"""
                <div style="display: flex; justify-content: center;">
                    <button onclick="navigator.clipboard.writeText('{escaped_value}').then(() => alert('Copied to clipboard!'))"
                        style="
                            background-color: #4CAF50;
                            color: white;
                            padding: 6px 12px;
                            border: none;
                            border-radius: 5px;
                            cursor: pointer;
                            font-size: 14px;
                        ">📋 Copy</button>
                </div>
                """
            components.html(copy_code, height=40)

def display_status(status_dict: dict):
    """Display real-time status of each agent"""
    st.markdown("### 🚦 Agent Processing Status")
    for agent, status in status_dict.items():
        status_color = "green" if status == "✅ Done" else ("orange" if status == "⏳ In Progress" else "red")
        st.markdown(f"- **{agent}**: <span style='color:{status_color}'>{status}</span>", unsafe_allow_html=True)

def display_error_logs(errors: list):
    """Display collected errors"""
    if errors:
        st.markdown("### ❌ Errors")
        for error in errors:
            st.error(error)


def display_recruiter_details_streamlit(heading,recruiter_data):
    """
    Displays a list of recruiter details in a Streamlit UI.

    Each recruiter will have their name, a button to open their LinkedIn profile,
    and their email address (if available).

    Args:
        recruiter_data (list of dict): A list of recruiter objects.
            Each object should have:
            - 'name' (str)
            - 'linkedin_profile_url' (str)
            - 'email_address' (str, or 'Not publicly available')
    """
    st.header(heading)
    

    if not recruiter_data:
        st.info("No recruiter details to display.")
        return

    # Use Streamlit's columns or just iterate to create cards/sections
    # For a simple list, direct iteration with st.expander or st.container works well.
    # Let's use st.container for a card-like look for each recruiter.

    for i, recruiter in enumerate(recruiter_data):
        with st.container(border=True): # Adds a visual border around each recruiter's info
            recruiter_ID = ''.join(filter(lambda x: not x.isdigit(), recruiter.split("/")[-1]))
            st.subheader(recruiter_ID)
            linkedin_url = recruiter
            if linkedin_url:
                # Streamlit's button can directly open URLs
                st.link_button(
                    label="View LinkedIn Profile",
                    url=linkedin_url,
                    help=f"Go to {recruiter_ID}'s LinkedIn profile",
                    type="primary" # Optional: makes the button blue
                )
            else:
                st.write("LinkedIn Profile: Not available")

            
            
            # Optional: Add a separator for better visual distinction if not using st.container border
            # if i < len(recruiter_data) - 1:
            #     st.divider()
