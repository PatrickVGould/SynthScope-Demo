"""
These are the modoules for the generation of the search strategy
"""

import re
from langchain import PromptTemplate, LLMChain
from langchain.chat_models import ChatOpenAI
import docx
from docx.shared import Inches
from docx2pdf import convert
import time
import json

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

def searchstrat_developer(original_question, temperature=0.3):
    """
    This is the main module for the generation of the search strategy
    The module takes the original question as input and returns a list 
    of the search strategy components which is then exported to pdf
    """
    summary = []
    summary_dict = {}

    # Ask the LLM for a new research question to-do: create a list of 5 different questions
    # Then ask the user which one they prefer or to keep the original question
    print("Developing new research questions...")
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
        print(f"Option {question_dedupe.index(question)+1}: {question_only}")
    # Ask the user which question they prefer
    time.sleep(1)
    question_choice = int(input(f"Which question do you prefer? (1-{str(len(question_dedupe))})"))
    new_question = question_options[question_choice-1]
    print(f"You chose option {question_choice}: {new_question}")

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
    print("Developing document title...")
    doctitle_question = question_developer(
        new_question+"\nDocument Title:",
        persona_dict["doctitle_developer"]
        )
    summary.append("Document Title: " + str(doctitle_question))
    summary_dict['Document Title'] = str(doctitle_question)

    # Ask the LLM for a logical file title which is used to name the files later
    print("Developing file title...")    
    filetitle_question = question_developer(
        new_question+"\nFile Title:",
        persona_dict["filetitle_developer"]
        )
    summary.append("File Title: " + str(filetitle_question))
    summary_dict['File Title'] = str(filetitle_question)

    # get the best clinical question statement (PICO,PECO,SPIDER) from the llm
    print("Determining which population statement template to use...")
    intorexp_question = question_developer(new_question, persona_dict["intorexp_developer"])
    summary.append(("Best clinical question statement: " + str(intorexp_question)))
    summary_dict["Best clinical question statement"] = str(intorexp_question)

    print("Developing population statement...")
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
    print("Developing inclusion and exclusion criteria...")
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
    print("Developing search strategy...")
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
    print("Determining which databases to search...")
    database_question = question_developer(
        str(new_question+"\nList of databases:"), persona_dict["database_developer"]
        )
    summary.append(("List of suggested databases:\n"+database_question))
    summary_dict["List of suggested databases"] = database_question
    print("List of suggested databases:\n"+database_question)

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
    print(f"Developing search strategy for each database (n={len(database_list)})...")
    for database in database_list:
        print("Developing search strategy for "+database+" ...")
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
    
    print("Writing file...")
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

def docx_generator(summary_dict):
    """
    The word_generator function takes the summary_dict dictionary and generates a Word 
    document with the summary information.
    It uses the templates/wordtemplate.docx for the formatting.
    """
    print("Generating Word summary of search strategy...")
    document_title = summary_dict["Document Title"]
    old_question = summary_dict["Old Question"]
    rationale = summary_dict["Rationale"]
    new_question = summary_dict["New Question"]
    best_clinical_question_statement = summary_dict["Best clinical question statement"]
    population_statement = summary_dict["Population Statement"]
    inclusion_exclusion_criteria = summary_dict["Inclusion and Exclusion Criteria"]
    final_search_strategy = summary_dict["Final Search Strategy"]
    suggested_databases = summary_dict["List of suggested databases"]
    all_database_strategy = summary_dict["All Database Strategy"]

    # Create a new Word document
    doc = docx.Document()

    # Set the document title
    doc.add_heading(str(document_title).strip('"'), 0)

    #add the logo
    doc.add_picture('synthscopelogo.png', width=Inches(4))

    # Add the summary information to the document
    doc.add_heading('Old Question', level=1)
    doc.add_paragraph(old_question)

    doc.add_heading('New Question', level=1)
    doc.add_paragraph(new_question)

    doc.add_heading('Rationale', level=1)
    doc.add_paragraph(rationale)

    doc.add_heading('Best Clinical Question Statement', level=1)
    doc.add_paragraph(best_clinical_question_statement)

    doc.add_heading('Population Statement', level=1)
    doc.add_paragraph(population_statement)

    doc.add_heading('Inclusion and Exclusion Criteria', level=1)
    doc.add_paragraph(inclusion_exclusion_criteria)

    doc.add_heading('Final Search Strategy', level=1)
    doc.add_paragraph(final_search_strategy)

    doc.add_heading('List of suggested databases', level=1)
    doc.add_paragraph(suggested_databases)

    doc.add_heading('All Database Strategy', level=1)
    doc.add_paragraph(all_database_strategy)

    file_name = str(summary_dict["File Title"]).strip('"').strip('.pdf') + ".docx"

    # Save the document
    doc.save('./search_summaries/' + file_name)
    time.sleep(1)
    convert('./search_summaries/' + file_name)
    print("File generated at search_summaries/"+file_name)
