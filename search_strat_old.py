import streamlit as st
import re
import json
import time
import docx
from docx.shared import Inches
from docx2pdf import convert
from langchain import PromptTemplate, LLMChain
from langchain.chat_models import ChatOpenAI
import time

def question_developer(user_input, persona, temperature=0):
    """
    Module to generate a new research question based on the user input and persona
    """
    question = persona + user_input
    template = """Question: {question}

    Answer:"""
    prompt = PromptTemplate(template=template, input_variables=["question"])
    llm_chain = LLMChain(
        prompt=prompt,
        llm=ChatOpenAI(temperature=temperature, max_tokens=2000),
        verbose=False
        )


    return llm_chain.predict(question=question)

def searchstrat_developer(original_question, output_placeholder=None, temperature=0.3):
    """
    This is the main module for the generation of the search strategy
    The module takes the original question as input and returns a list 
    of the search strategy components which is then exported to pdf
    """
    summary = []
    summary_dict = {}

    # Ask the LLM for a new research question to-do: create a list of 5 different questions
    # Then ask the user which one they prefer or to keep the original question
    output_placeholder.write("Developing new research questions...")
    with open('perssonadict.json', 'r') as f:
        persona_dict = json.load(f)
    question_options = []
    new_question_regex = r"New Question:\s+(.*)\n"
    rationale_regex = r"Rationale:\s+(.*)"
    for i in range(10):
        new_question_output = question_developer(
            original_question,
            persona_dict["question_developer"],
            temperature
            )
        try:
            question_only = re.search(new_question_regex, str(new_question_output)).group(1)
            question_only = question_only.strip("\n")
            question_options.append(new_question_output)
            #print(f"Option {i+1}: {question_only}")
        except:
            pass

    # Deduplicate the list of questions as the LLM sometimes repeats questions especially with a low temperature
    question_dedupe = []
    for question in question_options:
        if question not in question_dedupe:
            question_dedupe.append(question) 
    for question in question_dedupe:
        question_only = re.search(new_question_regex, str(question)).group(1)
        output_placeholder.write(f"Option {question_dedupe.index(question)+1}: {question_only}")
    # Ask the user which question they prefer
    time.sleep(1)
    question_choice = int(input(f"Which question do you prefer? (1-{str(len(question_dedupe))})"))
    new_question = question_options[question_choice-1]
    output_placeholder.write(f"You chose option {question_choice}: {new_question}")

    new_question = re.search(new_question_regex, str(new_question_output)).group(1)
    rationale = re.search(rationale_regex, str(new_question_output)).group(1)

    summary.append(str((f"""Old Question: {original_question}
    New Question: {new_question}
    Rationale: {rationale}
    """)))
    summary_dict["Old Question"] = original_question
    summary_dict["New Question"] = new_question
    summary_dict["Rationale"] = rationale

    # Ask the LLM for a logical document title which is used as the pdf header later
    output_placeholder.write("Developing document title...")
    doctitle_question = question_developer(
        new_question+"\nDocument Title:",
        persona_dict["doctitle_developer"]
        )
    summary.append("Document Title: " + str(doctitle_question))
    summary_dict['Document Title'] = str(doctitle_question)

    # Ask the LLM for a logical file title which is used to name the files later
    output_placeholder.write("Developing file title...")    
    filetitle_question = question_developer(
        new_question+"\nFile Title:",
        persona_dict["filetitle_developer"]
        )
    summary.append("File Title: " + str(filetitle_question))
    summary_dict['File Title'] = str(filetitle_question)

    # get the best clinical question statement (PICO,PECO,SPIDER) from the llm
    output_placeholder.write("Determining which population statement template to use...")
    intorexp_question = question_developer(new_question, persona_dict["intorexp_developer"])
    summary.append(("Best clinical question statement: " + str(intorexp_question)))
    summary_dict["Best clinical question statement"] = str(intorexp_question)

    output_placeholder.write("Developing population statement...")
    #If interorexp contains intervention, then PICO is PICO
    # If the llm wants to use PICO or PECO, then create a PICO/PECO question
    if "pico" in intorexp_question.lower():
        pico_question = question_developer(new_question, persona_dict["PICO_developer"])
        summary.append("PICO: " + (pico_question))
        pop_statement = pico_question
    # If the llm wants to use SPIDER, then create a SPIDER question
    elif "peco" in intorexp_question.lower():
        pico_question = question_developer(new_question, persona_dict["PECO_developer"])
        summary.append("PECO Statement: "+(pico_question))
        pop_statement = pico_question
    # If the llm wants to use SPIDER, then create a SPIDER question
    elif "spider" in intorexp_question.lower():
        spider_question = question_developer(new_question, persona_dict["SPIDER_developer"])
        summary.append("SPIDER Statement: "+(spider_question))
        pop_statement = spider_question
    # Add Population Statement to summary dictionary
    summary_dict["Population Statement"] = pop_statement

    # Ask the LLM for inclusion and exclusion criteria
    output_placeholder.write("Developing inclusion and exclusion criteria...")
    incexc_question = question_developer(
        str(
            pop_statement+
            "\nMy Research Question: "+
            new_question
            ),
        persona_dict["incexc_developer"]
        )
    summary.append((incexc_question))
    summary_dict["Inclusion and Exclusion Criteria"] = incexc_question

    # Ask the LLM for a search strategy
    output_placeholder.write("Developing search strategy...")
    searchstrat_question = question_developer(
        str(
            "My Research Question: "+
            new_question+"\nPopulation Statement: "+
            pop_statement+
            "\n"+
            incexc_question+
            "\n\n"+
            "Final Search Strategy:"
        ),
        persona_dict["searchstrat_developer"]
        )
    summary.append(("Final Search Strategy:\n"+searchstrat_question))
    summary_dict["Final Search Strategy"] = searchstrat_question

    # Ask the LLM for a list of databases to search
    output_placeholder.write("Determining which databases to search...")
    database_question = question_developer(
        str(new_question+"\nList of databases:"), persona_dict["database_developer"]
        )
    summary.append(("List of suggested databases:\n"+database_question))
    summary_dict["List of suggested databases"] = database_question
    output_placeholder.write("List of suggested databases:\n"+database_question)

    #convert whatever list the LLM returns into a list by asking the LLM to return a list
    database_list = question_developer(
        str(database_question+"\nList:('"), persona_dict["list_returner"]
        )
    if "and" in database_list:
        database_list = database_list.remove("and")
    database_list = eval(database_list)
    #print("Database list type = "+str(type(database_list)))
    #print("Database list = "+str(database_list))

    # Develop a search strategy for each database by asking the LLM for each database
    all_database_strats = ""
    output_placeholder.write(f"Developing search strategy for each database (n={len(database_list)})...")
    for database in database_list:
        output_placeholder.write("Developing search strategy for "+database+" ...")
        database_strat = question_developer(
            str("My Search Strategy: "+
                searchstrat_question+
                "\nDatabase that will be searched: "+
                database+"\nSearch strategy specific to "+
                database+
                ":"
                ),
            persona_dict["databasesearchstrat_developer"]
            )
        summary.append(str("Search strategy specific to "+database+":\n"+database_strat))
        summary_dict["Search strategy specific to "+database] = database_strat
        print("Search strategy specific to "+database+":\n"+database_strat)
        all_database_strats += "\nStrategy for " + database + ":\n" + database_strat+"\n"

    summary_dict["All Database Strategy"] =(
        "Search Strategy for all databases:\n"+
        all_database_strats
    )
    
    output_placeholder.write("Writing file...")
    with open('summary_file.txt','w',encoding='utf-8') as handle:
        for item in summary:
            handle.write(item+"\n")
    
    pubmed_question = question_developer(
        str(searchstrat_question)+"\n Pubmed Query: (", persona_dict["pubmedquery_developer"]
        )
    summary.append("Pubmed Query: "+str(pubmed_question))
    summary_dict["Pubmed Query"] = str(pubmed_question)

    docx_generator(summary_dict)
    return summary_dict



