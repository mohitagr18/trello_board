import os
import base64
import yaml
import streamlit as st
from dotenv import load_dotenv
from crewai import Agent, Task, Crew
from config.trello_tools import BoardDataFetcherTool, CardDataFetcherTool

def load_sample_board_image():
    """
    Load and encode sample board image.
    
    Returns:
        str: Base64 encoded image or None if not found
    """
    try:
        # Adjust path as needed
        with open("assets/sample_trello_board.png", "rb") as img_file:
            return base64.b64encode(img_file.read()).decode('utf-8')
    except FileNotFoundError:
        st.warning("Sample board image not found. Please add an image to the assets folder.")
        return None

def load_css_file(css_file_path):
    """
    Load CSS from external file.
    """
    try:
        with open(css_file_path, "r") as css_file:
            return css_file.read()
    except FileNotFoundError:
        st.warning(f"CSS file not found at {css_file_path}")
        return None
    
def load_env_variables():
    """
    Load environment variables from .env file.
    """
    load_dotenv()
    
    # Set OpenAI-specific vars
    os.environ['OPENAI_API_KEY'] = os.getenv('OPENAI_API_KEY2')
    os.environ['OPENAI_MODEL_NAME'] = os.getenv('OPENAI_MODEL_NAME')

def load_yaml_configs():
    """
    Load YAML configuration files.
    
    Returns:
        Dict containing agent and task configurations
    """
    files = {
        'agents': 'config/agents.yaml',
        'tasks': 'config/tasks.yaml',
    }

    configs = {}
    for config_type, file_path in files.items():
        try:
            with open(file_path, 'r') as file:
                configs[config_type] = yaml.safe_load(file)
        except yaml.YAMLError as e:
            st.error(f"Error parsing YAML file {file_path}: {e}")
            return None
    return configs

def create_agents(agents_config):
    """
    Create CrewAI agents based on configuration.
    
    Args:
        agents_config (dict): Agent configurations from YAML
    
    Returns:
        tuple: Data collection and analysis agents
    """
    data_collection_agent = Agent(
        config=agents_config['data_collection_agent'],
        tools=[BoardDataFetcherTool(), CardDataFetcherTool()]
    )

    analysis_agent = Agent(
        config=agents_config['analysis_agent']
    )

    return data_collection_agent, analysis_agent

def create_tasks(tasks_config, data_collection_agent, analysis_agent):
    """
    Create CrewAI tasks based on configuration.
    
    Args:
        tasks_config (dict): Task configurations from YAML
        data_collection_agent (Agent): Data collection agent
        analysis_agent (Agent): Analysis agent
    
    Returns:
        tuple: Data collection, analysis, and report generation tasks
    """
    data_collection = Task(
        config=tasks_config['data_collection'],
        agent=data_collection_agent
    )

    data_analysis = Task(
        config=tasks_config['data_analysis'],
        agent=analysis_agent
    )

    report_generation = Task(
        config=tasks_config['report_generation'],
        agent=analysis_agent
    )

    return data_collection, data_analysis, report_generation

def generate_trello_report(api_key, api_token, board_id):
    """
    Generate Trello board report using CrewAI.
    
    Args:
        api_key (str): Trello API key
        api_token (str): Trello API token
        board_id (str): Trello board ID
    
    Returns:
        str: Generated report
    """
    # Set Trello credentials
    os.environ['TRELLO_API_KEY'] = api_key
    os.environ['TRELLO_API_TOKEN'] = api_token
    os.environ['TRELLO_BOARD_ID'] = board_id

    # Load configurations
    configs = load_yaml_configs()
    if not configs:
        st.error("Failed to load configurations")
        return None

    # Create agents and tasks
    data_collection_agent, analysis_agent = create_agents(configs['agents'])
    data_collection, data_analysis, report_generation = create_tasks(
        configs['tasks'], 
        data_collection_agent, 
        analysis_agent
    )

    # Create and execute crew
    crew = Crew(
        agents=[data_collection_agent, analysis_agent],
        tasks=[data_collection, data_analysis, report_generation],
        verbose=True
    )

    try:
        result = crew.kickoff()
        return result.raw
    except Exception as e:
        st.error(f"Error generating report: {e}")
        return None

