import streamlit as st
import base64
import pandas as pd
from search_strat import searchstrat_developer

openai_api_key = st.secrets["OPENAI_API_KEY"]
pinecone_api_key = st.secrets["PINECONE_API_KEY"]
index_name = st.secrets["PINECONE_INDEX_NAME"]

# Main app function
def main():
    st.title("SynthScope: Automatic Systematic Review Tool")
    st.write(
        """
        SynthScope is an automatic systematic review tool that uses advanced AI LLMs to quickly and accurately summarize and synthesize large volumes of scientific literature that is imported by the user.
        With SynthScope, you can save time and reduce errors by automating the title/abstract, and full text screening stages of the literature review, enabling you to focus on the analysis and insights that matter most to your research.
        """
    )

    st.sidebar.title("SynthScope Features")
    feature = st.sidebar.selectbox(
        "Choose a feature",
        (
            "Select...",
            "Search Strategy Generation",
            "Database Search",
            "Title and Abstract Screening",
            "Full Text PDF Retrieval",
            "Full Text Screening",
            "Risk of Bias Screening",
            "Summary Generation",
            "Report Generation",
        ),
    )

    if feature == "Search Strategy Generation":
        search_strategy_generation()
    elif feature == "Database Search":
        database_search()
    elif feature == "Title and Abstract Screening":
        title_abstract_screening()
    elif feature == "Full Text PDF Retrieval":
        full_text_pdf_retrieval()
    elif feature == "Full Text Screening":
        full_text_screening()
    elif feature == "Risk of Bias Screening":
        risk_of_bias_screening()
    elif feature == "Summary Generation":
        summary_generation()
    elif feature == "Report Generation":
        report_generation()

def download_link(object_to_download, download_filename, download_link_text):
    """
    Generates a link to download the given object_to_download.
    """
    if isinstance(object_to_download, pd.DataFrame):
        object_to_download = object_to_download.to_csv(index=False)

    # Some strings <-> bytes conversions necessary here
    b64 = base64.b64encode(object_to_download.encode()).decode()

    return f'<a href="data:file/txt;base64,{b64}" download="{download_filename}">{download_link_text}</a>'

def search_strategy_generation():
    st.markdown("## Generate Search Strategy")
    user_input = st.text_input("Enter your research question:")
    if st.button("Generate"):
        if user_input:
            summary_dict = searchstrat_developer(user_input)

            docx_filename = str(summary_dict["File Title"]).strip('"').strip('.pdf') + ".docx"
            pdf_filename = str(summary_dict["File Title"]).strip('"') + ".pdf"

            # Display download links
            with open('summary_file.txt', 'r', encoding='utf-8') as file:
                summary_text = file.read()
            st.markdown(download_link(summary_text, "summary.txt", "Download Summary as TXT"), unsafe_allow_html=True)
            st.markdown(download_link(summary_dict, docx_filename, "Download Summary as DOCX"), unsafe_allow_html=True)
            st.markdown(download_link(summary_dict, pdf_filename, "Download Summary as PDF"), unsafe_allow_html=True)

        else:
            st.error("Please enter a research question.")


def database_search():
    st.header("Database Search")
    st.write("SynthScope will run the search strategy on a range of academic databases.")
    databases = st.multiselect("Select databases to search", ["Database 1", "Database 2", "Database 3"])
    if st.button("Run Database Search"):
        # Call your backend function here to run the database search
        pass


def title_abstract_screening():
    st.header("Title and Abstract Screening")
    st.write("SynthScope will screen the titles and abstracts of the results for if they meet the search strategy criteria and creates a file of articles that met criteria.")
    if st.button("Start Title and Abstract Screening"):
        # Call your backend function here to perform title and abstract screening
        pass
        uploaded_file = st.file_uploader("Choose a file to upload", type=['txt', 'csv', 'json'])

    if uploaded_file is not None:
        file_details = {
            "filename": uploaded_file.name,
            "filetype": uploaded_file.type,
            "file_size": uploaded_file.size
        }
        st.write(file_details)

        # Read the file content
        file_content = uploaded_file.getvalue().decode("utf-8")
        st.write(file_content)


def full_text_pdf_retrieval():
    st.header("Full Text PDF Retrieval")
    st.write("SynthScope will pull the full text pdf files for the papers that passed the first screening. You can pull the articles from the database search or upload a ris file")
    if st.button("Retrieve Full Text PDFs"):
        # Call your backend function here to retrieve full text PDFs
        pass


def full_text_screening():
    st.header("Full Text Screening")
    st.write("SynthScope will complete a screening of the full text of the papers and determines which ones meet the criteria.")
    if st.button("Start Full Text Screening"):
        # Call your backend function here to perform full text screening
        pass


def risk_of_bias_screening():
    st.header("Risk of Bias Screening")
    st.write("SynthScope will screen the included papers against the cochrane risk of bias tool and create a risk of bias table, risk of bias graph, and risk of biassummary.")
    if st.button("Start Risk of Bias Screening"):
    # Call your backend function here to perform risk of bias screening
        pass

def summary_generation():
    st.header("Summary Generation")
    st.write("SynthScope will summarize the full text papers that met criteria and return this summary of the articles that met criteria to the user.")
    if st.button("Generate Summary"):
    # Call your backend function here to generate the summary
        pass

def report_generation():
    st.header("Report Generation")
    st.write("SynthScope will create a full literature review report on the above process including introduction, methods, results, discussion, and conclusion.")
    report_format = st.selectbox("Choose report format", ["PDF", "Word", "HTML"])
    if st.button("Generate Report"):
    # Call your backend function here to generate the report
        pass

if __name__ == "__main__":
    main()
