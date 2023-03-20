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

def develop_new_questions(user_input, persona_dict):
    question_options = []
    new_question_regex = r"New Question:\s+(.*)\n"
    rationale_regex = r"Rationale:\s+(.*)"
    for i in range(10):
        new_question_output = question_developer(user_input, persona_dict["question_developer"], temperature=0.3)
        try:
            question_only = re.search(new_question_regex, str(new_question_output)).group(1)
            question_only = question_only.strip("\n")
            question_options.append(new_question_output)
        except:
            pass

    question_dedupe = []
    for question in question_options:
        if question not in question_dedupe:
            question_dedupe.append(question)
    return question_dedupe

def get_new_question_rationale(new_question_output):
    new_question_regex = r"New Question:\s+(.*)\n"
    rationale_regex = r"Rationale:\s+(.*)"
    new_question = re.search(new_question_regex, str(new_question_output)).group(1)
    rationale = re.search(rationale_regex, str(new_question_output)).group(1)
    ques_rat_list = [new_question, rationale]
    return ques_rat_list

def develop_document_title(new_question, persona_dict):
    doctitle_question = question_developer(new_question + "\nDocument Title:", persona_dict["doctitle_developer"])
    return str(doctitle_question)

def develop_file_title(new_question, persona_dict):
    filetitle_question = question_developer(new_question + "\nFile Title:", persona_dict["filetitle_developer"])
    return str(filetitle_question)

def determine_population_statement_template(new_question, persona_dict):
    intorexp_question = question_developer(new_question, persona_dict["intorexp_developer"])
    return str(intorexp_question)

def develop_population_statement(new_question, pop_statement_template, persona_dict):
    if "pico" in pop_statement_template.lower():
        pico_question = question_developer(new_question, persona_dict["PICO_developer"])
        pop_statement = pico_question
    elif "peco" in pop_statement_template.lower():
        pico_question = question_developer(new_question, persona_dict["PECO_developer"])
        pop_statement = pico_question
    elif "spider" in pop_statement_template.lower():
        spider_question = question_developer(new_question, persona_dict["SPIDER_developer"])
        pop_statement = spider_question
    return pop_statement

def develop_inclusion_exclusion_criteria(new_question, pop_statement, persona_dict):
    incexc_question = question_developer(str(pop_statement + "\nMy Research Question: " + new_question), persona_dict["incexc_developer"])
    return incexc_question

def develop_search_strategy(new_question, pop_statement, incexc_question, persona_dict):
    searchstrat_question = question_developer(str("My Research Question: " + new_question + "\nPopulation Statement: " + pop_statement + "\n" + incexc_question + "\n\n" + "Final Search Strategy:"), persona_dict["searchstrat_developer"])
    return searchstrat_question

def determine_databases_to_search(new_question, persona_dict):
    database_question = question_developer(str(new_question + "\nList of databases:"), persona_dict["database_developer"])
    return str(database_question)

def get_database_list(database_question, persona_dict):
    database_list = question_developer(str(database_question + "\nList:('"), persona_dict["list_returner"])
    if "and" in database_list:
        database_list = database_list.remove("and")
    database_list = eval(database_list)
    return database_list

def develop_database_search_strategies(database_list, searchstrat_question, persona_dict):
    all_database_strats = ""
    for database in database_list:
        database_strat = question_developer(str("My Search Strategy: " + searchstrat_question + "\nDatabase that will be searched: " + database + "\nSearch strategy specific to " + database + ":"), persona_dict["databasesearchstrat_developer"])
        all_database_strats += "\nStrategy for " + database + ":\n" + database_strat + "\n"
    return all_database_strats

def develop_pubmed_query(searchstrat_question, persona_dict):
    pubmed_question = question_developer(str(searchstrat_question) + "\n Pubmed Query: (", persona_dict["pubmedquery_developer"])
    return str(pubmed_question)

def write_summary_to_file(summary):
    with open('summary_file.txt', 'w', encoding='utf-8') as handle:
        for item in summary:
            handle.write(item + "\n")