def main():
    """
    Main Streamlit application
    """
    st.set_page_config(
        page_title="Trello Board Insights", 
        page_icon="📊", 
        layout="wide"
    )

    # Initialize environment variables and configurations
    load_env_variables()

    # Load custom CSS
    css_content = load_css_file("assets/style.css")
    if css_content:
        st.markdown(f"<style>{css_content}</style>", unsafe_allow_html=True)

    st.title("🔍 Trello Board Insights Generator")

    # Credential inputs and board selection
    with st.sidebar:
        st.header("🔐 Trello Insights Options")
        
        # Board type selection
        st.sidebar.markdown("### Choose Board Type")
        board_type = st.radio("Select Board",
            ["Sample Board", "My Trello Board"]
        )

        # Credentials input based on board type
        if board_type == "Sample Board":
            # Use predefined sample board credentials from .env
            api_key = os.getenv('TRELLO_API_KEY')
            api_token = os.getenv('TRELLO_API_TOKEN')
            board_id = os.getenv('TRELLO_BOARD_ID')
            
            # st.info("Using sample board credentials from .env file")

        else:
            # Custom board credentials input
            api_key = st.text_input("Trello API Key", type="password")
            api_token = st.text_input("Trello API Token", type="password")
            board_id = st.text_input("Trello Board ID")

            # About section
        st.sidebar.markdown("### About Trello Insights")
        st.sidebar.info("""
        This tool uses AI to:
        - Collect Trello board data
        - Analyze task and project information
        - Generate actionable insights
        """)

        st.info("""
        ### How to Get Trello Credentials
        1. Login to Trello
        2. Go to https://trello.com/app-key
        3. Generate API Key
        4. Create Token with read access
        5. Find Board ID in board URL
        """)

    # Content area
    st.subheader("Trello Board Preview")
    
    # Load and display sample board image only for Sample Board
    if board_type == "Sample Board":
        sample_board_image = load_sample_board_image()
        if sample_board_image:
            st.image(f"data:image/png;base64,{sample_board_image}", use_container_width=True)
        else:
            st.warning("Unable to load sample board image")

    # Generate insights section
    st.text("")
    st.subheader("Generate Insights")
    
    # Generate report button with note about generation time
    st.info("⏳ Note: Report generation may take approximately 1 minute.")

    # # Custom CSS for a larger, more prominent button
    # st.markdown("""
    # <style>
    # div.stButton > button {
    #     font-size: 20px;
    #     font-weight: bold;
    #     height: 3em;
    #     width: 30%;
    #     background-color: #FF5722;
    #     color: white;
    #     border-radius: 10px;
    #     border: none;
    #     margin-top: 10px;
    #     margin-bottom: 20px;
    # }
    # div.stButton > button:hover {
    #     background-color: #E64A19;
    #     color: white;
    # }
    # </style>
    # """, unsafe_allow_html=True)
    
    generate_button = st.button("🚀 Generate Sprint Report")
    # generate_button = st.button("Generate Sprint Report")

    if generate_button:
        # Validate credentials based on board type
        if board_type == "Sample Board":
            if not (api_key and api_token and board_id):
                st.warning("Sample board credentials not found in .env file")
            else:
                with st.spinner("Generating insights from sample board..."):
                    report = generate_trello_report(api_key, api_token, board_id)
                    
                    if report:
                        st.success("Sample Board Report Generated!")
                        st.markdown(report)
        
        else:  # Custom Board
            if not (api_key and api_token and board_id):
                st.warning("Please enter all Trello credentials")
            else:
                with st.spinner("Generating insights from your board..."):
                    report = generate_trello_report(api_key, api_token, board_id)
                    
                    if report:
                        st.success("Your Board Report Generated!")
                        st.markdown(report)


if __name__ == "__main__":
    main()