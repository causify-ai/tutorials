


<!-- toc -->

- [DATA605 Class Projects](#data605-class-projects)
  * [Choosing a project](#choosing-a-project)
  * [Working](#working)
  * [Pre-requisites](#pre-requisites)
  * [Project assignment](#project-assignment)
    + [Documentation](#documentation)
    + [Working on the project](#working-on-the-project)
  * [Example of a class project](#example-of-a-class-project)

<!-- tocstop -->


# DATA605 Class Projects

- The goal of the class project is to learn cutting-edge modern big data
  technology and write a (small) example of a system using it
- Each class project is similar in spirit to the tutorials for various
  technologies (e.g., Git, Docker, SQL, Mongo, Airflow, Dask) we have looked at and
  studied in classes

## Choosing a project

- Each student should pick one of the projects from the [signup sheet](https://docs.google.com/spreadsheets/d/1Ez5uRvOgvDMkFc9c6mI21kscTKnpiCSh4UkUh_ifLIw/edit?gid=0#gid=0)
  - The difficulty of the project does affect the final grade, but we want to
    give a way for everyone to select a project based on their level of computer
    literacy
  - Each project has a long description in the 
    [Google Doc](https://docs.google.com/document/d/1fEd7_oLhFnA5ovzj_HMb9EeMU84nOGEGeWqNRZSz2wo)
    under an header with the same name of the Project Name
  - You need to fill out the yellow fields in the 
    Google Sheet, such as Name, GitHub user, UMD ID, GitHub   
    issue, Date can add you to the repo
  - An easy project should take around 2-3 full-days to complete and will yield a B or C as grade, if well-done
  - A medium project should take around 4-5 full-days of work 
    to complete and will yield a A or B as grade, if well-done
  - A difficult project should take around 6-7 days of work
    to complete and will yield a A or A+ as grade, if well-done

- The project is individual
  - Students can discuss and help each other (they will do that even if we say
    not to)
  - Students should not have exactly the same project
  - If there are no more projects left for any reason, then we will add more

- The goal is to get your hands dirty and figure things out
  - Often working is all about trying different approaches until one works out
  - Google and ChatGPT are your friends, but don't abuse them: copy-pasting
    without understanding doesn't help you
  - Make sure you understand what a piece of code does
    and why
 
- On the sign-up sheet, you will find several baseline project proposals
  suggested by us. You can either choose from the given projects or propose your
  own project. You can improve, change, and add other technologies and components
  to enhance your project
- Your project choice should align with your learning goals and interests,
  presenting an excellent opportunity to explore various technologies and enhance
  your resume.

- When you choose one of the projects from the sign-up sheet, fill out the
  corresponding information promptly. If you decide to propose a modification,
  send us an email with the desired information and we will update the sign-up
  sheet and Google Doc for you.

- Please note that you are required to finalize your project selection within
  one week
- The project duration is approximately four weeks, so timely selection is
  crucial for effective planning and execution.

- Your grades will be influenced by factors such as project complexity, your
  efforts and understanding, and adherence to given project guidelines.

## Working

- You will work in the same way open-source developers (and specifically
  developers on Causify.AI) contribute to a project

- Each step of the project is delivered by committing code to your dir
  corresponding to your project ([more below](#submitting-project)) and doing a GitHub Pull Request
  (PR)
  - You can / should commit regularly and not only once at the end
  - This allows us to review intermediate results and give you feedback (like
    companies adopting Agile methodology do)
- We will do a review of the project in the middle of the project and give you
  some feedback on what to improve

- You can model your working setup locally by following the 
  in the (document)[https://github.com/causify-ai/helpers/blob/master/docs/onboarding/intern.set_up_development_on_laptop.how_to_guide.md] 

## Pre-requisites

- Watch, star, and fork the Causify.AI repo
- Install Docker on your computer
  - Ok to use Docker natively on Mac and Linux
  - Use VMware in Windows
    - If you have problems installing it on your laptop, use one computer from
      UMD or your friends
- After signing up for a project accept the invitation to collaborate sent to the
  email that you used to register your GitHub account, or check
  [here](https://github.com/causify-ai/tutorials/invitations)
- Check your GitHub issue on https://github.com/causify-ai/tutorials/issues
  - Make sure you are assigned to it

## Project assignment

- Each project requires the following steps
  - Create a Docker container installing all the needed tools (e.g., Redis and
    `redis-py`)
  - You should use Docker Compose to build single or multi-container systems
  - Jupyter notebook (if possible), otherwise a Python script implementing the
    project
  - Only Python3 on Linux/Mac should be used
  - You can always communicate with the tech using Python libraries or HTTP APIs

- Only Python should be used together with the needed configs for the specific
  tools
- Everything needs to run locally: no project should use cloud resources unless the project requires do that explicitly
  - E.g., it's not ok to use an AWS DB instance, you want to install Postgres in
    your container
- Make sure there is a way of building your project with Python, Docker

### Documentation

For your course project, you’re not just building something cool—you’re also
teaching others how to use a Big Data, AI, LLM, or data science tech (like
Redis or PyTorch). Instead of a project report, you’ll create a tutorial
that’s hands-on and beginner-friendly. Think of it as your chance to help a
classmate get started with the same tech. The goal of this tutorial help
pickup a new technology in 60 Minutes! That should make sure the tutorial is
not lengthy and covers all the important aspects a  developer should know
before 

You will submit your code as a package that include in accordance with the
following guidelines mentioned [here](https://github.com/causify-ai/tutorials/blob/master/docs/all.how_write_tutorials.how_to_guide.md):

- You will submit two markdown files 
  * `XYZ.API.md`: A markdown about the API and the software layer written by you on top of the native API
  * `XYZ.example.md`:  A markdown with a full example of an application     using the API


  - At least 1 page (60 lines): explain how to run the system by starting the
    container system, e.g.,
    - Report command lines
    - How the output looks like
    - ...
  - At least 3 pages (60 lines): describe exactly what you have done
    - Describe the script/notebook with examples of the output
    - Use diagrams (e.g., use `mermaid`)
    - Describe the schema used in the DB if you have any
    - ...

- The script/notebook should be able to run end-to-end without errors, otherwise
  the project is not considered complete
  Idelly the notebook should run correctly by executing 
  "Restart and Run all cells" before a commit is pushed.
  - We are not going to debug your code
  - If there are problems we will use the GitHub issue to communicate and we
    expect you to fix the problem

**NOTE**: The Markdown files should not be copy-paste of the notebook's cells and output.

### Working on the  project

- Each project will need to be organized like a proper open 
  source project, including filing issues, opening PRs, 
  checking in the code in https://github.com/causify-ai/tutorials

- The tag of your projects follows the schema
  `Spring{year}_{project_title_without_spaces}`
  - E.g., if the project title is "Redis cache to fetch user profiles", the tag
    is `Spring2025_Redis_cache_to_fetch_user_profiles`

- Create a GitHub issue with the project tag as title (e.g.,
  `Spring2025_Redis_cache_to_fetch_user_profiles`) and assign the issue to
  yourself
  - Copy/paste the description of the project and add a link to the Google doc
    with the description
  - We will use this issue to communicate as the project progresses

- Create a branch in Git named after your project
  - E.g., `TutorialsTask645_Redis_cache_to_fetch_user_profiles` 
  where 645 is the issue number. 
  ```
  > cd $HOME/src
  > git clone git@github.com:causify-ai/tutorials.git tutorials1
  > cd $HOME/src/tutorials1
  > git checkout master
  > git checkout -b TutorialsTask645_Redis_cache_to_fetch_user_profiles
  ...
  ```

- You should add files only under the directory corresponding to your project
  which is like `{GIT_ROOT}/sandbox/projects/{project_tag}`
  - E.g., on the dir cloned on my laptop the dir is named
    `~/src/tutorials1/sandbox/projects/TutorialsTask645_Redis_cache_to_fetch_user_profiles`

- You always need to create a PR from your branch and add your TAs and
  `@gpsaggese` as reviewers
  - Remember that you can't push directly to `master`
  - You can only push code to your branch

- Copy the files from the template project to your project

  ```bash
  > cd $GIT_ROOT
  > cp -r sandbox/projects/project_template sorrentum_sandbox/projects/{project_tag}
  > git add sorrentum_sandbox/projects/{project_tag}
  ```

- You can use consecutive branch and PR names as you make progress
  - E.g., `TutorialsTask645_Redis_cache_to_fetch_user_profiles_1`,
    `TutorialsTask645_Redis_cache_to_fetch_user_profiles_2`, ...

## Examples of a class project

- The layout of each project should follow the example in
  https://github.com/causify-ai/tutorials/tree/master/tutorial_asana
- Examples for neo4j in 
  https://github.com/causify-ai/tutorials/tree/master/tutorial_neo4j
- Projects from 2024 
  https://github.com/causify-ai/kaizenflow/tree/master/sorrentum_sandbox/spring2024
- The tutorials from DATA605 class 
