# Implementation Plan for SynthScope

## Overview

SynthScope is an automatic systematic review tool that leverages advanced AI LLMs (large language models) to quickly and accurately summarize and synthesize large volumes of scientific literature imported by the user. With SynthScope, users can automate the title/abstract and full-text screening stages of the literature review process, saving time and reducing errors while focusing on the analysis and insights that matter most to their research.

## Key Features
- Automated literature screening using advanced AI LLMs
- Fast and accurate summarization and synthesis of scientific literature
- Supports a wide range of research fields and domains
- Saves time and reduces errors in the literature review process
- Can complete reviews in most languages 

### Core Components

- [ ] SynthScope Shell

### Development Phases
#### Phase 1: Development of Core Functionality:
- Repository and Documentation
    - Clean up the existing code repository or create a new one with only the required parts.
    - Remove unnecessary files and code from the existing repository.
    - Organize the code into modular components for easy maintenance and updates.
    - Document plan for modules that are needing to be completed, next steps, and other relevant information in the repository.
    - Create a detailed README file outlining the project's purpose, structure, and instructions for use.
    - Document all code using comments and docstrings to ensure clarity and maintainability.
- Web App Interface
    - Develop a user-friendly web app interface using Streamlit or a similar framework.
    - Module for importing literature sources (e.g., CSV, XML, or direct API integration with databases)
    - Module for configuring AI model settings (e.g., sensitivity, specificity, or summarization length)
    - Module for displaying summarized and synthesized results
    - Module for exporting results (e.g., CSV, Word, or PDF format)
- Implement an API for easy integration with other platforms and tools.
    - Develop a RESTful API with clear documentation and examples.
    - Ensure that the API supports common authentication methods and adheres to best practices for security and performance.
    - Include API endpoints for literature import, AI model configuration, result retrieval, risk of bias, and summarisation
#### Phase 2: Validation and Testing
- Design and conduct a validation study.
    - Establish a validation study protocol, including the selection of systematic reviews, performance metrics, and statistical analysis methods.
    - Develop a procedure for selecting a diverse range of highly-cited systematic reviews across multiple research fields and domains to test SynthScope's performance.
    - Test SynthScope on a range of highly-cited systematic reviews, comparing its sensitivity and specificity to human-completed studies.
    - Tweak synthscope until getting comparable results with just the initial small team
- Implement the validation study protocol by running SynthScope on the selected systematic reviews and comparing its output to human-completed reviews:
    Calculate performance metrics, such as sensitivity, specificity, positive predictive value (PPV), negative predictive value (NPV), and time-to-result to assess the accuracy of SynthScope.
    - Another layer of tweak and refine the AI model and functionality until it achieves similar accuracy to human reviewers.
- Analyze the results of the initial validation study to identify areas of improvement in SynthScope's AI model and functionality.
    - Iterate on the AI model and application features, incorporating feedback from collaborators and the findings of the validation study.
    - Conduct further validation with five independent researchers internationally.
- Engage five independent researchers from diverse research fields to test SynthScope on their own systematic reviews.
    - Collect feedback and performance metrics from these researchers to further validate SynthScope's accuracy and utility in real-world scenarios.


- Design a Statistically Sound Validation Study:
    - Collaborate with Brendon Stubbs and Trevor Thompson to design a validation study that meets statistical rigor.
    - Determine the sample size of systematic reviews for testing, ensuring adequate power to detect meaningful differences between human and AI performance.
    - Select a diverse range of highly-cited systematic reviews, covering various research fields and domains.
    - Develop a standardized process for comparing SynthScope's performance to human-completed studies, considering factors such as sensitivity,- Collaborate with Brendon Stubbs and Trevor Thompson to design and conduct a validation study.
- Testing:
    - Run SynthScope on a range of highly-cited systematic reviews (**n=?**), comparing its sensitivity and specificity to human-completed studies.
    - Tweak and refine the model, and functionality until it achieves similar accuracy to human reviewers.
    - Include a time-to-completion metric to compare the speed of SynthScope to human reviewers.
    - Conduct further validation with five independent researchers internationally.
#### Phase 3: Finalization and Publication
Summarize the findings of the validation studies and the tool's performance in a scientific paper.

Describe the validation study methodology, including the selection of systematic reviews, performance metrics, and statistical analysis methods.
Report the performance of SynthScope compared to human-completed reviews, highlighting its accuracy, sensitivity, specificity, PPV, and NPV.
Collaborate with co-authors and research partners to finalize and submit the paper for publication.

Work with collaborators to revise the manuscript based on feedback and peer review.
Submit the paper to a relevant journal for publication.
Launch the SynthScope web app and API for public use.

Ensure that the web app and API are fully functional and optimized for performance and security before launching.
Provide comprehensive documentation and user support materials.
Develop a marketing and outreach strategy to promote the tool within the research community.

Leverage social media, blog posts, and conference presentations to raise

## Timeline
- Phase 1: Development of Core Functionality (2-3 months)
- Phase 2: Validation and Testing (3-4 months)
- Phase 3: Finalization and Publication (1-2 months)

## Project Leads
- ***Patrick Gould*** - UNSW School of Psychiatry
    - *Overall project coordination software development*
- ***Joseph Jakes*** - UNSW School of Psychology (Confirm)
    - *Software development and extended functionality *

## Collaborators
- ***Prof Phil Ward*** - UNSW School of Psychiatry
    - *Navigating testing/publication/and networks with other researchers*
- ***Dr Brendon Stubbs*** - King's College London
    - *Systematic review expert and helping lead the evaluation of sensitivity and specificty*
- ***Dr Trevor Thompson*** - Grenwich (confirm)
    - *Statistics and networked meta analysis expert. Assistance with validation plan and initial development of validation software*