def search_strategy_generation():
    st.header("Search Strategy Generation")
    st.write("SynthScope will assist the user in generating a search strategy via the gpt-3.5-turbo OpenAI model and langchain.")
    st.markdown("## Generate Search Strategy")
    user_input = st.text_input("Enter your research question:")
    search_query = st.text_input("Enter your search query:")
    if st.button("Generate Search Strategy"):
        if user_input:
            output_placeholder = st.empty()
            summary = []
            summary_dict = {}

            # Ask the LLM for a new research question to-do: create a list of 5 different questions
            # Then ask the user which one they prefer or to keep the original question
            output_placeholder.write("Developing new research questions...")
            with open('perssonadict.json', 'r') as f:
                persona_dict = json.load(f)
            question_options = []
            new_question_regex = r"New Question:\s+(.*)\n"
            rationale_regex = r"Rationale:\s+(.*)"
            for i in range(10):
                new_question_output = question_developer(
                    user_input,
                    persona_dict["question_developer"],
                    temperature = 0.3
                    )
                try:
                    question_only = re.search(new_question_regex, str(new_question_output)).group(1)
                    question_only = question_only.strip("\n")
                    question_options.append(new_question_output)
                    #print(f"Option {i+1}: {question_only}")
                except:
                    pass

            # Deduplicate the list of questions as the LLM sometimes repeats questions especially with a low temperature
            question_dedupe = []
            for question in question_options:
                if question not in question_dedupe:
                    question_dedupe.append(question) 
            for question in question_dedupe:
                question_only = re.search(new_question_regex, str(question)).group(1)
                output_placeholder.write(f"Option {question_dedupe.index(question)+1}: {question_only}")
            # Ask the user which question they prefer
            time.sleep(1)
            question_choice = int(input(f"Which question do you prefer? (1-{str(len(question_dedupe))})"))
            new_question = question_options[question_choice-1]
            output_placeholder.write(f"You chose option {question_choice}: {new_question}")

            new_question = re.search(new_question_regex, str(new_question_output)).group(1)
            rationale = re.search(rationale_regex, str(new_question_output)).group(1)

            summary.append(str((f"""Old Question: {user_input}
            New Question: {new_question}
            Rationale: {rationale}
            """)))
            summary_dict["Old Question"] = user_input
            summary_dict["New Question"] = new_question
            summary_dict["Rationale"] = rationale

            # Ask the LLM for a logical document title which is used as the pdf header later
            output_placeholder.write("Developing document title...")
            doctitle_question = question_developer(
                new_question+"\nDocument Title:",
                persona_dict["doctitle_developer"]
                )
            summary.append("Document Title: " + str(doctitle_question))
            summary_dict['Document Title'] = str(doctitle_question)

            # Ask the LLM for a logical file title which is used to name the files later
            output_placeholder.write("Developing file title...")    
            filetitle_question = question_developer(
                new_question+"\nFile Title:",
                persona_dict["filetitle_developer"]
                )
            summary.append("File Title: " + str(filetitle_question))
            summary_dict['File Title'] = str(filetitle_question)

            # get the best clinical question statement (PICO,PECO,SPIDER) from the llm
            output_placeholder.write("Determining which population statement template to use...")
            intorexp_question = question_developer(new_question, persona_dict["intorexp_developer"])
            summary.append(("Best clinical question statement: " + str(intorexp_question)))
            summary_dict["Best clinical question statement"] = str(intorexp_question)

            output_placeholder.write("Developing population statement...")
            #If interorexp contains intervention, then PICO is PICO
            # If the llm wants to use PICO or PECO, then create a PICO/PECO question
            if "pico" in intorexp_question.lower():
                pico_question = question_developer(new_question, persona_dict["PICO_developer"])
                summary.append("PICO: " + (pico_question))
                pop_statement = pico_question
            # If the llm wants to use SPIDER, then create a SPIDER question
            elif "peco" in intorexp_question.lower():
                pico_question = question_developer(new_question, persona_dict["PECO_developer"])
                summary.append("PECO Statement: "+(pico_question))
                pop_statement = pico_question
            # If the llm wants to use SPIDER, then create a SPIDER question
            elif "spider" in intorexp_question.lower():
                spider_question = question_developer(new_question, persona_dict["SPIDER_developer"])
                summary.append("SPIDER Statement: "+(spider_question))
                pop_statement = spider_question
            # Add Population Statement to summary dictionary
            summary_dict["Population Statement"] = pop_statement

            # Ask the LLM for inclusion and exclusion criteria
            output_placeholder.write("Developing inclusion and exclusion criteria...")
            incexc_question = question_developer(
                str(
                    pop_statement+
                    "\nMy Research Question: "+
                    new_question
                    ),
                persona_dict["incexc_developer"]
                )
            summary.append((incexc_question))
            summary_dict["Inclusion and Exclusion Criteria"] = incexc_question

            # Ask the LLM for a search strategy
            output_placeholder.write("Developing search strategy...")
            searchstrat_question = question_developer(
                str(
                    "My Research Question: "+
                    new_question+"\nPopulation Statement: "+
                    pop_statement+
                    "\n"+
                    incexc_question+
                    "\n\n"+
                    "Final Search Strategy:"
                ),
                persona_dict["searchstrat_developer"]
                )
            summary.append(("Final Search Strategy:\n"+searchstrat_question))
            summary_dict["Final Search Strategy"] = searchstrat_question

            # Ask the LLM for a list of databases to search
            output_placeholder.write("Determining which databases to search...")
            database_question = question_developer(
                str(new_question+"\nList of databases:"), persona_dict["database_developer"]
                )
            summary.append(("List of suggested databases:\n"+database_question))
            summary_dict["List of suggested databases"] = database_question
            output_placeholder.write("List of suggested databases:\n"+database_question)

            #convert whatever list the LLM returns into a list by asking the LLM to return a list
            database_list = question_developer(
                str(database_question+"\nList:('"), persona_dict["list_returner"]
                )
            if "and" in database_list:
                database_list = database_list.remove("and")
            database_list = eval(database_list)
            #print("Database list type = "+str(type(database_list)))
            #print("Database list = "+str(database_list))

            # Develop a search strategy for each database by asking the LLM for each database
            all_database_strats = ""
            output_placeholder.write(f"Developing search strategy for each database (n={len(database_list)})...")
            for database in database_list:
                output_placeholder.write("Developing search strategy for "+database+" ...")
                database_strat = question_developer(
                    str("My Search Strategy: "+
                        searchstrat_question+
                        "\nDatabase that will be searched: "+
                        database+"\nSearch strategy specific to "+
                        database+
                        ":"
                        ),
                    persona_dict["databasesearchstrat_developer"]
                    )
                summary.append(str("Search strategy specific to "+database+":\n"+database_strat))
                summary_dict["Search strategy specific to "+database] = database_strat
                print("Search strategy specific to "+database+":\n"+database_strat)
                all_database_strats += "\nStrategy for " + database + ":\n" + database_strat+"\n"

            summary_dict["All Database Strategy"] =(
                "Search Strategy for all databases:\n"+
                all_database_strats
            )
            
            output_placeholder.write("Writing file...")
            with open('summary_file.txt','w',encoding='utf-8') as handle:
                for item in summary:
                    handle.write(item+"\n")
            
            pubmed_question = question_developer(
                str(searchstrat_question)+"\n Pubmed Query: (", persona_dict["pubmedquery_developer"]
                )
            summary.append("Pubmed Query: "+str(pubmed_question))
            summary_dict["Pubmed Query"] = str(pubmed_question)

            return summary_dict

        else:
            st.error("Please enter a research question.")
        pass
