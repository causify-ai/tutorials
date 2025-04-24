<!-- toc -->

- [DATA605 Class Projects](#data605-class-projects)
  * [Choosing a project](#choosing-a-project)
  * [Pre-requisites](#pre-requisites)
    + [Contribution to the repo](#contribution-to-the-repo)
  * [Configuring your system](#configuring-your-system)
  * [Working on the project](#working-on-the-project)
    + [Documentation](#documentation)
  * [Submission](#submission)
  * [Examples of a class project](#examples-of-a-class-project)

<!-- tocstop -->

# DATA605 Class Projects

- The goal of the class project is to learn a cutting-edge modern big data
  technology and write a (small) example of a system using it
- Each class project is similar in spirit to the tutorials for various
  technologies we have looked at and studied in classes (e.g., Git, Docker, SQL,
  Mongo, Airflow, Dask)
- Through the class projects you will learn how a tool fits your data science,
  data engineering, machine learning workflows.

## Choosing a project

- Each student should pick one project from the
  [signup sheet](https://docs.google.com/spreadsheets/d/1Ez5uRvOgvDMkFc9c6mI21kscTKnpiCSh4UkUh_ifLIw/edit?gid=0#gid=0)
  - The difficulty of the project does affect the final grade, but we want to
    give a way for everyone to select a project based on their level of computer
    literacy
  - Each project has a description in the
    [Google Doc](https://docs.google.com/document/d/1fEd7_oLhFnA5ovzj_HMb9EeMU84nOGEGeWqNRZSz2wo)
    under a header with the same name of the Project Name
  - You need to fill out the yellow fields in the
    [signup sheet](https://docs.google.com/spreadsheets/d/1Ez5uRvOgvDMkFc9c6mI21kscTKnpiCSh4UkUh_ifLIw/edit?gid=0#gid=0),
    such as Name, GitHub user, UMD ID, Date
  - Once done, we will add you to the repo so that you can start working

- The project is individual
  - Students can discuss and help each other (they will do that even if we say
    not to)
  - Students should not have exactly the same project

- The goal is to get your hands dirty and figure things out
  - Often working is all about trying different approaches until one works out
  - Make sure you code by understanding the tool and what your code is doing
    with it
  - Google and ChatGPT are your friends, but don't abuse them: copy-pasting code
    is not recommended and won't benefit the learning outcomes
- The projects are designed in a way that once you understand the underlying
  technology:
  - Easy Project: Takes 2-3 days to complete
  - Medium Difficulty Project: Takes 4-5 to complete
  - Difficult Project: Takes 6-8 to complete.

- It is highly recommended to choose a project from the sign up sheet
  - If you really need to propose a new idea or suggest modifications, please
    contact us: we will review but we won't guarantee we can accommodate all
    requests
- Your project should align with your learning goals and interests, offering a
  great opportunity to explore various technologies and strengthen your resume.
- If selecting a project from the sign-up sheet, ensure you fill out the
  corresponding details promptly. For modifications, email us with the necessary
  information, and we will update the sign-up sheet and Google Doc accordingly.
- **Project selection must be finalized within one week** to allow sufficient
  time for planning and execution.
- The project duration is approximately **four weeks**, making timely selection
  crucial.
- Your grade will be based on **project complexity, effort, understanding, and
  adherence to guidelines**.

**NOTE**:

- If you choose to use a paid service, you are responsible for the costs
  incurred. In any case, you are expected to use the services efficiently to keep
  them within free tier usage
- To save costs/improve usage, you should make sure that the services are turned
  off/shutdown when not being used.

## Pre-requisites

- Watch, star, and fork the Causify.AI repos
  - [tutorials](https://github.com/causify-ai/tutorials)
  - [kaizenflow](https://github.com/causify-ai/kaizenflow)
  - [helpers](https://github.com/causify-ai/helpers)

- Install Docker on your computer
  - You can use Docker natively on Mac and Linux
  - Use VMware in Windows or dual-boot
    - If you have problems installing it on your laptop, it recommended to use
      one computer from UMD, or perhaps a device of one your friends
- After signing up for a project accept the invitation to collaborate sent to
  the email that you used to register your GitHub account, or check
  [here](https://github.com/causify-ai/tutorials/invitations)
- Check your GitHub issue on https://github.com/causify-ai/tutorials/issues
  - Make sure you are assigned to it
- Only Python should be used together with the needed configs for the specific
  tools
  - You can always communicate with the tech using Python libraries or HTTP APIs

- Unless specified by project description, everything needs to run locally
  without using cloud resources.
  - E.g., it's not ok to use an AWS DB instance, you want to install Postgres in
    your container for any database requirements

### Contribution to the repo

- You will work in the same way open-source developers (and specifically
  developers on Causify.AI) contribute to a project

- Each project will need to be organized like a proper open source project,
  including filing issues, opening PRs, checking in the code in
  https://github.com/causify-ai/tutorials

- Set up your working environment by following the instructions in the
  [document](/helpers_root/docs/onboarding/intern.set_up_development_on_laptop.how_to_guide.md)

- Each step of the project is delivered by committing code to the dir
  corresponding to your project and doing a GitHub Pull Request (PR)
  - You should commit regularly and not just once at the end
  - We will specifically do a reviews of intermediate results of the project and
    give you some feedback on what to improve (adopting Agile methodology)

- **Project Tag Naming Convention**
  - Your project tag should follows this format:
    `Spring{year}_{project_title_without_spaces}`
    - Example: if your project title is **"Redis cache to fetch user
      profiles"**, your project branch will be:
      **`Spring2025_Redis_cache_to_fetch_user_profiles`**

- **Create a GitHub Issue**
  - Create a **GitHub issue** with your **project tag** as the title.
    - Example: `Spring2025_Redis_cache_to_fetch_user_profiles`
  - Copy/paste the project description and add a link to the Google Doc with the
    details.
  - Assign the issue to yourself.
  - We will use this issue for project-related discussions.
  - Update the
    [signup sheet](https://docs.google.com/spreadsheets/d/1Ez5uRvOgvDMkFc9c6mI21kscTKnpiCSh4UkUh_ifLIw/edit?gid=0#gid=0)
    with the git hub issue link.

- **Create a Git Branch Named After the Issue**
  - Name your Git branch as follows: `TutorTask{issue_number}_{project_tag}`
    - Example: If your issue number is **#645**, your branch name should be:
      **`TutorTask645_Spring2025_Redis_cache_to_fetch_user_profiles`**

- **Steps to create the branch:**

  ```bash
  > cd $HOME/src
  > git clone --recursive git@github.com:causify-ai/tutorials.git tutorials1
  > cd $HOME/src/tutorials1
  > git checkout master
  > git checkout -b TutorTask645_Spring2025_Redis_cache_to_fetch_user_profiles
  ```

- **Add Files Only in Your Project Directory**
  - Add your project files under the following directory:
    `{GIT_ROOT}/DATA605/Spring2025/projects/{branch_name}`
    - Example: If you cloned the repo on your laptop, your directory should be:
      `~/src/tutorials1/DATA605/Spring2025/projects/TutorTask645_Spring2025_Redis_cache_to_fetch_user_profiles`
  - Copy the template files to the project directory:
    ```bash
    > cp -r ~/src/tutorials1/DATA605/tutorial_template/ ~/src/tutorials1/DATA605/Spring2025/projects/{branch_name}
    ```
  - Start working on the files

- **Create a Pull Request (PR)**:
  - Always create a **Pull Request (PR)** from your branch.
  - Add your TAs (e.g., `@tkpratardan`, `@Prahar08modi`) and `@gpsaggese` as
    reviewers.
  - You cannot push directly to the `master` branch. Only push commits to **your
    project branch.**

- **Naming for Consecutive Updates**
  - When making progress, use incremental branch names by appending `_1`, `_2` to
    your branch name, etc.
    - Example:
      - `TutorTask645_Spring2025_Redis_cache_to_fetch_user_profiles_1`
      - `TutorTask645_Spring2025_Redis_cache_to_fetch_user_profiles_2`

## Configuring your system

Before starting implementation, you need to choose **one** of the two supported Docker-based workflows. Finalize your setup choice before proceeding with development.

### 1. Simple Docker Setup (`data605_style`) — Recommended for Students

- A minimal and straightforward setup, modeled after what we use in DATA605 tutorials.
- The environment comes with Python, Jupyter, and commonly-used packages already installed.
- Simple scripts (`docker_build.sh`, `docker_bash.sh`, `docker_jupyter.sh`) help you build the container, launch it, and start working immediately.
- Ideal for students who:
  - Are new to Docker or want to avoid setup overhead
  - Need a reliable, pre-built environment to focus on the tutorial and project code

- You may still customize the Dockerfile, expose other ports, or add project-specific dependencies as needed.

### 2. Causify-style Thin Docker Environment (`causify_style`)

- A production-style Docker setup used in internships, RA/TA work, at Causify AI.
- Uses a thin Docker layer, with logic written in Python and reusable script structure.

- **Why choose this?**
  - Encouraged for students familiar with Docker or looking to grow into advanced workflows
  - Recommended for contributing to Causify, MSML610, and DATA605 long-term projects

- Setup Guide:
  - To configure your system for this approach, follow this detailed guide:  
    - [Set Up Development on Laptop](https://github.com/causify-ai/helpers/blob/master/docs/onboarding/intern.set_up_development_on_laptop.how_to_guide.md)

  - You may also refer to this reference checklist curated for interns:  
    - [Intern Onboarding Reference](https://github.com/causify-ai/helpers/blob/master/docs/onboarding/intern.onboarding_checklist.reference.md#must-read)

> *Note: You don’t have to follow everything in the intern checklist — it’s meant to help you become a better developer/researcher.*

### Want to Learn More?

If you’re unsure which setup is best or want to explore both, refer to the full breakdown in the tutorial template:  
  - [Tutorial Template: Two Docker Approaches](https://github.com/causify-ai/tutorials/blob/master/DATA605/tutorial_template/README.md)

## Working on the project

### Project Goal

- For your course project, you're not just building something cool, but you're
  also teaching others how to use a Big Data, AI, LLM, or data science tech
- As a project report, you'll create a tutorial that's hands-on and
  beginner-friendly
  - Think of it as your chance to help a classmate get started with the same
    tech
  - The goal of this tutorial is to help pickup a new technology in 60 Minutes!
  - That should make sure the tutorial is not lengthy and covers all the
    important aspects a developer should know before starting building with that
    technology.

### Understanding the deliverables

- Use the project template files in `//tutorials/DATA605/tutorial_template` to
  understand the deliverables and the coding style. They consist of:

- **Utils Module**:
  - This file is meant to contain helper functions, reusable logic, and API wrappers.
  - Keep the notebooks focused on documentation and outputs. Place any logic or workflow functions inside this module.
- **Scripts/Notebooks**:
  - You will work on one API file and one Example (Your project) file.
  - We encourage you to use Python files (Utils module) and call the code from notebooks.
- **Markdowns**:
  - One markdown file linked to each python script, i.e, API and example.

For more guidance on this structure and the rationale behind it, see [How to write the Tutorial](https://github.com/causify-ai/tutorials/blob/master/docs/all.how_write_tutorials.how_to_guide.md).

In general

- For API: you are expected to describe the API, its architecture, etc.
- For Example: You are expected to use the project tool according to the
  specifications mentioned in
  [Google Doc](https://docs.google.com/document/d/1fEd7_oLhFnA5ovzj_HMb9EeMU84nOGEGeWqNRZSz2wo)

## Submission

Your submission must include the following files:

1. `XYZ.API.md`:  
   - A markdown file documenting the native API and the software layer you have written on top of it

2. `XYZ.API.ipynb`:  
   - A Jupyter notebook demonstrating usage of the native API and your wrapper layer, with clean, minimal cells

3. `XYZ.example.md`:  
   - A markdown file presenting a complete example of an application that uses your API layer

4. `XYZ.example.ipynb`:  
   - A Jupyter notebook corresponding to the example above, demonstrating end-to-end functionality

5. `XYZ_utils.py`:  
   - A Python module containing reusable utility functions and wrappers around the API
   - The notebooks should invoke logic from this file instead of embedding complex code inline

### Submission Guidelines

- Each markdown file should explain the intent and design decisions:
  - Avoid copy-pasting code cells or raw outputs from the notebooks
  - Instead, use the markdown to communicate the reasoning behind your choices

- Each notebook should:
  - Be self-contained and executable from top to bottom via "Restart and Run All"
  - Use functions from `XYZ_utils.py` to keep the cells concise and maintainable
  - Demonstrate functionality clearly and logically with clean, commented outputs

- Docker setup:
  - Include clear instructions on how to build and run your Docker container
  - Mention expected terminal outputs when running scripts (e.g., starting Jupyter, mounting volumes, etc.)

- Visual documentation:
  - Include diagrams and flowcharts when relevant (e.g., using `mermaid`)
  - Provide schema descriptions if your project uses a database or structured data

- Projects that do not run end-to-end or lack proper documentation will be considered incomplete
  - In case of issues, they will be flagged through GitHub issues, and you will be expected to resolve them in a timely manner

## Examples of a class project

The layout of each project should follow the examples in

- Example for
  [langchain tutorial](https://github.com/causify-ai/tutorials/tree/master/tutorial_langchain)
- Examples for
  [neo4j](https://github.com/causify-ai/tutorials/tree/master/tutorial_neo4j)
- Example for
  [open_ai tutorial](https://github.com/causify-ai/tutorials/tree/master/tutorial_openai)
- Example for
  [github tutorial (data605_style)](https://github.com/causify-ai/tutorials/tree/master/tutorial_github_data605_style)
- Example for
  [github tutorial (causify_style)](https://github.com/causify-ai/tutorials/tree/master/tutorial_github_causify_style)

> Note that the tutorials from DATA605 class are built using a simpler approach
  for Docker and bash (e.g., `bash` scripts instead of Python code)
